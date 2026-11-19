"""Read-only both-diagonal Gaussian witness on archived builtin:curva_bezier meshes.

This experiment does not define a mixed global error or an adaptation criterion.
Boundary turning density is retained but excluded from Gaussian comparisons.
"""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import statistics
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tests/quad'))
from test_m4_real_model_hybrid import CONTROLS, basis, golden
from independent_common_grid import load_physical_obj
from quad_generation_metrics import cross, dot, norm


PROBE_SOURCE = r'''#include "typed_mixed_curvature.h"
#include <iomanip>
#include <iostream>
#include <string>

int main(int argc, char** argv) {
  using namespace apmesh::quad::research;
  try {
    if (argc != 2 || (std::string(argv[1]) != "02" && std::string(argv[1]) != "13"))
      throw std::invalid_argument("Expected diagonal 02 or 13");
    std::size_t n = 0, m = 0;
    if (!(std::cin >> n >> m) || n == 0 || m == 0 || n > 1000000 || m > 1000000)
      throw std::invalid_argument("Invalid diagnostic input size");
    std::vector<MixedPoint3> points(n);
    for (auto& p : points)
      for (auto& coordinate : p)
        if (!(std::cin >> coordinate))
          throw std::invalid_argument("Invalid diagnostic coordinate");
    std::vector<MixedFace> faces(m);
    for (auto& f : faces) {
      std::size_t arity = 0;
      if (!(std::cin >> arity) || (arity != 3 && arity != 4))
        throw std::invalid_argument("Invalid diagnostic face arity");
      f.resize(arity);
      for (auto& id : f)
        if (!(std::cin >> id))
          throw std::invalid_argument("Invalid diagnostic face vertex");
      if (arity == 4 && std::string(argv[1]) == "13")
        std::rotate(f.begin(), f.begin() + 1, f.end());
    }
    std::string extra;
    if (std::cin >> extra)
      throw std::invalid_argument("Trailing diagnostic input");
    const auto result = AuditMixedCurvature(points, faces);
    std::cout << std::setprecision(17);
    std::cout << "node,boundary,angle_sum,dual_area,defect,density\n";
    for (std::size_t i = 0; i < result.vertices.size(); ++i) {
      const auto& v = result.vertices[i];
      std::cout << i << ',' << v.boundary << ',' << v.incident_angle_sum << ','
                << v.barycentric_area << ',' << v.angle_defect << ','
                << v.angle_defect_density << '\n';
    }
  } catch (const std::exception& error) {
    std::cerr << error.what() << '\n';
    return 1;
  }
}
'''


def gaussian_from_derivatives(du, dv, duu, duv, dvv):
    """Smooth Gaussian curvature, without production clipping or FindUV."""
    normal = cross(du, dv)
    square = dot(normal, normal)
    if not math.isfinite(square) or square <= 0:
        raise ValueError("Singular analytical surface")
    value = (dot(normal, duu)*dot(normal, dvv)-dot(normal, duv)**2)/square**2
    if not math.isfinite(value):
        raise ValueError("Nonfinite analytical Gaussian curvature")
    return value


def source_gaussian(u, v, controls=CONTROLS):
    if not (0 <= u <= 1 and 0 <= v <= 1):
        raise ValueError("Foreign source parameter")
    bu, du = basis(u)
    bv, dv = basis(v)
    ddu = (6*(1-u), 18*u-12, 6-18*u, 6*u)
    ddv = (6*(1-v), 18*v-12, 6-18*v, 6*v)
    def derivative(a, b):
        return tuple(sum(a[i]*b[j]*controls[i][j][axis] for i in range(4) for j in range(4)) for axis in range(3))
    return gaussian_from_derivatives(derivative(du, bv), derivative(bu, dv), derivative(ddu, bv),
                                     derivative(du, dv), derivative(bu, ddv))


