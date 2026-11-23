"""Single-port built local research STUDIO reviewer, without Vite dev/HMR.

Commands: build, preflight, smoke, original-smoke, serve. This is a local
research review mode, not an offline installer or production authentication.
"""

from __future__ import annotations

import argparse
from collections.abc import Callable
from hashlib import sha256
import json
import os
from pathlib import Path
import signal
import subprocess
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from . import local_launcher, local_static_site

BASE = local_launcher.API_ADDRESS
FIVE = {"p1", "band", "west", "north", "both"}


def require(value: bool, code: str):
    if not value:
        raise local_launcher.LocalStudioError("v511_" + code)


def preflight() -> dict:
    """Verify source locks, runtime API closure and every built file."""
    _, source = local_launcher.source_preflight()
    graph = local_launcher._source_imports(entrypoint="local_review_asgi")
    require(graph["external_imports"] == ["fastapi"] and
            "local_static_site" in graph["source_modules"] and
            "local_loopback_guard" in graph["source_modules"],
            "static_asgi_import_graph_changed")
    build = local_static_site.verify_inventory()
    require(build["npm_source_lock_sha256"] ==
            sha256((local_launcher.WEB / "package-lock.json").read_bytes()).hexdigest(),
            "npm_lock_source_drift")
    python = local_launcher._venv_python()
    local_launcher._verify_runtime_install(python)
    return {
        "schema": "apmesh.meshstudio.v511.static_local_reviewer.v1",
        "classification": "SINGLE_PORT_BUILT_RESEARCH_REVIEW_NOT_RELEASE",
        "static_assets": build["static_asset_count"],
        "inventory_sha256": sha256(
            (local_static_site.DIST / local_static_site.MANIFEST_NAME).read_bytes()
        ).hexdigest(),
        "npm_source_lock_sha256": build["npm_source_lock_sha256"],
        "python_source_lock_sha256": source["source_lock_sha256"],
        "minimal_python_runtime_packages": source["minimal_python_count"],
        "static_asgi_source_modules": graph["source_modules"],
        "vite_server_running": False,
        "vite_hmr_running": False,
        "native_cpp_recompiled": False,
        "scientific_lod_qualified": False,
        "physical_gpu_certified": False,
    }


def build() -> dict:
    """Run npm TypeScript/Vite production build, inventoring exact bytes."""
    source = local_launcher.setup()
    node = local_launcher._check_node()
    local_launcher._run_command([node["npm_executable"], "run", "build"],
                                cwd=local_launcher.WEB)
    result = local_static_site.create_inventory()
    require(result["static_asset_count"] > 2, "no_real_built_scripts")
    return {
        "schema": "apmesh.meshstudio.v511.static_research_build.v1",
        "built_asset_count": result["static_asset_count"],
        "source_npm_lock_sha256": result["npm_source_lock_sha256"],
        "sha256": sha256(
            (local_static_site.DIST / local_static_site.MANIFEST_NAME).read_bytes()
        ).hexdigest(),
        "minimal_python_runtime_packages": source["minimal_python_count"],
        "not_a_signed_or_offline_installer": True,
        "scientific_lod_qualified": False,
    }


def _request(path: str, *, headers: dict[str, str] | None = None,
             method: str = "GET"):
    return Request(BASE + path, headers=headers or {}, method=method,
                   data=b"" if method == "POST" else None)


def _negative(path: str, expected: int, *,
              headers: dict[str, str] | None = None,
              method: str = "GET") -> None:
    try:
        urlopen(_request(path, headers=headers, method=method), timeout=8)
    except HTTPError as error:
        require(error.code == expected,
                "unexpected_status:" + path + ":" + str(error.code))
    else:
        raise local_launcher.LocalStudioError(
            "v511_security_rejection_missing:" + path)


def _browser_review(directory: Path) -> None:
    from .v59_reviewer import _browser_review as browser
    browser(directory, base_url=BASE, include_static=True)


