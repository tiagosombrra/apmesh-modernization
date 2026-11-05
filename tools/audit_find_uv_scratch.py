"""Admit only the reviewed local FindUV scratch storage delta in historical guards."""

import hashlib
import re

from audit_find_uv_recording import compact

ORIGINAL_SHA256 = "6447f5105efe18f2e84b8a23917ae2b845d2d6c6a73d2611a3279b7fe3d69ddc"
DECLARATION = "std::array<std::array<double,3>,3>matrix;"


def restore_find_uv_scratch(text):
    """Reverse the storage syntax, then require the entire pinned previous solver."""
    source = compact(text)
    if DECLARATION not in source:
        return text
    starts = list(re.finditer(
        r"tuple\s*<\s*double\s*,\s*double\s*>\s+PatchBezier::FindUV"
        r"\s*\(\s*const\s+PointAdaptive&\s*point\s*\)\s*\{", text))
    if len(starts) != 1 or source.count(DECLARATION) != 1:
        raise ValueError("Ambiguous FindUV scratch declaration or function")
    start = starts[0].start()
    end = text.find("\n}", start)
    if end < 0:
        raise ValueError("Missing complete FindUV scratch scope")
    end += 2
    body = text[start:end]
    body, declarations = re.subn(
        r"std::array\s*<\s*std::array\s*<\s*double\s*,\s*3\s*>\s*,\s*3\s*>\s+matrix;",
        "Matrix<double, 3, 3> matrix;", body)
    body, swaps = re.subn(r"matrix\[([^\[\]]+)\]\.swap\(matrix\[([^\[\]]+)\]\)",
                         r"matrix.row(\1).swap(matrix.row(\2))", body)
    body, accesses = re.subn(r"matrix\[([^\[\]]+)\]\[([^\[\]]+)\]",
                            r"matrix(\1, \2)", body)
    if ((declarations, swaps, accesses) != (1, 2, 35)
            or hashlib.sha256(compact(body).encode()).hexdigest() != ORIGINAL_SHA256):
        raise ValueError("FindUV scratch changed beyond the pinned storage delta")
    return text[:start] + body + text[end:]
