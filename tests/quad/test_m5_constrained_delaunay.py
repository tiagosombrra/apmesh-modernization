#!/usr/bin/env python3
"""Research-only locally Delaunay exterior UV, using actual C++ Quadtree outputs.

Constrained outer boundary and QUAD/TRI seam are preserved. Ear clipping and
exact rational Lawson flips do not reproduce 1993 contour contraction,
historic point-insertion policy, physical XYZ, or production mesh generation.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from fractions import Fraction as Q
import hashlib
import json
import math
from pathlib import Path


def require(ok, why):
    if not ok:
        raise ValueError(why)


def read_obj(path):
    vertices, quads, triangles = [], [], []
    for line in path.read_text(encoding="ascii").splitlines():
        fields = line.split()
        if not fields:
            continue
        if fields[0] == "v":
            vertices.append(tuple(float(x) for x in fields[1:4]))
        elif fields[0] == "f":
            face = tuple(int(x) - 1 for x in fields[1:])
            require(len(face) in (3, 4), "Unexpected OBJ face")
            (quads if len(face) == 4 else triangles).append(face)
    return vertices, quads, triangles


def edges(faces):
    out = defaultdict(list)
    for i, face in enumerate(faces):
        for a, b in zip(face, face[1:] + face[:1]):
            out[tuple(sorted((a, b)))].append((i, a, b))
    return out


def exact_vertices(vertices):
    return [tuple(Q(str(x)) for x in p[:2]) for p in vertices]


def cross(pts, a, b, c):
    x,y = pts[a]
    u,v = pts[b]
    w,z = pts[c]
    return (u-x)*(z-y) - (v-y)*(w-x)


def incircle(pts, a, b, c, d):
    ax,ay=pts[a];bx,by=pts[b];cx,cy=pts[c];dx,dy=pts[d]
    ax-=dx;ay-=dy;bx-=dx;by-=dy;cx-=dx;cy-=dy
    return ((ax*ax+ay*ay)*(bx*cy-by*cx)
            -(bx*bx+by*by)*(ax*cy-ay*cx)
            +(cx*cx+cy*cy)*(ax*by-ay*bx))


def clip_ears(pts, perimeter):
    """Split convex cells while retaining each collinear edge vertex."""
    order=list(perimeter)
    triangles=[]
    while len(order)>3:
        ear=None
        for j,b in enumerate(order):
            a,c=order[j-1],order[(j+1)%len(order)]
            if cross(pts,a,b,c)<=0:
                continue
            if any(cross(pts,a,b,k)>=0 and cross(pts,b,c,k)>=0
                   and cross(pts,c,a,k)>=0
                   for k in order if k not in (a,b,c)):
                continue
            triangles.append((a,b,c))
            ear=j
            break
        require(ear is not None, "No valid ear in subdivided exterior cell")
        order.pop(ear)
    require(cross(pts,*order)>0, "Final triangle is inverted")
    triangles.append(tuple(order))
    return triangles


def make_exterior(native_vertices, rows):
    vertices=list(native_vertices)
    points=exact_vertices(vertices)
    ids={(x,y):i for i,(x,y,z) in enumerate(vertices)}
    candidates=set(ids)
    boxes=[tuple(float(row[k]) for k in
           ("min_u","min_v","max_u","max_v")) for row in rows]
    for x0,y0,x1,y1 in boxes:
        candidates.update(((x0,y0),(x1,y0),(x1,y1),(x0,y1)))
    triangles=[]
    for row,(x0,y0,x1,y1) in zip(rows,boxes):
        if row["region"]!="excluded_boundary_unmeshed":
            continue
        frame=(((x0,y0),(x1,y0)),((x1,y0),(x1,y1)),
               ((x1,y1),(x0,y1)),((x0,y1),(x0,y0)))
        perimeter=[]
        for a,b in frame:
            dx,dy=b[0]-a[0],b[1]-a[1]
            items=[p for p in candidates
                   if abs(dx*(p[1]-a[1])-dy*(p[0]-a[0]))<1e-14
                   and min(a[0],b[0])<=p[0]<=max(a[0],b[0])
                   and min(a[1],b[1])<=p[1]<=max(a[1],b[1])]
            items.sort(key=lambda p:(p[0]-a[0])*dx+(p[1]-a[1])*dy)
            require(len(items)>=2 and items[0]==a and items[-1]==b,
                    "Incomplete exterior leaf boundary")
            for p in items[:-1]:
                if p not in ids:
                    ids[p]=len(vertices)
                    vertices.append((p[0],p[1],0.0))
                    points.append(tuple(Q(str(x)) for x in p))
                perimeter.append(ids[p])
        require(len(perimeter)>=4 and len(set(perimeter))==len(perimeter),
                "Malformed leaf polygon")
        triangles.extend(clip_ears(points,perimeter))
    require(len(vertices)==69 and len(triangles)==36,
            "Unexpected 19-leaf CDT vertex/triangle inventory")
    return vertices,points,triangles


def optimize(pts, triangles):
    output=list(triangles)
    constraint={edge for edge,refs in edges(output).items() if len(refs)==1}
    require(len(constraint)==36, "Initial constrained boundary changed")
    flips=0
    for _ in range(4096):
        incidence=edges(output)
        changed=False
        for (a,b),refs in sorted(incidence.items()):
            if len(refs)!=2 or (a,b) in constraint:
                continue
            i,j=refs[0][0],refs[1][0]
            c=next(v for v in output[i] if v not in (a,b))
            d=next(v for v in output[j] if v not in (a,b))
            if cross(pts,a,b,c)<0:
                c,d=d,c
            require(cross(pts,a,b,c)>0 and cross(pts,a,b,d)<0,
                    "Invalid edge neighbor orientation")
            if cross(pts,c,d,a)*cross(pts,c,d,b)>=0:
                continue
            if incircle(pts,a,b,c,d)<=0:
                continue
            require(tuple(sorted((c,d))) not in incidence,
                    "Lawson flip would duplicate an edge")
            t0,t1=(c,d,b),(d,c,a)
            require(cross(pts,*t0)>0 and cross(pts,*t1)>0,
                    "Inverted Lawson result")
            output[i],output[j]=t0,t1
            flips+=1
            changed=True
            break
        if not changed:
            break
    else:
        raise ValueError("Lawson flips did not converge")
    require({edge for edge,refs in edges(output).items() if len(refs)==1}
            ==constraint, "Constrained ring boundary changed")
    locally_delaunay=0
    for (a,b),refs in edges(output).items():
        if len(refs)!=2:
            continue
        c=next(v for v in output[refs[0][0]] if v not in (a,b))
        d=next(v for v in output[refs[1][0]] if v not in (a,b))
        if cross(pts,a,b,c)<0:
            c,d=d,c
        if cross(pts,c,d,a)*cross(pts,c,d,b)<0:
            require(incircle(pts,a,b,c,d)<=0,
                    "Interior edge violates local Delaunay condition")
            locally_delaunay+=1
    require(flips==8 and locally_delaunay==24,
            "Unexpected deterministic Lawson research fixture")
    return output,flips,locally_delaunay


def validate(vertices, quads, triangles):
    require(len(vertices)==69 and len(set(vertices))==69
            and len(quads)==42 and len(triangles)==36,
            "Mixed-mesh vertex/face count or identity incorrect")
    pts=exact_vertices(vertices)
    incidence=defaultdict(list)
    areas={}
    used=set()
    for kind,faces,size in (("QUAD",quads,4),("TRI",triangles,3)):
        total=Q(0)
        for face in faces:
            require(len(face)==size and len(set(face))==size
                    and all(0<=k<len(vertices) for k in face),
                    "Invalid face indices")
            twice=sum((pts[face[i]][0]*pts[face[(i+1)%size]][1]
                       -pts[face[(i+1)%size]][0]*pts[face[i]][1]
                       for i in range(size)),Q(0))
            require(twice>0,"Inverted or zero-area face")
            total+=twice/2
            used.update(face)
            for a,b in zip(face,face[1:]+face[:1]):
                incidence[tuple(sorted((a,b)))].append((kind,a,b))
        areas[kind]=total
    require(used==set(range(len(vertices))),"Orphan vertex")
    require(areas=={"QUAD":Q(1,4),"TRI":Q(3,4)},
            "Incorrect domain area partition")
    seam=[]
    outer=[]
    for edge,refs in incidence.items():
        require(len(refs) in (1,2),"Nonmanifold edge")
        if len(refs)==2:
            require(refs[0][1:]==refs[1][1:][::-1],
                    "Mismatched interface edge winding")
            if refs[0][0]!=refs[1][0]:
                seam.append(edge)
        else:
            outer.append(edge)
    require(len(seam)==20 and len(outer)==16,
            "Incorrect QUAD/TRI seam or external boundary")
    require(len(vertices)-len(incidence)+len(quads)+len(triangles)==1,
            "Expected one topological disk")
    graph=defaultdict(set)
    for a,b in seam:
        graph[a].add(b)
        graph[b].add(a)
    require(len(graph)==20 and all(len(g)==2 for g in graph.values()),
            "Interface must be single closed cycle")
    reached=set()
    todo=[next(iter(graph))]
    while todo:
        v=todo.pop()
        if v not in reached:
            reached.add(v)
            todo.extend(graph[v]-reached)
    require(reached==set(graph),"Disconnected interface")
    for a,b in outer:
        x,y=pts[a];xx,yy=pts[b]
        require((x==xx and x in (0,1)) or (y==yy and y in (0,1)),
                "Outer boundary does not match domain")
    # Detect any split-side vertex inadvertently skipped by a mesh edge.
    for a,b in incidence:
        ax,ay=pts[a];bx,by=pts[b]
        for k,(x,y) in enumerate(pts):
            if k in (a,b):
                continue
            if min(ax,bx)<=x<=max(ax,bx) and min(ay,by)<=y<=max(ay,by):
                require(cross(pts,a,b,k)!=0,"Hanging vertex")
    return sorted(seam)


def negative_cases(v,q,t):
    variants=[(v,q,t[1:]),(v,q,[t[0][::-1]]+t[1:]),
              (v,q,t+t[:1]),(v,q[1:],t)]
    damaged=list(v)
    damaged[-1]=damaged[0]
    variants.append((damaged,q,t))
    refused=0
    for a,b,c in variants:
        try:
            validate(a,b,c)
        except ValueError:
            refused+=1
    require(refused==5,"Invalid input not rejected")


def min_angle(vertices, faces):
    value=180.0
    for f in faces:
        for i,k in enumerate(f):
            a=vertices[k];b=vertices[f[(i+1)%3]];c=vertices[f[(i+2)%3]]
            x,y=b[0]-a[0],b[1]-a[1]
            u,v=c[0]-a[0],c[1]-a[1]
            value=min(value,math.degrees(math.atan2(abs(x*v-y*u),x*u+y*v)))
    return value


def write_obj(path,vertices,quads,tris):
    with path.open("w",encoding="ascii",newline="\n") as output:
        output.write("# C++ QUAD + research local constrained Delaunay UV; NOT 1993 full hybrid.\n")
        for x,y,z in vertices:
            output.write(f"v {x:.17g} {y:.17g} {z:.17g}\n")
        output.write("g QUAD_native_cpp_unmodified\n")
        for face in quads:
            output.write("f "+" ".join(str(i+1) for i in face)+"\n")
        output.write("g TRI_exterior_local_Lawson_research\n")
        for face in tris:
            output.write("f "+" ".join(str(i+1) for i in face)+"\n")


def svg(path, native, quad, fan, fan_tri, exterior, optimized, seam):
    models=(("Prior 60-triangle fan",fan,fan_tri),
            ("36-triangle ear clipping",native,exterior),
            ("36-triangle local Delaunay",native,optimized))
    lines=['<svg xmlns="http://www.w3.org/2000/svg" width="2070" height="748" '
           'viewBox="0 0 2070 748" data-origin="native-cpp-quad-research-lawson">',
           '<rect width="2070" height="748" fill="#fbfdff"/>',
           '<text x="25" y="36" font-family="Arial" font-size="24">'
           'Actual C++ QUAD and research exterior TRI comparison (UV)</text>']
    for j,(title,vertices,triangles) in enumerate(models):
        start=25+690*j
        lines.append(f'<text x="{start}" y="75" font-family="Arial" '
                     f'font-size="18">{title}</text>')
        for faces,color,tag in ((triangles,"#edc1a9","TRI"),
                                (quad,"#add4ed","QUAD")):
            for face in faces:
                points=" ".join(
                    f"{start+575*vertices[i][0]:.4f},{670-575*vertices[i][1]:.4f}"
                    for i in face)
                lines.append(f'<polygon data-kind="{tag}" points="{points}" '
                             f'fill="{color}" stroke="#30495b" stroke-width="0.8"/>')
        for a,b in seam:
            lines.append(f'<line x1="{start+575*native[a][0]:.4f}" '
                         f'y1="{670-575*native[a][1]:.4f}" '
                         f'x2="{start+575*native[b][0]:.4f}" '
                         f'y2="{670-575*native[b][1]:.4f}" '
                         'stroke="#be3851" stroke-width="2.3"/>')
        lines.append(f'<rect x="{start}" y="95" width="575" height="575" '
                     'fill="none" stroke="#243d50" stroke-width="2"/>')
    lines.append('<text x="26" y="730" font-family="Arial" font-size="14">'
                 '42 unchanged C++ QUAD; seam 20 edges; Z=0; '
                 'NOT historic 1993 Delaunay/contour contraction.</text></svg>')
    path.write_text("\n".join(lines)+"\n",encoding="utf-8")


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--directory",type=Path,required=True)
    folder=parser.parse_args().directory
    previous=json.loads((folder/"experimental_hybrid_manifest.json")
                        .read_text(encoding="utf-8"))
    require(previous["status"]=="UV_conforming_experimental_fan_NOT_historical_Delaunay"
            and previous["quad_count"]==42 and previous["tri_count"]==60,
            "Prior M5 C++/fan provenance failed")
    with (folder/"tree_regions.csv").open(newline="",encoding="utf-8") as fh:
        rows=list(csv.DictReader(fh))
    require(len(rows)==19 and Counter(x["region"] for x in rows)
            =={"quad_candidate":7,"excluded_boundary_unmeshed":12},
            "Native 19-leaf Quadtree partition changed")
    outcomes=[]
    for mode in ("vertex_mean","area_centroid"):
        cpp,quads,native_tri=read_obj(folder/f"quads_{mode}.obj")
        fan,fan_quads,fan_tri=read_obj(folder/f"hybrid_experimental_{mode}.obj")
        require(len(cpp)==53 and not native_tri and len(quads)==42
                and fan[:53]==cpp and fan_quads==quads and len(fan_tri)==60,
                "Source C++ QUAD differs from qualified M5 baseline")
        vertices,points,ears=make_exterior(cpp,rows)
        require(vertices[:53]==cpp,"Native C++ QUAD source coordinates changed")
        triangles,flips,checked=optimize(points,ears)
        seam=validate(vertices,quads,triangles)
        negative_cases(vertices,quads,triangles)
        initial_angle=min_angle(vertices,ears)
        optimized_angle=min_angle(vertices,triangles)
        require(optimized_angle>initial_angle,
                "No expected positive minimum-angle improvement")
        write_obj(folder/f"hybrid_research_local_delaunay_{mode}.obj",
                  vertices,quads,triangles)
        outcomes.append((vertices,quads,fan,fan_tri,ears,triangles,seam,
                         flips,checked,initial_angle,optimized_angle))
    require(outcomes[0][5]==outcomes[1][5] and
            outcomes[0][6]==outcomes[1][6],
            "Different center rules altered external topology")
    v,q,fan,fan_t,ear,tri,seam,*_=outcomes[1]
    svg(folder/"research_local_delaunay_comparison.svg",v,q,fan,fan_t,ear,tri,seam)
    output={
        "schema":1,
        "source":"native_CPP_19_leaf_Quadtree_and_qualified_M5_fan",
        "algorithm":"ear clipping with exact-rational Lawson flips",
        "status":"RESEARCH_CONSTRAINED_LOCALLY_DELAUNAY_NOT_HISTORICAL",
        "historical_1993_Delaunay_contraction_implemented":False,
        "production_hybrid_enabled":False,"all_quad_extension_enabled":False,
        "native_cpp_quads_unchanged":True,
        "quad_count":42,"tri_count":36,"vertices":69,
        "quad_area":0.25,"tri_area":0.75,"total_area":1.0,
        "quad_tri_seam_edges":20,"outer_boundary_edges":16,
        "lawson_flips_per_rule":[z[7] for z in outcomes],
        "local_delaunay_edges_per_rule":[z[8] for z in outcomes],
        "ear_min_angle_degrees":[z[9] for z in outcomes],
        "optimized_min_angle_degrees":[z[10] for z in outcomes],
        "negative_mutations_rejected":5,
        "native_input_sha256":{name:hashlib.sha256((folder/name).read_bytes()).hexdigest()
            for name in ("tree_regions.csv","quads_vertex_mean.obj",
                         "quads_area_centroid.obj")}
    }
    (folder/"research_local_delaunay_manifest.json").write_text(
        json.dumps(output,indent=2)+"\n",encoding="utf-8")
    print("m5_local_cdt=ok native_cpp_quads=42 research_tri=36 "
          "seam=20 area=1 lawson_flips=8 negative=5 historical_1993=NOT_DONE")


if __name__=="__main__":
    main()
