"""Independent 8x8 UV topology preflight for the second source-error AFT band.

The dyadic model is an audit oracle, not native Quadtree execution,
original AFT reconstruction, physical mesh acceptance or an adaptive epoch.
"""

from collections import deque
from dataclasses import dataclass
from itertools import combinations
from math import isfinite

GRID = 8
COARSE = 4
# Level-2 cell (1,1) was refined in the original 19-leaf P1 tree;
# the first connected band then refined cells (0,0), (1,0), (0,1).
FIRST_BAND = frozenset({(1, 1), (0, 0), (1, 0), (0, 1)})
SECOND_SOURCE_SAMPLE = (0.8, 0.1)
NEIGHBORS = ((1, 0), (-1, 0), (0, 1), (0, -1))


@dataclass(frozen=True)
class BandTopology:
    selected: tuple
    leaves: int
    quad_uv_tiles: int
    uv_area: float
    connected: bool
    no_holes: bool
    vertex_manifold: bool

    @property
    def admitted_disk(self):
        return self.connected and self.no_holes and self.vertex_manifold


def source_coarse_cell(sample):
    """Find the measured physical AFT residual's level-2 source cell."""
    if len(sample) != 2 or not all(isfinite(x) and 0.0 < x < 1.0 for x in sample):
        raise ValueError("Source residual requires two finite interior UV coordinates")
    return (int(sample[0] * COARSE), int(sample[1] * COARSE))


def _eligible_tiles(subdivided):
    tiles = set()
    for x in range(COARSE):
        for y in range(COARSE):
            if (x, y) in subdivided:
                children = ((2*x + dx, 2*y + dy, 2*x + dx + 1, 2*y + dy + 1)
                            for dx in (0, 1) for dy in (0, 1))
            else:
                children = ((2*x, 2*y, 2*x + 2, 2*y + 2),)
            for x0, y0, x1, y1 in children:
                # Native CaptureLeafPolygons excludes source-boundary leaves.
                if x0 <= 0 or y0 <= 0 or x1 >= GRID or y1 >= GRID:
                    continue
                tiles.update((u, v) for u in range(x0, x1)
                             for v in range(y0, y1))
    return tiles


def _flood(tiles, seeds):
    visited = set()
    queue = deque(seeds)
    while queue:
        u, v = queue.popleft()
        if (u, v) not in tiles or (u, v) in visited:
            continue
        visited.add((u, v))
        queue.extend((u+du, v+dv) for du, dv in NEIGHBORS)
    return visited


def _vertex_link_manifold(tiles):
    # A diagonal-only pair creates a bow-tie at its central UV grid vertex.
    for x in range(1, GRID):
        for y in range(1, GRID):
            sw = (x-1, y-1) in tiles
            se = (x, y-1) in tiles
            nw = (x-1, y) in tiles
            ne = (x, y) in tiles
            if (sw and ne and not se and not nw) or (se and nw and not sw and not ne):
                return False
    return True


def inspect_band(extra_refinements=()):
    """Inspect actual source-cell coordinates in an independent dyadic surrogate."""
    chosen = tuple(sorted(extra_refinements))
    if len(set(chosen)) != len(chosen):
        raise ValueError("Repeated source cell refinement")
    if any(not (0 <= x < COARSE and 0 <= y < COARSE)
           or (x, y) in FIRST_BAND for x, y in chosen):
        raise ValueError("Invalid or already refined level-2 source cell")
    subdivided = FIRST_BAND | set(chosen)
    tiles = _eligible_tiles(subdivided)
    if not tiles:
        raise ValueError("Empty QUAD UV region")
    connected = _flood(tiles, [next(iter(tiles))]) == tiles
    complement = {(x, y) for x in range(GRID) for y in range(GRID)} - tiles
    exterior = {p for p in complement if 0 in p or GRID-1 in p}
    no_holes = _flood(complement, exterior) == complement
    # Each level-2 cell replaced by four level-3 leaves adds three leaves.
    return BandTopology(chosen, 16 + 3*len(subdivided), len(tiles),
                        len(tiles)/(GRID*GRID), connected, no_holes,
                        _vertex_link_manifold(tiles))


def candidate_bands(sample=SECOND_SOURCE_SAMPLE):
    """Enumerate source-local bridge subsets without choosing a physical policy."""
    origin = source_coarse_cell(sample)
    if origin in FIRST_BAND:
        raise ValueError("Error source cell has already been refined")
    neighbors = sorted((origin[0]+du, origin[1]+dv)
                       for du, dv in NEIGHBORS
                       if 0 <= origin[0]+du < COARSE
                       and 0 <= origin[1]+dv < COARSE
                       and (origin[0]+du, origin[1]+dv) not in FIRST_BAND)
    records = []
    for count in range(len(neighbors)+1):
        for extras in combinations(neighbors, count):
            records.append(inspect_band((origin,) + extras))
    return tuple(sorted(records, key=lambda r: (len(r.selected), r.selected)))
