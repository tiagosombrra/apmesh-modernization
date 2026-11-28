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
from quad_two_ring_comparison import compare_reports, paired_group

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

    def test_independent_eigenvalues(self):
        # Rotation of diag(1,2,3) around z by pi/4 gives a known non-diagonal case.
        for c in ([[1.5,-0.5,0],[-0.5,1.5,0],[0,0,3]],[[1,0,0],[0,2,0],[0,0,3]]):
            for p,q in zip(eigenvalues3(c),(1,2,3)):self.assertAlmostEqual(p,q,places=12)
        # The observed failure is diagonal with a repeated tangent eigenvalue.
        for values in ((1.1111105555558335e-7,0.33333316666674995,0.33333316666674995),(0,0,0),(2,2,2),(1e-20,1,1)):
            c=[[values[i] if i==j else 0 for j in range(3)] for i in range(3)]
            for p,q in zip(eigenvalues3(c),values):self.assertAlmostEqual(p,q,places=12)
        # Dense known spectrum: C=2I-v*v^T for v=(1,2,3)/sqrt(14).
        c=[[2*int(i==j)-(i+1)*(j+1)/14 for j in range(3)] for i in range(3)]
        for p,q in zip(eigenvalues3(c),(1,2,2)):self.assertAlmostEqual(p,q,places=12)

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

    def test_complete_two_ring_distinguishes_counterexample_and_is_explicit(self):
        xyz=[(x,y,(x*x+y*y)/2) for y in (-0.1,0,0.1) for x in (-0.1,0,0.1)]
        normals=[(-p[0],-p[1],1) for p in xyz]
        faces=[(0,1,4,3),(1,2,5,4),(3,4,7,6),(4,5,8,7)]
        old,_=jet.native_records(PROBE,xyz,normals,faces)
        new,_=jet.native_records(PROBE,xyz,normals,faces,policy='complete_two_ring')
        self.assertTrue(all(r['ring']==2 and r['support']==list(range(9)) for r in new))
        self.assertAlmostEqual(new[1]['K'],1/1.01**2,places=10)
        with self.assertRaises(ValueError):audit_records(xyz,normals,faces,old,required_ring=2)
        bad=subprocess.run([str(PROBE),'--unknown-ring'],input='',text=True,capture_output=True,timeout=30)
        self.assertEqual(bad.returncode,1);self.assertEqual(bad.stdout,'')
        reports=[]
        for records in (old,new):
            data=copy.deepcopy(records)
            for p,r in zip(xyz,data):
                d=1+p[0]**2+p[1]**2
                r.update(analytical_K=1/d**2,analytical_H=(d+1)/(2*d**1.5))
                for channel in ('K','H'):r[f'abs_{channel}_difference']=abs(r[channel]-r[f'analytical_{channel}'])
            stage=dict(step='1',epoch='1',retry='-1',domain_generation='1',reference_tri_accepted='1',reason='fixture',scheme='QUAD_TRI',file='fixed.obj',sha256='fixed',nodes=9,coverage={'available':9},per_node=data)
            reports.append(dict(source='fixture',inputs_sha256={'fixed.obj':'fixed'},mixed_global_error=None,accepted_mixed_epochs=0,stages=[stage]))
        reports[1]['neighborhood_policy']='complete_two_ring'
        result,_=compare_reports(*reports)
        self.assertEqual(result['stages'][0]['boundary']['K']['paired_changes']['improved'],4)
        bad=copy.deepcopy(reports[1]);bad['inputs_sha256']['fixed.obj']='changed'
        with self.assertRaises(ValueError):compare_reports(reports[0],bad)
        bad=copy.deepcopy(reports[1]);bad['stages'][0]['per_node'][1]['ring']=1
        with self.assertRaises(ValueError):compare_reports(reports[0],bad)

    def test_larger_stencil_can_worsen_analytical_curvature(self):
        xyz=[(x,y,x**4) for y in (-0.2,-0.1,0,0.1,0.2) for x in (-0.2,-0.1,0,0.1,0.2)]
        normals=[(-4*p[0]**3,0,1) for p in xyz]
        faces=[(r*5+c,r*5+c+1,r*5+c+6,r*5+c+5) for r in range(4) for c in range(4)]
        old,_=jet.native_records(PROBE,xyz,normals,faces)
        new,_=jet.native_records(PROBE,xyz,normals,faces,policy='complete_two_ring')
        self.assertAlmostEqual(old[12]['H'],0.01,places=10)
        self.assertAlmostEqual(new[12]['H'],31/700,places=10)
        self.assertGreater(abs(new[12]['H']),abs(old[12]['H'])+0.03)

    def test_paired_coverage_and_worsening_cannot_be_dropped(self):
        old=[dict(status='available',boundary=True,abs_K_difference=1,abs_H_difference=2,scale=1,condition=2,support=[0]) for _ in range(3)]
        new=copy.deepcopy(old)
        new[0].update(abs_K_difference=0.5,abs_H_difference=3,support=[0,1])
        new[1].update(status='rank_deficient',abs_K_difference=None,abs_H_difference=None,support=[0,1])
        result=paired_group(old,new)
        self.assertEqual(result['coverage'],dict(both_available=2,original_only=1,variant_only=0,neither=0))
        self.assertEqual(result['K']['paired_changes'],dict(improved=1,worsened=0,numerical_tie=1))
        self.assertEqual(result['H']['paired_changes'],dict(improved=0,worsened=1,numerical_tie=1))


if __name__=='__main__':unittest.main()
