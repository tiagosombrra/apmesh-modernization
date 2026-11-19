"""Independent Python reference checks and actual native pipeline controls."""
import copy
import math
from pathlib import Path
import subprocess
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools'))
import quad_quadratic_curvature as jet
from independent_jet_oracle import audit_records, eigenvalues3, qr_solve

PROBE=Path(sys.argv.pop(1)).resolve()


class JetReferenceTests(unittest.TestCase):
    def test_closed_form_mean_plane_paraboloid_saddle(self):
        for a,b,c in ((0,0,0),(0.5,0.5,0),(0.5,-0.5,0),(0,0,1),(0.5,0,0)):
            controls=tuple(tuple((i/3,j/3,a*i*(i-1)/6+b*j*(j-1)/6+c*i*j/9) for j in range(4)) for i in range(4))
            for u,v in ((0,0),(0.2,0.7),(1,1)):
                p,q=2*a*u+c*v,2*b*v+c*u
                expected=((1+q*q)*2*a-2*p*q*c+(1+p*p)*2*b)/(2*(1+p*p+q*q)**1.5)
                self.assertAlmostEqual(jet.source_mean(u,v,controls),expected,places=12)

    def test_independent_householder_solution(self):
        beta=(0.3,0.2,-0.1,0.25,0.08,-0.15)
        a=[];b=[]
        for x in (-1,0,1):
            for y in (-1,0,1):
                row=(1,x,y,x*x,x*y,y*y);a.append(row)
                b.append(sum(p*q for p,q in zip(row,beta))+0.02*(x*x-2/3)*y)
        rank,actual=qr_solve(a,b)
        self.assertEqual(rank,6)
        for p,q in zip(actual,beta):self.assertAlmostEqual(p,q,places=12)
        for row in a:
            # Replacing one quadratic column gives a genuine deficient system.
            self.assertEqual(len(row),6)
        bad=[list(row[:5])+[row[3]] for row in a]
        self.assertLess(qr_solve(bad,b)[0],6)

    def test_characteristic_eigenvalues(self):
        # Rotation of diag(1,2,3) around z by pi/4 gives a known non-diagonal case.
        for c in ([[1.5,-0.5,0],[-0.5,1.5,0],[0,0,3]],[[1,0,0],[0,2,0],[0,0,3]]):
            for p,q in zip(eigenvalues3(c),(1,2,3)):self.assertAlmostEqual(p,q,places=12)

    def test_native_boundary_counterexample_is_not_erased(self):
        xyz=[(x,y,(x*x+y*y)/2) for y in (-0.1,0,0.1) for x in (-0.1,0,0.1)]
        normals=[(-p[0],-p[1],1) for p in xyz]
        faces=[(0,1,4,3),(1,2,5,4),(3,4,7,6),(4,5,8,7)]
        rows,_=jet.native_records(PROBE,xyz,normals,faces)
        self.assertAlmostEqual(rows[4]['K'],1,places=10)
        self.assertAlmostEqual(rows[4]['H'],1,places=10)
        self.assertAlmostEqual(rows[1]['K'],0,places=10)
        self.assertGreater(abs(rows[1]['K']-1/1.01**2),0.9)
        for fault in ('masked','foreign','H','boundary','condition'):
            wrong=copy.deepcopy(rows)
            if fault=='masked':wrong[4].update(status='rank_deficient',K=None,H=None)
            elif fault=='foreign':wrong[4]['support']=wrong[4]['support'][:-1]
            elif fault=='boundary':wrong[4]['boundary']=True
            elif fault=='condition':wrong[4]['condition']+=1
            else:wrong[4]['H']+=1
            with self.assertRaises(ValueError):audit_records(xyz,normals,faces,wrong)

    def test_native_coarse_coverage_has_no_zero_fallback(self):
        xyz=[(0,0,0),(1,0,0),(1,1,0),(0,1,0),(0.5,0.5,0)]
        normals=[(0,0,1)]*5;faces=[(0,1,4),(1,2,4),(2,3,4),(3,0,4)]
        rows,_=jet.native_records(PROBE,xyz,normals,faces)
        self.assertTrue(all(r['status']=='insufficient_samples' and r['ring']==2 and r['K'] is None and r['H'] is None for r in rows))
        wrong=copy.deepcopy(rows);wrong[0]['K']=wrong[0]['H']=0
        with self.assertRaises(ValueError):audit_records(xyz,normals,faces,wrong)

    def test_native_malformed_probe_rejects_before_output(self):
        r=subprocess.run([str(PROBE)],input='0 0\n',text=True,capture_output=True,timeout=30)
        self.assertEqual(r.returncode,1);self.assertEqual(r.stdout,'');self.assertTrue(r.stderr.strip())


if __name__=='__main__':unittest.main()
