#!/usr/bin/env python3
"""Qualify native ideal-Vertex ownership without changing selection or borrowed best."""
import argparse
from collections import Counter
import hashlib
import itertools
import json
import os
from pathlib import Path
import subprocess
import tempfile
CONTEXTS=list(itertools.product(range(7),range(2),range(2)))
PENDING_PHASES={20,30,31,40,50,51}
OBSERVER={'attempts','entered','phase','events','constructed','freed','ideal_xy','ideal_owner','ideal_view','ideal_front','cleanup_calls'}
FAILURE_FIELDS={'cleanup_calls','freed','ideal_front','observers','retained_blocks','retained_bytes','best_kind','best_id','best_xy'}
def normal(j,context):
 mode,reverse,prefix=context
 assert j['context']==list(context) and j['attempts']>=0 and j['entered']==1 and not j['threw'] and not j['denied']
 assert j['phase']==[90,90,70,71,72,90,90][mode]
 assert j['result']==(1 if mode in (1,6) else 0)
 assert j['constructed']==j['freed']==int(mode<5) and j['retained_blocks']==j['retained_bytes']==0
 assert j['owners']==j['views']==4+prefix*3+int(mode==0)
 assert j['mesh']==prefix and j['edge_owners']==4+prefix*3 and j['borrowed']==4+prefix*3
 assert j['adjacency']==[2,2,2,2,*([2,2,2] if prefix else [0,0,0]),0]
 assert j['destroyed']==[1,1,1,1,*([1,1,1] if prefix else [0,0,0]),0]
 assert j['face']==([1,105,106,107,5.5,5+1/3,0.5] if prefix else [0]*7)
 assert j['last_vertex_id']==int(mode==0)
 assert j['best_kind']==(1 if mode==0 else 2 if mode in (1,6) else 0)
 assert j['best_id']==(1 if mode==0 else 104 if mode in (1,6) else -1)
 assert j['best_xy']==([1,2] if mode==0 else [0,1] if mode in (1,6) else [0,0])
 assert [j[n] for n in ('ideal_owner','ideal_view','ideal_front')]==([1,1,1] if mode==0 else [0,0,0])
 assert j['observers']==(5 if mode==0 else 4 if mode in (1,2,6) else 2)

def check(j, exit_code, context, target, baseline, profile, original=False):
 mode,reverse,prefix=context
 assert tuple(context) in CONTEXTS and profile in ('gcc','asan','crt')
 assert j['context']==list(context) and j['target']==target and j['action']==0 and j['entered']==1
 assert j['cleanup_allocations']==0
 if target==0 or target>baseline['attempts']:
  normal(j,context)
  assert exit_code==0 and j['attempts']==baseline['attempts']
  assert j['cleanup_calls']==int(not original and mode in (1,2,3,4))
  return 'normal' if target==0 else 'beyond-window normal control'
 assert j['attempts']==target and j['denied']==j['threw']==1 and j['result']==-1
 assert j['phase'] in {10,20,30,31,40,50,51,52,61}
 for key in ('mesh','edge_owners','borrowed','adjacency','face','destroyed','area'):
  assert j[key]==baseline[key],key
 assert j['constructed'] in (0,1) and j['constructed']<=int(mode<5)
 assert j['ideal_xy']==([1,2] if j['constructed'] else [0,0])
 pending=bool(j['constructed'] and j['phase'] in PENDING_PHASES)
 owned=bool(j['constructed'] and j['phase']==52)
 assert j['ideal_owner']==int(owned) and j['ideal_view']==0
 front=int(j['constructed'] and (j['phase']==52 or original and j['phase']==51))
 assert j['ideal_front']==front
 assert j['owners']==4+3*prefix+int(owned) and j['views']==4+3*prefix
 assert j['observers']==(4 if mode in (0,1,2,6) else 2)+front
 assert j['last_vertex_id']==int(j['phase'] in {50,51,52})
 cleanup=int(not original and (pending or mode<5 and j['phase']==61))
 assert j['cleanup_calls']==cleanup
 expected=(1,80) if profile=='gcc' else (2,88)
 assert (j['retained_blocks'],j['retained_bytes'])==(expected if pending and original else (0,0))
 assert exit_code==int(pending and original)
 if pending:
  assert j['freed']==int(not original)
  assert j['best_kind']==(1 if original else 3)
  assert j['best_id']==(int(j['phase'] in {50,51}) if original else -1)
  assert j['best_xy']==([1,2] if original else [0,0])
  return 'original unowned ideal retained' if original else 'nonallocating production cleanup'
 if owned:
  assert j['freed']==1 and j['best_kind']==1 and j['best_id']==1 and j['best_xy']==[1,2]
  return 'already-owned view-publication failure'
 if j['phase']==61:
  assert j['best_kind']==2 and j['best_id'] in (103,104) and j['freed']==int(mode<5)
  assert j['best_xy']==([2,1.5] if j['best_id']==103 else [0,1])
  return 'borrowed selection after ideal retirement' if mode<5 else 'topology borrowed selection'
 assert j['best_kind']==0 and j['best_id']==-1 and j['best_xy']==[0,0] and j['freed']==0
 return 'ideal constructor unwind' if mode<5 else 'topology without ideal'


