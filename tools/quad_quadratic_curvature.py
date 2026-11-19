"""Read-only adopted quadratic-jet K/H candidate on retained Bezier snapshots.

Available means a finite converged full-rank estimate, not certified accuracy.
No legacy node curvature, geometry, global error or adaptive state is changed.
"""
import argparse
import copy
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import statistics
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tests/quad'))
from independent_common_grid import load_physical_obj
from independent_jet_oracle import audit_records
from quad_diagonal_curvature import source_gaussian
from quad_generation_metrics import cross, dot, norm
from test_m4_real_model_hybrid import CONTROLS, basis, golden

STATUSES = {'available','insufficient_samples','duplicate_samples','degenerate_scale','ambiguous_frame',
            'undefined_orientation','rank_deficient','solver_unconverged','nonfinite'}


def source_mean(u, v, controls=CONTROLS):
    bu, du = basis(u);bv, dv = basis(v)
    ddu=(6*(1-u),18*u-12,6-18*u,6*u)
    ddv=(6*(1-v),18*v-12,6-18*v,6*v)
    def derivative(a,b):
        return tuple(sum(a[i]*b[j]*controls[i][j][k] for i in range(4) for j in range(4)) for k in range(3))
    qu,qv,quu,quv,qvv=[derivative(a,b) for a,b in ((du,bv),(bu,dv),(ddu,bv),(du,dv),(bu,ddv))]
    normal=cross(qu,qv);size=norm(normal)
    if size <= 0 or not math.isfinite(size):
        raise ValueError('Singular analytical mean reference')
    return (dot(normal,quu)*dot(qv,qv)-2*dot(normal,quv)*dot(qu,qv)+dot(normal,qvv)*dot(qu,qu))/(2*size**3)


def native_records(probe, xyz, normals, faces):
    data=f'{len(xyz)} {len(faces)}\n'
    data+=''.join(' '.join(map(repr,(*p,*n)))+'\n' for p,n in zip(xyz,normals))
    data+=''.join(' '.join(map(str,(len(f),*f)))+'\n' for f in faces)
    process=subprocess.run([str(probe)],input=data,text=True,capture_output=True,timeout=120)
    if process.returncode:
        raise ValueError('Native jet probe failed: '+process.stderr)
    rows=list(csv.DictReader(io.StringIO(process.stdout)))
    result=[]
    for row in rows:
        if row['status'] not in STATUSES:
            raise ValueError('Unknown native jet status')
        record={k:(None if v=='' else float(v)) for k,v in row.items() if k not in ('node','status','ring','boundary','support')}
        if any(v is not None and not math.isfinite(v) for v in record.values()):
            raise ValueError('Nonfinite native jet export')
        if row['boundary'] not in ('0','1'):
            raise ValueError('Invalid native boundary flag')
        record.update(node=int(row['node']),status=row['status'],ring=int(row['ring']),boundary=row['boundary']=='1',
                      support=list(map(int,row['support'].split('|'))))
        result.append(record)
    audit=audit_records(xyz,normals,faces,result)
    return result,audit


def forgery_controls(xyz, normals, faces, rows):
    available=next((i for i,r in enumerate(rows) if r['status']=='available' and abs(r['H'])>1e-5),None)
    if available is None:
        forged=copy.deepcopy(rows)
        forged[0]['K']=forged[0]['H']=0.0
        try:audit_records(xyz,normals,faces,forged)
        except ValueError:return 1
        raise ValueError('Zero fallback escaped unavailable-node audit')
    for fault in ('missing','duplicate','support','K','H','status','normal','ring','masked_available'):
        forged=copy.deepcopy(rows);r=forged[available]
        if fault=='missing':forged.pop()
        elif fault=='duplicate':forged[-1]=copy.deepcopy(forged[0])
        elif fault=='support':r['support']=r['support'][:-1]
        elif fault=='K':r['K']+=1
        elif fault=='H':r['H']=-r['H']
        elif fault=='status':r['status']='insufficient_samples'
        elif fault=='normal':r['fit_nz']+=1
        elif fault=='ring':r['ring']=3
        else:r.update(status='rank_deficient',K=None,H=None)
        try:audit_records(xyz,normals,faces,forged)
        except ValueError:continue
        raise ValueError('Forged jet observation escaped: '+fault)
    return 9


