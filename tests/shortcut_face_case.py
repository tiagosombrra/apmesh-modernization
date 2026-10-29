#!/usr/bin/env python3
"""Qualify pending Face ownership at the public three-edge geometry shortcut."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

CONTEXTS=[(s,r,p) for s in (0,1) for r in (0,1,2) for p in (0,1)]

def analyze(d,code,sorted_flag,rotation,prefix,mode,total,original=False):
    if (d['sorted'],d['rotation'],d['prefix'],d['mode'])!=(sorted_flag,rotation,prefix,str(mode)):raise ValueError('Wrong public-wrapper case identity')
    if d['profile'] not in ('native-allocation-observer','msvc-debug-crt') or total not in (3,4):raise ValueError('Unsupported instrument or allocation inventory')
    if sorted_flag not in (0,1) or rotation not in (0,1,2) or prefix not in (0,1):raise ValueError('Unsupported shortcut fixture context')
    triangles=prefix+1
    if any(d[k]!=3*triangles for k in ('owner_vertices','owner_edges','live_vertices','adjacency','free_edges')):raise ValueError('Live native owners, adjacency or free-state missing')
    if d['destroyed']!=[1]*(triangles*3)+[0]*(6-triangles*3):raise ValueError('Native owner destruction is not exactly once')
    if d['rejected'] or d['last_edge']:raise ValueError('Unchanged caller queue/counter state differs')
    guard=str(mode).startswith('guard-')
    if guard:
        count=int(str(mode)[6:])
        if count not in range(3) or prefix or d['front_count']!=count or d['front']!=count or d['returned']!=14 or d['mesh'] or d['last_face']:raise ValueError('Public fewer-than-three guard differs')
        if any(d[k] for k in ('seen','entered','attempts','denied','constructed','adopted','done','threw','face_freed','mid_freed','retained_blocks','retained_bytes')) or d['phase']!=-1:raise ValueError('Guard-only case entered a Face window or retained storage')
        if d['geometry_faces'] or d['before_id']!=-1 or d['face_id']!=-1 or d['before_mesh'] or d['endpoint_ids']!=[0]*3 or d['midpoint']!=[0]*2 or d['area']:raise ValueError('Guard fabricated a Face observation')
        if d['cleanup_calls'] or d['cleanup_allocations']:raise ValueError('Guard entered cleanup')
        return 'guard only'
    ordinal=int(mode)
    if d['front_count']!=3 or d['front']!=3:raise ValueError('Shortcut changed original front order/size')
    if d['seen']!=1 or d['entered']!=1 or d['before_mesh']!=prefix or d['before_id']!=prefix:raise ValueError('Shortcut window or committed prefix is missing')
    if d['attempts']!=(ordinal or total) or d['denied']!=int(ordinal>0) or d['threw']!=int(ordinal>0) or d['done']!=int(ordinal==0):raise ValueError('Missing calibrated denial/propagation')
    if d['returned']!=(-1 if ordinal else 5):raise ValueError('Native return status differs')
    completed=not ordinal or ordinal==total
    if (d['constructed'],d['adopted'],d['phase'])!=(int(completed),int(ordinal==0),2 if not ordinal else 1 if completed else 0):raise ValueError('Native construction/publication timing differs')
    if d['last_face']!=prefix+int(ordinal!=1) or d['mesh']!=prefix+int(ordinal==0) or d['geometry_faces']!=d['mesh']:raise ValueError('Original ID timing or Face prefix differs')
    if completed:
        if d['face_id']!=triangles or d['endpoint_ids']!=[101+3*prefix+(rotation+n)%3 for n in range(3)]:raise ValueError('Original front-to-Face endpoint ordering differs')
        if d['midpoint']!=[3*prefix+0.5,1/3] or d['area']!=0.5:raise ValueError('Independent midpoint/area expectation differs')
    elif d['face_id']!=-1 or d['endpoint_ids']!=[0]*3 or d['midpoint']!=[0]*2 or d['area']:raise ValueError('Incomplete Face construction was observed as complete')
    retained=bool(original and ordinal==total)
    cleanup=int(not original and ordinal==total)
    if d['cleanup_allocations'] or d['cleanup_calls']!=cleanup:raise ValueError('Cleanup allocated or did not execute exactly once')
    freed=int(completed and not retained)
    if d['face_freed']!=freed or d['mid_freed']!=freed:raise ValueError('Actual Face/cache destruction differs')
    if retained:
        if code!=1 or (d['retained_blocks'],d['retained_bytes'])!=((2,136) if total==3 else (3,144)):raise ValueError('Original pending-ownership failure not retained')
        return 'failed original pending ownership'
    if code or d['retained_blocks'] or d['retained_bytes']:raise ValueError('Unexpected storage retention or exit')
    return 'preserved' if not original else ('normal observed' if not ordinal else 'construction unwind')


def qualify(exe,output,original=None,broken=None,runtime=None,asan_control=False):
    output.mkdir(parents=True,exist_ok=False)
    env=os.environ.copy()
    if runtime:env['PATH']=str(runtime.resolve())+os.pathsep+env.get('PATH','')
    if asan_control:env['ASAN_OPTIONS']='detect_leaks=0:alloc_dealloc_mismatch=1:halt_on_error=1'
    report={'status':'running','cases':[],'executables':{},'normal_comparisons':0,
            'denial_comparisons':0,'guard_comparisons':0,'original_failed_pending_owner_contracts':0,
            'nonallocating_cleanups':0,'wrong_deleter_detections':0,
            'scope':'Public exact-three shortcut, cyclic fronts, sorting flags and zero/one committed prefix; no arbitrary topology or whole-process/retry claim'}
    for label,binary in [('candidate',exe),('original',original),('broken',broken)]:
        if binary:report['executables'][label]={'path':str(binary.resolve()),'sha256':hashlib.sha256(binary.read_bytes()).hexdigest()}

    def run(binary,label,s,rotation,prefix,mode):
        command=[str(binary.resolve()),str(s),str(rotation),str(prefix),str(mode)]
        name=f'{label}-{s}-{rotation}-{prefix}-{mode}.log'
        with (output/name).open('xb') as log:
            process=subprocess.run(command,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=30)
        raw=(output/name).read_bytes();text=raw.decode(errors='replace').replace('\r\n','\n')
        case={'label':label,'sorted':s,'rotation':rotation,'prefix':prefix,'mode':str(mode),
              'command':command,'exit':process.returncode,'log':name,'log_sha256':hashlib.sha256(raw).hexdigest()}
        report['cases'].append(case)
        if label=='broken':
            expected=f'borrowed_endpoint_destroyed={3*prefix} phase=1 denied=1\n'
            if process.returncode!=4 or text!=expected:raise ValueError('Actual wrong-deleter borrower destruction was not detected')
            case['actual_wrong_deleter_detected']=True;report['wrong_deleter_detections']+=1
            return case
        if mode=='uaf-control':
            if process.returncode==0 or 'ERROR: AddressSanitizer: heap-use-after-free' not in text:
                raise ValueError('Actual ASan invalid-access control was not detected')
            case['expected_invalid_access_detected']=True
            return case
        if 'ERROR: AddressSanitizer:' in text:raise ValueError('Unexpected native invalid access')
        case['observation']=json.loads(text)
        return case

    def unchanged(d):
        return {k:v for k,v in d.items() if k not in ('cleanup_calls','cleanup_allocations','face_freed','mid_freed','retained_blocks','retained_bytes')}

    try:
        candidate={};totals={}
        for label,binary in [('candidate',exe)]+([('original',original)] if original else []):
            for s,rotation,prefix in CONTEXTS:
                first=run(binary,label,s,rotation,prefix,0);total=first['observation']['attempts']
                if total not in (3,4):raise ValueError('Unsupported allocation calibration')
                context=(s,rotation,prefix)
                if label=='candidate':totals[context]=total
                elif total!=totals[context]:raise ValueError('Original/candidate allocation counts differ')
                cases=[first]+[run(binary,label,s,rotation,prefix,n) for n in range(1,total+1)]
                for case in cases:
                    mode=case['mode'];d=case['observation']
                    case['pending_owner_contract']=analyze(d,case['exit'],s,rotation,prefix,mode,total,label=='original')
                    key=(s,rotation,prefix,mode)
                    if label=='candidate':
                        candidate[key]=d;report['nonallocating_cleanups']+=d['cleanup_calls']
                    else:
                        report['original_failed_pending_owner_contracts']+=case['pending_owner_contract']=='failed original pending ownership'
                        if unchanged(d)!=unchanged(candidate[key]):raise ValueError('Native state, geometry or ID timing differs')
                        if mode=='0':
                            if {k:v for k,v in d.items() if k not in ('cleanup_calls','cleanup_allocations')}!={k:v for k,v in candidate[key].items() if k not in ('cleanup_calls','cleanup_allocations')}:
                                raise ValueError('Normal original/candidate traces differ')
                            report['normal_comparisons']+=1
                        else:report['denial_comparisons']+=1
            for count in range(3):
                mode=f'guard-{count}';case=run(binary,label,0,0,0,mode);d=case['observation']
                case['pending_owner_contract']=analyze(d,case['exit'],0,0,0,mode,3,label=='original')
                if label=='candidate':candidate[mode]=d
                else:
                    if d!=candidate[mode]:raise ValueError('Native guard result differs')
                    report['guard_comparisons']+=1
        for mode in ('denial-control','leak-control'):
            case=run(exe,'control',0,0,0,mode);d=case['observation']
            valid=(case['exit']==0 and d['attempts']==d['denied']==d['threw']==1 and not d['retained_blocks'] and not d['retained_bytes']) if mode=='denial-control' else (case['exit']==1 and d['retained_blocks']>0 and d['retained_bytes']>0)
            if not valid:raise ValueError('Independent allocation instrument control failed')
            case['independent_control_detected']=True
        if asan_control:run(exe,'control',0,0,0,'uaf-control')
        if broken:
            for s,rotation,prefix in CONTEXTS:
                run(broken,'broken',s,rotation,prefix,totals[(s,rotation,prefix)])
        report.update(status='passed',expected_outcomes=len(report['cases']))
    except Exception as error:report.update(status='failed',failure=repr(error));raise
    finally:(output/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--exe',type=Path,required=True)
    parser.add_argument('--original',type=Path)
    parser.add_argument('--broken',type=Path)
    parser.add_argument('--runtime',type=Path)
    parser.add_argument('--asan-control',action='store_true')
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--repeatable-output',action='store_true')
    args=parser.parse_args()
    if args.repeatable_output:
        args.output.mkdir(parents=True,exist_ok=True)
        args.output=Path(tempfile.mkdtemp(prefix='run-',dir=args.output))/'evidence'
    result=qualify(args.exe,args.output,args.original,args.broken,args.runtime,args.asan_control)
    print(json.dumps({k:result[k] for k in ('status','expected_outcomes','normal_comparisons','original_failed_pending_owner_contracts','nonallocating_cleanups','wrong_deleter_detections')}))
