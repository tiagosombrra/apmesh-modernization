#!/usr/bin/env python3
"""Create a valid four-sheet OCCT complex from a verified analytic interface graph.

This is a controlled reconstruction, not a conversion of the original source B-Rep.
Source cuboids remain separate; only the four selected surface sheets are sewn.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
import json
from pathlib import Path

import cadquery as cq
from OCP.BRepBuilderAPI import BRepBuilderAPI_Sewing
from validate_interface_graph import check


def construct(graph: dict, *, nonmanifold: bool = True, tolerance: float = 1e-8,
              displace_sheet: str | None = None, offset: float = 2e-5):
    """Assemble four bounded source-derived surfaces with an OCCT topology operation."""
    check(json.loads(json.dumps(graph)))
    if tolerance <= 0:
        raise ValueError('Sewing tolerance must be positive')
    original_faces=[]
    spine=graph['reconstructed_spatial_curve']['endpoints']
    for sheet in graph['sheets']:
        label='/'.join(sheet['region_pair'])
        radial=sheet['radial_xy']
        # Full rectangular face extent is twice its centroid displacement.
        far=(2*radial[0], 2*radial[1])
        shift=offset if label==displace_sheet else 0.0
        a=cq.Vector(spine[0][0]+shift,spine[0][1],spine[0][2])
        b=cq.Vector(spine[1][0]+shift,spine[1][1],spine[1][2])
        c=cq.Vector(far[0]+shift,far[1],spine[1][2])
        d=cq.Vector(far[0]+shift,far[1],spine[0][2])
        face=cq.Face.makeFromWires(cq.Wire.makePolygon([a,b,c,d,a]))
        if not face.isValid() or abs(face.Area()-sheet['area'])>1e-8:
            raise ValueError('Invalid source-derived face')
        original_faces.append(face)
    sewing=BRepBuilderAPI_Sewing(tolerance,True,True,True,True)
    sewing.SetNonManifoldMode(nonmanifold)
    for face in original_faces:
        sewing.Add(face.wrapped)
    sewing.Perform()
    result=cq.Shape(sewing.SewedShape())
    faces=result.Faces()
    if not result.isValid() or len(faces)!=4 or not all(f.isValid() for f in faces):
        raise ValueError('Sewn four-sheet complex is not kernel-valid')
    # Count edge identity by native TopoDS_IsSame rather than rounded geometry.
    groups=[]
    for face_index,face in enumerate(faces):
        for edge in face.Edges():
            match=next((g for g in groups if g['edge'].wrapped.IsSame(edge.wrapped)),None)
            if match is None:
                match={'edge':edge,'face_indices':set()}
                groups.append(match)
            match['face_indices'].add(face_index)
    counts={}
    for group in groups:
        n=len(group['face_indices'])
        counts[n]=counts.get(n,0)+1
    common=[g for g in groups if len(g['face_indices'])==4]
    summary={
        'schema':'apmesh-r2-constructed-nonmanifold-occt-v1',
        'source_scope':'LOCAL_ANALYTIC_THREE_BOX_SOURCE_MIRROR',
        'shape_type':result.ShapeType(),
        'kernel_valid':bool(result.isValid()),
        'faces':len(faces),
        'face_areas':[round(face.Area(),12) for face in faces],
        'unique_topological_edges':len(groups),
        'edge_incidence_histogram':dict(sorted(counts.items())),
        'multiple_edges_reported_by_sewing':sewing.NbMultipleEdges(),
        'max_edge_incidence':max(counts),
        'shared_four_incident_edge_count':len(common),
        'shared_edge_length':round(common[0]['edge'].Length(),12) if len(common)==1 else None,
        'nonmanifold_mode':nonmanifold,
        'sewing_tolerance':tolerance,
        'displaced_sheet':displace_sheet,
        'classification':'CONSTRUCTED_CAD_SURFACE_COMPLEX_NOT_APMESH_BP',
        'g2_external_admission':'NOT_GRANTED',
    }
    return summary,result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--interface-graph',type=Path,required=True)
    parser.add_argument('--output-json',type=Path,required=True)
    parser.add_argument('--output-brep',type=Path,default=None)
    args=parser.parse_args()
    graph=json.loads(args.interface_graph.read_text(encoding='utf-8'))
    report,shape=construct(graph)
    args.output_json.parent.mkdir(parents=True,exist_ok=True)
    args.output_json.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    if args.output_brep:
        args.output_brep.parent.mkdir(parents=True,exist_ok=True)
        shape.exportBrep(str(args.output_brep))
    print(json.dumps(report,sort_keys=True))

if __name__=='__main__':
    main()
