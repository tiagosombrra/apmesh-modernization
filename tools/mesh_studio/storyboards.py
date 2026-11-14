"""Fully vector, provenance-safe synthetic research technique storyboards.

The stage drawings in this module are SIMULATED instructional schematics.
They are never a recording of the APMesh generator's internal execution.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET

from .import_obj import import_obj
from .metric2d import Metric2D
from .svg_figure import URI, _tag, audit_svg

ET.register_namespace("", URI)

BG = "#ffffff"
INK = "#182a40"
MUTED = "#55677a"
BORDER = "#d2dae3"
SOFT = "#f3f6f9"
QUAD = "#79bfba"
TRI = "#d4e4f5"
HIGHLIGHT = "#edab59"
ERROR = "#bc4350"


def node(parent, name, **attributes):
    return ET.SubElement(parent, _tag(name), {key.replace("_", "-"): str(value)
                                               for key, value in attributes.items()})


def label(parent, x, y, value, *, size=20, color=INK, weight="normal", anchor="start"):
    node(parent, "text", x=f"{x:.2f}", y=f"{y:.2f}", fill=color,
         font_family="DejaVu Sans, sans-serif", font_size=size,
         font_weight=weight, text_anchor=anchor).text = value


def polygon(parent, points, fill, *, stroke=INK, width=1.6, **attrs):
    return node(parent, "polygon", points=" ".join(f"{x:.3f},{y:.3f}" for x, y in points),
                fill=fill, stroke=stroke, stroke_width=width, stroke_linejoin="round", **attrs)


def line(parent, x1, y1, x2, y2, *, stroke=INK, width=2, dash=None):
    args = {"x1":f"{x1:.2f}", "y1":f"{y1:.2f}", "x2":f"{x2:.2f}",
            "y2":f"{y2:.2f}", "stroke":stroke, "stroke_width":width}
    if dash:
        args["stroke_dasharray"] = dash
    node(parent,"line",**args)


def _base(title, subtitle, *, width, height, width_mm, height_mm, source_hash, recipe):
    root = ET.Element(_tag("svg"), {
        "width":f"{width_mm:g}mm", "height":f"{height_mm:g}mm",
        "viewBox":f"0 0 {width} {height}", "version":"1.1", "role":"img",
        "aria-label":f"Synthetic APMesh Mesh Studio figure: {title}",
        "data-provenance":"SIMULATED", "data-recipe":recipe,
        "data-source-sha256":source_hash,
    })
    node(root,"title").text = title
    node(root,"desc").text = (
        "SIMULATED educational technique illustration, not an observed APMesh "
        "execution or a measured result; each panel is synthetically constructed.")
    node(root,"rect",width=width,height=height,fill=BG)
    label(root,38,44,title,size=30,weight="bold")
    label(root,38,75,subtitle,size=17,color=MUTED)
    line(root,38,91,width-38,91,stroke=BORDER)
    label(root,40,height-20,"SIMULATED • CONCEPTUAL FIGURE • NOT AN APMesh SCIENTIFIC RESULT",
          size=17,weight="bold",color=ERROR)
    return root


def _panel(root, id_, x, y, w, h, letter, title, note):
    g = node(root,"g",id=id_,data_panel=id_,data_provenance="SIMULATED")
    node(g,"rect",x=x,y=y,width=w,height=h,rx=10,fill=BG,stroke=BORDER,stroke_width=1.5)
    label(g,x+17,y+32,f"({letter})  {title}",size=19,weight="bold")
    label(g,x+17,y+h-15,note,size=15,color=MUTED)
    return g


def _write(root, output, *, type_, panel_count, metadata):
    output=Path(output)
    output.parent.mkdir(parents=True,exist_ok=True)
    ET.ElementTree(root).write(output,encoding="utf-8",xml_declaration=True)
    audit = audit_svg(output)
    ids = [el for el in root.iter() if el.attrib.get("data-panel")]
    if not audit["vector_only"] or len(ids)!=panel_count:
        raise ValueError("narrative_vector_semantics_invalid")
    receipt = {
        "schema":"apmesh.meshstudio.synthetic_storyboard.v1",
        "figure_type":type_,"provenance":"SIMULATED","synthetic":True,
        "observed_generator_events":0,"panel_count":panel_count,
        "panel_ids":[el.attrib["data-panel"] for el in ids],
        "true_vector_svg":True,"svg_sha256":hashlib.sha256(output.read_bytes()).hexdigest(),
        "svg_audit":audit,"metadata":metadata,
    }
    output.with_suffix(".audit.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",
                                                   encoding="utf-8")
    return receipt


def render_hybrid_story(fixture, output):
    """Six stages from the actual synthetic 1-QUAD/8-TRI source fixture."""
    fixture=Path(fixture)
    mesh=import_obj(fixture)
    if not mesh.synthetic or mesh.quads!=1 or mesh.triangles!=8 or len(mesh.points)!=8:
        raise ValueError("unexpected_synthetic_hybrid_fixture")
    # Only fixture coordinates are source-backed; quadtree and AFT operations
    # are explicit illustrative stages, not purported source runtime events.
    uv=[face.uv for face in mesh.faces]
    if any(face is None for face in uv):
        raise ValueError("hybrid_source_requires_uv")
    root=_base("Hybrid QUAD/TRI — construction storyboard",
               "Illustrative pipeline • a source fixture, not a generator trace",
               width=1320,height=890,width_mm=210,height_mm=141,
               source_hash=mesh.source_sha256,recipe="hybrid-six-panel-v1")
    panels=[(0,0,"Source boundary","Outer and inner constraints"),
            (0,1,"Sizing scaffold","Schematic graded region"),
            (0,2,"Interior QUAD","1 quadrilateral formed"),
            (1,0,"Remaining front","Exterior region unfilled"),
            (1,1,"TRI closure","8 triangles added conceptually"),
            (1,2,"UV → XYZ lift","Analytic illustrative curvature")]
    x0=40;gapx=16; w=400; h=345; y0=108; gapy=24
    panel_ids=[]
    for i,(row,col,title,subtitle) in enumerate(panels):
        x=x0+col*(w+gapx); y=y0+row*(h+gapy)
        p=_panel(root,f"hybrid-stage-{i+1:02d}",x,y,w,h,"abcdef"[i],title,subtitle)
        panel_ids.append(p.attrib["data-panel"])
        # The original fixture square spans [-1,+1]; preserve its exact UV extent.
        px=x+87;py=y+74;side=225
        def xy(pair):return(px+((pair[0]+1)/2)*side,py+((1-pair[1])/2)*side)
        corners=[(-1,-1),(1,-1),(1,1),(-1,1)]
        inner=[(-0.5,-0.5),(0.5,-0.5),(0.5,0.5),(-0.5,0.5)]
        if i!=5:
            node(p,"rect",x=px,y=py,width=side,height=side,fill=SOFT)
            if i in (0,1,3):
                polygon(p,list(map(xy,corners)),"none",width=2.5)
                polygon(p,list(map(xy,inner)),"none",stroke=HIGHLIGHT,width=3.8)
                if i==1:
                    for step in range(1,4):
                        line(p,px+step*side/4,py,px+step*side/4,py+side,stroke="#adbbc9",width=1,dash="5 5")
                        line(p,px,py+step*side/4,px+side,py+step*side/4,stroke="#adbbc9",width=1,dash="5 5")
                if i==3:
                    polygon(p,list(map(xy,inner)),QUAD,width=2)
                    for u,v in zip(inner,inner[1:]+inner[:1]):
                        a,b=xy(u),xy(v)
                        line(p,*a,*b,stroke=HIGHLIGHT,width=5)
            if i in (2,4):
                face_list = mesh.faces[:1] if i==2 else mesh.faces
                for face in face_list:
                    poly=list(map(xy,face.uv))
                    polygon(p,poly,QUAD if face.element_type=="quad" else TRI,width=1.6,
                            data_cell_type=face.element_type,data_panel_face=f"{i+1}")
                if i==2:
                    polygon(p,list(map(xy,corners)),"none",stroke=BORDER,width=1.6)
        else:
            # Exact fixture UV connectivity, lifted to a *separate* synthetic
            # biquadratic polynomial z(u,v) with an orthographic projection.
            def projected(point):
                u,v=point
                z=0.25*(1-u*u)*(1-v*v)
                return (x+199+u*92-v*56, y+185-u*32-v*55-z*105)
            for face in mesh.faces:
                polygon(p,list(map(projected,face.uv)),
                        QUAD if face.element_type=="quad" else TRI,width=1.8,
                        data_cell_type=face.element_type,data_panel_face="6")
            label(p,x+41,y+296,"z = 0.25(1-u²)(1-v²)",size=16,color=MUTED)
    assert len(panel_ids)==6
    return _write(root,output,type_="hybrid_construction",panel_count=6,
                  metadata={"source_obj_sha256":mesh.source_sha256,
                            "cells":{"quad":1,"triangle":8},
                            "stage_types":["simulated"]*6,
                            "analytic_lift":"z=0.25*(1-u*u)*(1-v*v)",
                            "event_capture_available":False})


def quadrilateral_boundary_parity(cells):
    """Count edge incidences; connected-disk validity is a separate condition."""
    counts={}
    for face in cells:
        if len(face)!=4 or len(set(face))!=4:
            raise ValueError("invalid_all_quad_cell")
        for a,b in zip(face,face[1:]+face[:1]):
            k=tuple(sorted((a,b)))
            counts[k]=counts.get(k,0)+1
            if counts[k]>2:
                raise ValueError("nonmanifold_quad_edge")
    internal=sum(count==2 for count in counts.values())
    boundary=sum(count==1 for count in counts.values())
    if 4*len(cells)!=2*internal+boundary:
        raise ValueError("quadrangulation_incidence_failure")
    return {"quads":len(cells),"interior_edges":internal,"boundary_edges":boundary,
            "boundary_is_even":boundary%2==0}


def render_all_quad_parity(output):
    """Compare valid 2x2 quad disk to impossible fixed 5-edge disk boundary."""
    cells=[(0,1,4,3),(1,2,5,4),(3,4,7,6),(4,5,8,7)]
    report=quadrilateral_boundary_parity(cells)
    if report!={"quads":4,"interior_edges":4,"boundary_edges":8,"boundary_is_even":True}:
        raise ValueError("unexpected_all_quad_truth")
    root=_base("All-QUAD — fixed-boundary parity",
               "Conforming topological disk • necessary condition, not sufficient",
               width=1200,height=645,width_mm=190,height_mm=102,
               source_hash="synthetic-topology-all-quad-v1",recipe="all-quad-parity-v1")
    left=_panel(root,"parity-even",40,112,544,455,"a","EVEN boundary: 8 edges","2x2 all-quad; 4 faces, 4 internal edges")
    right=_panel(root,"parity-odd",616,112,544,455,"b","ODD boundary: 5 edges","Fixed 5-edge disk: no conforming all-quad")
    for row in range(2):
        for col in range(2):
            x=145+col*140;y=202+row*140
            polygon(left,[(x,y),(x+140,y),(x+140,y+140),(x,y+140)],QUAD,width=2)
    vertices=[(887+145*math.sin(2*math.pi*k/5),360-145*math.cos(2*math.pi*k/5)) for k in range(5)]
    polygon(right,vertices,"#faebee",stroke=ERROR,width=3.5)
    for i,p in enumerate(vertices):
        node(right,"circle",cx=f"{p[0]:.3f}",cy=f"{p[1]:.3f}",r=5,fill=ERROR)
    label(right,895,354,"E = 5",size=31,weight="bold",color=ERROR,anchor="middle")
    label(root,72,603,"4F = 2E_int + E_boundary  ⇒  E_boundary must be even",size=23,weight="bold")
    return _write(root,output,type_="all_quad_parity",panel_count=2,
                  metadata={"positive":report,"negative":{"fixed_boundary_edges":5,
                             "conforming_all_quad_disk_exists":False},
                            "scope":"conforming disk with fixed boundary segmentation"})


def render_anisotropy_story(output):
    """Draw unit metric balls for two analytically defined SPD fields."""
    iso=Metric2D(1,0,1)
    ani=Metric2D(16,0,1)
    if not math.isclose(ani.length(0.25,0),1) or not math.isclose(ani.length(0,1),1):
        raise ValueError("synthetic_metric_oracle_failed")
    root=_base("Sizing fields — isotropic vs anisotropic",
               "Prescribed SPD examples, not outputs of the APMesh adapter",
               width=1200,height=645,width_mm=190,height_mm=102,
               source_hash="synthetic-tensor-diag16-1-v1",recipe="spd-metric-ellipses-v1")
    left=_panel(root,"metric-iso",40,112,544,455,"a","Isotropic metric M = I","Unit metric ball is a circle")
    right=_panel(root,"metric-aniso",616,112,544,455,"b","Anisotropic M = diag(16, 1)","Horizontal: 0.25; vertical: 1.0")
    for panel,cx,metric in [(left,312,iso),(right,887,ani)]:
        cy=325;factor=155
        for i in range(-3,4):
            line(panel,cx-202,cy+i*32,cx+202,cy+i*32,stroke="#e2e8ef",width=1)
            line(panel,cx+i*32,cy-162,cx+i*32,cy+162,stroke="#e2e8ef",width=1)
        h,v=metric.unit_ellipse_axes()
        node(panel,"ellipse",cx=cx,cy=cy,rx=f"{factor*h:.3f}",ry=f"{factor*v:.3f}",
             fill="#d1eae7",fill_opacity="0.67",stroke="#227f82",stroke_width=3)
        line(panel,cx-196,cy,cx+196,cy,stroke=INK,width=1.8)
        line(panel,cx,cy-170,cx,cy+170,stroke=INK,width=1.8)
        node(panel,"circle",cx=cx,cy=cy,r=4,fill=INK)
        label(panel,cx+170,cy-8,"u",size=18)
        label(panel,cx+12,cy-156,"v",size=18)
    # The two unit-metric edge vectors have different physical lengths.
    label(right,881,515,"ℓ_M(0.25,0) = ℓ_M(0,1) = 1",size=18,weight="bold",anchor="middle")
    label(left,312,515,"ℓ_M(1,0) = ℓ_M(0,1) = 1",size=18,weight="bold",anchor="middle")
    label(root,55,602,"ℓ_M(e) = √(eᵀ M e)   |   M symmetric positive definite",size=22,weight="bold")
    return _write(root,output,type_="anisotropy_metric",panel_count=2,
                  metadata={"metric_iso":{"m00":1,"m01":0,"m11":1},
                            "metric_anisotropic":{"m00":16,"m01":0,"m11":1},
                            "unit_metric_edges":[[0.25,0],[0,1]],
                            "metric_frame":"illustrative planar XY",
                            "tensor_source":"synthetic_prescribed"})
