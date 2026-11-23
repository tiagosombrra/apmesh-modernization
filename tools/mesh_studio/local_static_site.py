"""Source-inventoried static research UI served by the existing local API port.

No Vite development server, HMR runtime, raw source files, arbitrary filesystem
paths, browser CDN dependency, installer or original C++ execution are admitted.
The inventory protects post-build file tampering; it is not code-signing.
"""

from __future__ import annotations

from hashlib import sha256
import json
import mimetypes
from pathlib import Path, PurePosixPath
import re
from typing import Awaitable, Callable

from .dependency_lock_audit import ROOT

WEB = ROOT / "tools/mesh_studio/web"
DIST = WEB / "dist"
MANIFEST_NAME = ".apmesh-local-review-inventory.json"
SCHEMA = "apmesh.meshstudio.v511.static_research_inventory.v1"
MAX_FILES = 512
MAX_FILE_BYTES = 40_000_000
MAX_TOTAL_BYTES = 100_000_000
MAX_MANIFEST_BYTES = 200_000
SAFE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,220}$")
EXTENSIONS = frozenset({
    ".html", ".js", ".css", ".svg", ".ico", ".png", ".jpg", ".jpeg",
    ".gif", ".webp", ".woff", ".woff2", ".wasm",
})


class StaticReviewError(ValueError):
    """The local built preview lacks an exact verified inventory."""


def require(ok: bool, message: str) -> None:
    if not ok:
        raise StaticReviewError("v511_" + message)


def _sha(data: bytes) -> str:
    return sha256(data).hexdigest()


def validate_name(name: str) -> None:
    """Prohibit unindexed aliases, traversal, escape and hidden payload files."""
    path = PurePosixPath(name)
    require(
        type(name) is str and SAFE_NAME.fullmatch(name) is not None and
        not name.startswith("/") and not name.endswith("/") and
        all(part not in (".", "..") and not part.startswith(".")
            for part in path.parts) and
        path.suffix.lower() in EXTENSIONS and
        not ("\\" in name or "%" in name or "//" in name),
        "unsafe_static_filename",
    )


def _file_bytes(root: Path, name: str) -> bytes:
    validate_name(name)
    path = root.joinpath(*name.split("/"))
    require(path.is_file() and not path.is_symlink() and
            not any(parent.is_symlink() for parent in path.parents
                    if parent != root.parent and parent != root),
            "static_asset_missing_or_symlink:" + name)
    require(path.stat().st_size <= MAX_FILE_BYTES,
            "static_asset_oversized:" + name)
    return path.read_bytes()


def _scan_assets(root: Path) -> dict:
    require(root.is_dir() and not root.is_symlink(), "static_dist_missing")
    entries = list(root.rglob("*"))
    require(not any(p.is_symlink() for p in entries),
            "symlink_in_static_build")
    paths = [p for p in entries if p.is_file()]
    require(len(paths) <= MAX_FILES + 1, "too_many_static_assets")
    result = {}
    count = 0
    for path in sorted(paths):
        name = path.relative_to(root).as_posix()
        if name == MANIFEST_NAME:
            continue
        validate_name(name)
        body = _file_bytes(root, name)
        count += len(body)
        require(count <= MAX_TOTAL_BYTES, "static_total_bytes_exceeded")
        result[name] = {"size": len(body), "sha256": _sha(body)}
    require("index.html" in result and "bench.html" in result and
            any(k.endswith(".js") for k in result),
            "static_required_pages_or_scripts_missing")
    return result


def canonicalize_built_html(root: Path) -> None:
    """Normalize only Vite-emitted HTML newlines; leave JS/CSS/source untouched."""
    for name in ("index.html", "bench.html"):
        path = root / name
        require(path.is_file() and not path.is_symlink(),
                "canonical_html_missing:" + name)
        require(path.stat().st_size <= MAX_FILE_BYTES,
                "canonical_html_oversized:" + name)
        data = path.read_bytes()
        # Windows Vite may produce CRCRLF when HTML input is checked out CRLF.
        # Standardize the emitted text, without touching scientific source data.
        canonical = data.replace(b"\\r\\r\\n", b"\\n").replace(
            b"\\r\\n", b"\\n")
        require(b"\\r" not in canonical,
                "unexpected_html_carriage_return:" + name)
        if canonical != data:
            path.write_bytes(canonical)


