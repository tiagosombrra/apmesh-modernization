"""CurvaBezier research projection for the previously measured adjacent grouping."""

from collections import Counter, defaultdict, deque
from fractions import Fraction
from functools import lru_cache
from hashlib import sha256
from math import dist
from statistics import median

from quad_generation_metrics import cross, element_quality, load_physical_obj, norm
from test_m1_figure7_oracle import GOLDEN, MIDPOINTS, area_centroid, subdivide, transform
from test_m4_real_model_hybrid import golden

def edge_set(face):
    return [tuple(sorted((a,b))) for a,b in zip(face,face[1:]+face[:1])]
def boundary(faces):
    return {edge for edge,n in Counter(e for f in faces for e in edge_set(f)).items() if n==1}
def inside(p,box):
    return all(box[k]<=p[k]<=box[k+2] for k in (0,1))
def span(box):
    return box[2]-box[0]
def project_parent(box):
    size=2*span(box)
    x,y=(int(box[k]/size)*size for k in range(2))
    return (x,y,x+size,y+size)
def neighbors(box,grid):
    x,y,X,Y=box
    return [
        [n for n in grid if n[3]==y and max(x,n[0])<min(X,n[2])],
        [n for n in grid if n[0]==X and max(y,n[1])<min(Y,n[3])],
        [n for n in grid if n[1]==Y and max(x,n[0])<min(X,n[2])],
        [n for n in grid if n[2]==x and max(y,n[1])<min(Y,n[3])]]
def sides_mask(box,grid):
    n=neighbors(box,grid)
    if any(len(g)>2 or any(not .5<=span(b)/span(box)<=2 for b in g) for g in n):
        return None
    return tuple(i for i,g in zip("SENW",n) if len(g)==2)
POINTS={"A":(0,0),"B":(1,0),"C":(1,1),"D":(0,1),"O":(Fraction(1,2),)*2,**MIDPOINTS}
@lru_cache(maxsize=None)
def pattern(mask):
    for name,_,cycles,*_ in GOLDEN:
        chosen={a:tuple(Fraction(v) for v in p) for a,p in POINTS.items() if any(a in c for c in cycles)}
        for turns in range(4):
            coords={a:transform(p,False,turns) for a,p in chosen.items()}
            if {s for s,p in MIDPOINTS.items() if p in coords.values()}!=set(mask):
                continue
            v,f=subdivide(coords,cycles,area_centroid)
            return name,[[tuple(map(float,v[j])) for j in face] for face in f]
    raise AssertionError(mask)
def pattern_on(box,mask):
    name,faces=pattern(mask)
    return name,[tuple(tuple(box[k]+span(box)*p[k] for k in (0,1)) for p in f) for f in faces]
def cross2(a,b,p):
    return (b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])
def owning_box(face,grid):
    center=tuple(sum(p[k] for p in face)/len(face) for k in (0,1))
    box,=[box for box in grid if all(box[k]<center[k]<box[k+2] for k in (0,1))]
    return box
