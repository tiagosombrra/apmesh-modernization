"""Same-site independent Bernstein source-surface error audit for mixed physical OBJ.

This is a discrete 64x64 UV-grid metric, not a continuous error bound,
a physical finite-element solution error or a scientific acceptance policy.
It deliberately does not use the C++/native element interpolators.
"""
import math

from test_m4_real_model_hybrid import golden


def load_physical_obj(path):
    xyz, uv, faces = [], [], []
    for line in path.read_text(encoding="ascii").splitlines():
        words = line.split()
        if not words:
            continue
        if words[0] == "v":
            xyz.append(tuple(map(float, words[1:])))
        elif words[0] == "vt":
            uv.append(tuple(map(float, words[1:])))
        elif words[0] == "f":
            faces.append(tuple(int(value.split("/")[0])-1 for value in words[1:]))
    if not xyz or len(xyz) != len(uv) or not faces:
        raise ValueError("Empty or inconsistent physical OBJ source")
    for f in faces:
        if len(f) not in (3, 4) or len(set(f)) != len(f) or any(i < 0 or i >= len(uv) for i in f):
            raise ValueError("Non-TRI/QUAD, repeated or foreign physical OBJ face")
    if any(not all(math.isfinite(x) for x in p) for p in xyz+uv):
        raise ValueError("Nonfinite physical OBJ source coordinate")
    return xyz, uv, faces


def barycentric(xy, a, b, c):
    denominator = (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
    if denominator <= 1e-15:
        raise ValueError("Invalid source TRI determinant")
    q = ((xy[0]-a[0])*(c[1]-a[1])-(xy[1]-a[1])*(c[0]-a[0])) / denominator
    r = ((b[0]-a[0])*(xy[1]-a[1])-(b[1]-a[1])*(xy[0]-a[0])) / denominator
    return (1-q-r, q, r)


def inverse_bilinear(uv, xy):
    # Solve the genuine four-node UV bilinear inverse without splitting QUAD.
    (x0,y0),(x1,y1),(x2,y2),(x3,y3) = uv
    a = (x1-x0, y1-y0)
    b = (x3-x0, y3-y0)
    c = (x0-x1+x2-x3, y0-y1+y2-y3)
    s = t = 0.5
    converged = False
    for _ in range(30):
        f = (x0+s*a[0]+t*b[0]+s*t*c[0]-xy[0],
             y0+s*a[1]+t*b[1]+s*t*c[1]-xy[1])
        ds = (a[0]+t*c[0], a[1]+t*c[1])
        dt = (b[0]+s*c[0], b[1]+s*c[1])
        determinant = ds[0]*dt[1]-ds[1]*dt[0]
        if not math.isfinite(determinant) or abs(determinant) <= 1e-16:
            raise ValueError("Degenerate physical QUAD UV inversion")
        delta_s = (f[0]*dt[1]-f[1]*dt[0])/determinant
        delta_t = (ds[0]*f[1]-ds[1]*f[0])/determinant
        s -= delta_s
        t -= delta_t
        if max(abs(delta_s),abs(delta_t)) < 1e-14:
            converged = True
            break
    mismatch = max(abs(x0+s*a[0]+t*b[0]+s*t*c[0]-xy[0]),
                   abs(y0+s*a[1]+t*b[1]+s*t*c[1]-xy[1]))
    if not converged or not -1e-8 <= s <= 1+1e-8 or \
            not -1e-8 <= t <= 1+1e-8 or mismatch > 1e-10:
        raise ValueError("Physical QUAD UV inverse did not converge")
    return ((1-s)*(1-t), s*(1-t), s*t, (1-s)*t)


def common_grid_source_error(path, grid=64):
    """Return uniform-UV and Bernstein-Jacobian-weighted error on fixed sites."""
    if grid < 4 or grid > 256:
        raise ValueError("Unsupported independent source quadrature grid")
    xyz, uv, faces = load_physical_obj(path)
    boxes = []
    for face in faces:
        points = [uv[index] for index in face]
        boxes.append((points, min(p[0] for p in points), max(p[0] for p in points),
                      min(p[1] for p in points), max(p[1] for p in points)))
    total_squared = 0.0
    total_weighted_squared = 0.0
    total_jacobian = 0.0
    maximum = 0.0
    type_points = {"TRI": 0, "QUAD": 0}
    for iy in range(grid):
        v = (iy+0.5)/grid
        for ix in range(grid):
            u = (ix+0.5)/grid
            face_index = None
            for i, (polygon, x0, x1, y0, y1) in enumerate(boxes):
                if not x0-1e-13 <= u <= x1+1e-13 or \
                        not y0-1e-13 <= v <= y1+1e-13:
                    continue
                # All admitted native UV faces are convex and CCW. Reject a
                # hole by requiring an actual containing face for every site.
                if all((polygon[(k+1)%len(polygon)][0]-polygon[k][0])*(v-polygon[k][1]) -
                       (polygon[(k+1)%len(polygon)][1]-polygon[k][1])*(u-polygon[k][0])
                       >= -1e-12 for k in range(len(polygon))):
                    face_index = i
                    break
            if face_index is None:
                raise ValueError("Mixed source grid contains an uncovered UV site")
            face = faces[face_index]
            polygon = boxes[face_index][0]
            weights = barycentric((u,v), *polygon) if len(face) == 3 else \
                inverse_bilinear(polygon, (u,v))
            approximation = tuple(
                sum(w*xyz[index][axis] for w,index in zip(weights,face))
                for axis in range(3))
            exact, du, dv = golden(u, v)
            square = sum((a-b)**2 for a,b in zip(exact,approximation))
            cross = (du[1]*dv[2]-du[2]*dv[1],
                     du[2]*dv[0]-du[0]*dv[2],
                     du[0]*dv[1]-du[1]*dv[0])
            jacobian = math.sqrt(sum(z*z for z in cross))
            if not math.isfinite(square) or not math.isfinite(jacobian) or jacobian <= 0:
                raise ValueError("Nonfinite or degenerate source differential error")
            total_squared += square
            total_weighted_squared += square*jacobian
            total_jacobian += jacobian
            maximum = max(maximum, math.sqrt(square))
            type_points["QUAD" if len(face) == 4 else "TRI"] += 1
    count = grid*grid
    if sum(type_points.values()) != count or not all(type_points.values()):
        raise ValueError("Missing TRI or QUAD region on source grid")
    return {"source_grid": grid, "sample_count": count,
            "max_xyz": maximum,
            "rms_uv": math.sqrt(total_squared/count),
            "rms_source_area": math.sqrt(total_weighted_squared/total_jacobian),
            "quad_sites": type_points["QUAD"], "tri_sites": type_points["TRI"]}
