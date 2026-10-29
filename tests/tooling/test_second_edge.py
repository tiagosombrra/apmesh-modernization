"""Challenge second-edge cleanup and preservation of a first-edge/Face prefix."""
from pathlib import Path
import copy
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tests'))
sys.path.insert(0,str(ROOT/'tools'))
from second_edge_case import analyze
from prepare_second_edge_probe import prepare
CONTEXT=(0,0,1,1,1)
NORMAL={'context': [0, 0, 1, 1, 1],
 'target': 0,
 'action': 0,
 'entered': 1,
 'phase': 7,
 'attempts': 9,
 'denied': 0,
 'threw': 0,
 'status': 6,
 'before_id': 1,
 'edge_id': 2,
 'before_owners': 9,
 'freed': 1,
 'mid_freed': 1,
 'first_freed': 1,
 'first_mid_freed': 1,
 'cleanup_calls': 0,
 'cleanup_allocations': 0,
 'retained_blocks': 0,
 'retained_bytes': 0,
 'mesh': 4,
 'owners': 10,
 'views': 10,
 'front': 4,
 'rejected': 0,
 'cell': 2,
 'borrowed': 8,
 'owner_pending': 1,
 'view_pending': 1,
 'queue_pending': 0,
 'cell_pending': 1,
 'free_edges': 0,
 'last_edge': 2,
 'last_face': 4,
 'first_id': 1,
 'first_owned': 1,
 'first_view': 1,
 'first_adjacency': 2,
 'first_cell': 1,
 'first_free': 0,
 'destroyed': [1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0],
 'adjacency': [2, 2, 2, 0, 0, 0, 3, 3, 2, 4, 2, 0],
 'first_geometry': [107, 110, 3.5, 0.5],
 'pending_geometry': [2, 110, 108, 4.5, 0.5, 4, 5],
 'faces': [[1, 101, 102, 103, 0.5, 0.3333333333333333, 0.5],
           [2, 107, 108, 110, 4, 0.3333333333333333, 1],
           [3, 107, 110, 111, 3, 1, 1.5],
           [4, 110, 108, 109, 5, 1, 1.5]]}
FAILED={'context': [0, 0, 1, 1, 1],
 'target': 6,
 'action': 0,
 'entered': 1,
 'phase': 3,
 'attempts': 6,
 'denied': 1,
 'threw': 1,
 'status': -1,
 'before_id': 1,
 'edge_id': 2,
 'before_owners': 9,
 'freed': 0,
 'mid_freed': 0,
 'first_freed': 1,
 'first_mid_freed': 1,
 'cleanup_calls': 0,
 'cleanup_allocations': 0,
 'retained_blocks': 3,
 'retained_bytes': 272,
 'mesh': 1,
 'owners': 9,
 'views': 9,
 'front': 4,
 'rejected': 1,
 'cell': 1,
 'borrowed': 8,
 'owner_pending': 0,
 'view_pending': 0,
 'queue_pending': 0,
 'cell_pending': 0,
 'free_edges': 6,
 'last_edge': 2,
 'last_face': 1,
 'first_id': 1,
 'first_owned': 1,
 'first_view': 1,
 'first_adjacency': 2,
 'first_cell': 1,
 'first_free': 1,
 'destroyed': [1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0],
 'adjacency': [2, 2, 2, 0, 0, 0, 3, 3, 2, 4, 2, 0],
 'first_geometry': [107, 110, 3.5, 0.5],
 'pending_geometry': [2, 110, 108, 4.5, 0.5, 4, 5],
 'faces': [[1, 101, 102, 103, 0.5, 0.3333333333333333, 0.5],
           [0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 0]]}

def normal():
 d=copy.deepcopy(NORMAL);d['owned']=1;return d

def denied():
 d=copy.deepcopy(FAILED)
 d.update(owned=1,cleanup_calls=1,freed=1,mid_freed=1,retained_blocks=0,retained_bytes=0,pending_geometry=[0]*7)
 d['adjacency'][7]-=1;d['adjacency'][9]-=1
 return d

