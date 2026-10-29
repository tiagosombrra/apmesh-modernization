"""Challenge first-edge ownership observations and reversible instrumentation."""
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests'))
sys.path.insert(0, str(ROOT / 'tools'))
from first_edge_case import analyze
from prepare_first_edge_probe import prepare


def normal():
    return dict(context=[0,0,0,0],target=0,owned=1,cleanup_calls=0,cleanup_allocations=0,
                pending_adjacent=2,threw=0,status=6,entered=1,phase=7,attempts=9,
                denied=0,before_id=0,edge_id=1,before_owners=4,freed=1,mid_freed=1,
                mesh=2,owners=5,views=5,front=3,rejected=0,cell=1,borrowed=4,
                adjacent_a=3,adjacent_c=3,owner_pending=1,view_pending=1,
                queue_pending=0,cell_pending=1,faces=2,free_edges=0,last_edge=1,
                last_face=2,face_order=567578,destroyed=[0,0,0,0,1,1,1,1],
                retained_blocks=0,retained_bytes=0)


def denied():
    d = normal()
    d.update(target=6,cleanup_calls=1,pending_adjacent=0,threw=1,status=-1,phase=3,
             attempts=6,denied=1,mesh=0,owners=4,views=4,cell=0,adjacent_a=2,
             adjacent_c=2,owner_pending=0,view_pending=0,cell_pending=0,faces=0,
             free_edges=4,last_face=0,face_order=0)
    return d


class FirstEdgeTests(unittest.TestCase):
    def reject(self, data=None, **changes):
        d = normal() if data is None else data
        d.update(changes)
        with self.assertRaises((ValueError, KeyError)):
            analyze(d,0,(0,0,0,0),d['target'],9)

    def test_normal(self):
        self.assertEqual(analyze(normal(),0,(0,0,0,0),0,9),'normal')

    def test_candidate_cleanup(self):
        self.assertEqual(analyze(denied(),0,(0,0,0,0),6,9),'nonallocating pending cleanup')

    def test_original_failure_is_not_candidate_qualification(self):
        d=denied()
        d.update(owned=0,cleanup_calls=0,freed=0,mid_freed=0,adjacent_a=3,
                 adjacent_c=3,pending_adjacent=2,retained_blocks=3,retained_bytes=272)
        self.assertEqual(analyze(d,1,(0,0,0,0),6,9,True),'original pending ownership failed')
        with self.assertRaises(ValueError):analyze(d,1,(0,0,0,0),6,9)

    def test_constructor_unwind(self):
        d=denied()
        d.update(target=1,attempts=1,phase=0,cleanup_calls=0,freed=0,mid_freed=0,
                 edge_id=-1,last_edge=0)
        self.assertEqual(analyze(d,0,(0,0,0,0),1,9),'construction unwind')

    def test_later_owned_partial_publication(self):
        d=denied()
        d.update(target=8,attempts=8,phase=5,cleanup_calls=0,adjacent_a=3,
                 adjacent_c=3,pending_adjacent=2,owners=5,views=5,owner_pending=1,
                 view_pending=1,free_edges=5)
        self.assertEqual(analyze(d,0,(0,0,0,0),8,9),'owned partial publication')

    def test_measured_msvc_original_retention(self):
        d=denied()
        d.update(target=8,attempts=8,owned=0,cleanup_calls=0,freed=0,mid_freed=0,
                 adjacent_a=3,adjacent_c=3,pending_adjacent=2,retained_blocks=5,
                 retained_bytes=296)
        self.assertEqual(analyze(d,1,(0,0,0,0),8,11,True),'original pending ownership failed')
        d['retained_bytes']=288
        with self.assertRaises(ValueError):analyze(d,1,(0,0,0,0),8,11,True)

    def test_context_identity(self):self.reject(context=[1,0,0,0])
    def test_missing_window(self):self.reject(entered=0)
    def test_wrong_owner_variant(self):self.reject(owned=0)
    def test_missing_denial(self):self.reject(denied(),denied=0)
    def test_missing_cleanup(self):self.reject(denied(),cleanup_calls=0)
    def test_duplicate_cleanup(self):self.reject(denied(),cleanup_calls=2)
    def test_cleanup_allocation(self):self.reject(denied(),cleanup_allocations=1)
    def test_stale_adjacency(self):self.reject(denied(),pending_adjacent=1)
    def test_wrong_endpoint_adjacency(self):self.reject(denied(),adjacent_c=3)
    def test_retained_payload(self):self.reject(denied(),retained_blocks=1)
    def test_unfreed_cache(self):self.reject(denied(),mid_freed=0)
    def test_borrowed_endpoint_destruction(self):self.reject(borrowed=3)
    def test_duplicate_owner_retirement(self):self.reject(destroyed=[0,0,0,0,2,1,1,1])
    def test_original_id_timing(self):self.reject(denied(),last_edge=0)
    def test_lost_committed_prefix(self):
        d=denied()
        d.update(context=[0,0,0,1],before_owners=7,borrowed=7,owners=7,views=7,
                 mesh=1,faces=1,last_face=1,face_order=123,
                 destroyed=[1,1,1,0,1,1,1,1])
        self.assertEqual(analyze(d,0,(0,0,0,1),6,9),'nonallocating pending cleanup')
        d['mesh']=0
        with self.assertRaises(ValueError):analyze(d,0,(0,0,0,1),6,9)
    def test_changed_face_order(self):self.reject(face_order=567785)
    def test_changed_cell_publication(self):self.reject(cell_pending=0)
    def test_missing_owner_publication(self):self.reject(owner_pending=0)
    def test_changed_allocation_inventory(self):self.reject(attempts=8)
    def test_missing_observation(self):
        d=normal();del d['faces'];self.reject(d)

    def prepare_source(self, text):
        with tempfile.TemporaryDirectory() as directory:
            out=Path(directory);source=out/'front.cpp';source.write_text(text,newline='\n')
            return prepare(ROOT,out/'observed.cpp',out/'metadata.json',source)

    def test_prepare_candidate(self):
        r=self.prepare_source((ROOT/'src/crab_mesh/aft/advancing_front.cpp').read_text())
        self.assertTrue(r['owned']);self.assertEqual(r['reversible_edits'],8)

    def test_prepare_original(self):
        s=(ROOT/'src/crab_mesh/aft/advancing_front.cpp').read_text()
        start=s.index('      struct PendingEdgeDelete {');end=s.index('      e1 = pending_edge.get();',start)+len('      e1 = pending_edge.get();')
        s=s[:start]+'      e1 = new Edge(e->getV1(), best, ++lastEdgeId);'+s[end:]
        s=s.replace('      pending_edge.release();\n','')
        r=self.prepare_source(s)
        self.assertFalse(r['owned']);self.assertEqual(r['reversible_edits'],7)

    def test_missing_anchor(self):
        s=(ROOT/'src/crab_mesh/aft/advancing_front.cpp').read_text().replace('      edges.push_back(e1);','')
        with self.assertRaises(ValueError):self.prepare_source(s)

    def test_ambiguous_anchor(self):
        s=(ROOT/'src/crab_mesh/aft/advancing_front.cpp').read_text()+'\n      edges.push_back(e1);\n'
        with self.assertRaises(ValueError):self.prepare_source(s)

    def test_missing_cleanup_anchor(self):
        s=(ROOT/'src/crab_mesh/aft/advancing_front.cpp').read_text().replace('          delete edge;','')
        with self.assertRaises(ValueError):self.prepare_source(s)


if __name__ == '__main__':unittest.main()
