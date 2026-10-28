"""Challenge pending ownership, ID sequencing and native source observations."""
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tests'))
sys.path.insert(0,str(ROOT/'tools'))
from face_adoption_case import analyze
from prepare_face_adoption_probe import prepare


def normal():
    return dict(front_based=1,geometry=0,prefix=0,mode='0',profile='native-allocation-observer',
                threw=0,done=1,seen=1,entered=1,attempts=3,denied=0,phase=2,constructed=1,
                adopted=1,before_id=0,face_id=1,before_mesh=0,endpoint_ids=[101,102,103],
                midpoint=[0.5,1/3],area=0.5,face_freed=1,mid_freed=1,mesh=1,front=0,rejected=0,
                owner_vertices=3,owner_edges=3,live_vertices=3,adjacency=3,geometry_faces=1,
                free_edges=0,last_face=1,last_edge=0,destroyed=[1,1,1,0,0,0],retained_blocks=0,retained_bytes=0)


class FaceAdoptionTests(unittest.TestCase):
    def reject(self,**changes):
        d=normal();d.update(changes)
        with self.assertRaises(ValueError):analyze(d,0,1,0,0,0,3)

    def test_normal(self):
        self.assertEqual(analyze(normal(),0,1,0,0,0,3)['pending_owner_contract'],'preserved')

    def test_supported_geometry_context(self):
        d=normal();d.update(front_based=0,geometry=1,front=2)
        self.assertEqual(analyze(d,0,0,1,0,0,3)['pending_owner_contract'],'preserved')
        d.update(front_based=1,front=0)
        with self.assertRaises(ValueError):analyze(d,0,1,1,0,0,3)

    def test_failed_first_allocation_keeps_id(self):
        d=normal();d.update(mode='1',threw=1,done=0,attempts=1,denied=1,phase=0,constructed=0,
                             adopted=0,face_id=-1,endpoint_ids=[0]*3,midpoint=[0]*2,area=0,
                             face_freed=0,mid_freed=0,mesh=0,geometry_faces=0,last_face=0)
        self.assertEqual(analyze(d,0,1,0,0,1,3)['pending_owner_contract'],'preserved')
        d['last_face']=1
        with self.assertRaises(ValueError):analyze(d,0,1,0,0,1,3)

    def test_failed_publication_reclaims_payload(self):
        d=normal();d.update(mode='3',threw=1,done=0,denied=1,phase=1,adopted=0,mesh=0,geometry_faces=0)
        self.assertEqual(analyze(d,0,1,0,0,3,3)['pending_owner_contract'],'preserved')
        d['face_freed']=0
        with self.assertRaises(ValueError):analyze(d,0,1,0,0,3,3)

    def test_identity(self):
        self.reject(prefix=1);self.reject(geometry=1);self.reject(profile='unmeasured')

    def test_inactive_hook_or_denial(self):
        self.reject(attempts=0);self.reject(denied=1);self.reject(entered=0)

    def test_owner_and_prefix_state(self):
        self.reject(live_vertices=0);self.reject(adjacency=0);self.reject(mesh=0)
        self.reject(destroyed=[0]*6);self.reject(free_edges=1)

    def test_cache_geometry(self):
        self.reject(midpoint=[float('nan'),0]);self.reject(area=0);self.reject(endpoint_ids=[103,102,101])

    def test_retention_or_incomplete_release(self):
        self.reject(retained_blocks=1);self.reject(mid_freed=0);self.reject(adopted=0)

    def test_original_failure_is_not_candidate_validation(self):
        d=normal();d.update(mode='3',threw=1,done=0,denied=1,phase=1,adopted=0,mesh=0,
                             geometry_faces=0,face_freed=0,mid_freed=0,retained_blocks=2,retained_bytes=136)
        with self.assertRaises(ValueError):analyze(d,1,1,0,0,3,3)
        self.assertEqual(analyze(d,1,1,0,0,3,3,True)['pending_owner_contract'],'failed')

    def test_reversible_observer(self):
        with tempfile.TemporaryDirectory() as folder:
            folder=Path(folder);r=prepare(ROOT,folder/'observed.cpp',folder/'report.json')
            self.assertTrue(r['owned_pending_face']);self.assertEqual(r['reversible_edits'],3)

    def test_ambiguous_or_missing_anchor(self):
        original=(ROOT/'src/crab_mesh/aft/advancing_front.cpp').read_text()
        with tempfile.TemporaryDirectory() as folder:
            folder=Path(folder);source=folder/'source.cpp'
            for text in (original+original,original.replace('    f.release();','    f.reset();')):
                source.write_text(text)
                with self.assertRaises(ValueError):prepare(ROOT,folder/'observed.cpp',folder/'report.json',source)
                self.assertFalse((folder/'observed.cpp').exists())


if __name__=='__main__':unittest.main()
