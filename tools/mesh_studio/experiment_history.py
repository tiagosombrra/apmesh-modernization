"""Strict synthetic experiment history for scientific visualization prototypes.

This reader intentionally refuses non-synthetic records: the V1 CSV has no
model hash, metric definition, hardware or acceptance provenance sufficient for
comparing actual source executions. A separate versioned real-data adapter is
required before such evidence can enter an article comparison.
"""

from __future__ import annotations

from collections import defaultdict
import csv
from dataclasses import dataclass
from hashlib import sha256
import io
import math
from pathlib import Path

HEADERS = ("dataset", "method", "epoch", "acceptance", "normalized_error",
           "elements", "shape_quality_median", "wall_seconds", "synthetic")
ALLOWED_METHODS = frozenset(("tri", "hybrid", "all_quad"))
MAX_CSV_BYTES = 64 * 1024
MAX_ROWS = 256


class HistoryError(ValueError):
    """A history row cannot support the claimed experimental semantics."""


@dataclass(frozen=True)
class SyntheticEpoch:
    dataset: str
    method: str
    epoch: int
    accepted: bool
    normalized_error: float
    elements: int
    shape_quality_median: float
    wall_seconds: float


def _integer(value: str, field: str) -> int:
    if not value.isdecimal():
        raise HistoryError(f"invalid_{field}")
    return int(value)


def _positive_number(value: str, field: str, *, at_most_one: bool = False) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise HistoryError(f"invalid_{field}") from exc
    if not math.isfinite(number) or number <= 0 or (at_most_one and number > 1):
        raise HistoryError(f"invalid_{field}")
    return number


def load_synthetic_history(path: Path | str) -> tuple[tuple[SyntheticEpoch, ...], str]:
    """Load deterministic mock events while refusing claims of real measurements."""
    source = Path(path)
    if source.stat().st_size > MAX_CSV_BYTES:
        raise HistoryError("history_file_too_large")
    raw = source.read_bytes()
    try:
        payload = raw.decode("utf-8")
    except UnicodeError as exc:
        raise HistoryError("invalid_history_encoding") from exc
    reader = csv.DictReader(io.StringIO(payload, newline=""), strict=True)
    if tuple(reader.fieldnames or ()) != HEADERS:
        raise HistoryError("invalid_history_columns")
    result: list[SyntheticEpoch] = []
    seen: set[tuple[str, str, int]] = set()
    for raw_row in reader:
        if len(result) >= MAX_ROWS:
            raise HistoryError("history_row_limit")
        if None in raw_row or not all(isinstance(v, str) for v in raw_row.values()):
            raise HistoryError("malformed_history_row")
        if raw_row["synthetic"] != "True":
            raise HistoryError("real_history_requires_provenance_schema")
        dataset = raw_row["dataset"]
        method = raw_row["method"]
        if not dataset or len(dataset) > 128 or method not in ALLOWED_METHODS:
            raise HistoryError("invalid_history_identity")
        acceptance = raw_row["acceptance"]
        if acceptance not in ("accepted", "rejected"):
            raise HistoryError("invalid_history_acceptance")
        epoch = _integer(raw_row["epoch"], "epoch")
        elements = _integer(raw_row["elements"], "elements")
        if elements == 0:
            raise HistoryError("invalid_elements")
        key = (dataset, method, epoch)
        if key in seen:
            raise HistoryError("duplicate_history_event")
        seen.add(key)
        result.append(SyntheticEpoch(
            dataset=dataset, method=method, epoch=epoch,
            accepted=acceptance == "accepted",
            normalized_error=_positive_number(raw_row["normalized_error"], "error"),
            elements=elements,
            shape_quality_median=_positive_number(raw_row["shape_quality_median"],
                                                   "shape_indicator", at_most_one=True),
            wall_seconds=_positive_number(raw_row["wall_seconds"], "wall_seconds"),
        ))
    if not result:
        raise HistoryError("empty_history")
    groups: dict[tuple[str, str], list[SyntheticEpoch]] = defaultdict(list)
    for event in result:
        groups[(event.dataset, event.method)].append(event)
    for events in groups.values():
        if len(events) < 2 or sorted(e.epoch for e in events) != list(range(len(events))):
            raise HistoryError("nonconsecutive_history_epochs")
        baseline = next(e for e in events if e.epoch == 0)
        if not baseline.accepted:
            raise HistoryError("missing_accepted_baseline")
    return tuple(sorted(result, key=lambda e: (e.dataset, e.method, e.epoch))), sha256(raw).hexdigest()


def summarize_synthetic_history(events: tuple[SyntheticEpoch, ...], source_sha256: str) -> dict:
    """Retain rejected events as attempts, not interpolated accepted epochs."""
    if len(source_sha256) != 64 or not all(c in "0123456789abcdef" for c in source_sha256):
        raise HistoryError("invalid_history_source_hash")
    groups: dict[tuple[str, str], list[SyntheticEpoch]] = defaultdict(list)
    for e in events:
        groups[(e.dataset, e.method)].append(e)
    outputs = []
    for (dataset, method), rows in sorted(groups.items()):
        accepted = sorted((e for e in rows if e.accepted), key=lambda e: e.epoch)
        rejected = sorted((e for e in rows if not e.accepted), key=lambda e: e.epoch)
        outputs.append({
            "dataset": dataset, "method": method,
            "accepted_epochs": [e.epoch for e in accepted],
            "rejected_candidate_epochs": [e.epoch for e in rejected],
            "accepted_error_values": [e.normalized_error for e in accepted],
            "rejected_error_values": [e.normalized_error for e in rejected],
            "accepted_nonmonotone_error_steps": [
                accepted[i].epoch for i in range(1, len(accepted))
                if accepted[i].normalized_error > accepted[i-1].normalized_error],
        })
    return {
        "schema": "apmesh.meshstudio.synthetic_history.v1",
        "source_csv_sha256": source_sha256,
        "evidence_kind": "SYNTHETIC_TEST_DATA_NOT_MEASURED",
        "metric_scope": "INVENTED_NORMALIZED_ERROR_NOT_CROSS_METHOD_CERTIFICATION",
        "rows": len(events), "groups": outputs,
        "rejected_candidates_not_accepted_epochs": True,
    }
