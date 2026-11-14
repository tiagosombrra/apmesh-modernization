"""Regression, numerical integrity and publication audits for S5b mocks."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from .experiment_history import (HistoryError, load_synthetic_history,
                                 summarize_synthetic_history)
from .multi_model_publication import (CASES, HISTORY, FIXTURES,
                                      export_synthetic_comparison_bundle,
                                      FIG_W_MM, FIG_H_MM)
from .publication import _scan_pdf, _scan_svg


class HistoryTruthTests(unittest.TestCase):
    def test_fixture_epoch_inventory_and_rejected_attempts(self):
        events, digest = load_synthetic_history(HISTORY)
        summary = summarize_synthetic_history(events, digest)
        self.assertEqual(len(events), 8)
        self.assertEqual(len(summary['groups']), 2)
        self.assertEqual([g['accepted_epochs'] for g in summary['groups']], [[0, 1, 3], [0, 1, 3]])
        self.assertEqual([g['rejected_candidate_epochs'] for g in summary['groups']], [[2], [2]])
        self.assertEqual(summary['evidence_kind'], 'SYNTHETIC_TEST_DATA_NOT_MEASURED')

    def _mutate(self, before: str, after: str) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)/'history.csv'
            original = HISTORY.read_text(encoding='utf-8')
            self.assertIn(before, original)
            p.write_text(original.replace(before, after, 1), encoding='utf-8')
            with self.assertRaises(HistoryError):
                load_synthetic_history(p)

    def test_refuses_real_claim_without_real_data_schema(self):
        self._mutate(',True\n', ',False\n')

    def test_refuses_duplicate_event_and_invalid_negative_error(self):
        self._mutate('tri,1,accepted', 'tri,0,accepted')
        self._mutate('tri,1,accepted,0.55', 'tri,1,accepted,-0.55')

    def test_refuses_unqualified_missing_or_malformed_epoch(self):
        self._mutate('tri,1,accepted', 'tri,12,accepted')
        self._mutate('tri,2,rejected', 'tri,2,published')
        self._mutate('tri,1,accepted,0.55,38', 'tri,1,accepted,0.55,0')

    def test_refuses_nan_nonfinite_or_undocumented_columns(self):
        self._mutate('tri,1,accepted,0.55', 'tri,1,accepted,nan')
        self._mutate('dataset,method,epoch', 'dataset,algorithm,epoch')

    def test_accepted_error_increase_is_allowed_and_not_silenced(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)/'history.csv'
            original = HISTORY.read_text(encoding='utf-8')
            p.write_text(original.replace('tri,1,accepted,0.55',
                                          'tri,1,accepted,1.2', 1), encoding='utf-8')
            events, digest = load_synthetic_history(p)
            report = summarize_synthetic_history(events, digest)
            tri = next(g for g in report['groups'] if g['method'] == 'tri')
            self.assertEqual(tri['accepted_nonmonotone_error_steps'], [1])
            self.assertEqual(tri['rejected_candidate_epochs'], [2])

    def test_maximum_data_size_enforced(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)/'history.csv'
            p.write_bytes(b'x'*65537)
            with self.assertRaisesRegex(HistoryError, 'history_file_too_large'):
                load_synthetic_history(p)


class SyntheticComparisonPublicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory()
        cls.output = Path(cls.directory.name)/'figures'
        cls.receipt = export_synthetic_comparison_bundle(cls.output)

    @classmethod
    def tearDownClass(cls):
        cls.directory.cleanup()

    def test_gallery_inventory_is_typed_and_source_hashed(self):
        with (self.output/'topology_inventory.csv').open(newline='') as stream:
            import csv
            lines = list(csv.DictReader(stream))
        self.assertEqual([(int(r['triangles']),int(r['quads'])) for r in lines],
                         [(8, 0), (8, 1), (0, 4)])
        self.assertTrue(all(r['synthetic'] == 'true' and len(r['source_sha256']) == 64
                            for r in lines))
        recipe = json.loads((self.output/'figure.recipe.json').read_text())
        self.assertTrue(recipe['not_comparable_across_methods'])
        self.assertEqual(recipe['camera_policy'],
                         'PER_PANEL_INDEPENDENT_FIT_NOT_MATCHED_PHYSICAL_VIEW')
        self.assertTrue(recipe['source_P1_outside_comparison_matrix'])

    def test_history_records_rejected_not_as_accepted(self):
        summary = json.loads((self.output/'history_summary.json').read_text())
        self.assertEqual(summary['rows'], 8)
        self.assertEqual([g['rejected_candidate_epochs'] for g in summary['groups']], [[2], [2]])
        with (self.output/'epoch_events.csv').open(newline='') as stream:
            import csv
            rows = list(csv.DictReader(stream))
        self.assertEqual(sum(r['status']=='rejected' for r in rows),2)
        self.assertEqual(sum(r['status']=='accepted' for r in rows),6)
        self.assertTrue(all(r['synthetic']=='true' for r in rows))

    def test_all_adaptive_comparison_cells_are_not_available(self):
        matrix = json.loads((self.output/'study_matrix.json').read_text())
        self.assertEqual(len(matrix['cells']),6)
        self.assertTrue(all(c['status']=='NOT_AVAILABLE' for c in matrix['cells']))
        self.assertEqual(matrix['outside_factorial_studies'][0]['accepted_adaptive_epochs'],0)

    def test_both_figures_are_true_vector_with_fonts(self):
        for prefix in ('topology_gallery','epoch_timeline'):
            svg = _scan_svg(self.output/f'{prefix}.svg')
            pdf = _scan_pdf(self.output/f'{prefix}.pdf',FIG_W_MM,FIG_H_MM,min_drawings=20)
            self.assertTrue(svg['vector_only'])
            self.assertGreater(svg['path_elements'],40)
            self.assertTrue(pdf['vector_only_no_image_xobjects'])
            self.assertGreaterEqual(pdf['font_inventory'],2)

    def test_input_corruption_rejected_before_creating_figures(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'history.csv'
            path.write_text(HISTORY.read_text().replace('tri,1,accepted,0.55',
                                                        'tri,1,accepted,nan'),encoding='utf-8')
            with self.assertRaises(HistoryError):
                export_synthetic_comparison_bundle(Path(tmp)/'bad',history_csv=path)
            self.assertFalse((Path(tmp)/'bad').exists())

    def test_real_or_unqualified_source_refused_as_synthetic(self):
        with tempfile.TemporaryDirectory() as tmp:
            area=Path(tmp)/'fixtures';area.mkdir()
            for _, name in FIXTURES:
                shutil.copyfile(CASES/name, area/name)
                shutil.copyfile((CASES/name).with_suffix('.json'),(area/name).with_suffix('.json'))
            obj=area/FIXTURES[0][1]
            obj.write_text(obj.read_text().replace('SYNTHETIC', 'MEASURED',1))
            with self.assertRaisesRegex(Exception,'source_sha_mismatch'):
                export_synthetic_comparison_bundle(Path(tmp)/'bad',fixture_dir=area)
            self.assertFalse((Path(tmp)/'bad').exists())

    def test_regeneration_is_byte_for_byte_reproducible(self):
        with tempfile.TemporaryDirectory() as tmp:
            other=Path(tmp)/'repeat'
            export_synthetic_comparison_bundle(other)
            for original in self.output.iterdir():
                if original.is_file():
                    self.assertEqual(sha256(original.read_bytes()).digest(),
                                     sha256((other/original.name).read_bytes()).digest(),
                                     original.name)

    def test_reject_overwrite(self):
        with self.assertRaises(FileExistsError):
            export_synthetic_comparison_bundle(self.output)

    def test_latex_figure_pair_compiles(self):
        if not shutil.which('pdflatex'):
            self.skipTest('TeX not installed; manual LaTeX gate pending')
        with tempfile.TemporaryDirectory() as tmp:
            directory=Path(tmp)
            for name in ('include.tex','topology_gallery.pdf','epoch_timeline.pdf'):
                shutil.copy2(self.output/name,directory/name)
            source=('\\documentclass[twocolumn]{article}\n'
                    '\\usepackage{graphicx}\n'
                    '\\begin{document}\n'
                    '\\input{include.tex}\n'
                    '\\clearpage\n'
                    '\\end{document}\n')
            (directory/'smoke.tex').write_text(source,encoding='utf-8')
            result=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error',
                                   '-output-directory',str(directory),'smoke.tex'],
                                  cwd=directory,capture_output=True,text=True,timeout=45)
            self.assertEqual(result.returncode,0,result.stdout[-1300:]+result.stderr[-300:])
            self.assertTrue((directory/'smoke.pdf').is_file())


if __name__=='__main__':
    unittest.main()
