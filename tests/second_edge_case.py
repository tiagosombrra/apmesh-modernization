#!/usr/bin/env python3
"""Qualify native second-edge ownership while preserving first-edge/Face prefixes."""
"""Check independent geometry and the pending/owned second-edge boundary."""
import argparse
import hashlib
import itertools
import json
import os
from pathlib import Path
import subprocess
import tempfile
CONTEXTS=list(itertools.product((0,1),repeat=5))
CLEANUP_FIELDS={'owned','cleanup_calls','cleanup_allocations'}
FAILURE_FIELDS=CLEANUP_FIELDS|{'freed','mid_freed','adjacency','pending_geometry','retained_blocks','retained_bytes'}

def require(value,message):
 if not value:raise ValueError(message)

def cyclic(values):return min(tuple(values[i:]+values[:i]) for i in range(3))

def analyze(d,code,context,n,ctor,original=False):
 front,geometry,sorted_,prefix,first_new=context
 total=ctor+6;base_owners=4+2*first_new+3*prefix
 require(0<=n<=total,'Unsupported allocation denial')
 cleanup=int(not original and ctor<n<ctor+4)
 require(tuple(context) in CONTEXTS and ctor in (3,5),'Unsupported diagnosis context/profile')
 require(d['context']==list(context) and d['target']==n and d['action']==0 and d['owned']==int(not original),'Wrong case identity')
 require(d['entered']==1 and d['before_id']==first_new and d['before_owners']==base_owners,'Missing second-edge window/first-owner prefix')
 require(d['borrowed']==4+first_new+3*prefix,'Live borrower count differs')
 require(d['destroyed']==([1,1,1] if prefix else [0,0,0])+[0,0,0]+[1,1,1,1,first_new,0],'Borrower retirement is not exactly once')
 require(d['first_owned']==d['first_view']==1 and d['first_adjacency']==2 and d['first_cell']==first_new,'First edge lost owner/view/adjacency/cell publication')
 require(d['first_id']==(1 if first_new else 210) and d['first_freed']==d['first_mid_freed']==1,'First edge identity/retirement differs')
 require(d['first_geometry']==([107,110,3.5,0.5] if first_new else [110,107,3,0.5]),'First edge live endpoints/cache differ')
 require(d['last_edge']==first_new+int(n!=1) and d['edge_id']==(-1 if 0<n<=ctor else first_new+1),'Original new-expression ID timing differs')
 require(d['cleanup_allocations']==0 and d['cleanup_calls']==cleanup,'Production cleanup allocated or was not executed once')
 expected_faces=[]
 if prefix:expected_faces.append([1,101,102,103,0.5,1/3,0.5])
 if n==0:
  require(code==0 and d['threw']==d['denied']==0 and d['status']==(5 if geometry else 6),'Native normal status differs')
  require(d['phase']==7 and d['attempts']==total and d['retained_blocks']==d['retained_bytes']==0,'Normal window/allocation/retention differs')
  require(d['mesh']==d['last_face']==2+first_new+prefix and d['owners']==d['views']==base_owners+1,'Normal committed owners/Faces differ')
  require(d['front']==(0 if front else 3+first_new) and d['rejected']==d['queue_pending']==d['free_edges']==0,'Normal queue/free state differs')
  require(d['cell']==first_new+1 and d['cell_pending']==d['owner_pending']==d['view_pending']==1 and d['first_free']==0,'Normal owner/cell state differs')
  expected_faces.append([prefix+1,107,108,110,4 if first_new else 10/3,1/3,1 if first_new else 0.5])
  require(d['faces'][:len(expected_faces)]==expected_faces,'Committed prefix or selected first Face differs')
  remaining=d['faces'][len(expected_faces):d['mesh']]
  by_vertices={cyclic([108,109,110]):[5 if first_new else 11/3,1,1.5 if first_new else 1]}
  if first_new:by_vertices[cyclic([107,110,111])]=[3,1,1.5]
  require(len(remaining)==len(by_vertices),'Missing native remaining Face')
  for i,row in enumerate(remaining,start=len(expected_faces)+1):
   key=cyclic(row[1:4]);require(row[0]==i and key in by_vertices and row[4:]==by_vertices.pop(key),'Native Face order/orientation/midpoint/area differs')
  require(not by_vertices and d['faces'][d['mesh']:]==[[0]*7]*(4-d['mesh']),'Missing/extra Face data')
  adjacency=([2,2,2] if prefix else [0,0,0])+[0,0,0]+[2+first_new,3,2,3+first_new,2*first_new,0]
  require(d['adjacency']==adjacency,'Normal native endpoint adjacency differs')
  require(d['freed']==d['mid_freed']==1,'Normal second Edge/cache did not retire')
  contract='normal'
 else:
  phase=0 if n<=ctor else n-ctor
  require(d['threw']==d['denied']==1 and d['status']==-1 and d['attempts']==n and d['phase']==phase,'Calibrated native denial/propagation missing')
  require(d['mesh']==d['last_face']==prefix and d['faces']==expected_faces+[[0]*7]*(4-prefix),'Committed Face prefix changed')
  require(d['owners']==base_owners+(phase>=4) and d['views']==base_owners+(phase>=5),'Native owner/view publication timing differs')
  require(d['owner_pending']==(phase>=4) and d['view_pending']==(phase>=5),'Second edge ownership identity differs')
  require(d['first_free']==first_new and d['cell']==first_new and d['cell_pending']==0,'First-edge free/cell state changed')
  expected_front=3+first_new+front*(2*first_new-1)+(phase==6 and front)
  require(d['front']==expected_front and d['rejected']==((first_new+(phase==6)) if not front else 0) and d['queue_pending']==(phase==6),'Native first/second queue publication differs')
  require(d['free_edges']==3+3*first_new+(phase>=4),'Native committed free-edge state differs')
  adjacency=([2,2,2] if prefix else [0,0,0])+[0,0,0]+[2+first_new,2,2,2+first_new,2*first_new,0]
  if not cleanup:
   adjacency[7]+=int(phase>=2);adjacency[9]+=int(phase>=3)
  require(d['adjacency']==adjacency,'Missing/changed actual endpoint observations')
  retained=phase in (1,2,3) and original
  require(code==int(retained),'Unexpected native exit')
  require((d['retained_blocks'],d['retained_bytes'])==(((3,272) if ctor==3 else (5,296)) if retained else (0,0)),'Original pending storage or caller cleanup differs')
  require(d['freed']==d['mid_freed']==int(phase>=4 or cleanup),'Actual second Edge/cache release differs')
  contract='original pending ownership failed' if retained else 'nonallocating pending cleanup' if cleanup else 'construction unwind' if phase==0 else 'owned partial publication'
 constructed=n==0 or n>ctor
 expected_geometry=[first_new+1,110,108,3.5+first_new,0.5,3+first_new,4+first_new] if constructed and not cleanup else [0]*7
 require(d['pending_geometry']==expected_geometry,'Original second Edge endpoints/cache differ')
 return contract


