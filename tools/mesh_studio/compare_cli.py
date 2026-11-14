"""Headless CLI for visually distinct synthetic topology and experiment fixtures."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .multi_model_publication import export_synthetic_comparison_bundle


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', required=True, type=Path)
    args = parser.parse_args()
    receipt = export_synthetic_comparison_bundle(args.output_dir)
    print(json.dumps({'status': 'PASS_SYNTHETIC_ONLY',
                      'output_dir': str(args.output_dir),
                      'source': receipt['evidence_kind'],
                      'mock_event_count': receipt['mock_event_count']},
                     sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
