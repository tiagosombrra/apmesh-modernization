"""Challenge ideal ownership, observer removal and borrowed-selection contracts."""
from pathlib import Path
import copy
import sys
import unittest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tests'))
sys.path.insert(0,str(ROOT/'tools'))
from ideal_vertex_case import check
from prepare_ideal_vertex_probe import transform
CONTEXT=(0,0,1)
BASELINE={'context': [0, 0, 1],
 'target': 0,
 'action': 0,
 'attempts': 7,
 'denied': 0,
 'threw': 0,
 'result': 0,
 'entered': 1,
 'phase': 90,
 'events': 8054112259,
 'constructed': 1,
 'freed': 1,
 'ideal_xy': [1, 2],
 'cleanup_calls': 0,
 'cleanup_allocations': 0,
 'retained_blocks': 0,
 'retained_bytes': 0,
 'vertex_size': 80,
 'owners': 8,
 'views': 8,
 'observers': 5,
 'mesh': 1,
 'edge_owners': 7,
 'borrowed': 7,
 'ideal_owner': 1,
 'ideal_view': 1,
 'ideal_front': 1,
 'best_kind': 1,
 'best_id': 1,
 'best_xy': [1, 2],
 'last_vertex_id': 1,
 'area': 0.5,
 'adjacency': [2, 2, 2, 2, 2, 2, 2, 0],
 'face': [1, 105, 106, 107, 5.5, 5.333333333333333, 0.5],
 'destroyed': [1, 1, 1, 1, 1, 1, 1, 0]}
ORIGINAL={'context': [0, 0, 1],
 'target': 6,
 'action': 0,
 'attempts': 6,
 'denied': 1,
 'threw': 1,
 'result': -1,
 'entered': 1,
 'phase': 51,
 'events': 3759144963,
 'constructed': 1,
 'freed': 0,
 'ideal_xy': [1, 2],
 'cleanup_calls': 0,
 'cleanup_allocations': 0,
 'retained_blocks': 1,
 'retained_bytes': 80,
 'vertex_size': 80,
 'owners': 7,
 'views': 7,
 'observers': 5,
 'mesh': 1,
 'edge_owners': 7,
 'borrowed': 7,
 'ideal_owner': 0,
 'ideal_view': 0,
 'ideal_front': 1,
 'best_kind': 1,
 'best_id': 1,
 'best_xy': [1, 2],
 'last_vertex_id': 1,
 'area': 0.5,
 'adjacency': [2, 2, 2, 2, 2, 2, 2, 0],
 'face': [1, 105, 106, 107, 5.5, 5.333333333333333, 0.5],
 'destroyed': [1, 1, 1, 1, 1, 1, 1, 0]}

def pending():
 d=copy.deepcopy(ORIGINAL)
 d.update(cleanup_calls=1,freed=1,ideal_front=0,observers=4,retained_blocks=0,retained_bytes=0,best_kind=3,best_id=-1,best_xy=[0,0])
 return d

