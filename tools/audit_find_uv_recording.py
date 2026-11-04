"""Normalize only the pinned FindUV diagnostic binding for historical source guards."""

import hashlib
import re
from pathlib import Path

HEADER = "include/data/patch/find_uv_statistics.h"
HEADER_SHA256 = "05b1984cb0d438f791476dd20d8ec3720690b2fe7e365ccad0a673ff2eebd97c"
CALL = "apmesh::diagnostics::RecordFindUvCall();"
EXIT = "apmesh::diagnostics::RecordFindUvImaxExit();"
INCLUDE = '#include"data/patch/find_uv_statistics.h"'


def compact(text):
    return re.sub(r"\s+", "", re.sub(r"//[^\n]*|/\*.*?\*/", "", text, flags=re.S))


def validate_find_uv_header(root, sources):
    """The normalizer is admitted only with the complete reviewed helper implementation."""
    if any("apmesh::diagnostics::RecordFindUv" in source for source in sources):
        header = Path(root) / HEADER
        if not header.is_file() or hashlib.sha256(header.read_bytes()).hexdigest() != HEADER_SHA256:
            raise ValueError("FindUV recording header differs from the reviewed implementation")


def restore_find_uv_recording(text):
    """Restore only one entry increment and one I_MAX increment in their original slots."""
    source = compact(text)
    if "apmesh::diagnostics::RecordFindUv" not in source:
        return text
    starts = [
        f"tuple<double,double>Patch{kind}::FindUV(constPointAdaptive&point){{{CALL}"
        for kind in ("Bezier", "Hermite")
    ]
    exit_slot = "if(iter>=I_MAX){constunsignedlonglonghit=" + EXIT
    if (source.count(CALL) != 1 or source.count(EXIT) != 1
            or source.count(INCLUDE) != 1 or source.count("externunsignedintI_MAX;") != 1
            or sum(source.count(start) for start in starts) != 1
            or source.count(exit_slot) != 1):
        raise ValueError("FindUV recording moved, duplicated or changed")
    # Keep preprocessor line boundaries for older guards that strip includes.
    restored = re.sub(r'^[ \t]*#include[ \t]*"data/patch/find_uv_statistics.h"[ \t]*\n',
                      '', text, count=1, flags=re.M)
    restored = re.sub(
        r'extern\s+unsigned\s+int\s+I_MAX\s*;',
        'extern unsigned int I_MAX;\n'
        'extern std::atomic<unsigned long long> FINDUV_TOTAL_CALLS;\n'
        'extern std::atomic<unsigned long long> FINDUV_IMAX_EXITS;', restored, count=1)
    restored = restored.replace(
        CALL, 'FINDUV_TOTAL_CALLS.fetch_add(1ULL, std::memory_order_relaxed);', 1)
    return restored.replace(
        EXIT, '1ULL + FINDUV_IMAX_EXITS.fetch_add(1ULL, std::memory_order_relaxed);', 1)
