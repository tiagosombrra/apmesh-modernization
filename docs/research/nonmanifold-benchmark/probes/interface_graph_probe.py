#!/usr/bin/env python3
"""Reconstruct a provenance-preserving interface graph for three contacting CAD boxes.

This isolated R2 feasibility probe does NOT produce APMesh BP or modify the input B-Rep.
It reconstructs four geometric surface sheets meeting along one shared spatial curve,
then independently compares the source-contact topology to an analytic three-region oracle.
"""
from __future__ import annotations

import argparse
from collections import defaultdict, Counter
import json
import math
from pathlib import Path

import cadquery as cq
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepExtrema import BRepExtrema_DistShapeShape

UPSTREAM_REPO = 'fusion-energy/model_benchmark_zoo'
UPSTREAM_COMMIT = '3a2e69fe62209e33a1e176d816609d69a2aebadc'
UPSTREAM_PATH = 'src/model_benchmark_zoo/three_touching_cuboids.py'
DEFAULT_WIDTH = 5.0
# Used to verify an analytic construction at exact nominal box coordinates.
COORD_ABS_BUDGET = 1.0e-10
FACE_REL_BUDGET = 1.0e-10


def make_solids(width: float = DEFAULT_WIDTH, shifts: dict[str, tuple[float, float, float]] | None = None):
    """Mirror the pinned upstream three-box CAD recipe without fusing its solids."""
    if not math.isfinite(width) or width <= 0:
        raise ValueError('Width must be finite and positive')
    shifts = shifts or {}
    centers = {
        'A': (-width / 2, width / 2, 0.0),
        'B': (width / 2, width / 2, 0.0),
        'C': (-width / 2, -width / 2, 0.0),
    }
    solids = {}
    for label, center in centers.items():
        dx, dy, dz = shifts.get(label, (0.0, 0.0, 0.0))
        if not all(math.isfinite(c) for c in (dx, dy, dz)):
            raise ValueError('Non-finite offset')
        shape = cq.Workplane('XY').transformed(
            offset=(center[0] + dx, center[1] + dy, center[2] + dz)
        ).box(width, width, width).val()
        solids[label] = shape
    return solids


def edge_ends(edge):
    """Get two endpoint coordinates, normalized to a canonical unoriented order."""
    pts = [tuple(float(c) for c in v.toTuple()) for v in edge.Vertices()]
    if edge.geomType() != 'LINE' or len(pts) != 2:
        return None
    return tuple(sorted(pts))


def max_coordinate_difference(a, b):
    return max(abs(x - y) for p, q in zip(a, b) for x, y in zip(p, q))


def group_exact_candidate_edges(solids, budget: float):
    """Screen geometrically equal SOURCE edges, never mutate the kernel topology."""
    groups = []
    for body_id, solid in solids.items():
        for edge in solid.Edges():
            ends = edge_ends(edge)
            if ends is None:
                continue
            found = None
            for group in groups:
                if max_coordinate_difference(ends, group['endpoints']) <= budget:
                    # An endpoint match is only a candidate: the B-Rep curve must coincide.
                    query = BRepExtrema_DistShapeShape(edge.wrapped, group['source_edges'][0][1].wrapped)
                    query.Perform()
                    if not query.IsDone():
                        raise RuntimeError('OCC native curve-distance evaluation failed')
                    dist = query.Value()
                    if dist <= budget and abs(edge.Length() - group['source_edges'][0][1].Length()) <= budget:
                        found = group
                        break
            if found is None:
                found = {'endpoints': ends, 'source_edges': []}
                groups.append(found)
            found['source_edges'].append((body_id, edge))
    return groups


def faces_using_native_edge(solid, target):
    """Find a face by TopoDS_IsSame edge identity (not by close coordinates)."""
    result = []
    for index, face in enumerate(solid.Faces()):
        if any(target.wrapped.IsSame(edge.wrapped) for edge in face.Edges()):
            result.append((index, face))
    return result


