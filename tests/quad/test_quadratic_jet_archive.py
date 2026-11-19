"""Bind the adopted read-only jet candidate to three existing real histories."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools'))
from quad_quadratic_curvature import measure_archive


def unique(paths):
    paths=list(paths)
    if len(paths)!=1:raise ValueError('Missing or ambiguous real jet archive')
    return paths[0]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--probe',type=Path,required=True)
    parser.add_argument('--article-root',type=Path,required=True)
    parser.add_argument('--history-root',type=Path,required=True)
    parser.add_argument('--directory',type=Path,required=True)
    args=parser.parse_args();args.directory.mkdir(parents=True,exist_ok=False)
    archives={'article':unique(args.article_root.glob('article-*.steps')),
              'original-rejected':unique(args.history_root.rglob('accepted.steps')),
              'stable-retry':unique(args.history_root.rglob('stable-accepted.steps'))}
    receipt=dict(schema='apmesh.quad.jet_archives.v1',cases={})
    for label,archive in archives.items():
        report=measure_archive(archive,args.probe.resolve(),args.directory/label)
        if report['rejected_forgeries']!=10:raise ValueError('Missing actual jet forgery controls')
        unavailable=[s for s in report['stages'] if s['step']=='0']
        if not all(s['coverage']['insufficient_samples']==5 for s in unavailable):raise ValueError('Initial jet unavailability changed')
        receipt['cases'][label]=dict(stages=[{k:v for k,v in s.items() if k!='per_node'} for s in report['stages']],
                                    inputs_sha256=report['inputs_sha256'],independent_agreement_max=report['independent_agreement_max'],
                                    rejected_forgeries=report['rejected_forgeries'])
        print(json.dumps(dict(case=label,stages=len(report['stages']),forgeries=report['rejected_forgeries'])),flush=True)
    if sum(len(v['stages']) for v in receipt['cases'].values())!=22:raise ValueError('Incomplete actual jet histories')
    receipt.update(status='passed',probe_sha256=hashlib.sha256(args.probe.read_bytes()).hexdigest(),
                   mixed_global_error=None,accepted_mixed_epochs=0,
                   accuracy='Unqualified for estimator adoption: retained full-rank one-sided paraboloid counterexample and real errors must remain visible.')
    (args.directory/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')


if __name__=='__main__':main()
