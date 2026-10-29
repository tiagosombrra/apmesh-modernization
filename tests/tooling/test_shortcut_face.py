"""Challenge shortcut ownership, native observations and exact-source preparation."""
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tests'))
sys.path.insert(0,str(ROOT/'tools'))
from shortcut_face_case import analyze
from prepare_shortcut_probe import prepare


def normal():
    return dict(sorted=0,rotation=0,prefix=0,front_count=3,mode='0',
                profile='native-allocation-observer',threw=0,done=1,returned=5,
                seen=1,entered=1,attempts=3,denied=0,phase=2,constructed=1,adopted=1,
                before_id=0,face_id=1,before_mesh=0,endpoint_ids=[101,102,103],
                midpoint=[0.5,1/3],area=0.5,face_freed=1,mid_freed=1,
                mesh=1,front=3,rejected=0,owner_vertices=3,owner_edges=3,
                live_vertices=3,adjacency=3,geometry_faces=1,free_edges=3,
                last_face=1,last_edge=0,destroyed=[1,1,1,0,0,0],
                retained_blocks=0,retained_bytes=0,cleanup_calls=0,cleanup_allocations=0)


def denied():
    d=normal()
    d.update(mode='3',threw=1,done=0,returned=-1,denied=1,phase=1,adopted=0,
             mesh=0,geometry_faces=0,cleanup_calls=1)
    return d


def guard(count=0):
    d=normal()
    d.update(front_count=count,mode=f'guard-{count}',returned=14,done=0,seen=0,entered=0,
             attempts=0,phase=-1,constructed=0,adopted=0,before_id=-1,face_id=-1,
             endpoint_ids=[0]*3,midpoint=[0]*2,area=0,face_freed=0,mid_freed=0,
             mesh=0,geometry_faces=0,last_face=0,front=count)
    return d


class ShortcutFaceTests(unittest.TestCase):
    def reject(self,**changes):
        d=normal();d.update(changes)
        with self.assertRaises(ValueError):analyze(d,0,0,0,0,'0',3)

    def test_normal(self):
        self.assertEqual(analyze(normal(),0,0,0,0,'0',3),'preserved')

    def test_candidate_publication_cleanup(self):
        self.assertEqual(analyze(denied(),0,0,0,0,'3',3),'preserved')

    def test_original_failure_is_not_candidate_validation(self):
        d=denied();d.update(cleanup_calls=0,face_freed=0,mid_freed=0,
                           retained_blocks=2,retained_bytes=136)
        self.assertEqual(analyze(d,1,0,0,0,'3',3,True),'failed original pending ownership')
        with self.assertRaises(ValueError):analyze(d,1,0,0,0,'3',3)

    def test_guard_only(self):
        for n in range(3):
            self.assertEqual(analyze(guard(n),0,0,0,0,f'guard-{n}',3),'guard only')

    def test_guard_does_not_fabricate_face(self):
        for key,value in [('seen',1),('cleanup_calls',1),('geometry_faces',1),('face_id',1)]:
            d=guard();d[key]=value
            with self.assertRaises(ValueError):analyze(d,0,0,0,0,'guard-0',3)

    def test_unsupported_guard(self):
        with self.assertRaises(ValueError):analyze(guard(3),0,0,0,0,'guard-3',3)

    def test_context_domain_and_identity(self):
        self.reject(sorted=1);self.reject(rotation=1);self.reject(prefix=1);self.reject(mode='1')
        d=normal();d['rotation']=3
        with self.assertRaises(ValueError):analyze(d,0,0,3,0,'0',3)

    def test_profile_and_calibration(self):
        self.reject(profile='unmeasured');self.reject(attempts=0)
        with self.assertRaises(ValueError):analyze(normal(),0,0,0,0,'0',0)

    def test_actual_window(self):
        self.reject(seen=0);self.reject(entered=0);self.reject(before_mesh=1);self.reject(before_id=1)

    def test_construction_and_publication(self):
        self.reject(constructed=0);self.reject(adopted=0);self.reject(phase=0)

    def test_actual_payload_frees(self):
        self.reject(face_freed=0);self.reject(mid_freed=0)
        d=denied();d['face_freed']=0
        with self.assertRaises(ValueError):analyze(d,0,0,0,0,'3',3)

    def test_nonallocating_exact_cleanup(self):
        d=denied()
        for key,value in [('cleanup_calls',0),('cleanup_calls',2),('cleanup_allocations',1)]:
            bad=d.copy();bad[key]=value
            with self.assertRaises(ValueError):analyze(bad,0,0,0,0,'3',3)

    def test_live_endpoint_owners(self):
        self.reject(owner_vertices=0);self.reject(owner_edges=0);self.reject(live_vertices=0)
        self.reject(adjacency=0);self.reject(destroyed=[0]*6)

    def test_front_and_prefix_state(self):
        self.reject(front=0);self.reject(rejected=1);self.reject(free_edges=0)
        self.reject(mesh=0);self.reject(geometry_faces=0)

    def test_endpoint_order_and_geometry(self):
        self.reject(endpoint_ids=[103,102,101]);self.reject(midpoint=[0,0]);self.reject(area=0)

    def test_original_new_expression_id_timing(self):
        d=normal();d.update(mode='1',threw=1,done=0,returned=-1,attempts=1,denied=1,
                           phase=0,constructed=0,adopted=0,face_id=-1,endpoint_ids=[0]*3,
                           midpoint=[0]*2,area=0,face_freed=0,mid_freed=0,mesh=0,
                           geometry_faces=0,last_face=0)
        self.assertEqual(analyze(d,0,0,0,0,'1',3),'preserved')
        d['last_face']=1
        with self.assertRaises(ValueError):analyze(d,0,0,0,0,'1',3)

    def test_native_return_and_denial(self):
        self.reject(returned=6);self.reject(denied=1);self.reject(threw=1);self.reject(done=0)

    def test_retained_storage_rejected(self):
        self.reject(retained_blocks=1);self.reject(retained_bytes=1)

    def test_reversible_source_observation(self):
        with tempfile.TemporaryDirectory() as folder:
            folder=Path(folder);r=prepare(ROOT,folder/'observed.cpp',folder/'report.json')
            self.assertTrue(r['owned_shortcut']);self.assertEqual(r['reversible_edits'],4)

    def test_missing_or_ambiguous_anchor(self):
        original=(ROOT/'src/crab_mesh/aft/advancing_front.cpp').read_text()
        with tempfile.TemporaryDirectory() as folder:
            folder=Path(folder);source=folder/'source.cpp'
            for text in (original+original,original.replace('    pending_face.release();','    pending_face.reset();')):
                source.write_text(text)
                with self.assertRaises(ValueError):prepare(ROOT,folder/'observed.cpp',folder/'report.json',source)
                self.assertFalse((folder/'observed.cpp').exists())
