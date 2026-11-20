#!/usr/bin/env python3
"""Bounded bicubic approximation pilot for one native cylindrical CAD face.

This is NOT general STEP conversion. Polynomial control nets are interpolated
in native surface parameters and audited on denser, non-interpolation grids.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import math
from pathlib import Path

import numpy as np
import cadquery as cq
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.BRepTools import BRepTools
from OCP.gp import gp_Pnt

from audit_analytic_bp import surface as independent_casteljau_surface


class UnsupportedGeometry(ValueError):
    """Selected face is outside the deliberately narrow approximation domain."""


def bernstein3(t):
    return np.asarray(((1-t)**3, 3*t*(1-t)**2, 3*t*t*(1-t), t**3),dtype=float)


def xyz(point):
    return (point.X(),point.Y(),point.Z())


def native_face_distance(face, xyz_value):
    point=BRepBuilderAPI_MakeVertex(gp_Pnt(*xyz_value)).Vertex()
    calc=BRepExtrema_DistShapeShape(point,face.wrapped)
    calc.Perform()
    if not calc.IsDone():
        raise RuntimeError('Native geometric oracle failed')
    return calc.Value()


def approximate_cylindrical_face(face, *, absolute_budget_mm, relative_budget,
                                 convergence_grid=(9,17,33)):
    """Return one approximate polynomial patch and explicit negative evidence.

    Budgets are caller-provided BEFORE fitting; neither is tuned from residuals.
    Both budgets must be met (more restrictive threshold wins).
    """
    if face.geomType()!='CYLINDER':
        raise UnsupportedGeometry('Only cylindrical faces are admitted')
    wires=face.Wires()
    if len(wires)!=1 or len(wires[0].Edges())!=4:
        raise UnsupportedGeometry('Must have exactly one four-edge trim wire')
    if any(not (math.isfinite(x) and x>0) for x in (absolute_budget_mm,relative_budget)):
        raise ValueError('Error budgets must be finite and strictly positive')
    if list(convergence_grid)!=sorted(set(convergence_grid)) or not all(n>=5 and n%2==1 for n in convergence_grid):
        raise ValueError('Convergence grids must be increasing odd sizes >=5')
    limits=BRepTools.UVBounds_s(face.wrapped)
    if any(not math.isfinite(x) or abs(x)>1e50 for x in limits):
        raise UnsupportedGeometry('Nonfinite or unbounded trimmed domain')
    u0,u1,v0,v1=limits
    if not (0<u1-u0<=math.pi/2+1e-9 and v1>v0):
        raise UnsupportedGeometry('Angular span outside admitted quarter-cylinder interval')
    adaptor=BRepAdaptor_Surface(face.wrapped,True)
    grid=(0,1/3,2/3,1)
    collocation=np.stack([[xyz(adaptor.Value(u0+u*(u1-u0),v0+v*(v1-v0))) for u in grid] for v in grid])
    matrix=np.stack([bernstein3(t) for t in grid])
    # F = B(v) @ C @ B(u).T; solve both directions without a sampled fit shortcut.
    first=np.linalg.solve(matrix,collocation)
    controls=np.linalg.solve(matrix,first.transpose(1,0,2)).transpose(1,0,2)
    net=[tuple(map(float,p)) for p in controls.reshape(16,3)]
    samples=[]
    max_abs=0.0
    for count in convergence_grid:
        errors=[]
        for j in range(count):
            v=j/(count-1)
            for i in range(count):
                u=i/(count-1)
                predicted=independent_casteljau_surface(net,u,v)
                actual=xyz(adaptor.Value(u0+u*(u1-u0),v0+v*(v1-v0)))
                errors.append(math.dist(actual,predicted))
        current=max(errors)
        max_abs=max(max_abs,current)
        samples.append({'grid_per_axis':count,'sample_count':count*count,
                        'max_parameter_corresponding_distance_mm':current,
                        'rms_parameter_corresponding_distance_mm':math.sqrt(sum(x*x for x in errors)/len(errors))})
    source_bbox=face.BoundingBox()
    scale=source_bbox.DiagonalLength
    limit=min(absolute_budget_mm,relative_budget*scale)
    # An independent distance-to-trimmed-face check is an auxiliary oracle only.
    independent_distances=[]
    for j in range(7):
        for i in range(7):
            u,v=i/6,j/6
            point=independent_casteljau_surface(net,u,v)
            independent_distances.append(native_face_distance(face,point))
    report={
        'schema':'apmesh-s3b-single-cylinder-bicubic-pilot-v1',
        'classification':'SYNTHETIC_OR_SOURCE_FACE_PILOT_NOT_COMPLETE_MODEL',
        'source_face_type':'CYLINDER','trim_wire_count':1,'trim_edge_count':4,
        'native_uv_domain':[float(x) for x in limits],
        'source_bbox_diagonal_mm':scale,
        'predeclared_absolute_budget_mm':absolute_budget_mm,
        'predeclared_relative_budget_of_face_diagonal':relative_budget,
        'effective_strict_budget_mm':limit,
        'collocation_parameters':list(grid),
        'interpolation_points':16,
        'bicubic_controls':16,
        'convergence':samples,
        'maximum_pointwise_sampled_error_mm':max_abs,
        'native_face_max_distance_mm':max(independent_distances),
        'native_face_distance_samples':len(independent_distances),
        'budget_pass':bool(max_abs<=limit),
        'continuous_distance_bound':'NOT_CERTIFIED',
        'shared_curve_graph':'NOT_VALIDATED',
        'full_original_model_converted':False,
        'apmesh_generation':'NOT_RUN',
    }
    return net,report


def synthetic_quarter_cylinder(radius=3.0,height=4.0):
    """Author a trimmed four-edge kernel face; not an original industrial CAD."""
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace
    from OCP.gp import gp_Ax3,gp_Cylinder,gp_Dir,gp_Pnt
    geom=gp_Cylinder(gp_Ax3(gp_Pnt(0,0,0),gp_Dir(0,0,1)),radius)
    return cq.Face(BRepBuilderAPI_MakeFace(geom,0,math.pi/2,0,height).Face())


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--absolute-budget-mm',type=float,required=True)
    p.add_argument('--relative-budget',type=float,required=True)
    p.add_argument('--source-step',type=Path)
    p.add_argument('--source-sha256',type=str)
    p.add_argument('--face-index',type=int)
    args=p.parse_args()
    if args.source_step:
        if not args.source_sha256 or args.face_index is None:
            p.error('Actual STEP requires both --source-sha256 and --face-index')
        digest=sha256(args.source_step.read_bytes()).hexdigest()
        if digest!=args.source_sha256:
            raise ValueError('Original STEP raw SHA-256 mismatch')
        shape=cq.importers.importStep(str(args.source_step)).val()
        if not (0<=args.face_index<len(shape.Faces())):
            raise ValueError('Source face index out of range')
        face=shape.Faces()[args.face_index]
        source={'kind':'ORIGINAL_STEP_FACE','raw_sha256':digest,'face_index':args.face_index}
    else:
        face=synthetic_quarter_cylinder()
        source={'kind':'AUTHOR_CONSTRUCTED_QUARTER_CYLINDER','radius_mm':3,'height_mm':4}
    net,report=approximate_cylindrical_face(face,absolute_budget_mm=args.absolute_budget_mm,
                                           relative_budget=args.relative_budget)
    report['source']=source
    bp='\n'.join(['// Isolated cylindrical bicubic approximation pilot; not complete CAD conversion']+
                  ['v '+' '.join(format(x,'.17g') for x in p) for p in net]+ 
                  ['p '+' '.join(str(i) for i in range(16))])+'\n'
    report['bp_sha256']=sha256(bp.encode()).hexdigest()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(bp,encoding='utf8')
    args.output.with_suffix('.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:report[k] for k in ('source','budget_pass','maximum_pointwise_sampled_error_mm','native_face_max_distance_mm','continuous_distance_bound')},sort_keys=True))


if __name__=='__main__':
    main()