def measure_archive(archive, probe, output):
    archive,output=Path(archive).resolve(),Path(output).resolve()
    with (archive/'manifest.csv').open(encoding='utf-8') as handle:manifest=list(csv.DictReader(handle))
    if not manifest:raise ValueError('Empty jet archive')
    hashes={archive/'manifest.csv':hashlib.sha256((archive/'manifest.csv').read_bytes()).hexdigest()}
    stages=[];forgeries=0;available_controls=False;agreement=dict(coefficient=0.0,K=0.0,H=0.0)
    for source in manifest:
        for scheme,key in (('TRI','tri_obj'),('QUAD_TRI','quad_tri_obj')):
            path=(archive/source[key]).resolve()
            if path.parent!=archive:raise ValueError('Foreign jet archive path')
            hashes[path]=hashlib.sha256(path.read_bytes()).hexdigest()
            xyz,uv,faces=load_physical_obj(path)
            normals=[]
            for p,at in zip(xyz,uv):
                expected,du,dv=golden(*at)
                if not all(0<=t<=1 for t in at) or math.dist(p,expected)>2e-7*max(1,norm(p)):
                    raise ValueError('Jet archive requires builtin:curva_bezier')
                normals.append(cross(du,dv))
            rows,maximum=native_records(probe,xyz,normals,faces)
            for k,v in maximum.items():agreement[k]=max(agreement[k],v)
            # Fixed QUAD representation: cyclic rotation changes no stencil/order/value.
            rotated=[f[1:]+f[:1] if len(f)==4 else f for f in faces]
            if any(len(f)==4 for f in faces):
                other,_=native_records(probe,xyz,normals,rotated)
                if rows!=other:raise ValueError('QUAD cycle changed the jet estimator')
            has_available=any(r['status']=='available' and abs(r['H'])>1e-5 for r in rows)
            if forgeries==0 or (has_available and not available_controls):
                forgeries+=forgery_controls(xyz,normals,faces,rows)
                available_controls=available_controls or has_available
            for i,row in enumerate(rows):
                row.update(analytical_K=source_gaussian(*uv[i]),analytical_H=source_mean(*uv[i]))
                row['abs_K_difference']=abs(row['K']-row['analytical_K']) if row['K'] is not None else None
                row['abs_H_difference']=abs(row['H']-row['analytical_H']) if row['H'] is not None else None
            def stats(key, boundary=None):
                values=[r[key] for r in rows if r[key] is not None and (boundary is None or r['boundary']==boundary)]
                return dict(count=len(values),maximum=max(values) if values else None,median=statistics.median(values) if values else None)
            status={name:sum(r['status']==name for r in rows) for name in sorted(STATUSES)}
            stage=dict({k:source[k] for k in ('step','epoch','retry','domain_generation','reference_tri_accepted','reason')},
                       scheme=scheme,file=path.name,sha256=hashes[path],nodes=len(xyz),coverage=status,
                       K_absolute=stats('abs_K_difference'),H_absolute=stats('abs_H_difference'),
                       boundary_K=stats('abs_K_difference',True),boundary_H=stats('abs_H_difference',True),
                       interior_K=stats('abs_K_difference',False),interior_H=stats('abs_H_difference',False),
                       per_node=rows)
            stages.append(stage)
    if not all(hashlib.sha256(p.read_bytes()).hexdigest()==h for p,h in hashes.items()):raise ValueError('Jet input bytes changed')
    report=dict(schema='apmesh.quad.quadratic_jet.v1',source='builtin:curva_bezier',stages=stages,
                inputs_sha256={p.name:h for p,h in hashes.items()},probe_sha256=hashlib.sha256(Path(probe).read_bytes()).hexdigest(),
                independent_agreement_max=agreement,rejected_forgeries=forgeries,mixed_global_error=None,accepted_mixed_epochs=0,
                scope='Adopted nodal candidate only. Available means finite/full rank, not accurate. K and H errors remain separate; boundary fits are one-sided; no global aggregation, adaptation or legacy mean repair.')
    output.mkdir(parents=True,exist_ok=False)
    (output/'jet.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    with (output/'nodes.csv').open('w',newline='',encoding='utf-8') as handle:
        identity=['step','epoch','retry','domain_generation','reference_tri_accepted','reason','scheme','file','sha256']
        writer=csv.DictWriter(handle,identity+list(stages[0]['per_node'][0]));writer.writeheader()
        for stage in stages:
            for record in stage['per_node']:
                row=dict({k:stage[k] for k in identity},**record);row['support']='|'.join(map(str,row['support']));writer.writerow(row)
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive',type=Path,required=True);parser.add_argument('--probe',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();report=measure_archive(args.archive,args.probe,args.output)
    print(json.dumps(dict(stages=len(report['stages']),rejected_forgeries=report['rejected_forgeries'],agreement=report['independent_agreement_max'])))


if __name__=='__main__':main()
