"""Separate input changes from reduction-order changes in the real algorithm."""

from collections import Counter
import csv
import json
from itertools import zip_longest
from pathlib import Path

import argparse

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("first", type=Path)
parser.add_argument("second", type=Path)
parser.add_argument("--report", type=Path, required=True)
args = parser.parse_args()
a = csv.DictReader(args.first.open(encoding="utf-8"))
b = csv.DictReader(args.second.open(encoding="utf-8"))
counts = Counter()
first = []
visits=0
for x,y in zip_longest(a,b):
    if x is None or y is None:
        raise ValueError(f"Trace lengths differ at visit {visits}")
    visits+=1
    if [x[k] for k in ['call','step','patch','vertex']] != [y[k] for k in ['call','step','patch','vertex']]:
        raise ValueError(f'Unaligned vertex visit {visits}')
    nx = [n for n in x['neighbors'].split('|') if n]
    ny = [n for n in y['neighbors'].split('|') if n]
    same_inputs = x['old_x']==y['old_x'] and x['old_y']==y['old_y'] and sorted(nx)==sorted(ny)
    order_changed = nx != ny
    sum_changed = x['raw_x']!=y['raw_x'] or x['raw_y']!=y['raw_y']
    if order_changed: counts['ordered_neighbor_lists_differ']+=1
    if same_inputs and order_changed: counts['identical_inputs_different_order']+=1
    if same_inputs and order_changed and sum_changed:
        counts['identical_inputs_different_order_different_sum']+=1
        if len(first)<4: first.append({'first':x,'second':y})
result={'compared_vertex_visits':visits,'counts':dict(counts),'isolated_examples':first}
args.report.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps(result,indent=2))
