"""Reproducible source-verified cold/warm HTTP-in-process research benchmark.

These timings are TestClient request durations, not network, user-to-paint or GPU.
Cold mode deliberately clears both caches; it is a cache-disabled proxy, NOT
a separate historical-commit experiment. Keep all source SHA checks enabled.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
import math
from pathlib import Path
import platform
import statistics
from time import perf_counter_ns
from typing import Any

from fastapi.testclient import TestClient

from . import web_api

SCHEMA = "apmesh.meshstudio.v5.cache_cold_warm_http_testclient.v1"
MAX_PAIRS = 100
VALID_ENDPOINTS = ("face", "quality")


def _percentile_nearest_rank(samples: list[float], proportion: float) -> float:
    if not samples or not 0.0 <= proportion <= 1.0:
        raise ValueError("invalid_benchmark_percentile")
    ordered = sorted(samples)
    return ordered[max(0, math.ceil(proportion * len(ordered)) - 1)]


def _summary(samples: list[float]) -> dict[str, float | int]:
    return {
        "count": len(samples),
        "p50_ms": statistics.median(samples),
        "p95_ms": _percentile_nearest_rank(samples, 0.95),
        "mean_ms": statistics.fmean(samples),
        "min_ms": min(samples),
        "max_ms": max(samples),
    }


def _clear() -> None:
    web_api._verified_document.cache_clear()
    web_api._verified_quality.cache_clear()


def _request(client: TestClient, uri: str) -> tuple[float, dict]:
    start = perf_counter_ns()
    response = client.get(uri)
    duration_ms = (perf_counter_ns() - start) / 1_000_000.0
    if response.status_code != 200:
        raise ValueError(f"original_source_benchmark_http_status_{response.status_code}")
    payload = response.json()
    if not isinstance(payload, dict):
        raise ValueError("invalid_source_benchmark_body")
    return duration_ms, payload


def measure(model: str, endpoint: str, pairs: int = 16) -> dict[str, Any]:
    """Alternate measurement order while retaining the same verified source."""
    if model not in web_api.CATALOG or endpoint not in VALID_ENDPOINTS:
        raise ValueError("unknown_original_source_or_endpoint")
    if type(pairs) is not int or pairs < 4 or pairs > MAX_PAIRS:
        raise ValueError("invalid_benchmark_sample_count")
    relative, status, source_sha = web_api.CATALOG[model]
    path = web_api.ROOT / relative
    if not path.is_file() or sha256(path.read_bytes()).hexdigest() != source_sha:
        raise ValueError("benchmark_source_sha_mismatch")
    uri = (f"/api/v1/models/{model}/faces/0" if endpoint == "face"
           else f"/api/v1/models/{model}/quality")
    elapsed: dict[str, list[float]] = {"cache_disabled_proxy": [],
                                      "warm_source_cache": []}
    recorded_orders: list[list[str]] = []
    baseline: dict | None = None
    try:
        with TestClient(web_api.app) as client:
            for pair in range(pairs):
                # Alternating order counters schedule effects without
                # pretending consecutive TestClient samples are independent.
                order = (("cache_disabled_proxy", "warm_source_cache")
                         if pair % 2 == 0 else
                         ("warm_source_cache", "cache_disabled_proxy"))
                recorded_orders.append(list(order))
                for mode in order:
                    _clear()
                    if mode == "warm_source_cache":
                        # Untimed request warms parsing and quality caches;
                        # each timed call still rehashes the original OBJ.
                        _, primed = _request(client, uri)
                        if primed.get("source_sha256") not in (None, source_sha):
                            raise ValueError("source_sha_mismatch_in_warmup")
                    duration_ms, payload = _request(client, uri)
                    if endpoint == "face":
                        if payload.get("source_sha256") != source_sha or payload.get("source_face_id") != 0:
                            raise ValueError("original_face_provenance_changed")
                    else:
                        if payload.get("source_sha256") != source_sha:
                            raise ValueError("original_quality_provenance_changed")
                    if baseline is None:
                        baseline = payload
                    elif payload != baseline:
                        raise ValueError("cache_changed_original_scientific_response")
                    elapsed[mode].append(duration_ms)
    finally:
        _clear()
    a = elapsed["cache_disabled_proxy"]
    b = elapsed["warm_source_cache"]
    return {
        "schema": SCHEMA,
        "classification": "ACTUAL_PINNED_ORIGINAL_OBJ_SOURCE_TESTCLIENT_CACHE_PROXY_NOT_GPU",
        "model": model,
        "source_status": status,
        "source_sha256": source_sha,
        "endpoint": uri,
        "pairs": pairs,
        "orders": recorded_orders,
        "cache_disabled_proxy": _summary(a),
        "warm_source_cache": _summary(b),
        "paired_cold_minus_warm_ms": _summary([cold - warm for cold, warm in zip(a, b)]),
        "raw_ms": elapsed,
        "equivalent_original_scientific_json": True,
        "caches_cleared_between_modes": True,
        "each_request_original_source_sha_rechecked": True,
        "scope": "IN_PROCESS_FASTAPI_TESTCLIENT_WALL_MS_NOT_NETWORK_OR_BROWSER_RENDER",
        "limitations": [
            "cache_disabled_proxy_is_not_historical_unmodified_code",
            "single_python_process_not_independent_replicates",
            "time_includes_TestClient_request_and_json_serialization",
            "no_TCP_tls_browser_event_to_paint_or_GPU",
            "staged_candidate_is_not_an_accepted_adaptive_epoch",
            "source_model_and_configuration_remain_unchanged",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--pairs", type=int, default=16)
    args = parser.parse_args()
    cases = [(m, e) for m in ("p1", "band") for e in VALID_ENDPOINTS]
    rows = [measure(model, endpoint, pairs=args.pairs) for model, endpoint in cases]
    receipt = {
        "schema": "apmesh.meshstudio.v5.cache_benchmark_receipt.v1",
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "source_catalog_cases": rows,
        "source_models_distinct": ["p1", "band"],
        "physical_GPU_qualified": False,
        "numerical_acceptance_changed": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n",
                           encoding="utf-8")
    print("V5_SOURCE_VERIFIED_CACHE_BENCHMARK=" + json.dumps({
        f"{row['model']}.{row['endpoint'].split('/')[-1]}": {
            "cold_p50_ms": round(row["cache_disabled_proxy"]["p50_ms"], 4),
            "warm_p50_ms": round(row["warm_source_cache"]["p50_ms"], 4),
            "cold_p95_ms": round(row["cache_disabled_proxy"]["p95_ms"], 4),
            "warm_p95_ms": round(row["warm_source_cache"]["p95_ms"], 4),
            "pair_count": row["pairs"],
        } for row in rows
    }, sort_keys=True))


if __name__ == "__main__":
    main()