def common_face_area(first, second):
    """Measure geometric co-surface area using the native OCCT Boolean kernel."""
    common = BRepAlgoAPI_Common(first.wrapped, second.wrapped)
    common.Build()
    if not common.IsDone():
        raise RuntimeError('OCC face common Boolean failed')
    return cq.Shape(common.Shape()).Area()


def find_spine(solids, width, budget):
    """Locate the full vertical segment present in three independent source solids."""
    expected = ((0.0, 0.0, -width / 2), (0.0, 0.0, width / 2))
    matches = [g for g in group_exact_candidate_edges(solids, budget)
               if len({body for body, _ in g['source_edges']}) >= 3
               and max_coordinate_difference(g['endpoints'], expected) <= budget]
    if len(matches) != 1:
        raise ValueError(f'Expected one three-body central source segment; found {len(matches)}')
    match = matches[0]
    by_body = defaultdict(list)
    for body, edge in match['source_edges']:
        by_body[body].append(edge)
    if sorted(by_body) != ['A', 'B', 'C'] or any(len(v) != 1 for v in by_body.values()):
        raise ValueError('Central segment must have one source edge in each of A/B/C')
    return match, by_body


def analyze(width=DEFAULT_WIDTH, shifts=None, source_solids=None):
    """Infer the non-manifold sheet graph while retaining per-body source entity IDs."""
    if source_solids is not None and shifts is not None:
        raise ValueError("Supply either source solids or shifts, not both")
    solids = source_solids if source_solids is not None else make_solids(width, shifts)
    source_solids = {}
    for name, solid in solids.items():
        source_solids[name] = {
            'faces': len(solid.Faces()), 'edges': len(solid.Edges()),
            'is_valid': solid.isValid(), 'volume': float(solid.Volume()),
        }
        if not solid.isValid() or abs(solid.Volume() - width**3) > width**3 * FACE_REL_BUDGET:
            raise ValueError('Invalid source solid')
    spine, edges = find_spine(solids, width, COORD_ABS_BUDGET)
    face_uses = []
    for body in ('A', 'B', 'C'):
        uses = faces_using_native_edge(solids[body], edges[body][0])
        if len(uses) != 2:
            raise ValueError(f'Expected two source faces incident on central edge in {body}')
        for index, face in uses:
            face_uses.append({'body': body, 'face_index': index, 'face': face})
    if len(face_uses) != 6:
        raise ValueError('Six original face uses expected')
    # Cluster co-surface faces using an independent geometric Boolean operation.
    # This creates an analysis graph, NOT a TopoDS sewing/welding operation.
    parent = list(range(len(face_uses)))
    def find(i):
        while parent[i] != i:
            i = parent[i]
        return i
    for i in range(len(face_uses)):
        for j in range(i + 1, len(face_uses)):
            if face_uses[i]['body'] == face_uses[j]['body']:
                continue
            area = common_face_area(face_uses[i]['face'], face_uses[j]['face'])
            if area > FACE_REL_BUDGET * width * width:
                # An overlap that is not the whole face would require imprinted splits.
                ai, aj = face_uses[i]['face'].Area(), face_uses[j]['face'].Area()
                if abs(area-ai) > FACE_REL_BUDGET * width * width or abs(area-aj)>FACE_REL_BUDGET * width * width:
                    raise ValueError('Partial face overlap: explicit feature splitting required')
                na = face_uses[i]['face'].normalAt().toTuple()
                nb = face_uses[j]['face'].normalAt().toTuple()
                if abs(sum(x*y for x,y in zip(na,nb)) + 1.0) > FACE_REL_BUDGET:
                    raise ValueError('Coincident interface normals are not opposing')
                pi,pj=find(i),find(j)
                if pi != pj:
                    parent[pj]=pi
    clusters=defaultdict(list)
    for i, use in enumerate(face_uses):
        clusters[find(i)].append(use)
    sheets=[]
    for group in clusters.values():
        if len(group)>2:
            raise ValueError('Ambiguous multi-face overlap, do not silently collapse')
        bodies=sorted({x['body'] for x in group})
        if len(bodies)!=len(group):
            raise ValueError('Repeated use from the same body in one surface sheet')
        regions=sorted(bodies + (['VOID'] if len(group)==1 else []))
        centroid=group[0]['face'].Center().toTuple()
        radial=(centroid[0],centroid[1])
        if math.hypot(*radial) <= COORD_ABS_BUDGET:
            raise ValueError('Sheet radial direction is ambiguous')
        source=[{'body':x['body'],'face_index':x['face_index'],
                 'area':round(x['face'].Area(),12),
                 'normal':tuple(round(z,12) for z in x['face'].normalAt().toTuple())}
                for x in sorted(group,key=lambda x:x['body'])]
        sheets.append({'region_pair':regions,'source_faces':source,'radial_xy':radial,
                       'area':round(group[0]['face'].Area(),12),
                       'spine_boundary':list(spine['endpoints'])})
    sheets.sort(key=lambda x:tuple(x['region_pair']))
    source_counts=Counter(len(sheet['source_faces']) for sheet in sheets)
    observed_pairs=[tuple(s['region_pair']) for s in sheets]
    expected_pairs=[('A','B'),('A','C'),('B','VOID'),('C','VOID')]
    if observed_pairs!=expected_pairs:
        raise ValueError(f'Unexpected region incidence, expected {expected_pairs}, observed {observed_pairs}')
    if len(sheets)!=4 or dict(source_counts)!={2:2,1:2}:
        raise ValueError('Not exactly four independent sheets')
    # A second, analytic oracle for the fixed upstream three-quadrant occupancy:
    # NW=A, NE=B, SW=C, SE=VOID. Every axis ray is exactly one sheet.
    expected_rays={('A','B'):(0,1),('A','C'):(-1,0),('B','VOID'):(1,0),('C','VOID'):(0,-1)}
    for sheet in sheets:
        key=tuple(sheet['region_pair']);r=sheet['radial_xy'];length=math.hypot(*r)
        normalized=(r[0]/length,r[1]/length)
        if any(abs(x-y)>COORD_ABS_BUDGET for x,y in zip(normalized,expected_rays[key])):
            raise ValueError(f'Wrong geometric sheet orientation for {key}')
        if abs(sheet['area']-width*width) > FACE_REL_BUDGET*width*width:
            raise ValueError('Wrong sheet area')
    return {
        'schema':'apmesh-r2-multibody-interface-graph-v1',
        'scope':'LOCAL_PINNED_SOURCE_MIRROR_NOT_UPSTREAM_EXECUTION',
        'upstream':{'repository':UPSTREAM_REPO,'commit':UPSTREAM_COMMIT,'path':UPSTREAM_PATH},
        'geometry':{'width':width,'coordinate_unit':'upstream_model_unit_unspecified',
                    'source_bodies':source_solids},
        'original_topological_identity':{'bodies':len(source_solids),
            'central_source_edges':3,'central_source_face_uses':len(face_uses),
            'central_source_edge_shared_across_bodies':False},
        'reconstructed_spatial_curve':{
            'curve_id':'C0','endpoints':list(spine['endpoints']),
            'length':round(edges['A'][0].Length(),12),
            'incident_sheet_count':len(sheets),
            'provenance':'INFERRED_SHARED_GEOMETRY_FROM_DISTINCT_BREP_EDGES_NOT_WELDED'},
        'sheets':sheets,
        'analytic_region_oracle':{'quadrants':{'NW':'A','NE':'B','SW':'C','SE':'VOID'},
                                  'expected_region_pairs':[list(p) for p in expected_pairs],
                                  'passed':True},
        'output_classification':'GEOMETRIC_INTERFACE_GRAPH_FEASIBLE_NOT_APMESH_BP_ADMITTED',
        'g2_admission':'BLOCKED_INDEPENDENT_SOURCE_ORACLE_AND_GEOMETRY_FIT_PENDING',
    }


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    result=analyze()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'output':str(args.output),'incident_sheets':result['reconstructed_spatial_curve']['incident_sheet_count'],
       'source_edge_identity_shared':result['original_topological_identity']['central_source_edge_shared_across_bodies'],
       'g2_admission':result['g2_admission']},sort_keys=True))


if __name__ == '__main__':
    main()