def qualify(exe,output,profile='gcc',original=None,stale=None,unobserved=None,runtime=None):
 output.mkdir(parents=True,exist_ok=False)
 env=dict(os.environ)
 if runtime:env['PATH']=str(runtime.resolve())+os.pathsep+env.get('PATH','')
 if profile=='asan':env['ASAN_OPTIONS']='detect_leaks=0:alloc_dealloc_mismatch=1:halt_on_error=1'
 r={'status':'running','cases':[],'executables':{},'normal_comparisons':0,'denial_comparisons':0,
    'nonallocating_cleanups':0,'original_failed_contracts':0,'borrower_destruction_detections':0,
    'stale_observer_detections':0,'instrument_controls':0,'unobserved_normal_comparisons':0}
 for label,binary in [('candidate',exe),('original',original),('stale',stale),('unobserved',unobserved)]:
  if binary:r['executables'][label]={'path':str(binary.resolve()),'sha256':hashlib.sha256(binary.read_bytes()).hexdigest()}
 def run(binary,label,context,n,action=0):
  argv=[str(binary.resolve()),*map(str,context),str(n),str(action)]
  name=label+'-'+''.join(map(str,context))+f'-{n}-{action}.log'
  with (output/name).open('xb') as log:p=subprocess.run(argv,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=20)
  raw=(output/name).read_bytes()
  c={'label':label,'context':list(context),'target':n,'action':action,'argv':argv,'exit':p.returncode,'log':name,'sha256':hashlib.sha256(raw).hexdigest()}
  r['cases'].append(c)
  return c,raw.decode(errors='replace').replace('\r\n','\n')
 try:
  candidates={};baselines={}
  for label,binary in [('candidate',exe)]+([('original',original)] if original else []):
   for context in CONTEXTS:
    first,text=run(binary,label,context,0);first['observation']=json.loads(text)
    baseline=first['observation'];total=baseline['attempts']
    if label=='candidate':baselines[context]=baseline
    else:assert total==baselines[context]['attempts']
    for n in range(total+2):
     if n==0:c=first
     else:c,text=run(binary,label,context,n);c['observation']=json.loads(text)
     j=c['observation'];c['contract']=check(j,c['exit'],context,n,baseline,profile,label=='original')
     if label=='candidate':
      candidates[context,n]=j
      if c['contract']=='nonallocating production cleanup':r['nonallocating_cleanups']+=1
     else:
      pending=c['contract']=='original unowned ideal retained'
      r['original_failed_contracts']+=pending
      excluded=FAILURE_FIELDS if pending else {'cleanup_calls'}
      assert {k:v for k,v in j.items() if k not in excluded}=={k:v for k,v in candidates[context,n].items() if k not in excluded}
      r['normal_comparisons' if n==0 else 'denial_comparisons']+=1
      if c['contract']=='borrowed selection after ideal retirement':
       bad,text=run(binary,'wrong-best',context,n,2)
       assert bad['exit']==4 and text.splitlines() in (['borrowed_vertex_destroyed=2'],['borrowed_vertex_destroyed=3'])
       bad['contract']='actual borrowed-best destruction detected';r['borrower_destruction_detections']+=1
     if label=='candidate' and stale and j['phase']==51 and j['constructed']:
      bad,text=run(stale,'stale',context,n,3 if profile=='asan' else 0)
      if profile=='asan':
       assert bad['exit']!=0 and 'ERROR: AddressSanitizer: heap-use-after-free' in text and 'ReadVertexX' in text
      else:
       d=json.loads(text);bad['observation']=d
       assert bad['exit']==0 and d['ideal_front']==1 and d['freed']==1 and d['retained_blocks']==d['retained_bytes']==0
       try:check(d,bad['exit'],context,n,baseline,profile)
       except AssertionError:pass
       else:raise AssertionError('Actual stale observer passed candidate contract')
      bad['contract']='actual stale frontVertices observer detected';r['stale_observer_detections']+=1
  if unobserved:
   for context in CONTEXTS:
    c,text=run(unobserved,'unobserved',context,0);c['observation']=json.loads(text)
    assert c['exit']==0
    assert {k:v for k,v in c['observation'].items() if k not in OBSERVER}=={k:v for k,v in baselines[context].items() if k not in OBSERVER}
    c['contract']='exact unobserved normal comparison';r['unobserved_normal_comparisons']+=1
  for name in ['denial-control','leak-control']+(['uaf-control'] if profile=='asan' else []):
   c,text=run(exe,'instrument',(0,0,0),name)
   if name=='uaf-control':assert c['exit']!=0 and 'ERROR: AddressSanitizer: heap-use-after-free' in text
   else:
    j=json.loads(text);c['observation']=j
    if name=='denial-control':assert c['exit']==0 and j['attempts']==j['denied']==j['threw']==1 and j['retained_blocks']==j['retained_bytes']==0
    else:assert c['exit']==1 and (j['retained_blocks'],j['retained_bytes'])==((1,80) if profile=='gcc' else (2,88))
   c['contract']='independent invalid instrument detected';r['instrument_controls']+=1
  r.update(status='passed',native_outcomes=len(r['cases']),counts=dict(Counter(c['contract'] for c in r['cases'])))
 except Exception as error:r.update(status='failed',failure=repr(error));raise
 finally:(output/'report.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
 return r


if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 for name in ('exe','original','stale','unobserved','runtime','output'):p.add_argument('--'+name,type=Path,required=name in ('exe','output'))
 p.add_argument('--profile',choices=('gcc','asan','crt'),default='gcc');p.add_argument('--repeatable-output',action='store_true');args=p.parse_args()
 if args.repeatable_output:
  args.output.mkdir(parents=True,exist_ok=True);args.output=Path(tempfile.mkdtemp(prefix='run-',dir=args.output))/'evidence'
 result=qualify(args.exe,args.output,args.profile,args.original,args.stale,args.unobserved,args.runtime)
 print(json.dumps({k:v for k,v in result.items() if k not in ('cases','executables')}))
