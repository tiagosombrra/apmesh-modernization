#!/usr/bin/env python3
"""Controlled curved four-sheet bicubic BP/BRep experiment, not a CAD converter."""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

# Four authored cubic control points define a genuinely curved spatial centerline.
# They correspond to x=0.4*t*(1-t), y=0.3*t*(1-t)*(2*t-1), z=-2.5+5*t.
CURVE = ((0.0, 0.0, -2.5), (2.0/15.0, -0.1, -5.0/6.0),
         (2.0/15.0, 0.1, 5.0/6.0), (0.0, 0.0, 2.5))
RAYS = ((0.0, 5.0), (-5.0, 0.0), (5.0, 0.0), (0.0, -5.0))
REGIONS = (('A','B'),('A','C'),('B','VOID'),('C','VOID'))
SIDES = ((0,1,2,3),(3,7,11,15),(12,13,14,15),(0,4,8,12))
REVERSED_PATCH = 1


def generate():
    """Encode four ruled, curved Bezier sheets with canonical indexed C0 controls."""
    points = list(CURVE)
    patches = []
    for k, (dx, dy) in enumerate(RAYS):
        reverse = (k == REVERSED_PATCH)
        ids = []
        for row in range(4):
            j = 3-row if reverse else row
            for col in range(4):
                if col == 0:
                    ids.append(j)
                else:
                    old = CURVE[j]
                    points.append((old[0]+(col/3)*dx, old[1]+(col/3)*dy,old[2]))
                    ids.append(len(points)-1)
        sides=[]
        for slot, offsets in enumerate(SIDES):
            curve='C0' if slot==3 else f'P{k}:S{slot}'
            sides.append({'slot':slot,'curve_id':curve,
                          'control_indices':[ids[m] for m in offsets],
                          'orientation': ('reversed' if reverse else 'forward') if slot==3 else 'local'})
        patches.append({'index':k,'region_pair':list(REGIONS[k]),
                        'reverse_v':reverse,'radial_xy':[dx,dy],
                        'control_indices':ids,'sides':sides})
    if len(points)!=52:
        raise AssertionError('Unexpected vertex budget')
    bp = '\n'.join([
        '// Research R3 curved controlled source, not externally admitted CAD',
        '// Four curved bicubic patches, shared C0 referenced by vertex IDs 0..3',
        *('v '+' '.join(format(float(x),'.17g') for x in p) for p in points),
        *('p '+' '.join(map(str,p['control_indices'])) for p in patches),
    ])+'\n'
    manifest={
        'schema':'apmesh-r3-curved-bicubic-v1',
        'classification':'CONSTRUCTED_CURVED_ANALYTIC_CONTROL',
        'external_model_admission':'NOT_GRANTED',
        'source_cad_conversion':'NOT_PERFORMED',
        'apmesh_tri_generation':'NOT_RUN',
        'units':'synthetic_unspecified',
        'canonical_curve':'C0',
        'canonical_control_indices':[0,1,2,3],
        'canonical_curve_control_points':[list(x) for x in CURVE],
        'common_curve_incidence':4,
        'reversed_shared_side_patch':REVERSED_PATCH,
        'unique_vertex_count':len(points),
        'patch_count':len(patches),
        'unique_curve_count':13,
        'patches':patches,
        'bp_sha256':hashlib.sha256(bp.encode('utf-8')).hexdigest(),
    }
    return bp,manifest


def native_surface_complex(*, nonmanifold=True, displaced_patch=None, offset=2e-5):
    """Use native OCCT cubic surfaces and explicit nonmanifold sewing for a control."""
    import cadquery as cq
    from OCP.TColgp import TColgp_Array2OfPnt
    from OCP.gp import gp_Pnt
    from OCP.Geom import Geom_BezierSurface
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace, BRepBuilderAPI_Sewing

    sewing = BRepBuilderAPI_Sewing(1e-8, True, True, True, True)
    sewing.SetNonManifoldMode(nonmanifold)
    for k,(dx,dy) in enumerate(RAYS):
        poles = TColgp_Array2OfPnt(1,4,1,4)
        for i in range(4):
            for j in range(4):
                t = 3-j if k==REVERSED_PATCH else j
                x,y,z=CURVE[t]
                if displaced_patch==k:
                    x += offset
                poles.SetValue(i+1,j+1,gp_Pnt(x+(i/3)*dx,y+(i/3)*dy,z))
        made=BRepBuilderAPI_MakeFace(Geom_BezierSurface(poles),1e-7)
        if not made.IsDone():
            raise ValueError('Native curved face construction failed')
        face=cq.Face(made.Face())
        if not face.isValid():
            raise ValueError('Invalid native curved face')
        sewing.Add(face.wrapped)
    sewing.Perform()
    shell = cq.Shape(sewing.SewedShape())
    if not shell.isValid() or len(shell.Faces())!=4:
        raise ValueError('Native curved four-sheet complex not valid')
    native_groups=[]
    for i,face in enumerate(shell.Faces()):
        for edge in face.Edges():
            found=next((g for g in native_groups if g['edge'].wrapped.IsSame(edge.wrapped)),None)
            if found is None:
                found={'edge':edge,'faces':set()}
                native_groups.append(found)
            found['faces'].add(i)
    hist=Counter(len(g['faces']) for g in native_groups)
    report={
        'schema':'apmesh-r3-native-curved-topology-v1',
        'kernel_valid':bool(shell.isValid()),
        'faces':len(shell.Faces()),
        'unique_edges':len(native_groups),
        'edge_incidence_histogram':dict(sorted(hist.items())),
        'four_incident_edges':hist[4],
        'nonmanifold_mode':nonmanifold,
        'displaced_patch':displaced_patch,
        'sewing_tolerance':1e-8,
        'classification':'CONSTRUCTED_NOT_EXTERNAL',
    }
    return shell,report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out-dir',type=Path,required=True)
    args=parser.parse_args()
    args.out_dir.mkdir(parents=True,exist_ok=True)
    bp,manifest=generate()
    bpfile=args.out_dir/'four_sheet_curved.bp'
    sidecar=args.out_dir/'four_sheet_curved.sidecar.json'
    bpfile.write_text(bp,encoding='utf-8')
    sidecar.write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    shape,report=native_surface_complex()
    shape.exportBrep(str(args.out_dir/'four_sheet_curved.brep'))
    (args.out_dir/'native_curved_report.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'bp_sha256':manifest['bp_sha256'],'native':report},sort_keys=True))


if __name__=='__main__':
    main()
