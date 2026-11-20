"""Native-kernel controls, source STEP roundtrips and adversarial R3.C2 tests."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import cadquery as cq
from r3c2_native import extract, source_solids, UnsupportedContact, _topology
from r3c2_bp import convert
from r3c2_audit import audit


class SourcePartialContactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases={}
        for name in ('t_junction','cross_junction'):
            shape,graph=extract(name)
            bp,sidecar=convert(name,shape,graph)
            cls.cases[name]=(shape,graph,bp,sidecar)

    def test_t_junction_native_and_independent_bp(self):
        shape,graph,bp,sidecar=self.cases['t_junction']
        self.assertEqual(graph['source_solid_count'],2)
        self.assertEqual(graph['contact_count'],1)
        self.assertEqual(graph['sheet_count'],5)
        self.assertEqual(graph['native_topology']['face_per_edge_histogram'],{1:14,3:2})
        output=audit(bp,sidecar,shape)
        self.assertEqual((output['patch_count'],output['unique_control_vertices']), (5,64))
        self.assertEqual((output['shared_three_face_curves'],output['unique_boundary_curves']), (2,16))
        self.assertLess(output['max_native_surface_distance'],1e-8)
        self.assertLess(output['max_analytic_coordinate_error'],2e-12)

    def test_cross_junction_native_and_independent_bp(self):
        shape,graph,bp,sidecar=self.cases['cross_junction']
        self.assertEqual(graph['source_solid_count'],3)
        self.assertEqual(graph['contact_count'],2)
        self.assertEqual(graph['sheet_count'],10)
        self.assertEqual(graph['native_topology']['face_per_edge_histogram'],{1:28,3:4})
        output=audit(bp,sidecar,shape)
        self.assertEqual((output['patch_count'],output['unique_control_vertices']), (10,128))
        self.assertEqual((output['shared_three_face_curves'],output['unique_boundary_curves']), (4,32))
        self.assertLess(output['max_native_surface_distance'],1e-8)

    def test_source_host_face_area_conservation(self):
        for name,(shape,graph,bp,sidecar) in self.cases.items():
            for entry in graph['contact_records']:
                self.assertAlmostEqual(sum(entry['wings_area'])+entry['overlap_area'],entry['original_host_area'])
                self.assertAlmostEqual(entry['overlap_area'],entry['original_arm_area'])
                self.assertEqual(entry['generated_sheet_count'],5)
            self.assertEqual(len({i for p in sidecar['patches'] for i in p['control_vertex_ids']}),sidecar['unique_control_vertices'])

    def test_native_brep_roundtrip_for_both_cases(self):
        for name,(shape,graph,bp,sidecar) in self.cases.items():
            with self.subTest(name=name),tempfile.TemporaryDirectory() as folder:
                target=Path(folder)/'test.brep'
                shape.exportBrep(str(target))
                restored=cq.Shape.importBrep(str(target))
                receipt=audit(bp,sidecar,restored)
                self.assertEqual(receipt['shared_three_face_curves'],2 if name=='t_junction' else 4)

    def test_native_step_source_roundtrip_for_both_cases(self):
        for name in ('t_junction','cross_junction'):
            with self.subTest(name=name),tempfile.TemporaryDirectory() as folder:
                assembly=cq.Assembly(name=name)
                for body,shape in source_solids(name).items():
                    assembly.add(shape,name=body)
                path=Path(folder)/'original_source_mirror.step'
                assembly.export(str(path),exportType='STEP')
                solids=cq.importers.importStep(str(path)).val().Solids()
                mapped={}
                for body in solids:
                    x,y,z=body.Center().toTuple()
                    label='main' if abs(y)<0.01 else (
                        'branch' if name=='t_junction' else ('top_arm' if y>0 else 'bottom_arm'))
                    self.assertNotIn(label,mapped)
                    mapped[label]=body
                shape,graph=extract(name,mapped)
                bp,meta=convert(name,shape,graph)
                self.assertEqual(audit(bp,meta,shape)['shared_three_face_curves'],2 if name=='t_junction' else 4)

    def test_original_solids_unchanged_by_split(self):
        for name in ('t_junction','cross_junction'):
            solids=source_solids(name)
            before={k:(len(s.Edges()),len(s.Faces()),s.Volume()) for k,s in solids.items()}
            extract(name,solids)
            after={k:(len(s.Edges()),len(s.Faces()),s.Volume()) for k,s in solids.items()}
            self.assertEqual(before,after)

    def test_deterministic_bp_and_source_metadata(self):
        for name in ('t_junction','cross_junction'):
            _,graph,bp,meta=self.cases[name]
            second_bp,second_meta=convert(name)
            self.assertEqual(bp,second_bp)
            self.assertEqual(json.dumps(meta,sort_keys=True),json.dumps(second_meta,sort_keys=True))

    def test_t_gap_and_near_contact_both_rejected(self):
        for gap in (1e-5,1e-9,1e-10):
            with self.subTest(gap=gap):
                with self.assertRaises(UnsupportedContact):
                    extract('t_junction',source_solids('t_junction',gap=gap))

    def test_cross_gap_rejected(self):
        with self.assertRaisesRegex(UnsupportedContact,'Expected one positive-area'):
            extract('cross_junction',source_solids('cross_junction',gap=1e-5))

    def test_volume_penetration_rejected(self):
        for name in ('t_junction','cross_junction'):
            with self.subTest(name=name),self.assertRaisesRegex(UnsupportedContact,'Overlapping source solid volumes'):
                extract(name,source_solids(name,penetration=0.01))

    def test_smaller_height_requires_hole_or_complex_split(self):
        for name in ('t_junction','cross_junction'):
            with self.subTest(name=name),self.assertRaisesRegex(UnsupportedContact,'not two quadrilateral wings'):
                extract(name,source_solids(name,arm_height_scale=0.8))

    def test_edge_only_contact_rejected(self):
        with self.assertRaisesRegex(UnsupportedContact,'Expected one positive-area'):
            extract('t_junction',source_solids('t_junction',offset_x=12.5))

    def test_partial_larger_branch_face_rejected(self):
        with self.assertRaisesRegex(UnsupportedContact,'Partial trimming of both source faces'):
            extract('t_junction',source_solids('t_junction',arm_width_scale=5))

    def test_invalid_source_model_inputs_rejected(self):
        for parameter in ({'arm_height_scale':0},{'gap':float('nan')},{'penetration':-1}):
            with self.subTest(parameter=parameter),self.assertRaises(ValueError):
                source_solids('t_junction',**parameter)

    def test_false_external_admission_rejected(self):
        shape,graph,bp,meta=self.cases['t_junction']
        fake=copy.deepcopy(meta)
        fake['external_model_admission']='PASS'
        with self.assertRaisesRegex(ValueError,'False external admission'):
            audit(bp,fake,shape)

    def test_false_apmesh_meshing_claim_rejected(self):
        shape,graph,bp,meta=self.cases['t_junction']
        fake=copy.deepcopy(meta)
        fake['apmesh_generation']='ACCEPTED'
        with self.assertRaisesRegex(ValueError,'False APMesh TRI claim'):
            audit(bp,fake,shape)

    def test_perturbed_bp_rehashed_rejected_by_geometry_oracle(self):
        shape,graph,bp,meta=self.cases['t_junction']
        all_lines=bp.splitlines()
        first=next(i for i,line in enumerate(all_lines) if line.startswith('v '))
        values=all_lines[first].split()
        values[1]=str(float(values[1])+0.1)
        all_lines[first]=' '.join(values)
        changed='\n'.join(all_lines)+'\n'
        fake=copy.deepcopy(meta)
        fake['bp_sha256']=hashlib.sha256(changed.encode()).hexdigest()
        with self.assertRaisesRegex(ValueError,'analytic reconstruction'):
            audit(changed,fake,shape)

    def test_corrupt_shared_curve_orientation_rejected(self):
        shape,graph,bp,meta=self.cases['t_junction']
        fake=copy.deepcopy(meta)
        shared=next(s for p in fake['patches'] for s in p['sides']
                    if s['curve_id'] in set(fake['triple_edge_curves']))
        shared['control_vertex_ids']=shared['control_vertex_ids'][::-1]
        with self.assertRaisesRegex(ValueError,'Side control identity drift'):
            audit(bp,fake,shape)

    def test_native_shape_tampering_rejected(self):
        _,_,bp,meta=self.cases['t_junction']
        ordinary=cq.Workplane('XY').box(20,5,5).val()
        with self.assertRaisesRegex(ValueError,'Native source mesh/shell not valid'):
            audit(bp,meta,ordinary)


if __name__=='__main__':
    unittest.main()
