#!/usr/bin/env python3
"""Privately replay the frozen S3.Y selected S40 atlas from the S3.W bundle.

This script does not redistribute original or derived STEP/BP content. Never
promote an output unless original and parent hashes and the replayed child match.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tempfile
import zipfile

SOURCE_SHA = 'b79eb5be1fde71b6a8d086fe14800a1ec62e3a3c4618910c81c64d23718abf3b'
S3W_SHA = 'c826487d8cee76f6649100c59e5ce84fa6cb43c9004f53c68e3e565e86cdb174'
S3Y_SHA = 'af50597db4b8d7b3bcb2fc381596fefc95ba6b6e00ed169576bec7a6b7873177'
S3W_BP = 's40_spline_shared_repair.partial.bp'
S3W_MANIFEST = 's40_spline_shared_repair_manifest.json'
MAX_MEMBER_BYTES = 40_000_000


def _digest(blob):
    return hashlib.sha256(blob).hexdigest()


def _check_zip_member(info):
    if info.is_dir() or info.file_size>MAX_MEMBER_BYTES or info.file_size<=0:
        raise ValueError('Private archive entry missing, empty or too large')
    if info.compress_size==0 or info.file_size/info.compress_size>1000:
        raise ValueError('Private archive entry compression is unsafe')
    if info.external_attr >> 16 & 0o170000 == 0o120000:
        raise ValueError('Private archive must not supply symbolic links')
    p=PurePosixPath(info.filename)
    if p.is_absolute() or '..' in p.parts or '\\' in info.filename:
        raise ValueError('Private archive contains unsafe path')
    return p


def read_verified_s3w_bundle(path):
    """Select exactly one original-derived BP and matching named manifest."""
    with zipfile.ZipFile(path) as archive:
        found={S3W_BP:[],S3W_MANIFEST:[]}
        for info in archive.infolist():
            name=PurePosixPath(info.filename).name
            if name not in found:
                continue
            _check_zip_member(info)
            found[name].append(info)
        if any(len(v)!=1 for v in found.values()):
            raise ValueError('Missing or ambiguous S3.W private bundle member')
        bp=archive.read(found[S3W_BP][0]);mdata=archive.read(found[S3W_MANIFEST][0])
    if _digest(bp)!=S3W_SHA:
        raise ValueError('Private S3.W BP SHA-256 does not match frozen original')
    try:
        manifest=json.loads(mdata)
    except (UnicodeError,ValueError) as e:
        raise ValueError('Invalid S3.W manifest JSON') from e
    if (manifest.get('repaired_bp_sha256')!=S3W_SHA or
        manifest.get('combined_patches')!=148 or
        manifest.get('global_declared_control_points')!=1619 or
        manifest.get('original_step_218_hole_patch_ids_unchanged') is not True):
        raise ValueError('S3.W private manifest does not match frozen parent')
    return bp,mdata


def check_inputs(step_path,bundle_path,builder_path):
    if not step_path.is_file() or not bundle_path.is_file() or not builder_path.is_file():
        raise ValueError('Required STEP, private S3.W ZIP or public S3.Y builder missing')
    if _digest(step_path.read_bytes())!=SOURCE_SHA:
        raise ValueError('Original industrial STEP SHA-256 differs from frozen source')
    bp,manifest=read_verified_s3w_bundle(bundle_path)
    return bp,manifest


def replay_selected_s3y(step_path,bundle_path,builder_path,output_dir,
                       *,timeout_seconds=240):
    """Fail closed on any non-reproducible 156-patch S3.Y child."""
    bp,manifest=check_inputs(step_path,bundle_path,builder_path)
    if type(timeout_seconds) is not int or not 10<=timeout_seconds<=3600:
        raise ValueError('Invalid replay process timeout')
    # The original source/BP and intermediate child never enter a public repo.
    with tempfile.TemporaryDirectory(prefix='s40_s3y_private_') as tmp:
        root=Path(tmp)
        bp_path=root/S3W_BP
        manifest_path=root/S3W_MANIFEST
        trial_dir=root/'replayed_child'
        bp_path.write_bytes(bp)
        manifest_path.write_bytes(manifest)
        command=[sys.executable,str(builder_path.resolve()),
                 '--source-step',str(step_path.resolve()),
                 '--baseline-bp',str(bp_path),
                 '--baseline-manifest',str(manifest_path),
                 '--faces','3044','--interior-grid','17',
                 '--boundary-grid','31','--output-dir',str(trial_dir)]
        result=subprocess.run(command,capture_output=True,text=True,
                              timeout=timeout_seconds,check=False)
        if result.returncode!=0:
            raise ValueError('S3.Y replay script rejected original source and parent')
        child_path=trial_dir/'s40_three_curved_planar.CANDIDATE.bp'
        child_manifest=trial_dir/'candidate_manifest.json'
        native_audit=trial_dir/'native_audit.json'
        if not all(p.is_file() for p in (child_path,child_manifest,native_audit)):
            raise ValueError('S3.Y replay did not emit complete private native evidence')
        child=child_path.read_bytes()
        if _digest(child)!=S3Y_SHA:
            raise ValueError('Replayed selected child SHA-256 does not match frozen S3.Y')
        metadata=json.loads(child_manifest.read_text())
        audit=json.loads(native_audit.read_text())
        if metadata.get('candidate_bp_sha256')!=S3Y_SHA:
            raise ValueError('S3.Y candidate receipt differs from selected child hash')
        if metadata.get('candidate_patch_count')!=156 or metadata.get('candidate_control_count')!=1665:
            raise ValueError('Replayed S3.Y child cardinalities changed')
        if audit.get('status')!='PASS' or audit.get('native_boundary_OUT')!=0:
            raise ValueError('Replayed native original S3.Y trim gate did not pass')
        if output_dir.exists() and any(output_dir.iterdir()):
            raise ValueError('Private destination must be an empty directory')
        output_dir.mkdir(parents=True,exist_ok=True)
        (output_dir/'s40_selected_s3y.partial.bp').write_bytes(child)
        (output_dir/'s40_selected_s3y_manifest.json').write_text(json.dumps({
            'selected_bp_sha256':S3Y_SHA,
            'provenance':'frozen-s3w-original-step-s3y-3044-native-replay',
            'source_sha256':SOURCE_SHA,
            's3w_parent_sha256':S3W_SHA,
            'combined_patches':156,
            'global_declared_control_points':1665
        },indent=2,sort_keys=True)+'\n')
        (output_dir/'s40_selected_s3y_native_audit.json').write_text(
            json.dumps(audit,indent=2,sort_keys=True)+'\n')
        return {'state':'READY_FOR_PRIVATE_S40F4_CAD_NATIVE_TRIAL',
                'selected_child_sha256':S3Y_SHA,'source_sha256':SOURCE_SHA,
                'selected_patches':156,'admitted_original_faces':22,
                'original_native_replay_executed':True,
                'apmesh_cpp_tri_quad_executed':False}


def main(argv=None):
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--original-step',type=Path,required=True)
    cli.add_argument('--s3w-private-zip',type=Path,required=True)
    cli.add_argument('--s3y-builder',type=Path,required=True)
    cli.add_argument('--private-output-dir',type=Path,required=True)
    args=cli.parse_args(argv)
    try:
        receipt=replay_selected_s3y(args.original_step,args.s3w_private_zip,
                                    args.s3y_builder,args.private_output_dir)
    except (ValueError,FileNotFoundError,zipfile.BadZipFile,subprocess.TimeoutExpired,
            PermissionError,IsADirectoryError,NotADirectoryError) as e:
        receipt={'state':'BLOCKED_NO_NEW_S40_FACE_ADMISSION',
                 'reason':str(e),'selected_patches_unchanged':156,
                 'original_faces_represented_unchanged':22}
        print(json.dumps(receipt,indent=2))
        return 3
    print(json.dumps(receipt,indent=2))
    return 0


if __name__=='__main__':
    sys.exit(main())
