"""Synthetic visualization wire-size preflight, never a real method benchmark."""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import math
from pathlib import Path
from time import perf_counter

from .scene_transport import pack_geometry, MAX_SCENE_BYTES


def synthetic_grid(cells: int) -> dict:
    """Create a bounded regular QUAD scene without claiming real APMesh output."""
    if type(cells) is not int or not 1 <= cells <= 500_000:
        raise ValueError('unsupported_benchmark_cell_count')
    width = int(math.sqrt(cells))
    height = math.ceil(cells / width)
    points = [[i / width, j / height, 0.0]
              for j in range(height + 1) for i in range(width + 1)]
    faces = []
    for y in range(height):
        for x in range(width):
            if len(faces) == cells:
                break
            a = y * (width + 1) + x
            faces.append([a, a+1, a+width+2, a+width+1])
    return {'schema':'apmesh.meshstudio.web.v1',
            'source_sha256': sha256(f'SYNTHETIC_TRANSPORT_SIZE_ONLY:{cells}'.encode()).hexdigest(),
            'source_patch_ownership':'NOT_APMESH_SOURCE', 'coordinate_space':'xyz',
            'points':points, 'cells':faces,'source_face_ids':list(range(cells)),
            'cell_types':['quad']*cells,'triangles':0,'quads':cells,
            'warning':'SYNTHETIC SIZE BENCHMARK ONLY — NOT APMESH GENERATOR EVIDENCE'}


def benchmark(cells: tuple[int, ...]) -> dict:
    result = []
    for count in cells:
        started = perf_counter()
        payload = synthetic_grid(count)
        construct = perf_counter() - started
        started = perf_counter()
        binary = pack_geometry(payload)
        packing = perf_counter() - started
        started = perf_counter()
        text = json.dumps(payload, separators=(',', ':'), allow_nan=False).encode('utf-8')
        json_time = perf_counter() - started
        result.append({'cells': count, 'points': len(payload['points']),
                       'binary_bytes': len(binary), 'json_bytes': len(text),
                       'wire_ratio_binary_to_json':round(len(binary)/len(text), 5),
                       'construction_s':round(construct, 4),
                       'binary_pack_s':round(packing, 4),
                       'json_encode_s':round(json_time, 4)})
    return {'schema':'apmesh.meshstudio.synthetic_transport_benchmark.v1',
            'not_scientific_generator_data':True,
            'not_browser_frame_rate_or_gpu_test':True,
            'max_binary_bytes':MAX_SCENE_BYTES,
            'results':result}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cells', nargs='+', type=int, default=[1000, 50000])
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    summary = benchmark(tuple(args.cells))
    result = json.dumps(summary, sort_keys=True, indent=2) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(result, encoding='utf-8')
    else:
        print(result, end='')


if __name__ == '__main__':
    main()