def qualify_geometry(front,path,surface):
    xyz,uv,triangles=load_physical_obj(path)
    uv=tuple(uv)
    assert list(map(list,uv))==front["vertices"]
    leaves=list(map(tuple,front["leaves"]))
    seed_map=defaultdict(list)
    for raw in front["seed_faces"]:
        face=tuple(uv[v] for v in raw)
        seed_map[owning_box(face,leaves)].append(face)
    trace_edges=defaultdict(list)
    for box,faces in seed_map.items():
        for f in faces:
            for e in edge_set(f):
                trace_edges[e].append(box)
    seed_out={e:owners[0] for e,owners in trace_edges.items() if len(owners)==1}
    outer={i for e in boundary(triangles) for i in e}
    result=[]
    for idx,f in enumerate(triangles):
        if len(f)!=3 or sum(i in outer for i in f)!=1:
            continue
        exposed=[e for e in edge_set([uv[i] for i in f]) if e in seed_out]
        if len(exposed)!=1:
            continue
        short,=exposed
        box=seed_out[short]
        # This diagnostic specifically tests short seed half-sides facing the outer boundary.
        # Normalizing by which side of the owner carries the exposed edge leaves orientation free.
        a,b=short
        fixed=[k for k in (0,1) if a[k]==b[k] and a[k] in (box[k],box[k+2])]
        if len(fixed)!=1:
            continue
        axis,=fixed
        contour_point,=[uv[i] for i in f if i in outer]
        if not (contour_point[axis]<a[axis] if a[axis]==box[axis] else contour_point[axis]>a[axis]):
            continue
        parent=project_parent(box)
        children=[b for b in leaves if span(b)==span(box) and inside(b[:2],parent) and inside(b[2:],parent)]
        physical=[dist(xyz[i],xyz[j]) for i,j in edge_set(f)]
        face_size=median(physical)
        angle=element_quality(xyz,uv,f,lambda at:cross(*surface(*at)[1:]))["min_angle_xyz"]
        old_length=dist(*(surface(*xy)[0] for xy in short))
        ratio=lambda length:max(length,face_size)/min(length,face_size)
        entry=dict(face=idx,angle=angle,seed_edge=short,target_parent=parent,
                   old_edge=old_length,desired_size_reference=face_size,old_ratio=ratio(old_length))
        result.append(entry)
        if len(children)!=4 or not all(c in seed_map for c in children):
            entry["disposition"]="incomplete_seed_siblings"
            continue
        if a[axis] not in (parent[axis],parent[axis+2]):
            entry["disposition"]="internal_parent_side"
            continue
        tree=[c for c in leaves if c not in children]+[parent]
        around={n for g in neighbors(parent,tree) for n in g}
        changed=[c for c in around if sides_mask(c,leaves)!=sides_mask(c,tree)]
        mask=sides_mask(parent,tree)
        if mask is None or any(sides_mask(c,tree) is None for c in around):
            entry["disposition"]="would_break_two_to_one"
            continue
        # All child cells were seeded; use convex clearance distance independently for their parent.
        x,y,X,Y=parent
        if x==0 or y==0 or X==1 or Y==1:
            entry["disposition"]="parent_touches_domain_boundary"
            continue
        def gap(edge):
            c,d=[uv[i] for i in edge]
            lo0,hi0=sorted((c[0],d[0]))
            lo1,hi1=sorted((c[1],d[1]))
            return dist((0,0),(max(x-hi0,lo0-X,0),max(y-hi1,lo1-Y,0)))
        if any(gap(e)<.2*dist(*(uv[v] for v in e)) for e in boundary(triangles)):
            entry["disposition"]="parent_outside_template_clearance"
            continue
        name,faces=pattern_on(parent,mask)
        along=1-axis
        merged=[e for e in boundary(faces) if all(p[axis]==a[axis] for p in e) and
                min(p[along] for p in e)<=min(a[along],b[along]) and
                max(p[along] for p in e)>=max(a[along],b[along])]
        if len(merged)!=1:
            entry["disposition"]="no_single_replacement_edge"
            continue
        new_length=dist(*(surface(*p)[0] for p in merged[0]))
        exact_preserved=short in boundary(faces)
        entry.update(projected_pattern=name, projected_length=new_length, new_ratio=ratio(new_length),
                     projected_local_quad_count=len(faces), unchanged_short_edge=exact_preserved,
                     affected_neighbor_boxes=sorted(changed), replaced_seed_count=sum(len(seed_map[c]) for c in children),
                     projected_replacement_edge=merged[0], protected_requests=[])
        if exact_preserved or not ratio(new_length)<ratio(old_length)-1e-12 or old_length>=face_size:
            entry["disposition"]="no_physical_size_improvement"
            continue
        entry["disposition"]="eligible"
    return sorted(result,key=lambda r:(r["angle"],r["face"]))

def leaves_in(parent, grid):
    return {b for b in grid if span(b) * 2 == span(parent)
            and inside(b[:2], parent) and inside(b[2:], parent)}

