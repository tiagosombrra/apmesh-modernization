#!/usr/bin/env python3
"""Report bounded CAD support/trim suitability without silently converting faces.

Original CAD is imported from separately acquired, SHA-256-pinned STEP bytes.
Native BRep identities are reported independently of geometric proximity.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
import math
from pathlib import Path

import cadquery as cq
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.BRepTools import BRepTools
from OCP.BRep import BRep_Tool
from OCP.TopAbs import TopAbs_EDGE
from OCP.TopExp import TopExp
from OCP.TopTools import TopTools_IndexedMapOfShape
from OCP.TopoDS import TopoDS

from original_cad_planar_atlas import SOURCES, eligibility, same_index


SUPPORT_APPROXIMATION = frozenset(('CYLINDER', 'CONE', 'TORUS', 'SPHERE'))


def finite_uv_bounds(face):
    """Read the finite trim box, not the underlying infinite support bounds."""
    raw = BRepTools.UVBounds_s(face.wrapped)
    if any(not math.isfinite(x) or abs(x) >= 1e100 for x in raw):
        return None
    return [float(x) for x in raw]


def face_screen(face, face_index, shape, *, scale):
    adaptor = BRepAdaptor_Surface(face.wrapped, True)
    support = face.geomType()
    wires = face.Wires()
    edge_list = shape.Edges()
    recorded_edges=[]
    for edge in face.Edges():
        identity = same_index(edge_list, edge)
        recorded_edges.append(identity)
    # The source can contain degenerate edges omitted by CadQuery's Edges().
    if None in recorded_edges:
        raise ValueError('Native edge identity was omitted by CadQuery; use the full TopoDS edge map')
    category = 'UNASSESSED'
    reason = ''
    polynomial_details=None
    eligible, why = eligibility(face, scale)
    if support == 'PLANE' and eligible is not None:
        category='EXACT_PLANAR_QUAD_CANDIDATE'
    elif support == 'PLANE':
        category='PLANAR_PARTITION_REQUIRED'
        reason=why
    elif support == 'BSPLINE':
        bspline=adaptor.BSpline()
        weights=[bspline.Weight(u,v) for u in range(1,bspline.NbUPoles()+1)
                                   for v in range(1,bspline.NbVPoles()+1)]
        rational=bool(adaptor.IsURational() or adaptor.IsVRational())
        polynomial_details={
            'u_degree':int(adaptor.UDegree()),'v_degree':int(adaptor.VDegree()),
            'u_poles':int(bspline.NbUPoles()),'v_poles':int(bspline.NbVPoles()),
            'u_knots':int(bspline.NbUKnots()),'v_knots':int(bspline.NbVKnots()),
            'rational':rational,'minimum_weight':min(weights),'maximum_weight':max(weights),
            'all_weights_equal':max(weights)-min(weights) <= 1e-12,
        }
        category=('RATIONAL_BSPLINE_APPROX_OR_DECOMPOSE' if rational
                  else 'POLYNOMIAL_BSPLINE_TRIM_AND_DEGREE_AUDIT')
        reason='A spline support type does not imply one four-sided exact bicubic face'
    elif support in SUPPORT_APPROXIMATION:
        category='ANALYTIC_CURVE_APPROX_OR_DECOMPOSE'
        reason='Polynomial bicubic cannot generally reproduce nondegenerate rational curved support exactly'
    else:
        category='UNSUPPORTED_SURFACE_TYPE'
        reason='No admitted geometric conversion policy'
    return {
        'source_face_id':face_index, 'support_type':support,
        'category':category, 'limitation':reason,
        'native_area_mm2':face.Area(),
        'face_edge_ids_in_native_iteration':recorded_edges,
        'wire_count':len(wires),'wire_edge_counts':[len(w.Edges()) for w in wires],
        'has_multiple_wires':len(wires)>1,
        'native_support_is_u_periodic':bool(adaptor.IsUPeriodic()),
        'native_support_is_v_periodic':bool(adaptor.IsVPeriodic()),
        'finite_face_trim_uv_bounds':finite_uv_bounds(face),
        'spline_details':polynomial_details,
        'bp_conversion':'NOT_RUN',
    }


def screen(shape, *, model_id, raw_sha256):
    if not shape.isValid():
        raise ValueError('Invalid source BRep')
    scale=shape.BoundingBox().DiagonalLength
    if scale <= 0 or not math.isfinite(scale):
        raise ValueError('Invalid source scale')
    faces=shape.Faces()
    records=[face_screen(face,i,shape,scale=scale) for i,face in enumerate(faces)]
    groups=Counter(r['category'] for r in records)
    edge_to_faces={}
    edges=shape.Edges()
    full_edge_map=TopTools_IndexedMapOfShape()
    TopExp.MapShapes_s(shape.wrapped, TopAbs_EDGE, full_edge_map)
    degenerate_count=sum(bool(BRep_Tool.Degenerated_s(TopoDS.Edge_s(full_edge_map.FindKey(i))))
                         for i in range(1,full_edge_map.Extent()+1))
    if full_edge_map.Extent()-degenerate_count!=len(edges):
        raise ValueError('Nondegenerate edge graph differs from native TopoDS')
    for r in records:
        for edge_id in set(r['face_edge_ids_in_native_iteration']):
            edge_to_faces.setdefault(edge_id,set()).add(r['source_face_id'])
    incidence=Counter(map(len,edge_to_faces.values()))
    return {
        'schema':'apmesh-s3b-native-surface-screen-v1',
        'source_model':model_id,'source_raw_sha256':raw_sha256,'units':'mm',
        'source_valid_brep':True,'source_face_count':len(faces),
        'source_nondegenerate_edges':len(edges),
        'source_degenerate_edges':degenerate_count,
        'source_all_topods_edges':full_edge_map.Extent(),
        'edge_incidence_scope':'NONDEGENERATE_NATIVE_EDGES_ONLY',
        'face_classification_histogram':dict(sorted(groups.items())),
        'native_nondegenerate_edge_incidence':dict(sorted(incidence.items())),
        'face_records':records,
        'geometric_fit':'NOT_RUN',
        'bp_conversion':'NOT_RUN',
        'full_source_mesh_generation':'NOT_RUN',
        'original_external_multisheet_admission':'NOT_GRANTED',
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--model',choices=sorted(SOURCES),required=True)
    p.add_argument('--sources',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    filename,expected=SOURCES[args.model]
    path=args.sources/filename
    actual=sha256(path.read_bytes()).hexdigest()
    if actual != expected:
        raise ValueError('Pinned source SHA-256 mismatch')
    report=screen(cq.importers.importStep(str(path)).val(),
                  model_id=args.model,raw_sha256=actual)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n',encoding='utf8')
    print(json.dumps({k:report[k] for k in ('source_model','source_face_count','face_classification_histogram','native_nondegenerate_edge_incidence')}))


if __name__ == '__main__':
    main()
