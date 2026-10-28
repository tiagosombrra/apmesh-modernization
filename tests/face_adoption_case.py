#!/usr/bin/env python3
"""Qualify pending Face ownership using actual native selection and publication."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import tempfile

CONTEXTS = [(front,geometry,prefix) for front,geometry in ((0,0),(1,0),(0,1)) for prefix in (0,1)]


def analyze(d, code, front, geometry, prefix, ordinal, total, original=False):
    if (d['front_based'],d['geometry'],d['prefix'],d['mode']) != (front,geometry,prefix,str(ordinal)):
        raise ValueError('Wrong native adoption case identity')
    if d['profile'] not in ('native-allocation-observer','msvc-debug-crt') or (front,geometry,prefix) not in CONTEXTS:
        raise ValueError('Unqualified profile or queue/phase context')
    triangles=prefix+1
    if not all(d[k]==triangles*3 for k in ('owner_vertices','owner_edges','live_vertices','adjacency')):
        raise ValueError('Missing live native owner/adjacency inventory')
    if d['destroyed'] != [1]*(triangles*3)+[0]*(6-triangles*3):
        raise ValueError('Actual vertex owners did not destroy each vertex once')
    if d['free_edges'] or d['last_edge'] or d['front'] != (0 if front else triangles*2) or d['rejected']:
        raise ValueError('Original existing-edge queue/free-state trace changed')
    if d['mesh'] != (prefix if ordinal else triangles) or d['geometry_faces'] != d['mesh']:
        raise ValueError('Committed Face prefix or geometry changed')
    if d['threw'] != int(ordinal>0) or d['done'] != int(ordinal==0):
        raise ValueError('Allocation failure propagation or completion changed')
    if d['last_face'] != prefix+(ordinal!=1):
        raise ValueError('Original new-expression ID timing changed')
    if total not in (3,4) or d['seen'] != triangles or d['entered'] != 1:
        raise ValueError('Incomplete positive native adoption coverage')
    if d['attempts'] != (ordinal or total) or d['denied'] != int(ordinal>0):
        raise ValueError('Calibrated allocation denial is missing')
    if d['before_id'] != prefix or d['before_mesh'] != prefix:
        raise ValueError('Committed prefix identity is missing')
    completed=ordinal==0 or ordinal==total
    leaked=bool(original and ordinal==total)
    if (d['constructed'],d['adopted'],d['phase']) != (int(completed),int(ordinal==0),2 if ordinal==0 else 1 if completed else 0):
        raise ValueError('Native construction/publication transition differs')
    if d['face_freed'] != int(completed and not leaked) or d['mid_freed'] != d['face_freed']:
        raise ValueError('Pending Face/cache destruction is incomplete')
    if completed:
        if d['face_id'] != triangles or d['endpoint_ids'] != [101+prefix*3+n for n in range(3)]:
            raise ValueError('Pending Face/endpoint identity changed')
        if len(d['midpoint']) != 2 or any(not math.isfinite(x) for x in d['midpoint']) or d['midpoint'] != [3*prefix+0.5,1/3] or d['area'] != 0.5:
            raise ValueError('Independent native midpoint or area differs')
    elif d['face_id'] != -1 or d['endpoint_ids'] != [0]*3 or d['midpoint'] != [0]*2 or d['area']:
        raise ValueError('Uncompleted construction was published')
    if leaked:
        if code != 1 or d['retained_blocks'] != total-1 or d['retained_bytes'] <= 0:
            raise ValueError('Original failed pending-owner contract was not retained')
    elif code != 0 or d['retained_blocks'] or d['retained_bytes']:
        raise ValueError('Pending storage remains after front teardown')
    return {'pending_owner_contract':'failed' if leaked else 'preserved'}


def qualify(exe, output, original=None, broken=None, runtime=None, asan_control=False):
    output.mkdir(parents=True,exist_ok=False)
    env=os.environ.copy()
    if runtime:env['PATH']=str(runtime.resolve())+os.pathsep+env.get('PATH','')
    if asan_control:env['ASAN_OPTIONS']='detect_leaks=0:alloc_dealloc_mismatch=1:halt_on_error=1'
    report={'status':'running','cases':[],'executables':{},'normal_comparisons':0,
            'original_failed_pending_owner_contracts':0,'wrong_deleter_detections':0,
            'scope':'Actual native selector/makeMesh, existing edges, topology queues and prepared-root rejected geometry; no full rollback/retry claim'}

    def run(binary,label,front,geometry,prefix,mode):
        name=f'{label}-{front}-{geometry}-{prefix}-{mode}.log'
        command=[str(binary.resolve()),str(front),str(geometry),str(prefix),str(mode)]
        with (output/name).open('xb') as log:
            p=subprocess.run(command,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=30)
        raw=(output/name).read_bytes();text=raw.decode('utf-8',errors='replace')
        case={'label':label,'front':front,'geometry':geometry,'prefix':prefix,'mode':str(mode),
              'command':command,'exit_code':p.returncode,'log':name,'log_sha256':hashlib.sha256(raw).hexdigest()}
        report['cases'].append(case)
        if label=='broken':
            expected=f'borrowed_endpoint_destroyed={3*prefix} phase=1 denied=1\n'
            if p.returncode != 4 or text.replace('\r\n','\n') != expected:
                raise ValueError('Actual invalid-deleter borrower damage was not detected')
            case['expected_wrong_deleter_detected']=True
            report['wrong_deleter_detections']+=1
            return case
        if mode=='uaf-control':
            if p.returncode==0 or 'ERROR: AddressSanitizer: heap-use-after-free' not in text:
                raise ValueError('Actual ASan invalid-access control was not detected')
            case['expected_invalid_access_detected']=True
            return case
        if 'ERROR: AddressSanitizer:' in text:
            raise ValueError('Unexpected native invalid access')
        case['observation']=json.loads(text)
        return case

    try:
        normals={};totals={}
        binaries=[('candidate',exe)]+([('original',original)] if original else [])
        for label,binary in binaries:
            report['executables'][label]={'path':str(binary.resolve()),'sha256':hashlib.sha256(binary.read_bytes()).hexdigest()}
            for front,geometry,prefix in CONTEXTS:
                case=run(binary,label,front,geometry,prefix,0);d=case['observation'];total=d['attempts']
                case.update(analyze(d,case['exit_code'],front,geometry,prefix,0,total,label=='original'))
                context=(front,geometry,prefix)
                if label=='candidate':normals[context]=d;totals[context]=total
                else:
                    if d != normals[context]:raise ValueError('Successful original/candidate native traces differ')
                    report['normal_comparisons']+=1
                for ordinal in range(1,total+1):
                    case=run(binary,label,front,geometry,prefix,ordinal)
                    case.update(analyze(case['observation'],case['exit_code'],front,geometry,prefix,ordinal,total,label=='original'))
                    report['original_failed_pending_owner_contracts']+=case['pending_owner_contract']=='failed'
        for mode in ('denial-control','leak-control'):
            case=run(exe,'control',1,0,0,mode);d=case['observation']
            valid=(case['exit_code']==0 and d['attempts']==d['denied']==d['threw']==1 and d['retained_blocks']==d['retained_bytes']==0) if mode=='denial-control' else (case['exit_code']==1 and d['attempts']>0 and d['retained_blocks']>0 and d['retained_bytes']>0)
            if not valid:raise ValueError('Independent allocation/retention control failed')
            case['independent_control_detected']=True
        if asan_control:run(exe,'control',1,0,0,'uaf-control')
        if broken:
            report['executables']['broken']={'path':str(broken.resolve()),'sha256':hashlib.sha256(broken.read_bytes()).hexdigest()}
            for front,geometry,prefix in CONTEXTS:
                run(broken,'broken',front,geometry,prefix,totals[(front,geometry,prefix)])
        report.update(status='passed',expected_outcomes=len(report['cases']))
    except Exception as error:
        report.update(status='failed',failure=repr(error));raise
    finally:(output/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return report


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--exe',type=Path,required=True)
    p.add_argument('--original',type=Path)
    p.add_argument('--broken',type=Path)
    p.add_argument('--runtime',type=Path)
    p.add_argument('--asan-control',action='store_true')
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--repeatable-output',action='store_true')
    a=p.parse_args()
    if a.repeatable_output:
        a.output.mkdir(parents=True,exist_ok=True)
        a.output=Path(tempfile.mkdtemp(prefix='run-',dir=a.output))/'evidence'
    r=qualify(a.exe,a.output,a.original,a.broken,a.runtime,a.asan_control)
    print(json.dumps({k:r[k] for k in ('status','expected_outcomes','normal_comparisons','original_failed_pending_owner_contracts','wrong_deleter_detections')}))
