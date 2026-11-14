"""Scientific publication, vector audit, LaTeX and comparison regression."""

from __future__ import annotations

from dataclasses import replace
import csv
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from .comparison import ExperimentRun, compare_runs, controlled_p1_registry
from .import_obj import import_obj
from .publication import (_scan_pdf, _scan_svg, export_p1_paper_figure,
                          WIDTH_MM, HEIGHT_MM)

BASE = Path(__file__).parent / 'fixtures' / 'real_p1'
OBJ = BASE / 'accepted.obj'
REPORT = BASE / 'generator_report.json'
SOURCE_SHA = 'cbf6cd6308ba54544d06c5d562c491eb7d43ddb216365e0e9d188fd3430295e0'


def record(name='run1', **kw):
    base=dict(run_id=name, topology='tri', sizing='isotropic',
              evidence='synthetic', status='accepted',source_model_id='unit-square',
              source_model_sha256='a'*64,source_mesh_sha256='b'*64,
              metric_id='shape.v1',metric_value=.7,metric_units='dimensionless',
              element_count=12)
    base.update(kw)
    return ExperimentRun(**base)


class ExperimentMatrixTests(unittest.TestCase):
    def test_empty_matrix_has_six_explicit_missing_cells(self):
        result=compare_runs(())
        self.assertEqual(len(result['cells']),6)
        self.assertTrue(all(v['status']=='NOT_AVAILABLE' for v in result['cells']))
        self.assertFalse(result['comparable_pairs'])

    def test_p1_fixed16_not_falsely_labeled_isotropic_measurement(self):
        result=controlled_p1_registry(SOURCE_SHA)
        self.assertEqual(len(result['outside_factorial_studies']),1)
        self.assertEqual(result['outside_factorial_studies'][0]['accepted_adaptive_epochs'],0)
        self.assertEqual(len([c for c in result['cells'] if c['status']!='NOT_AVAILABLE']),0)

    def test_two_same_metric_compatible_synthetic_runs(self):
        result=compare_runs((record(),record('run2',metric_value=.75,
                         source_mesh_sha256='c'*64,topology='quad_tri')))
        self.assertEqual(len(result['comparable_pairs']),1)
        self.assertEqual(result['comparable_pairs'][0]['evidence'],'synthetic')
        self.assertEqual(result['cells'][0]['status'],'SYNTHETIC_ONLY')

    def test_incompatible_metric_never_compares_two_values(self):
        result=compare_runs((record(), record('run2',metric_id='quad_jacobian_v1')))
        self.assertEqual(result['comparable_pairs'],[])

    def test_incompatible_models_never_compare_two_values(self):
        result=compare_runs((record(),record('run2',source_model_sha256='f'*64)))
        self.assertEqual(result['comparable_pairs'],[])

    def test_mixed_real_and_synthetic_never_compares(self):
        result=compare_runs((record(),record('run2',evidence='source_measured')))
        self.assertEqual(result['comparable_pairs'],[])

    def test_rejected_run_retained_but_not_accepted(self):
        result=compare_runs((record('reject',status='rejected'),))
        self.assertEqual(result['cells'][0]['status'],'REJECTED_ONLY')
        self.assertEqual(result['cells'][0]['rejected_runs'],['reject'])
        self.assertFalse(result['comparable_pairs'])

    def test_invalid_metric_nan_is_rejected(self):
        with self.assertRaisesRegex(ValueError,'invalid_metric_value'):
            record(metric_value=float('nan'))

    def test_real_claim_without_model_hash_rejected(self):
        with self.assertRaisesRegex(ValueError,'unverified_model_source_hash'):
            record(evidence='source_measured',source_model_sha256=None)

    def test_duplicate_run_id_is_rejected(self):
        with self.assertRaisesRegex(ValueError,'duplicate_run_id'):
            compare_runs((record(), record()))

    def test_metric_definition_and_units_required(self):
        with self.assertRaisesRegex(ValueError,'metric_units_required'):
            record(metric_units=None)
        with self.assertRaisesRegex(ValueError,'metric_id_value_mismatch'):
            record(metric_value=None)


class ScientificFigureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory()
        cls.out=Path(cls.tmp.name)/'p1'
        cls.report=export_p1_paper_figure(OBJ,REPORT,cls.out)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_source_and_inventory_provenance(self):
        self.assertEqual(self.report['source_obj_sha256'],SOURCE_SHA)
        self.assertEqual(self.report['cell_inventory'],{'quad':42,'triangle':36})
        self.assertFalse(self.report['synthetic'])
        self.assertEqual(self.report['adaptive_epochs'],0)

    def test_vector_svg_has_no_images_or_active_objects(self):
        svg=_scan_svg(self.out/'figure.svg')
        self.assertTrue(svg['vector_only'])
        self.assertEqual(svg['image_elements'],0)
        self.assertGreater(svg['path_elements'],78)

    def test_true_vector_pdf_and_embedded_fonts(self):
        gate=_scan_pdf(self.out/'figure.pdf',WIDTH_MM,HEIGHT_MM)
        self.assertTrue(gate['vector_only_no_image_xobjects'])
        self.assertGreaterEqual(gate['font_inventory'],2)

    def test_source_p1_quality_samples_are_36_triangles_only(self):
        with (self.out/'triangle_quality.csv').open(newline='') as stream:
            rows=list(csv.DictReader(stream))
        self.assertEqual(len(rows),36)
        self.assertTrue(all(row['element_type']=='triangle' for row in rows))
        self.assertTrue(all(0<float(row['triangle_mean_ratio_3d_v1'])<=1 for row in rows))
        recipe=json.loads((self.out/'figure.recipe.json').read_text())
        self.assertEqual(recipe['quad_planar_quality'],'NOT_EVALUABLE_NONPLANAR')
        self.assertEqual(recipe['accepted_adaptive_epochs'],0)

    def test_cannot_overwrite_existing_figure_package(self):
        with self.assertRaises(FileExistsError):
            export_p1_paper_figure(OBJ,REPORT,self.out)

    def test_independent_regeneration_is_byte_identical(self):
        with tempfile.TemporaryDirectory() as tmp:
            target=Path(tmp)/'p1'
            export_p1_paper_figure(OBJ,REPORT,target)
            for orig in self.out.iterdir():
                if orig.is_file():
                    self.assertEqual(hashlib.sha256(orig.read_bytes()).digest(),
                                     hashlib.sha256((target/orig.name).read_bytes()).digest(), orig.name)

    def test_modified_original_obj_rejected_before_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'modified.obj'
            path.write_bytes(OBJ.read_bytes().replace(b'v ',b'v  ',1))
            with self.assertRaises((ValueError,AssertionError)):
                export_p1_paper_figure(path, REPORT, Path(tmp)/'no_result')
            self.assertFalse((Path(tmp)/'no_result').exists())

    def test_false_generator_receipt_rejected_before_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad=json.loads(REPORT.read_text())
            bad['adaptive_epochs']=2
            path=Path(tmp)/'false.json'
            path.write_text(json.dumps(bad))
            with self.assertRaises((ValueError,AssertionError)):
                export_p1_paper_figure(OBJ,path,Path(tmp)/'no_result')
            self.assertFalse((Path(tmp)/'no_result').exists())

    def test_svg_raster_and_external_dependency_mutations_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            for malicious in ('<image href="data:image/png;base64,a"/>',
                              '<script>evil</script>',
                              '<use href="https://example.com/a"/>'):
                path=Path(tmp)/'bad.svg'
                text=(self.out/'figure.svg').read_text()
                text=text.replace('</svg>', malicious+'</svg>')
                path.write_text(text)
                with self.assertRaises(ValueError):
                    _scan_svg(path)

    def test_pdf_with_raster_image_is_rejected(self):
        from reportlab.pdfgen import canvas
        from reportlab.lib.utils import ImageReader
        from PIL import Image
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'image.pdf'
            c=canvas.Canvas(str(path),pagesize=(WIDTH_MM*72/25.4,HEIGHT_MM*72/25.4))
            c.drawImage(ImageReader(Image.new('RGB',(4,4),(100,200,50))),50,50,40,40)
            c.save()
            with self.assertRaisesRegex(ValueError,'pdf_contains_raster_image_xobject'):
                _scan_pdf(path,WIDTH_MM,HEIGHT_MM)

    def test_pdf_in_tex_has_double_column_width_and_source_limits(self):
        latex=(self.out/'include.tex').read_text()
        self.assertIn(r'\begin{figure*}',latex)
        self.assertIn(r'width=\textwidth',latex)
        self.assertIn('not establish adaptive epochs',latex)

    def test_latex_smoke_compiles_with_actual_vector_pdf_when_available(self):
        if not shutil.which('pdflatex'):
            self.skipTest('LaTeX toolchain unavailable; gate must remain OPEN')
        doc=(r'\documentclass[twocolumn]{article}'+'\n'+
             r'\usepackage{graphicx}'+'\n'+
             r'\begin{document}'+'\n'+
             r'\section{Controlled P1 source}'+'\n'+
             r'\input{include.tex}'+'\n'+
             r'\clearpage'+'\n'+
             r'\end{document}'+'\n')
        (self.out/'smoke.tex').write_text(doc)
        result=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error',
                               '-output-directory',str(self.out),'smoke.tex'],
                              cwd=self.out,capture_output=True,text=True,timeout=40)
        self.assertEqual(result.returncode,0,result.stdout[-900:]+result.stderr[-400:])
        self.assertTrue((self.out/'smoke.pdf').is_file())


class DesktopGateTests(unittest.TestCase):
    def test_smoke_entry_is_importable_without_qt(self):
        from . import desktop_smoke
        self.assertTrue(callable(desktop_smoke.run_gui_smoke))

    def test_no_qt_is_explicit_blocker_not_fake_success(self):
        import importlib.util
        if all(importlib.util.find_spec(m) for m in ('PySide6','pyvista','pyvistaqt')):
            self.skipTest('Qt installed: run actual GUI via --smoke-output')
        p=subprocess.run(['python','-m','tools.mesh_studio.desktop_app',
                          '--smoke-output','not_written_without_qt.json'],
                         capture_output=True,text=True,timeout=20)
        self.assertEqual(p.returncode,2)
        self.assertIn('dependencies unavailable',p.stderr)
        self.assertFalse(Path('not_written_without_qt.json').exists())


if __name__=='__main__':
    unittest.main()
