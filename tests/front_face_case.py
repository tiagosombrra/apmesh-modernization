#!/usr/bin/env python3
"""Qualify native interception borrower lifetime and calibrated failure paths."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import tempfile


def analyze(d, code, layout, ordinal, total, original=False, consume=True):
    if d['layout'] != layout or d['mode'] != str(ordinal):
        raise ValueError('Wrong caller case identity')
    if d['profile'] not in ('native-allocation-observer', 'msvc-debug-crt'):
        raise ValueError('Unmeasured allocation profile')
    if d['retained_blocks'] != 0 or d['retained_bytes'] != 0 or d['destroyed_after_cleanup'] != [1]*5:
        raise ValueError('Incomplete native owner cleanup')
    if layout >= 4:
        if ordinal or code or any(d[k] for k in ('attempts', 'denied', 'threw', 'entered', 'finished', 'attached', 'cache_releases')):
            raise ValueError('Guard incorrectly counted as Face lifecycle coverage')
        phase, attached, finished, releases, late = -1, 0, 0, 0, False
    else:
        if total not in (3, 6) or d['entered'] != 1:
            raise ValueError('Incomplete positive allocation coverage')
        group = total // 3
        late = bool(ordinal > 2*group)
        phase = 4 if not ordinal else 0 if ordinal <= group else 1 if ordinal <= 2*group else 3
        attached = int(not ordinal or late)
        finished = int(ordinal == 0)
        releases = 3 if not ordinal else 0 if phase == 0 else 1 if phase == 1 else 2
        if d['attempts'] != (ordinal or total) or d['denied'] != int(ordinal > 0) or d['threw'] != int(ordinal > 0):
            raise ValueError('Incomplete allocation denial or exception propagation')
    damaged = bool(original and late)
    if (d['phase'], d['attached'], d['finished'], d['cache_releases']) != (phase, attached, finished, releases):
        raise ValueError('Native Face lifecycle trace differs')
    if d['cache_release_order'] != list(range(releases)) + [-1]*(3-releases):
        raise ValueError('Native midpoint release order changed')
    if code != int(damaged) or d['destroyed_before_owner_cleanup'] != ([1,1,1,0,0] if damaged else [0]*5):
        raise ValueError('Caller-owned endpoint lifetime violated')
    if (d['live_fields_checked'], d['adjacency_checked'], d['quarantined_handles'], d['consumer_reads']) != (2 if damaged else 5, 0 if damaged else 3, 3 if damaged else 0, 3 if consume else 0):
        raise ValueError('Missing live fields, adjacency or consuming-caller coverage')
    if d['result'] != (-1 if ordinal else [0,1,1,0,0,1][layout]):
        raise ValueError('Native interception decision changed')
    if attached:
        if d['attached_ids'] != [101,102,103] or len(d['midpoint']) != 2 or any(not math.isfinite(x) for x in d['midpoint']) or d['midpoint'] != [0.5, 1/3]:
            raise ValueError('Independent native cache/identity expectation differs')
    elif d['attached_ids'] != [0]*3 or d['midpoint'] != [0]*2:
        raise ValueError('Unpublished attachment reported as live')
    return {'borrower_contract': 'failed' if damaged else 'preserved',
            'coverage': 'guard-only' if layout >= 4 else 'positive Face lifecycle'}


def qualify(exe, output, original=None, runtime=None, asan_control=False):
    output.mkdir(parents=True, exist_ok=False)
    env = os.environ.copy()
    if runtime:
        env['PATH'] = str(runtime.resolve()) + os.pathsep + env.get('PATH', '')
    if asan_control:
        env['ASAN_OPTIONS'] = 'detect_leaks=0:alloc_dealloc_mismatch=1:halt_on_error=1'
    report = {'status': 'running', 'cases': [], 'executables': {},
              'original_failed_borrower_contracts': 0, 'normal_comparisons': 0,
              'scope': 'Bounded native interception; actual adjacency/owner reads; no whole-process/LSan claim'}

    def run(binary, label, layout, mode, consume=False, expired=False):
        name = f'{label}-{layout}-{mode}.log'
        command = [str(binary.resolve()), str(layout), str(mode)] + (['consume'] if consume else [])
        with (output/name).open('xb') as log:
            process = subprocess.run(command, env=env, stdout=log, stderr=subprocess.STDOUT, timeout=30)
        raw = (output/name).read_bytes()
        text = raw.decode('utf-8', errors='replace').replace('\r\n','\n')
        item = {'label': label, 'layout': layout, 'mode': str(mode), 'command': command,
                'exit_code': process.returncode, 'log': name, 'log_sha256': hashlib.sha256(raw).hexdigest()}
        report['cases'].append(item)
        if expired or mode == 'uaf-control':
            if process.returncode == 0 or 'ERROR: AddressSanitizer: heap-use-after-free' not in text:
                raise ValueError('Actual AddressSanitizer invalid-access control was not detected')
            if expired and ('consume_borrower phase=3 denied=1 destroyed=1,1,1\n' not in text or 'Face::~Face' not in text):
                raise ValueError('Original expired-borrower access context is missing')
            item['expected_invalid_access_detected'] = True
            return item
        if 'ERROR: AddressSanitizer:' in text:
            raise ValueError('Unexpected native invalid access')
        lines = text.splitlines()
        if consume:
            if len(lines) != 2 or not lines[0].startswith('consume_borrower phase='):
                raise ValueError('Missing actual consuming-caller marker')
        elif len(lines) != 1:
            raise ValueError('Ambiguous native observation')
        item['observation'] = json.loads(lines[-1])
        if consume:
            d = item['observation']
            expected = f"consume_borrower phase={d['phase']} denied={d['denied']} destroyed=" + ','.join(map(str,d['destroyed_before_owner_cleanup'][:3]))
            if lines[0] != expected:
                raise ValueError('Consuming-caller marker differs from native lifetime observation')
        return item

    try:
        normals = {}
        totals = {}
        for label, binary in [('candidate',exe)] + ([('original',original)] if original else []):
            report['executables'][label] = {'path': str(binary.resolve()), 'sha256': hashlib.sha256(binary.read_bytes()).hexdigest()}
            for layout in range(6):
                case = run(binary,label,layout,0,consume=True)
                d = case['observation']
                total = d['attempts']
                case.update(analyze(d,case['exit_code'],layout,0,total,original=label=='original'))
                if label == 'candidate':
                    normals[layout] = d
                    totals[layout] = total
                else:
                    if d != normals[layout]:
                        raise ValueError('Successful original/candidate traces differ')
                    report['normal_comparisons'] += 1
                for ordinal in range(1,total+1):
                    consume = label == 'candidate'
                    case = run(binary,label,layout,ordinal,consume=consume)
                    case.update(analyze(case['observation'],case['exit_code'],layout,ordinal,total,original=label=='original',consume=consume))
                    report['original_failed_borrower_contracts'] += case['borrower_contract'] == 'failed'
        for mode in ('denial-control','leak-control'):
            case = run(exe,'control',0,mode)
            d = case['observation']
            valid = (case['exit_code'] == 0 and d['attempts'] == d['denied'] == d['threw'] == 1 and d['retained_blocks'] == d['retained_bytes'] == 0) if mode == 'denial-control' else (case['exit_code'] == 2 and d['attempts'] > 0 and d['retained_blocks'] > 0 and d['retained_bytes'] > 0)
            if not valid or d['entered'] != 1:
                raise ValueError('Independent allocation/retention control was not detected')
            case['independent_control_detected'] = True
        if asan_control:
            run(exe,'control',0,'uaf-control')
            if original:
                for layout in range(4):
                    for ordinal in range(2*totals[layout]//3+1,totals[layout]+1):
                        run(original,'expired-original',layout,ordinal,consume=True,expired=True)
        report.update(status='passed',expected_outcomes=len(report['cases']))
    except Exception as error:
        report.update(status='failed',failure=repr(error))
        raise
    finally:
        (output/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return report


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--exe',type=Path,required=True)
    p.add_argument('--original',type=Path)
    p.add_argument('--runtime',type=Path)
    p.add_argument('--asan-control',action='store_true')
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--repeatable-output',action='store_true')
    args = p.parse_args()
    if args.repeatable_output:
        args.output.mkdir(parents=True,exist_ok=True)
        args.output = Path(tempfile.mkdtemp(prefix='run-',dir=args.output))/'evidence'
    result = qualify(args.exe,args.output,args.original,args.runtime,args.asan_control)
    print(json.dumps({k:result[k] for k in ('status','expected_outcomes','normal_comparisons','original_failed_borrower_contracts')}))
