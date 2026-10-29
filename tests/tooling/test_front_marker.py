"""Challenge marker retention, observer retirement and immutable source hooks."""
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tests'))
sys.path.insert(0,str(ROOT/'tools'))
from front_marker_case import analyze
from prepare_marker_probe import prepare


def normal():
    return dict(stage=0,prefix=0,mode='0',profile='native-allocation-observer',
                threw=0,done=1,attempts=4,denied=0,constructed=1,published=1,retiring=1,
                marker_freed=1,mid_freed=1,selection_seen=1,face_seen=1,marker_front=0,
                marker_owned=0,marker_rejected=0,cleanup_calls=1,cleanup_allocations=0,
                mesh=1,front=0,rejected=0,owner_vertices=3,owner_edges=3,live_vertices=3,
                adjacency=3,geometry_faces=1,free_edges=0,last_face=1,last_edge=0,
                destroyed=[1,1,1,0,0,0],retained_blocks=0,retained_bytes=0)


class FrontMarkerTests(unittest.TestCase):
    def reject(self,**changes):
        d=normal();d.update(changes)
        with self.assertRaises(ValueError):analyze(d,0,0,0,0,4,3)

    def test_normal(self):
        self.assertEqual(analyze(normal(),0,0,0,0,4,3),'preserved')

    def test_identity(self):
        self.reject(prefix=1);self.reject(stage=2);self.reject(mode='1')

    def test_profile(self):
        self.reject(profile='unqualified')

    def test_actual_selection(self):
        self.reject(selection_seen=0);self.reject(face_seen=0)

    def test_marker_lifecycle(self):
        self.reject(constructed=0);self.reject(published=0);self.reject(retiring=0)

    def test_observer_retirement(self):
        self.reject(marker_front=1);self.reject(marker_rejected=1);self.reject(marker_owned=1)

    def test_actual_cache_destruction(self):
        self.reject(marker_freed=0);self.reject(mid_freed=0)

    def test_nonallocating_cleanup(self):
        self.reject(cleanup_allocations=1);self.reject(cleanup_calls=0);self.reject(cleanup_calls=2)

    def test_live_owners(self):
        self.reject(owner_vertices=0);self.reject(owner_edges=0);self.reject(live_vertices=0)
        self.reject(adjacency=0);self.reject(destroyed=[0]*6)

    def test_prefix_and_counter(self):
        self.reject(mesh=0);self.reject(geometry_faces=0);self.reject(last_face=0)
        self.reject(last_edge=1);self.reject(free_edges=1)

    def test_calibration_and_propagation(self):
        self.reject(attempts=0);self.reject(denied=1);self.reject(threw=1);self.reject(done=0)

    def test_original_failure_is_not_candidate_validation(self):
        d=normal();d.update(mode='4',threw=1,done=0,denied=1,published=0,retiring=0,
                           marker_freed=0,mid_freed=0,selection_seen=0,face_seen=0,
                           cleanup_calls=0,mesh=0,front=3,geometry_faces=0,free_edges=3,
                           last_face=0,retained_blocks=3,retained_bytes=272)
        self.assertEqual(analyze(d,1,0,0,4,4,3,True),'failed original marker ownership')
        with self.assertRaises(ValueError):analyze(d,1,0,0,4,4,3)

    def test_reversible_observation(self):
        with tempfile.TemporaryDirectory() as folder:
            folder=Path(folder);r=prepare(ROOT,folder/'observed.cpp',folder/'report.json')
            self.assertTrue(r['owned_marker']);self.assertEqual(r['reversible_edits'],9)

    def test_missing_or_ambiguous_anchor(self):
        original=(ROOT/'src/crab_mesh/aft/advancing_front.cpp').read_text()
        with tempfile.TemporaryDirectory() as folder:
            folder=Path(folder);source=folder/'source.cpp'
            for text in (original+original,original.replace('    last = marker.get();','    last = nullptr;')):
                source.write_text(text)
                with self.assertRaises(ValueError):prepare(ROOT,folder/'observed.cpp',folder/'report.json',source)
                self.assertFalse((folder/'observed.cpp').exists())