def independent_metric(xyz, faces, diagonal):
    """Existing P2b cosine-law/Heron construction, with both explicit diagonals."""
    if diagonal not in ('02', '13') or not xyz or not faces:
        raise ValueError("Invalid diagonal witness input")
    uses = {}
    for face in faces:
        if len(face) not in (3, 4) or len(set(face)) != len(face) or any(i < 0 or i >= len(xyz) for i in face):
            raise ValueError("Invalid diagonal witness face")
        for a, b in zip(face, face[1:]+face[:1]):
            uses.setdefault(tuple(sorted((a, b))), []).append((a, b))
    if any(len(v) > 2 or (len(v) == 2 and v[0] != v[1][::-1]) for v in uses.values()):
        raise ValueError("Invalid diagonal witness incidence")
    boundary = {i for edge, values in uses.items() if len(values) == 1 for i in edge}
    angles, areas = [0.0]*len(xyz), [0.0]*len(xyz)
    for face in faces:
        triples = ((0, 1, 2),) if len(face) == 3 else ((0, 1, 2), (0, 2, 3)) if diagonal == '02' else ((1, 2, 3), (1, 3, 0))
        for slots in triples:
            ids = [face[k] for k in slots]
            lengths = [math.dist(xyz[ids[1]], xyz[ids[2]]), math.dist(xyz[ids[0]], xyz[ids[2]]), math.dist(xyz[ids[0]], xyz[ids[1]])]
            semi = sum(lengths)/2
            product = semi*math.prod(semi-x for x in lengths)
            if not math.isfinite(product) or product <= 0 or min(lengths) <= 1e-14:
                raise ValueError("Collapsed diagonal witness subtriangle")
            area = math.sqrt(product)
            for k, i in enumerate(ids):
                opposite, a, b = lengths[k], lengths[(k+1) % 3], lengths[(k+2) % 3]
                cosine = (a*a+b*b-opposite*opposite)/(2*a*b)
                angles[i] += math.acos(max(-1.0, min(1.0, cosine)))
                areas[i] += area/3
    result = []
    for i, (angle, area) in enumerate(zip(angles, areas)):
        if area <= 1e-14:
            raise ValueError("Unused or degenerate diagonal witness node")
        defect = (math.pi if i in boundary else 2*math.pi)-angle
        result.append(dict(node=i, boundary=i in boundary, angle_sum=angle, dual_area=area, defect=defect, density=defect/area))
    if not math.isclose(sum(n['defect'] for n in result), 2*math.pi, abs_tol=1e-7):
        raise ValueError("Diagonal disk Gauss-Bonnet witness failed")
    return result


def native_metric(probe, xyz, faces, diagonal):
    data = f'{len(xyz)} {len(faces)}\n'
    data += ''.join(' '.join(map(repr, p))+'\n' for p in xyz)
    data += ''.join(' '.join(map(str, (len(f), *f)))+'\n' for f in faces)
    run = subprocess.run([str(probe), diagonal], input=data, capture_output=True, text=True, timeout=30)
    if run.returncode:
        raise ValueError('Native diagonal witness failed: '+run.stderr)
    import io
    rows = list(csv.DictReader(io.StringIO(run.stdout)))
    if len(rows) != len(xyz):
        raise ValueError('Incomplete native diagonal witness')
    result = []
    for i, row in enumerate(rows):
        if int(row['node']) != i or row['boundary'] not in ('0', '1'):
            raise ValueError('Foreign native diagonal witness node')
        item = {k: float(row[k]) for k in ('angle_sum', 'dual_area', 'defect', 'density')}
        if not all(math.isfinite(x) for x in item.values()):
            raise ValueError('Nonfinite native diagonal witness')
        result.append(dict(item, node=i, boundary=row['boundary'] == '1'))
    return result


