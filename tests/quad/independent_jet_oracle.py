"""Independent tridiagonal/Sturm eigenvalue and Householder-QR jet audit.

The C++ estimator uses Jacobi eigen/SVD. This checker does not solve normal
equations or fit to analytical curvatures. Agreement bounds are instrument
checks, not scientific mesh/estimator acceptance thresholds.
"""
import math
import sys

from quad_generation_metrics import cross, dot, norm, delta


def close(a, b, tolerance=1e-7):
    if not math.isfinite(a) or not math.isfinite(b) or not math.isclose(a, b, rel_tol=tolerance, abs_tol=tolerance):
        raise ValueError('Independent jet numerical disagreement')


def eigenvalues3(c):
    """One Givens reduction, then indexed Sturm bisection; no Jacobi iteration.

    The previous acos cubic formula lost digits near a repeated spectrum,
    including a diagonal covariance. Scaling and pivot protection here are
    numerical safeguards for this reference, not new estimator thresholds.
    """
    scale = max(abs(x) for row in c for x in row)
    if scale == 0:
        return [0.0, 0.0, 0.0]
    a = [[x/scale for x in row] for row in c]
    radius = math.hypot(a[0][1], a[0][2])
    cosine, sine = (a[0][1]/radius, a[0][2]/radius) if radius else (1.0, 0.0)
    diagonal = [a[0][0],
                cosine*cosine*a[1][1]+2*cosine*sine*a[1][2]+sine*sine*a[2][2],
                sine*sine*a[1][1]-2*cosine*sine*a[1][2]+cosine*cosine*a[2][2]]
    off = [radius, cosine*sine*(a[2][2]-a[1][1])+(cosine*cosine-sine*sine)*a[1][2]]
    radii = [abs(off[0]), abs(off[0])+abs(off[1]), abs(off[1])]
    lower = math.nextafter(min(d-r for d,r in zip(diagonal,radii)), -math.inf)
    upper = math.nextafter(max(d+r for d,r in zip(diagonal,radii)), math.inf)
    pivot_floor = 16*sys.float_info.min

    def count_below(x):
        pivot = diagonal[0]-x
        if abs(pivot) < pivot_floor:
            pivot = -pivot_floor
        count = int(pivot < 0)
        for i in (1,2):
            pivot = diagonal[i]-x-off[i-1]*off[i-1]/pivot
            if abs(pivot) < pivot_floor:
                pivot = -pivot_floor
            count += int(pivot < 0)
        return count

    result = []
    for index in range(3):
        lo, hi = lower, upper
        for _ in range(160):
            mid = lo+(hi-lo)/2
            if mid == lo or mid == hi:
                break
            if count_below(mid) <= index:
                lo = mid
            else:
                hi = mid
        result.append((lo+(hi-lo)/2)*scale)
    return result


def qr_solve(design, values):
    """Column-pivoted Householder QR; returns rank and the full-rank minimizer."""
    a = [list(row) for row in design]
    y = list(values)
    order = list(range(6))
    guard = max(len(a), 6)*sys.float_info.epsilon*math.sqrt(sum(x*x for row in a for x in row))
    rank = 0
    for k in range(6):
        column = max(range(k, 6), key=lambda j: math.hypot(*(a[i][j] for i in range(k, len(a)))))
        for row in a:
            row[k], row[column] = row[column], row[k]
        order[k], order[column] = order[column], order[k]
        v = [a[i][k] for i in range(k, len(a))]
        length = math.hypot(*v)
        if length <= guard:
            break
        rank += 1
        alpha = -math.copysign(length, v[0])
        v[0] -= alpha
        square = sum(x*x for x in v)
        for j in range(k, 6):
            beta = 2*sum(v[i-k]*a[i][j] for i in range(k, len(a)))/square
            for i in range(k, len(a)):
                a[i][j] -= beta*v[i-k]
        beta = 2*sum(v[i-k]*y[i] for i in range(k, len(a)))/square
        for i in range(k, len(a)):
            y[i] -= beta*v[i-k]
        a[k][k] = alpha
        for i in range(k+1, len(a)):
            a[i][k] = 0
    if rank != 6:
        return rank, None
    permuted = [0.0]*6
    for i in reversed(range(6)):
        permuted[i] = (y[i]-sum(a[i][j]*permuted[j] for j in range(i+1,6)))/a[i][i]
    result = [0.0]*6
    for i, column in enumerate(order):
        result[column] = permuted[i]
    return rank, result