def create_inventory(root: Path = DIST) -> dict:
    """Pin built artifacts only after the hash-locked npm production build."""
    canonicalize_built_html(root)
    assets = _scan_assets(root)
    lock = WEB / "package-lock.json"
    require(lock.is_file(), "npm_source_lock_missing")
    receipt = {
        "schema": SCHEMA,
        "classification": "LOCAL_STATIC_RESEARCH_REVIEW_NOT_PRODUCTION_DISTRIBUTION",
        "npm_source_lock_sha256": _sha(lock.read_bytes()),
        "static_asset_count": len(assets),
        "static_assets": dict(sorted(assets.items())),
        "vite_dev_server_required_to_serve": False,
        "native_cpp_recompiled": False,
        "scientific_lod_qualified": False,
        "physical_gpu_certified": False,
    }
    body = (json.dumps(receipt, indent=2, sort_keys=True, allow_nan=False) +
            "\n").encode("utf-8")
    require(len(body) <= MAX_MANIFEST_BYTES, "static_inventory_oversized")
    (root / MANIFEST_NAME).write_bytes(body)
    verify_inventory(root)
    return receipt


def verify_inventory(root: Path = DIST) -> dict:
    """Reopen every built byte and reject any additions or modified assets."""
    require(root.is_dir() and not root.is_symlink(), "static_dist_missing")
    manifest = root / MANIFEST_NAME
    require(manifest.is_file() and not manifest.is_symlink() and
            manifest.stat().st_size <= MAX_MANIFEST_BYTES,
            "static_inventory_missing")
    raw = manifest.read_bytes()

    def unique_pairs(pairs):
        values = {}
        for key, value in pairs:
            require(key not in values, "duplicate_inventory_key")
            values[key] = value
        return values

    record = json.loads(raw, object_pairs_hook=unique_pairs)
    require(record.get("schema") == SCHEMA and
            record.get("classification") ==
            "LOCAL_STATIC_RESEARCH_REVIEW_NOT_PRODUCTION_DISTRIBUTION" and
            record.get("vite_dev_server_required_to_serve") is False and
            record.get("native_cpp_recompiled") is False and
            record.get("scientific_lod_qualified") is False and
            record.get("physical_gpu_certified") is False,
            "unsafe_static_inventory_claim")
    lock = WEB / "package-lock.json"
    require(lock.is_file() and _sha(lock.read_bytes()) ==
            record.get("npm_source_lock_sha256"),
            "npm_source_lock_drift")
    current = _scan_assets(root)
    require(record.get("static_assets") == current and
            record.get("static_asset_count") == len(current),
            "static_dist_asset_drift")
    require({p.relative_to(root).as_posix() for p in root.rglob("*")
             if p.is_file()} == (set(current) | {MANIFEST_NAME}),
            "unindexed_static_inventory_file")
    return record


async def _respond(send, status: int, body: bytes,
                   content_type: bytes = b"text/plain; charset=utf-8",
                   head: bool = False):
    await send({"type": "http.response.start", "status": status,
                "headers": [
                    (b"content-type", content_type),
                    (b"content-length", str(len(body)).encode("ascii")),
                    (b"cache-control", b"no-store"),
                    (b"x-content-type-options", b"nosniff"),
                    (b"x-frame-options", b"DENY"),
                    (b"referrer-policy", b"no-referrer"),
                    (b"cross-origin-resource-policy", b"same-origin"),
                ]})
    await send({"type": "http.response.body",
                "body": b"" if head else body})


class StaticResearchASGI:
    """Serve exact-hash verified build assets; delegate only /api to FastAPI."""

    def __init__(self, api: Callable[..., Awaitable], root: Path = DIST):
        self.api = api
        self.root = root
        self.inventory = verify_inventory(root)

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.api(scope, receive, send)
            return
        path = scope.get("path", "")
        if path.startswith("/api/"):
            await self.api(scope, receive, send)
            return
        method = scope.get("method")
        if method not in ("GET", "HEAD"):
            await _respond(send, 405, b"local_static_read_only",
                           head=method == "HEAD")
            return
        raw_path = scope.get("raw_path", b"")
        if (type(path) is not str or not path.startswith("/") or
                len(path) > 240 or b"%" in raw_path or
                "\\" in path or "//" in path or
                any(part in (".", "..") for part in path.split("/"))):
            await _respond(send, 400, b"invalid_static_path")
            return
        name = "index.html" if path == "/" else path[1:]
        if name not in self.inventory["static_assets"]:
            await _respond(send, 404, b"static_asset_not_registered")
            return
        try:
            data = _file_bytes(self.root, name)
            row = self.inventory["static_assets"][name]
            require(row["size"] == len(data) and
                    row["sha256"] == _sha(data),
                    "static_asset_modified_after_start")
        except (OSError, StaticReviewError):
            await _respond(send, 409, b"static_asset_integrity_failed")
            return
        guessed = mimetypes.guess_type(name)[0] or "application/octet-stream"
        if name.endswith(".js"):
            guessed = "text/javascript"
        if guessed.startswith("text/") or guessed in ("image/svg+xml",):
            guessed += "; charset=utf-8"
        await _respond(send, 200, data, guessed.encode("ascii"),
                       head=method == "HEAD")