class IdealVertexTests(unittest.TestCase):
 def test_normal_adoption(self):
  self.assertEqual(check(BASELINE,0,CONTEXT,0,BASELINE,'gcc'),'normal')
 def test_nonallocating_cleanup(self):
  d=pending();self.assertEqual(check(d,0,CONTEXT,d['target'],BASELINE,'gcc'),'nonallocating production cleanup')
 def test_original_is_not_candidate_qualification(self):
  self.assertEqual(check(ORIGINAL,1,CONTEXT,ORIGINAL['target'],BASELINE,'gcc',True),'original unowned ideal retained')
  with self.assertRaises(AssertionError):check(ORIGINAL,1,CONTEXT,ORIGINAL['target'],BASELINE,'gcc')
 def test_later_owned_partial_state(self):
  d=pending();d.update(target=d['target']+1,attempts=d['target']+1,phase=52,cleanup_calls=0,ideal_owner=1,ideal_front=1,observers=5,owners=8,best_kind=1,best_id=1,best_xy=[1,2])
  self.assertEqual(check(d,0,CONTEXT,d['target'],BASELINE,'gcc'),'already-owned view-publication failure')
 def test_source_reversible_observation(self):
  observed,owned,edits=transform((ROOT/'src/crab_mesh/aft/advancing_front.cpp').read_text())
  self.assertTrue(owned);self.assertEqual(len(edits),18)
  self.assertEqual(observed.count('ideal_test::BeginCleanup();'),1)
 def test_missing_and_ambiguous_source_anchors(self):
  source=(ROOT/'src/crab_mesh/aft/advancing_front.cpp').read_text()
  _,_,edits=transform(source)
  for old,new in edits:
   for bad in (source.replace(old,'',1),source.replace(old,old+'\n'+old,1)):
    with self.subTest(anchor=old),self.assertRaises(ValueError):transform(bad)
 def test_original_source_observation(self):
  source=(ROOT/'src/crab_mesh/aft/advancing_front.cpp').read_text()
  # Remove only the owner through exact reviewed production anchors.
  start=source.index('  struct PendingIdealVertexDelete {')
  end=source.index('  best = pending_ideal.get();',start)+len('  best = pending_ideal.get();')
  source=source[:start]+'  best = (geometryPhase) ? makeIdealVertex(e, h) : nullptr;'+source[end:]
  a=source.index('bool AdvancingFront::findBestVertex(');b=source.index('\nvoid AdvancingFront::insertInFront(',a)
  region=source[a:b].replace('pending_ideal.reset();','delete best;').replace('        pending_ideal.release();\n','')
  _,owned,edits=transform(source[:a]+region+source[b:]);self.assertFalse(owned);self.assertEqual(len(edits),16)
 def test_missing_cleanup(self):
  d=pending();d['cleanup_calls']=0
  with self.assertRaises(AssertionError):check(d,0,CONTEXT,d['target'],BASELINE,'gcc')
 def test_duplicate_cleanup(self):
  d=pending();d['cleanup_calls']=2
  with self.assertRaises(AssertionError):check(d,0,CONTEXT,d['target'],BASELINE,'gcc')
 def test_allocating_cleanup(self):
  d=pending();d['cleanup_allocations']=1
  with self.assertRaises(AssertionError):check(d,0,CONTEXT,d['target'],BASELINE,'gcc')
 def test_retained_vertex(self):
  d=pending();d['retained_blocks']=1
  with self.assertRaises(AssertionError):check(d,0,CONTEXT,d['target'],BASELINE,'gcc')
 def test_retained_bytes(self):
  d=pending();d['retained_bytes']=80
  with self.assertRaises(AssertionError):check(d,0,CONTEXT,d['target'],BASELINE,'gcc')
 def test_unfreed_vertex(self):
  d=pending();d['freed']=0
  with self.assertRaises(AssertionError):check(d,0,CONTEXT,d['target'],BASELINE,'gcc')
 def test_stale_observer(self):
  d=pending();d['ideal_front']=1
  with self.assertRaises(AssertionError):check(d,0,CONTEXT,d['target'],BASELINE,'gcc')
 def test_stale_observer_count(self):
  d=pending();d['observers']=5
  with self.assertRaises(AssertionError):check(d,0,CONTEXT,d['target'],BASELINE,'gcc')
 def test_lost_prefix(self):
  d=pending();d['mesh']=0
  with self.assertRaises(AssertionError):check(d,0,CONTEXT,d['target'],BASELINE,'gcc')
 def test_changed_prefix_geometry(self):
  d=pending();d['face']=[0, 0, 0, 0, 0, 0, 0]
  with self.assertRaises(AssertionError):check(d,0,CONTEXT,d['target'],BASELINE,'gcc')
 def test_lost_borrower(self):
  d=pending();d['borrowed']=0
  with self.assertRaises(AssertionError):check(d,0,CONTEXT,d['target'],BASELINE,'gcc')
 def test_borrower_destroyed(self):
  d=pending();d['destroyed']=[2, 2, 2, 2, 2, 2, 2, 2]
  with self.assertRaises(AssertionError):check(d,0,CONTEXT,d['target'],BASELINE,'gcc')
 def test_changed_adjacency(self):
  d=pending();d['adjacency']=[0, 0, 0, 0, 0, 0, 0, 0]
  with self.assertRaises(AssertionError):check(d,0,CONTEXT,d['target'],BASELINE,'gcc')
 def test_lost_edge_owner(self):
  d=pending();d['edge_owners']=0
  with self.assertRaises(AssertionError):check(d,0,CONTEXT,d['target'],BASELINE,'gcc')
 def test_changed_id_consumption(self):
  d=pending();d['last_vertex_id']=0
  with self.assertRaises(AssertionError):check(d,0,CONTEXT,d['target'],BASELINE,'gcc')
 def test_premature_owner_release(self):
  d=pending();d['ideal_owner']=1
  with self.assertRaises(AssertionError):check(d,0,CONTEXT,d['target'],BASELINE,'gcc')
 def test_premature_view(self):
  d=pending();d['ideal_view']=1
  with self.assertRaises(AssertionError):check(d,0,CONTEXT,d['target'],BASELINE,'gcc')
 def test_wrong_selection(self):
  d=pending();d['best_kind']=2
  with self.assertRaises(AssertionError):check(d,0,CONTEXT,d['target'],BASELINE,'gcc')
 def test_dereferenced_expired_best(self):
  d=pending();d['best_id']=1
  with self.assertRaises(AssertionError):check(d,0,CONTEXT,d['target'],BASELINE,'gcc')
 def test_changed_ideal(self):
  d=pending();d['ideal_xy']=[1, 3]
  with self.assertRaises(AssertionError):check(d,0,CONTEXT,d['target'],BASELINE,'gcc')
 def test_missing_denial(self):
  d=pending();d['denied']=0
  with self.assertRaises(AssertionError):check(d,0,CONTEXT,d['target'],BASELINE,'gcc')
 def test_missing_exception(self):
  d=pending();d['threw']=0
  with self.assertRaises(AssertionError):check(d,0,CONTEXT,d['target'],BASELINE,'gcc')
 def test_missing_window(self):
  d=pending();d['entered']=0
  with self.assertRaises(AssertionError):check(d,0,CONTEXT,d['target'],BASELINE,'gcc')
 def test_wrong_phase(self):
  d=pending();d['phase']=0
  with self.assertRaises(AssertionError):check(d,0,CONTEXT,d['target'],BASELINE,'gcc')
 def test_wrong_context(self):
  d=pending();d['context']=[0, 0, 0]
  with self.assertRaises(AssertionError):check(d,0,CONTEXT,d['target'],BASELINE,'gcc')
 def test_changed_owner_count(self):
  d=pending();d['owners']=0
  with self.assertRaises(AssertionError):check(d,0,CONTEXT,d['target'],BASELINE,'gcc')
 def test_changed_view_count(self):
  d=pending();d['views']=0
  with self.assertRaises(AssertionError):check(d,0,CONTEXT,d['target'],BASELINE,'gcc')