def use_neighbor(front, target, requests):
    grid = [tuple(box) for box in front['leaves']]
    parent = tuple(target['target_parent'])
    if not target['unchanged_short_edge'] or target['projected_pattern'] != 'T6':
        return dict(disposition='primary_edge_not_retained_by_T6')
    primary_children = leaves_in(parent, grid)
    if len(primary_children) != 4:
        return dict(disposition='primary_without_four_leaves')
    single = [b for b in grid if b not in primary_children] + [parent]
    a, b = target['seed_edge']
    side = next(i for i, (axis, edge) in enumerate(((1, 1), (0, 2), (1, 3), (0, 0)))
                if a[axis] == b[axis] == parent[edge])
    axis = 1 if side in (0, 2) else 0
    blockers = neighbors(parent, single)[side]
    if len(blockers) != 2 or any(span(box)*2 != span(parent) for box in blockers):
        return dict(disposition='retained_side_has_no_unique_fine_neighbor')
    adjacent = {project_parent(child) for child in blockers}
    if len(adjacent) != 1:
        return dict(disposition='retained_side_has_no_unique_fine_neighbor')
    second, = adjacent
    second_children = leaves_in(second, single)
    if len(second_children) != 4:
        return dict(disposition='neighbor_without_four_leaves')
    joint = [cell for cell in single if cell not in second_children] + [second]
    masks = {box:sides_mask(box, joint) for box in joint}
    result = dict(blocks=[parent,second], blockers=blockers, source_leaf_count=len(grid),
                  projected_leaf_count=len(joint), single_pattern=target['projected_pattern'])
    if any(mask is None for mask in masks.values()):
        return dict(result, disposition='would_break_two_to_one')
    label, faces = pattern_on(parent, masks[parent])
    along = 1 - axis
    edge_matches = [edge for edge in boundary(faces)
                    if all(p[axis] == a[axis] for p in edge)
                    and min(p[along] for p in edge) <= min(a[along], b[along])
                    and max(p[along] for p in edge) >= max(a[along], b[along])]
    if len(edge_matches) != 1:
        return dict(result, disposition='no_single_replacement_edge')
    length = dist(*(golden(*p)[0] for p in edge_matches[0]))
    size = target['desired_size_reference']
    ratio = max(length,size)/min(length,size)
    result.update(joint_pattern=label, joint_edge=edge_matches[0], projected_length=length,
                  projected_ratio=ratio, previous_length=target['old_edge'], previous_ratio=target['old_ratio'])
    if not ratio < target['old_ratio']-1e-12:
        return dict(result, disposition='no_physical_size_improvement')
    changed = [box for box in joint if box in grid and masks[box] != sides_mask(box, grid)]
    protected = [request for request in requests
                 if any(inside(request['site'], box) for box in [parent,second,*changed])]
    return dict(result, disposition='active_smaller_size_request' if protected else 'eligible',
                protected_requests=protected, changed_neighbor_boxes=changed)