class SecondEdgeTests(unittest.TestCase):
 def reject(self,data=None,**changes):
  d=normal() if data is None else data;d.update(changes)
  with self.assertRaises((ValueError,KeyError)):analyze(d,0,CONTEXT,d['target'],3)
 def test_normal(self):self.assertEqual(analyze(normal(),0,CONTEXT,0,3),'normal')
 def test_candidate_cleanup(self):self.assertEqual(analyze(denied(),0,CONTEXT,6,3),'nonallocating pending cleanup')
 def test_original_failure_is_not_candidate_qualification(self):
  d=copy.deepcopy(FAILED);d['owned']=0
  self.assertEqual(analyze(d,1,CONTEXT,6,3,True),'original pending ownership failed')
  with self.assertRaises(ValueError):analyze(d,1,CONTEXT,6,3)
 def test_msvc_retention(self):
  d=copy.deepcopy(FAILED);d.update(owned=0,target=8,attempts=8,retained_blocks=5,retained_bytes=296)
  self.assertEqual(analyze(d,1,CONTEXT,8,5,True),'original pending ownership failed')
  d['retained_bytes']=288
  with self.assertRaises(ValueError):analyze(d,1,CONTEXT,8,5,True)
 def test_constructor_failure_preserves_first_edge(self):
  d=denied();d.update(target=1,attempts=1,phase=0,cleanup_calls=0,freed=0,mid_freed=0,edge_id=-1,last_edge=1)
  self.assertEqual(analyze(d,0,CONTEXT,1,3),'construction unwind')
 def test_already_owned_partial_publication(self):
  d=copy.deepcopy(FAILED);d.update(owned=1,target=9,attempts=9,phase=6,retained_blocks=0,retained_bytes=0,freed=1,mid_freed=1,owners=10,views=10,owner_pending=1,view_pending=1,rejected=2,queue_pending=1,free_edges=7)
  self.assertEqual(analyze(d,0,CONTEXT,9,3),'owned partial publication')
 def test_wrong_case_identity(self):self.reject(target=1)
 def test_missing_window(self):self.reject(entered=0)
 def test_wrong_owner_variant(self):self.reject(owned=0)
 def test_missing_cleanup(self):self.reject(denied(),cleanup_calls=0)
 def test_duplicate_cleanup(self):self.reject(denied(),cleanup_calls=2)
 def test_cleanup_allocation(self):self.reject(denied(),cleanup_allocations=1)
 def test_pending_retention(self):self.reject(denied(),retained_blocks=1)
 def test_unfreed_cache(self):self.reject(denied(),mid_freed=0)
 def test_lost_first_owner(self):self.reject(denied(),first_owned=0)
 def test_lost_first_view(self):self.reject(denied(),first_view=0)
 def test_changed_first_identity(self):self.reject(denied(),first_id=2)
 def test_changed_first_cell(self):self.reject(denied(),first_cell=0)
 def test_changed_first_adjacency(self):self.reject(denied(),first_adjacency=1)
 def test_first_edge_cache_not_retired(self):self.reject(denied(),first_mid_freed=0)
 def test_stale_second_adjacency(self):
  d=denied();d['adjacency'][7]+=1;self.reject(d)
 def test_changed_first_cache(self):
  d=denied();d['first_geometry'][2]+=1;self.reject(d)
 def test_lost_face_prefix(self):self.reject(denied(),mesh=0)
 def test_changed_prefix_geometry(self):
  d=denied();d['faces'][0][6]=1;self.reject(d)
 def test_duplicate_borrower_retirement(self):
  d=denied();d['destroyed'][7]=2;self.reject(d)
 def test_original_id_timing(self):self.reject(denied(),last_edge=1)
 def test_normal_area(self):
  d=normal();d['faces'][1][6]+=1;self.reject(d)
 def test_normal_geometry(self):
  d=normal();d['pending_geometry'][1]=109;self.reject(d)
 def test_missing_observation(self):
  d=normal();del d['first_view'];self.reject(d)
 def prepare_source(self,text):
  with tempfile.TemporaryDirectory() as folder:
   folder=Path(folder);source=folder/'source.cpp';source.write_text(text,newline='\n')
   result=prepare(ROOT,folder/'observed.cpp',folder/'metadata.json',source)
   return result,(folder/'observed.cpp').read_text()
 def test_prepare_candidate(self):
  result,observed=self.prepare_source((ROOT/'src/crab_mesh/aft/advancing_front.cpp').read_text())
  self.assertTrue(result['owned']);self.assertEqual(result['reversible_edits'],8)
  self.assertEqual(observed.count('second_edge_test::BeginCleanup();'),1)
 def test_prepare_original(self):
  s=(ROOT/'src/crab_mesh/aft/advancing_front.cpp').read_text();start=s.index('      struct PendingSecondEdgeDelete {');end=s.index('      e2 = pending_second_edge.get();',start)+len('      e2 = pending_second_edge.get();')
  s=s[:start]+'      e2 = new Edge(best, e->getV2(), ++lastEdgeId);'+s[end:];s=s.replace('      pending_second_edge.release();\n','')
  result,_=self.prepare_source(s);self.assertFalse(result['owned']);self.assertEqual(result['reversible_edits'],7)
 def test_missing_anchor(self):
  s=(ROOT/'src/crab_mesh/aft/advancing_front.cpp').read_text().replace('      edges.push_back(e2);','')
  with self.assertRaises(ValueError):self.prepare_source(s)
 def test_ambiguous_anchor(self):
  s=(ROOT/'src/crab_mesh/aft/advancing_front.cpp').read_text()+'\n      edges.push_back(e2);\n'
  with self.assertRaises(ValueError):self.prepare_source(s)
 def test_missing_cleanup_delete(self):
  s=(ROOT/'src/crab_mesh/aft/advancing_front.cpp').read_text();start=s.index('      struct PendingSecondEdgeDelete {');s=s[:start]+s[start:].replace('          delete edge;','',1)
  with self.assertRaises(ValueError):self.prepare_source(s)
 def test_duplicate_cleanup_scope(self):
  s=(ROOT/'src/crab_mesh/aft/advancing_front.cpp').read_text();start=s.index('      struct PendingSecondEdgeDelete {');end=s.index('\n      };',start)+len('\n      };')
  with self.assertRaises(ValueError):self.prepare_source(s+'\n'+s[start:end])
 def test_other_edge_deleters_not_observed(self):
  s=(ROOT/'src/crab_mesh/aft/advancing_front.cpp').read_text()
  _,observed=self.prepare_source(s)
  first=s[s.index('      struct PendingEdgeDelete {'):s.index('      std::unique_ptr<Edge, PendingEdgeDelete>')]
  self.assertIn(first,observed)

if __name__=='__main__':unittest.main()