def coface_support(faces, count, query, ring, neighbors=None):
    if neighbors is not None:
        first = neighbors[query] | {query}
        return sorted(first if ring == 1 else first | set().union(*(neighbors[i] for i in first)))
    neighbors = [set() for _ in range(count)]
    for face in faces:
        for i in face:
            neighbors[i].update(j for j in face if j != i)
    first = neighbors[query] | {query}
    return sorted(first if ring == 1 else first | set().union(*(neighbors[i] for i in first)))


def audit_records(xyz, normals, faces, records, required_ring=None):
    if len(records) != len(xyz):
        raise ValueError('Incomplete jet node inventory')
    maximum = dict(coefficient=0.0, K=0.0, H=0.0)
    neighbors = [set() for _ in xyz]
    edges = {}
    for face in faces:
        for i in face:
            neighbors[i].update(j for j in face if j != i)
        for a,b in zip(face,face[1:]+face[:1]):
            key=tuple(sorted((a,b)))
            edges[key]=edges.get(key,0)+1
    boundary={i for edge,uses in edges.items() if uses==1 for i in edge}
    for i, row in enumerate(records):
        if row['node'] != i or row['ring'] not in (1,2):
            raise ValueError('Foreign jet node or ring')
        if required_ring is not None and row['ring'] != required_ring:
            raise ValueError('Jet output violates the explicitly selected ring policy')
        if row['boundary'] != (i in boundary):
            raise ValueError('Incorrect jet boundary classification')
        expected = coface_support(faces, len(xyz), i, row['ring'], neighbors)
        if row['support'] != expected:
            raise ValueError('Jet stencil differs from the complete approved ring')
        available = row['status'] == 'available'
        if available != (row['K'] is not None and row['H'] is not None):
            raise ValueError('Jet unavailable value was fabricated or available value omitted')
        if not available:
            if row['K'] is not None or row['H'] is not None:
                raise ValueError('Unavailable jet has a curvature fallback')
            status = row['status']
            if status == 'insufficient_samples':
                if len(expected) >= 6 or row['ring'] != 2:
                    raise ValueError('Incorrect insufficient-samples outcome')
            elif status == 'duplicate_samples':
                if len({xyz[j] for j in expected}) == len(expected):
                    raise ValueError('Unexplained duplicate-samples outcome')
            elif status == 'rank_deficient':
                if row['rank'] is None or row['rank'] >= 6 or row['scale'] <= 0:
                    raise ValueError('Unexplained rank-deficient outcome')
                t1,t2,normal = [tuple(row[p+k] for k in ('x','y','z')) for p in ('t1','t2','n')]
                points = [tuple(x/row['scale'] for x in delta(xyz[j],xyz[i])) for j in expected]
                matrix = [(1,dot(p,t1),dot(p,t2),dot(p,t1)**2,dot(p,t1)*dot(p,t2),dot(p,t2)**2) for p in points]
                rank,_ = qr_solve(matrix,[dot(p,normal) for p in points])
                if rank == 6:
                    raise ValueError('Independent QR contradicts unavailable rank')
            elif status == 'ambiguous_frame':
                h = max(math.dist(xyz[j],xyz[i]) for j in expected)
                if h <= 0:raise ValueError('Ambiguous-frame outcome has no scale')
                points = [tuple(x/h for x in delta(xyz[j],xyz[i])) for j in expected]
                center = [sum(p[k] for p in points)/len(points) for k in range(3)]
                c = [[sum((p[a]-center[a])*(p[b]-center[b]) for p in points)/len(points) for b in range(3)] for a in range(3)]
                eigen = eigenvalues3(c)
                guard = max(len(points),3)*sys.float_info.epsilon*max(map(abs,eigen))
                if eigen[1]-eigen[0] > guard:
                    raise ValueError('Independent covariance contradicts unavailable frame')
            else:
                # An unexplained numerical failure must stop qualification, not
                # silently reduce the measured coverage of these regular archives.
                raise ValueError('Unverified unavailable outcome: '+status)
            continue
        if row['rank'] != 6 or row['converged'] != 1:
            raise ValueError('Available jet lacks a converged full-rank fit')
        close(row['rank_guard'], max(len(expected),6)*sys.float_info.epsilon*row['sigma_max'], 1e-15)
        if not row['sigma_min'] > row['rank_guard']:
            raise ValueError('Available jet contradicts singular-value rank guard')
        close(row['condition'],row['sigma_max']/row['sigma_min'],1e-12)
        h = max(math.dist(xyz[j], xyz[i]) for j in expected)
        close(row['scale'], h, 1e-12)
        points = [tuple(x/h for x in delta(xyz[j], xyz[i])) for j in expected]
        center = [sum(p[k] for p in points)/len(points) for k in range(3)]
        covariance = [[sum((p[a]-center[a])*(p[b]-center[b]) for p in points)/len(points) for b in range(3)] for a in range(3)]
        eigen = eigenvalues3(covariance)
        for k in range(3):
            close(row[f'eig{k}'], eigen[k], 1e-10)
        vectors = [tuple(row[p+k] for k in ('x','y','z')) for p in ('t1','t2','n')]
        t1, t2, normal = vectors
        for a in range(3):
            close(norm(vectors[a]), 1, 1e-10)
            for b in range(a):
                close(dot(vectors[a], vectors[b]), 0, 1e-10)
        for k in range(3):
            close(cross(t1,t2)[k], normal[k], 1e-10)
            close(sum(covariance[k][j]*normal[j] for j in range(3)), row['eig0']*normal[k], 1e-10)
        axis = min(range(3), key=lambda k: abs(normal[k]))
        projected = [float(k == axis)-normal[axis]*normal[k] for k in range(3)]
        for k in range(3):
            close(t1[k], projected[k]/norm(projected), 1e-10)
        design, values = [], []
        for point in points:
            x, y = dot(point,t1), dot(point,t2)
            design.append((1,x,y,x*x,x*y,y*y))
            values.append(dot(point,normal))
        rank, coefficients = qr_solve(design, values)
        if rank != 6:
            raise ValueError('Independent QR does not confirm full rank')
        for k, value in enumerate(coefficients):
            close(row[f'c{k}'], value)
            maximum['coefficient'] = max(maximum['coefficient'], abs(row[f'c{k}']-value))
        residual = math.sqrt(sum((sum(a*b for a,b in zip(p,coefficients))-v)**2 for p,v in zip(design,values)))
        close(row['residual'], residual, 1e-10)
        close(row['offset'], h*coefficients[0], 1e-10)
        p, q = coefficients[1:3]
        r, s, t = 2*coefficients[3]/h, coefficients[4]/h, 2*coefficients[5]/h
        d = 1+p*p+q*q
        gaussian = (r*t-s*s)/(d*d)
        mean = ((1+q*q)*r-2*p*q*s+(1+p*p)*t)/(2*d**1.5)
        fitted = [(normal[k]-p*t1[k]-q*t2[k])/math.sqrt(d) for k in range(3)]
        reference = [x/norm(normals[i]) for x in normals[i]]
        alignment = dot(fitted, reference)
        if alignment < 0:
            fitted = [-x for x in fitted];mean = -mean
        for k, name in enumerate(('fit_nx','fit_ny','fit_nz')):
            close(row[name], fitted[k])
        close(row['alignment'], abs(alignment))
        close(row['K'], gaussian);close(row['H'], mean)
        maximum['K'] = max(maximum['K'], abs(row['K']-gaussian))
        maximum['H'] = max(maximum['H'], abs(row['H']-mean))
    return maximum