def geometric_size_requests(path, evaluate=golden):
    """Replay the approved residual seeds and three synchronous grading passes."""
    xyz, uv, faces = load_physical_obj(path)
    contour_rows = [line.split() for line in path.read_text(encoding="ascii").splitlines()
                    if line.startswith("# source_site ")]
    node_at = {point: i for i, point in enumerate(uv)}
    contour = [node_at[tuple(map(float, row[4:6]))] for row in contour_rows]
    owners = defaultdict(list)
    errors = []
    initial = []
    sites = []
    for i, face in enumerate(faces):
        edges = edge_set(face)
        for edge in edges:
            owners[edge].append(i)
        initial.append(median(dist(xyz[a], xyz[b]) for a, b in edges))
        weights = ([(1/3,)*3, (.6,.2,.2), (.2,.6,.2), (.2,.2,.6)] if len(face) == 3 else
                   [((1-s)*(1-t), s*(1-t), s*t, (1-s)*t) for s,t in
                    ((.5,.5), (.25,.25), (.75,.25), (.75,.75), (.25,.75))])
        samples = []
        for w in weights:
            at = tuple(sum(wj*uv[j][k] for wj,j in zip(w,face)) for k in range(2))
            point = tuple(sum(wj*xyz[j][k] for wj,j in zip(w,face)) for k in range(3))
            samples.append((dist(evaluate(*at)[0],point),at))
        error, at = max(samples, key=lambda sample: sample[0])
        errors.append(error)
        sites.append(at)

    count = len(faces)
    graph = [set() for _ in range(count+len(contour))]
    def connect(a,b):
        graph[a].add(b)
        graph[b].add(a)
    for incident in owners.values():
        if len(incident) == 2:
            connect(*incident)
    for i,(a,b) in enumerate(zip(contour,contour[1:]+contour[:1])):
        owner, = owners[tuple(sorted((a,b)))]
        connect(count+i,owner)
        connect(count+i,count+(i+1)%len(contour))
    lengths = arc_lengths(evaluate)
    initial += [float(row[12])*lengths[int(row[2])] for row in contour_rows]
    seeds = [max((i for i,f in enumerate(faces) if len(f)==arity),key=errors.__getitem__)
             for arity in (3,4)]
    distances = dict.fromkeys(seeds,0)
    queue = deque(seeds)
    target = initial[:]
    for i in seeds:
        target[i] /= 2
    while queue:
        i = queue.popleft()
        for j in sorted(graph[i]):
            if j not in distances:
                distances[j] = distances[i]+1
                queue.append(j)
    if len(distances) != len(graph):
        raise ValueError("Disconnected mixed sizing graph")
    for _ in range(3):
        updated = target[:]
        for i, adjacent in enumerate(graph):
            if distances[i] <= 3:
                for j in sorted(adjacent):
                    if distances[j] <= 3 and 1.35*target[j] < updated[i]:
                        updated[i] = 1.35*target[j]
        target = updated
    faces = [dict(face=i, site=at, h=target[i]) for i,at in enumerate(sites)
             if target[i]<initial[i]]
    curves = [dict(interval=i, previous_size=initial[count+i], h=target[count+i])
              for i in range(len(contour)) if target[count+i]<initial[count+i]]
    return faces, curves


def protected_size_requests(path):
    return geometric_size_requests(path)[0]


def select_adjacent_group(front_dir, front, predecessor, protect_neighbor=False):
    birth = front_dir / f"commit_{len(front['commits'])}.obj"
    xyz, uv, faces = load_physical_obj(birth)
    normal = lambda at: cross(*golden(*at)[1:])
    _, limiting = min((element_quality(xyz,uv,f,normal)["min_angle_xyz"],i)
                      for i,f in enumerate(faces) if len(f)==3)
    targets = qualify_geometry(front, birth, golden)
    target = next((row for row in targets if row["face"] == limiting), None)
    if target is None or target["disposition"] != "no_physical_size_improvement":
        return {"selection": {"disposition": "no_limiting_T6_edge"}}
    requests = protected_size_requests(predecessor)
    choice = use_neighbor(front,target,requests)
    if protect_neighbor and choice["disposition"] == "eligible":
        a,b,c,d = choice["blocks"][1]
        request = dict(site=[(a+c)/2,(b+d)/2],h=min(p["h"] for p in requests))
        choice = use_neighbor(front,target,[*requests,request])
    region = [uv[i] for i in faces[limiting]]
    if cross2(*region) < 0:
        region.reverse()
    return dict(selection=choice, target=target, region=region, requests=requests,
                predecessor_front=sha256((front_dir/"front.json").read_bytes()).hexdigest(),
                predecessor_birth=sha256(birth.read_bytes()).hexdigest())


def arc_lengths(evaluate):
    out=[]
    for side in range(4):
        def speed(t):
            uv=((t,0),(1,t),(t,1),(0,t))[side]
            return norm(evaluate(*uv)[1+side%2])
        def integrate(n):
            return (speed(0)+speed(1)+sum(speed(j/n)*(4 if j%2 else 2) for j in range(1,n)))/(3*n)
        a,b=integrate(1024),integrate(2048)
        assert abs(a-b)<2e-10
        out.append(b)
    return out
