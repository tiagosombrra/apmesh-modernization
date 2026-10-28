"""Challenge borrower lifetime, cache order and fail-closed native observations."""
from copy import deepcopy
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tests'))
sys.path.insert(0,str(ROOT/'tools'))
from front_face_case import analyze
from prepare_front_face_probe import prepare


def normal():
    return dict(layout=0,mode='0',profile='native-allocation-observer',attempts=3,denied=0,
                threw=0,entered=1,finished=1,phase=4,result=0,attached=1,attached_ids=[101,102,103],
                midpoint=[0.5,1/3],cache_releases=3,cache_release_order=[0,1,2],
                live_fields_checked=5,adjacency_checked=3,consumer_reads=3,quarantined_handles=0,
                destroyed_before_owner_cleanup=[0]*5,destroyed_after_cleanup=[1]*5,
                retained_blocks=0,retained_bytes=0)


class FrontFaceTests(unittest.TestCase):
    def reject(self, **changes):
        d=normal();d.update(changes)
        with self.assertRaises(ValueError): analyze(d,0,0,0,3)

    def test_normal(self):
        self.assertEqual(analyze(normal(),0,0,0,3)['borrower_contract'],'preserved')

    def test_guard_only(self):
        d=normal();d.update(layout=4,attempts=0,entered=0,finished=0,phase=-1,attached=0,
                             attached_ids=[0]*3,midpoint=[0]*2,cache_releases=0,cache_release_order=[-1]*3)
        self.assertEqual(analyze(d,0,4,0,0)['coverage'],'guard-only')

    def test_every_denial_prefix(self):
        for ordinal,phase,releases in [(1,0,0),(2,1,1),(3,3,2)]:
            d=normal();d.update(mode=str(ordinal),attempts=ordinal,denied=1,threw=1,finished=0,
                                 phase=phase,result=-1,attached=int(ordinal==3),cache_releases=releases,
                                 cache_release_order=list(range(releases))+[-1]*(3-releases))
            if ordinal<3:d.update(attached_ids=[0]*3,midpoint=[0]*2)
            self.assertEqual(analyze(d,0,0,ordinal,3)['borrower_contract'],'preserved')

    def test_wrong_identity(self):
        self.reject(layout=1);self.reject(mode='1');self.reject(profile='unmeasured')

    def test_empty_or_inactive_denial(self):
        self.reject(attempts=0);self.reject(denied=1);self.reject(threw=1)
        with self.assertRaises(ValueError):analyze(normal(),0,0,0,0)

    def test_lifecycle_and_release_order(self):
        self.reject(phase=3);self.reject(finished=0);self.reject(cache_release_order=[2,1,0])

    def test_borrowed_destruction_and_quarantine(self):
        self.reject(destroyed_before_owner_cleanup=[1,1,1,0,0]);self.reject(quarantined_handles=3)

    def test_live_fields_adjacency_and_consumption(self):
        self.reject(live_fields_checked=0);self.reject(adjacency_checked=0);self.reject(consumer_reads=0)

    def test_cache_and_cleanup(self):
        self.reject(midpoint=[float('nan'),0]);self.reject(attached_ids=[103,102,101])
        self.reject(retained_blocks=1);self.reject(destroyed_after_cleanup=[0]*5)

    def test_original_failure_stays_failure(self):
        d=normal();d.update(mode='3',denied=1,threw=1,phase=3,finished=0,result=-1,
                             cache_releases=2,cache_release_order=[0,1,-1],live_fields_checked=2,
                             adjacency_checked=0,consumer_reads=0,quarantined_handles=3,
                             destroyed_before_owner_cleanup=[1,1,1,0,0])
        with self.assertRaises(ValueError):analyze(d,1,0,3,3,consume=False)
        self.assertEqual(analyze(d,1,0,3,3,original=True,consume=False)['borrower_contract'],'failed')

    def test_observer_reversal(self):
        with tempfile.TemporaryDirectory() as folder:
            folder=Path(folder);r=prepare(ROOT,folder/'observed.cpp',folder/'report.json')
            self.assertEqual(r['reversible_edits'],4)

    def test_ambiguous_or_missing_anchor(self):
        original=(ROOT/'src/crab_mesh/aft/advancing_front.cpp').read_text()
        with tempfile.TemporaryDirectory() as folder:
            folder=Path(folder);source=folder/'source.cpp'
            for text in (original+original,original.replace('    Face f;','    Face another;')):
                source.write_text(text)
                with self.assertRaises(ValueError):prepare(ROOT,folder/'observed.cpp',folder/'report.json',source)
                self.assertFalse((folder/'observed.cpp').exists())


if __name__=='__main__':unittest.main()