def smoke(mode: str, *, original_directory: Path | None = None,
          on_ready: Callable[[], None] | None = None) -> dict:
    require(mode in ("smoke", "serve"), "unknown_server_mode")
    if original_directory:
        from .v59_reviewer import preflight as cpp_preflight
        original = cpp_preflight(original_directory)
        require(original["source_cpp_raw_postcommit_reopened"] is True,
                "original_cpp_postcommit_reaudit_required")
    else:
        original = None
    receipt = preflight()
    require(local_launcher._available(8765) and
            local_launcher._available(5173),
            "another_research_server_already_running")
    proc = None
    try:
        proc = local_launcher._spawn(
            [str(local_launcher._venv_python()), "-m", "uvicorn",
             "tools.mesh_studio.local_review_asgi:local_review_app",
             "--host", "127.0.0.1", "--port", "8765"],
            local_launcher.ROOT,
        )
        local_launcher._await_http(BASE + "/api/v1/health", proc, 35)
        health = local_launcher._get_json(BASE + "/api/v1/health")
        require(health.get("status") == "READY" and
                health.get("mode") == "READ_ONLY_LOCAL_RESEARCH",
                "read_only_source_api_health_drift")
        with urlopen(_request("/"), timeout=10) as response:
            html = response.read()
            require(response.status == 200 and
                    response.headers.get("X-Frame-Options") == "DENY" and
                    b"/assets/" in html and
                    b"@vite/client" not in html,
                    "wrong_static_html_or_hmr_source")
        with urlopen(_request("/bench.html"), timeout=10) as response:
            require(response.status == 200 and b"/assets/" in response.read(),
                    "built_benchmark_html_missing")
        for name, expected in local_static_site.verify_inventory()["static_assets"].items():
            with urlopen(_request("/" + name), timeout=20) as response:
                data = response.read()
                require(response.status == 200 and
                        sha256(data).hexdigest() == expected["sha256"],
                        "served_static_asset_not_source_inventoried:" + name)
        listing = local_launcher._get_json(BASE + "/api/v1/models")
        require({x["id"] for x in listing["models"]} == FIVE and
                all(x["accepted_adaptive_epochs"] == 0
                    for x in listing["models"]),
                "built_ui_source_catalog_changed")
        with urlopen(_request("/api/v1/models/p1/publication.svg"),
                     timeout=20) as response:
            vector = response.read()
            require(response.headers["X-Vector-Figure-SHA256"] ==
                    sha256(vector).hexdigest() and b"<image" not in vector,
                    "original_source_vector_sha_drift")
        rejects = (
            ("/", 400, {"Host": "untrusted.invalid:8765"}, "GET"),
            ("/api/v1/health", 400,
             {"Host": "untrusted.invalid:8765"}, "GET"),
            ("/", 403, {"Origin": "http://127.0.0.1:5173"}, "GET"),
            ("/api/v1/health", 403,
             {"Origin": "https://attacker.invalid"}, "GET"),
            ("/", 403, {"Sec-Fetch-Site": "cross-site"}, "GET"),
            ("/api/v1/health", 403,
             {"Sec-Fetch-Site": "cross-site"}, "GET"),
            ("/", 405, {}, "POST"),
            ("/api/v1/health", 405, {}, "POST"),
            ("/@vite/client", 404, {}, "GET"),
            ("/src/main.tsx", 404, {}, "GET"),
            ("/assets/%2e%2e/index.html", 400, {}, "GET"),
        )
        for path, expected, headers, method in rejects:
            _negative(path, expected, headers=headers, method=method)
        with urlopen(_request("/api/v1/health",
                              headers={"Origin": BASE}), timeout=6) as response:
            require(response.status == 200 and
                    response.headers.get("Access-Control-Allow-Origin") == BASE,
                    "local_same_origin_api_rejected")
        require(local_launcher._available(5173),
                "unexpected_vite_listener_in_static_mode")
        receipt["source_catalog_count"] = len(listing["models"])
        receipt["guarded_live_http_negative_probes"] = len(rejects)
        receipt["original_p1_svg_sha256"] = sha256(vector).hexdigest()
        receipt["actual_static_browser_assets_rehashed"] = receipt["static_assets"]
        receipt["api_and_static_same_origin"] = BASE
        if mode == "serve":
            print("Built read-only research interface: " + BASE, flush=True)
            print("No Vite development/HMR server is launched.", flush=True)
            print("Press Ctrl+C to terminate the local research server.",
                  flush=True)
            while proc.poll() is None:
                time.sleep(.35)
            raise local_launcher.LocalStudioError(
                "static_local_server_exited_unexpectedly")
        if original_directory:
            _browser_review(original_directory)
            receipt["actual_cpp_original_reviewer_browser"] = "PASS"
            receipt["original_cpp_source_sha256"] = original[
                "source_exact_files_rehashed"
            ]["r2720-native-accepted-scene.json"]["sha256"]
        if on_ready is not None:
            on_ready()
            receipt["reviewer_callback"] = "PASS"
        receipt["both_local_ports_in_use"] = False
        receipt["mode"] = "STATIC_SMOKE_COMPLETE_AND_CLEANUP_REQUESTED"
        return receipt
    except KeyboardInterrupt:
        if mode != "serve":
            raise
        receipt["mode"] = "USER_STOPPED_SINGLE_STATIC_SERVER"
        return receipt
    finally:
        if proc is not None:
            local_launcher._terminate(proc)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=(
        "build", "preflight", "smoke", "original-smoke", "serve"))
    parser.add_argument("--corpus", type=Path)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    if args.mode == "build":
        result = build()
    elif args.mode == "preflight":
        result = preflight()
    else:
        if args.mode == "original-smoke":
            from .v59_reviewer import CORPUS
            corpus = args.corpus or CORPUS
        else:
            corpus = None
        result = smoke("serve" if args.mode == "serve" else "smoke",
                       original_directory=corpus)
    rendered = json.dumps(result, indent=2, sort_keys=True,
                          allow_nan=False) + "\n"
    if args.receipt:
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(rendered, encoding="utf-8", newline="\n")
    print("V511_SINGLE_PORT_RESEARCH_REVIEWER=" +
          json.dumps(result, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