def compare_mesh(path, probe):
    xyz, uv, faces = load_physical_obj(path)
    for p, at in zip(xyz, uv):
        if math.dist(p, golden(*at)[0]) > 2e-7*max(1, norm(p)):
            raise ValueError('Diagonal experiment requires builtin:curva_bezier')
    metrics = {}
    for diagonal in ('02', '13'):
        actual = native_metric(probe, xyz, faces, diagonal)
        oracle = independent_metric(xyz, faces, diagonal)
        for a, b in zip(actual, oracle):
            if a['node'] != b['node'] or a['boundary'] != b['boundary']:
                raise ValueError('Native/oracle topology mismatch')
            for key in ('angle_sum', 'dual_area', 'defect', 'density'):
                # Density amplifies cancellation at fine nodes; compare primitives too.
                if not math.isclose(a[key], b[key], rel_tol=1e-7, abs_tol=1e-7):
                    raise ValueError('Native/oracle diagonal metric mismatch: '+key)
        metrics[diagonal] = actual
    nodes = []
    for i, (a, b) in enumerate(zip(metrics['02'], metrics['13'])):
        analytical = source_gaussian(*uv[i])
        interior = not a['boundary']
        nodes.append(dict(node=i+1, u=uv[i][0], v=uv[i][1], boundary=a['boundary'], analytical_gaussian=analytical,
                          density_02=a['density'], density_13=b['density'], area_02=a['dual_area'], area_13=b['dual_area'],
                          abs_difference_02=abs(a['density']-analytical) if interior else None,
                          abs_difference_13=abs(b['density']-analytical) if interior else None,
                          diagonal_difference=abs(a['density']-b['density']) if interior else None))
    interior = [n for n in nodes if not n['boundary']]
    def summary(key):
        values = [n[key] for n in interior]
        return dict(count=len(values), maximum=max(values) if values else None, median=statistics.median(values) if values else None)
    return dict(file=path.name, sha256=hashlib.sha256(path.read_bytes()).hexdigest(), nodes=len(xyz),
                quads=sum(len(f) == 4 for f in faces), triangles=sum(len(f) == 3 for f in faces),
                interior_nodes=len(interior), boundary_nodes=len(xyz)-len(interior),
                absolute_difference_02=summary('abs_difference_02'), absolute_difference_13=summary('abs_difference_13'),
                diagonal_difference=summary('diagonal_difference'), per_node=nodes)


def compare_archive(archive, probe, output):
    archive, output = Path(archive).resolve(), Path(output).resolve()
    with (archive/'manifest.csv').open(encoding='utf-8') as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError('Empty diagonal source history')
    stages = []
    inputs = {archive/'manifest.csv': hashlib.sha256((archive/'manifest.csv').read_bytes()).hexdigest()}
    for row in rows:
        for scheme, name in (('TRI', 'tri_obj'), ('QUAD_TRI', 'quad_tri_obj')):
            path = (archive/row[name]).resolve()
            if path.parent != archive:
                raise ValueError('Foreign diagonal archive mesh')
            inputs[path] = hashlib.sha256(path.read_bytes()).hexdigest()
            stage = compare_mesh(path, probe)
            stage.update({k: row[k] for k in ('step', 'epoch', 'retry', 'domain_generation', 'reference_tri_accepted', 'reason')})
            stage['scheme'] = scheme
            stages.append(stage)
    if not all(hashlib.sha256(p.read_bytes()).hexdigest() == h for p, h in inputs.items()):
        raise ValueError('Diagonal experiment mutated archived input')
    report = dict(schema='apmesh.quad.diagonal_curvature.v1', source='builtin:curva_bezier', stages=stages,
                  inputs_sha256={p.name: h for p, h in inputs.items()},
                  scope='Interior Gaussian angle-defect density diagnostic, inverse squared model units. Boundary turning density is not Gaussian error. Both diagonals use identical nodes. Different meshes have different node sites; no cross-mesh convergence/superiority or mixed-global-error claim.',
                  native_probe_sha256=hashlib.sha256(Path(probe).read_bytes()).hexdigest(),
                  mixed_global_curvature_error=None, accepted_mixed_adaptive_epochs=0)
    output.mkdir(parents=True, exist_ok=False)
    (output/'comparison.json').write_text(json.dumps(report, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    with (output/'nodes.csv').open('w', newline='', encoding='utf-8') as handle:
        identity = ['step', 'epoch', 'retry', 'domain_generation', 'reference_tri_accepted', 'reason', 'scheme', 'file', 'sha256']
        writer = csv.DictWriter(handle, identity+list(stages[0]['per_node'][0]))
        writer.writeheader()
        for stage in stages:
            for node in stage['per_node']:
                writer.writerow(dict({k: stage[k] for k in identity}, **node))
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-probe', type=Path)
    parser.add_argument('--archive', type=Path)
    parser.add_argument('--probe', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.write_probe:
        with args.write_probe.open('x', encoding='utf-8', newline='\n') as handle:
            handle.write(PROBE_SOURCE)
    elif args.archive and args.probe and args.output:
        report = compare_archive(args.archive, args.probe, args.output)
        print(json.dumps(dict(stages=len(report['stages']), status='written')))
    else:
        parser.error('Provide --write-probe or --archive, --probe and --output')


if __name__ == '__main__':
    main()