def qualify(exe,output,original=None,broken=None,stale=None,runtime=None,asan=False):
 output.mkdir(parents=True,exist_ok=False)
 env=dict(os.environ)
 if runtime:env['PATH']=str(runtime.resolve())+os.pathsep+env.get('PATH','')
 if asan:env['ASAN_OPTIONS']='detect_leaks=0:alloc_dealloc_mismatch=1:halt_on_error=1'
 r={'status':'running','cases':[],'executables':{},'normal_comparisons':0,'denial_comparisons':0,
    'nonallocating_cleanups':0,'original_failed_contracts':0,'wrong_deleter_detections':0,
    'stale_adjacency_detections':0,'instrument_controls':0,'fresh_first_edge_cleanups':0}
 for label,binary in [('candidate',exe),('original',original),('broken',broken),('stale',stale)]:
  if binary:r['executables'][label]={'path':str(binary.resolve()),'sha256':hashlib.sha256(binary.read_bytes()).hexdigest()}
 def run(binary,label,context,n,action=0):
  argv=[str(binary.resolve()),*map(str,context),str(n),str(action)]
  name=label+'-'+''.join(map(str,context))+f'-{n}-{action}.log'
  with (output/name).open('xb') as log:p=subprocess.run(argv,cwd=Path(__file__).resolve().parents[1],env=env,stdout=log,stderr=subprocess.STDOUT,timeout=20)
  raw=(output/name).read_bytes();c={'label':label,'context':list(context),'ordinal':n,'action':action,'argv':argv,'exit':p.returncode,'log':name,'log_sha256':hashlib.sha256(raw).hexdigest()}
  r['cases'].append(c);return c,raw.decode(errors='replace').replace('\r\n','\n')
 try:
  totals={};candidates={}
  for label,binary in [('candidate',exe)]+([('original',original)] if original else []):
   for context in CONTEXTS:
    first,text=run(binary,label,context,0);first['observation']=json.loads(text);total=first['observation']['attempts']
    require(total in (9,11),'Unsupported native allocation calibration')
    if label=='candidate':totals[context]=total
    else:require(total==totals[context],'Original/candidate allocation counts differ')
    for n in range(total+1):
     if n==0:c=first
     else:c,text=run(binary,label,context,n);c['observation']=json.loads(text)
     d=c['observation'];c['contract']=analyze(d,c['exit'],context,n,total-6,label=='original')
     if label=='candidate':
      candidates[(context,n)]=d;r['nonallocating_cleanups']+=d['cleanup_calls']
      r['fresh_first_edge_cleanups']+=d['cleanup_calls']*context[4]
     else:
      r['original_failed_contracts']+=c['contract']=='original pending ownership failed'
      excluded=FAILURE_FIELDS if total-6<n<total-2 else CLEANUP_FIELDS;peer=candidates[(context,n)]
      require({k:v for k,v in d.items() if k not in excluded}=={k:v for k,v in peer.items() if k not in excluded},'Native preservation comparison differs')
      r['normal_comparisons' if n==0 else 'denial_comparisons']+=1
  for context in CONTEXTS:
   total=totals[context];ctor=total-6
   if broken:
    for n in range(ctor+1,ctor+4):
     c,text=run(broken,'broken',context,n)
     require(c['exit']==4 and text==f'borrowed_endpoint_destroyed=7 phase={n-ctor} denied=1\n','Actual wrong-deleter damage missing')
     c['contract']='actual borrower destruction detected';r['wrong_deleter_detections']+=1
   if stale:
    for n in (ctor+2,ctor+3):
     c,text=run(stale,'stale',context,n,3 if asan else 0)
     if asan:require(c['exit']!=0 and 'ERROR: AddressSanitizer: heap-use-after-free' in text and 'ReadEdgeId' in text,'Actual expired-adjacency access missing')
     else:
      d=json.loads(text);c['observation']=d
      expired=d['adjacency'][7]-2+d['adjacency'][9]-(2+context[4])
      require(c['exit']==0 and expired==n-ctor-1 and d['retained_blocks']==d['retained_bytes']==0,'Actual stale adjacency observation missing')
      try:analyze(d,c['exit'],context,n,ctor)
      except ValueError:pass
      else:raise ValueError('Invalid detach-only cleanup passed the ownership checker')
     c['contract']='actual expired adjacency detected';r['stale_adjacency_detections']+=1
  for name in ['denial-control','leak-control']+(['uaf-control'] if asan else []):
   c,text=run(exe,'control',(0,0,0,0,0),name)
   if name=='uaf-control':require(c['exit']!=0 and 'ERROR: AddressSanitizer: heap-use-after-free' in text,'Actual ASan instrument control missing')
   else:
    d=json.loads(text);c['observation']=d
    valid=(c['exit']==0 and d['threw']==d['denied']==d['attempts']==1 and d['retained_blocks']==d['retained_bytes']==0) if name=='denial-control' else (c['exit']==1 and d['retained_blocks']==(1 if totals[(0,0,0,0,0)]==9 else 2) and d['retained_bytes']>0)
    require(valid,'Independent allocation instrument control missing')
   c['contract']='independent invalid instrument detected';r['instrument_controls']+=1
  r.update(status='passed',native_outcomes=len(r['cases']))
 except Exception as error:r.update(status='failed',failure=repr(error));raise
 finally:(output/'report.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
 return r


if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 for name in ('exe','original','broken','stale','runtime','output'):p.add_argument('--'+name,type=Path,required=name in ('exe','output'))
 p.add_argument('--asan-control',action='store_true');p.add_argument('--repeatable-output',action='store_true');args=p.parse_args()
 if args.repeatable_output:
  args.output.mkdir(parents=True,exist_ok=True);args.output=Path(tempfile.mkdtemp(prefix='run-',dir=args.output))/'evidence'
 result=qualify(args.exe,args.output,args.original,args.broken,args.stale,args.runtime,args.asan_control)
 print(json.dumps({k:v for k,v in result.items() if k not in ('cases','executables')}))
