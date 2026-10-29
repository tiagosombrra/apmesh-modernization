#!/usr/bin/env python3
"""Qualify native marker ownership and preserve original failed contracts."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile


def analyze(d,code,stage,prefix,ordinal,marker_total,face_total,original=False):
    if (d['stage'],d['prefix'],d['mode'])!=(stage,prefix,str(ordinal)):raise ValueError('Case identity differs')
    if d['profile'] not in ('native-allocation-observer','msvc-debug-crt'):raise ValueError('Unsupported instrument')
    triangles=prefix+1
    if any(d[k]!=3*triangles for k in ('owner_vertices','owner_edges','live_vertices','adjacency')):raise ValueError('Missing owner or live adjacency evidence')
    if d['destroyed']!=[1]*(3*triangles)+[0]*(6-3*triangles):raise ValueError('Incorrect final owner destruction')
    if d['last_edge'] or d['rejected'] or d['marker_owned'] or d['marker_rejected']:raise ValueError('Owner or queue boundary changed')
    expected_total=marker_total if stage==0 else face_total if stage==2 else None
    if d['threw']!=int(ordinal>0) or d['done']!=int(ordinal==0) or d['denied']!=int(ordinal>0):raise ValueError('Missing failure propagation or completion')
    if ordinal and d['attempts']!=ordinal:raise ValueError('Missing calibrated denial')
    if not ordinal and expected_total is not None and d['attempts']!=expected_total:raise ValueError('Normal calibration differs')
    if not ordinal:
        if (d['constructed'],d['published'],d['retiring'],d['marker_freed'],d['mid_freed'],d['marker_front'])!=(1,1,1,1,1,0):raise ValueError('Normal marker lifecycle differs')
        if d['mesh']!=triangles or d['geometry_faces']!=triangles or d['front'] or d['free_edges'] or d['last_face']!=triangles:raise ValueError('Normal native state differs')
        if d['selection_seen']!=triangles or d['face_seen']!=triangles:raise ValueError('Actual selector or publication not executed')
        failed=False
    elif stage==0:
        completed=ordinal==marker_total
        if (d['constructed'],d['published'],d['retiring'],d['marker_front'])!=(int(completed),0,0,0):raise ValueError('Marker construction/publication differs')
        if d['mesh'] or d['geometry_faces'] or d['last_face'] or d['front']!=3*triangles or d['free_edges']!=3*triangles:raise ValueError('Preselection state changed')
        if d['selection_seen'] or d['face_seen']:raise ValueError('Marker window was bypassed')
        failed=completed
    else:
        if (d['constructed'],d['published'],d['retiring'],d['marker_front'])!=(1,1,0,int(original)):raise ValueError('Published marker trace differs')
        if d['mesh']!=prefix or d['geometry_faces']!=prefix or d['selection_seen']!=triangles:raise ValueError('Committed prefix or native selection differs')
        if stage==1:
            if ordinal!=1 or d['front']!=2+int(original) or d['free_edges']!=3 or d['last_face']!=prefix or d['face_seen']!=prefix:raise ValueError('First selector denial boundary differs')
        elif d['front']!=int(original) or d['free_edges'] or d['last_face']!=prefix+int(ordinal>1) or d['face_seen']!=triangles:raise ValueError('Pending Face denial boundary differs')
        failed=True
    constructed = int(d['constructed'] == 1)
    if d['cleanup_allocations'] or d['cleanup_calls'] != (0 if original else constructed):
        raise ValueError('Cleanup allocated or was not executed exactly once')
    if not original and (d['marker_freed'] != constructed or d['mid_freed'] != constructed):
        raise ValueError('Constructed marker/cache were not actually destroyed')
    if failed and original:
        if code!=1 or d['retained_blocks']!=marker_total-1 or d['retained_bytes']<=0 or d['marker_freed'] or d['mid_freed']:raise ValueError('Original marker retention not reproduced')
        return 'failed original marker ownership'
    if code or d['retained_blocks'] or d['retained_bytes']:raise ValueError('Unexpected retention or exit')
    return 'preserved' if not original else ('normal lifecycle' if not ordinal else 'construction unwind')


def qualify(exe, output, original=None, broken=None, premature=None, runtime=None, asan_control=False):
    output.mkdir(parents=True,exist_ok=False)
    env=os.environ.copy()
    if runtime:env['PATH']=str(runtime.resolve())+os.pathsep+env.get('PATH','')
    if asan_control:env['ASAN_OPTIONS']='detect_leaks=0:alloc_dealloc_mismatch=1:halt_on_error=1'
    report={'status':'running','cases':[],'executables':{},'normal_comparisons':0,
            'denial_comparisons':0,'original_failed_marker_contracts':0,
            'nonallocating_cleanups':0,'invalid_observer_detections':0,'premature_detections':0,
            'scope':'Native existing-edge geometry front and zero/one committed prefix; first selector allocation only; no wrapper/retry/whole-process claim'}
    for label,binary in [('candidate',exe),('original',original),('broken',broken),('premature',premature)]:
        if binary:report['executables'][label]={'path':str(binary.resolve()),'sha256':hashlib.sha256(binary.read_bytes()).hexdigest()}

    def run(binary,label,stage,prefix,mode):
        command=[str(binary.resolve()),str(stage),str(prefix),str(mode)]
        name=f'{label}-{stage}-{prefix}-{mode}.log'
        with (output/name).open('xb') as log:
            process=subprocess.run(command,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=30)
        raw=(output/name).read_bytes();text=raw.decode(errors='replace').replace('\r\n','\n')
        case={'label':label,'stage':stage,'prefix':prefix,'mode':str(mode),'command':command,
              'exit':process.returncode,'log':name,'log_sha256':hashlib.sha256(raw).hexdigest()}
        report['cases'].append(case)
        if label=='broken':
            if process.returncode!=4 or text!='expired_marker_observer front=1 rejected=0 owned=0\n':
                raise ValueError('Actual expired queue observation was not detected')
            case['expected_invalid_observer_detected']=True;report['invalid_observer_detections']+=1
            return case
        if label=='premature':
            if process.returncode!=5 or text!='marker_destroyed_before_consumption\n':
                raise ValueError('Actual premature marker destruction was not detected')
            case['expected_premature_detected']=True;report['premature_detections']+=1
            return case
        if mode=='uaf-control':
            if process.returncode==0 or 'ERROR: AddressSanitizer: heap-use-after-free' not in text:
                raise ValueError('Actual invalid-access instrument control was not detected')
            case['expected_invalid_access_detected']=True;return case
        if 'ERROR: AddressSanitizer:' in text:raise ValueError('Unexpected invalid native access')
        case['observation']=json.loads(text)
        return case

    def core(d):
        ignored={'cleanup_calls','cleanup_allocations','marker_freed','mid_freed',
                 'marker_front','retained_blocks','retained_bytes','front'}
        values={k:v for k,v in d.items() if k not in ignored}
        values['front_without_marker']=d['front']-d['marker_front']
        return values

    try:
        candidate={};calibration={}
        for label,binary in [('candidate',exe)]+([('original',original)] if original else []):
            for prefix in (0,1):
                marker=run(binary,label,0,prefix,0);marker_total=marker['observation']['attempts']
                face=run(binary,label,2,prefix,0);face_total=face['observation']['attempts']
                if (marker_total,face_total) not in ((4,3),(6,4)):
                    raise ValueError('Unsupported native allocation calibration')
                if label=='candidate':calibration[prefix]=(marker_total,face_total)
                elif calibration[prefix]!=(marker_total,face_total):raise ValueError('Original/candidate calibration differs')
                cases=[marker,face,run(binary,label,1,prefix,0)]
                for stage,limit in ((0,marker_total),(1,1),(2,face_total)):
                    cases.extend(run(binary,label,stage,prefix,n) for n in range(1,limit+1))
                for case in cases:
                    stage=case['stage'];ordinal=int(case['mode']);d=case['observation']
                    case['marker_contract']=analyze(d,case['exit'],stage,prefix,ordinal,marker_total,face_total,label=='original')
                    key=(stage,prefix,ordinal)
                    if label=='candidate':
                        candidate[key]=d
                        report['nonallocating_cleanups']+=d['cleanup_calls']
                    else:
                        report['original_failed_marker_contracts']+=case['marker_contract']=='failed original marker ownership'
                        if core(d)!=core(candidate[key]):raise ValueError('Non-marker native state or timing differs')
                        if not ordinal:
                            if {k:v for k,v in d.items() if k not in ('cleanup_calls','cleanup_allocations')}!={k:v for k,v in candidate[key].items() if k not in ('cleanup_calls','cleanup_allocations')}:
                                raise ValueError('Normal native traces differ')
                            report['normal_comparisons']+=1
                        else:report['denial_comparisons']+=1
        for mode in ('denial-control','leak-control'):
            case=run(exe,'control',0,0,mode);d=case['observation']
            valid=(case['exit']==0 and d['attempts']==d['denied']==d['threw']==1 and not d['retained_blocks'] and not d['retained_bytes']) if mode=='denial-control' else (case['exit']==1 and d['retained_blocks']>0 and d['retained_bytes']>0)
            if not valid:raise ValueError('Independent allocation instrument control failed')
            case['independent_control_detected']=True
        if asan_control:run(exe,'control',0,0,'uaf-control')
        if broken:
            for prefix in (0,1):
                for stage in (1,2):run(broken,'broken',stage,prefix,1)
        if premature:
            for prefix in (0,1):run(premature,'premature',0,prefix,0)
        report.update(status='passed',expected_outcomes=len(report['cases']))
    except Exception as error:report.update(status='failed',failure=repr(error));raise
    finally:(output/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--exe',type=Path,required=True)
    parser.add_argument('--original',type=Path)
    parser.add_argument('--broken',type=Path)
    parser.add_argument('--premature',type=Path)
    parser.add_argument('--runtime',type=Path)
    parser.add_argument('--asan-control',action='store_true')
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--repeatable-output',action='store_true')
    args=parser.parse_args()
    if args.repeatable_output:
        args.output.mkdir(parents=True,exist_ok=True)
        args.output=Path(tempfile.mkdtemp(prefix='run-',dir=args.output))/'evidence'
    result=qualify(args.exe,args.output,args.original,args.broken,args.premature,args.runtime,args.asan_control)
    print(json.dumps({k:result[k] for k in ('status','expected_outcomes','normal_comparisons','original_failed_marker_contracts','nonallocating_cleanups','invalid_observer_detections','premature_detections')}))
