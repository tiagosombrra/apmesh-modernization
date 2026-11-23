"""Run the read-only Mesh Studio locally with a source-hash-locked minimal API.

This is a developer/research loopback launcher, not a signed installer, a
production service, a real GPU test, or an original C++ science admission.
"""

from __future__ import annotations

import argparse
import ast
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import shutil
import signal
import socket
import subprocess
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from .dependency_lock_audit import (
    ROOT, HASH, PIN, DependencyLockError, audit_all, require,
)

WEB = ROOT / "tools/mesh_studio/web"
VENV = WEB / ".venv-local-readonly"
API_ADDRESS = "http://127.0.0.1:8765"
WEB_ADDRESS = "http://127.0.0.1:5173"
SOURCE_PYTHON = ROOT / "tools/mesh_studio"
MINIMAL = frozenset({
    "annotated-doc", "annotated-types", "anyio", "click", "fastapi",
    "h11", "idna", "pydantic", "pydantic-core", "starlette",
    "typing-extensions", "typing-inspection", "uvicorn",
})
EXCLUDED = frozenset({
    "pymupdf", "fitz", "vtk", "matplotlib", "pillow",
    "numpy", "reportlab", "pypdf", "httpx",
})
VENDOR_TOP = frozenset({"fastapi"})
PYTHON = (3, 13)
NODE_MAJOR = 22
NPM_MAJOR = 10
MAX_LOGICAL_BLOCK = 50_000


class LocalStudioError(RuntimeError):
    """A source, platform, installation or local-server boundary failed."""


def _canonical(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name.lower())


def _sha(raw: bytes) -> str:
    return sha256(raw).hexdigest()


def _platform_profile() -> str:
    if sys.platform.startswith("linux"):
        return "requirements-web-ci-linux-py313.lock"
    if sys.platform == "win32":
        return "requirements-web-ci-windows-py313.lock"
    raise LocalStudioError("unsupported_platform_without_python_hash_lock")


def _source_imports(root: Path = SOURCE_PYTHON) -> dict:
    """Fail if the local web API reaches an unreviewed third-party import."""
    stack = ["web_api"]
    seen = set()
    vendors = set()
    while stack:
        module = stack.pop()
        if module in seen:
            continue
        seen.add(module)
        file = root / (module.replace(".", "/") + ".py")
        require(file.is_file(), "source_api_module_missing:" + module)
        tree = ast.parse(file.read_text(encoding="utf-8"), filename=str(file))
        for item in ast.walk(tree):
            if isinstance(item, ast.Call) and (
                isinstance(item.func, ast.Name) and item.func.id == "__import__"
                or isinstance(item.func, ast.Attribute) and item.func.attr == "import_module"
            ):
                raise LocalStudioError("dynamic_import_requires_review:" + module)
            if isinstance(item, ast.ImportFrom):
                if item.level:
                    require(item.level == 1, "unreviewed_relative_package_depth")
                    submodule = item.module
                    if submodule is None:
                        for alias in item.names:
                            possible = root / (alias.name.replace(".", "/") + ".py")
                            if possible.is_file():
                                stack.append(alias.name)
                    elif (root / (submodule.replace(".", "/") + ".py")).is_file():
                        stack.append(submodule)
                    else:
                        raise LocalStudioError("local_source_import_unresolved:" + str(submodule))
                    continue
                top = (item.module or "").split(".")[0]
            elif isinstance(item, ast.Import):
                for alias in item.names:
                    top = alias.name.split(".")[0]
                    if top not in sys.stdlib_module_names:
                        vendors.add(top)
                continue
            else:
                continue
            if top and top not in sys.stdlib_module_names:
                vendors.add(top)
    require(vendors == VENDOR_TOP,
            "runtime_web_api_vendor_import_drift:" + ",".join(sorted(vendors)))
    return {"source_modules": sorted(seen), "external_imports": sorted(vendors)}


def _project_hash_lock(text: str, source_file_sha256: str) -> tuple[str, dict]:
    """Project a preaudited full hash lock to its minimal local API closure."""
    rows = list(PIN.finditer(text))
    selected = []
    selected_pins = {}
    for index, match in enumerate(rows):
        name = _canonical(match.group(1))
        if name not in MINIMAL:
            continue
        require(name not in selected_pins, "duplicate_runtime_package:" + name)
        end = rows[index + 1].start() if index + 1 < len(rows) else len(text)
        block = text[match.start():end].rstrip() + "\n"
        require(len(block) < MAX_LOGICAL_BLOCK and HASH.findall(block),
                "missing_minimal_dependency_hash:" + name)
        selected_pins[name] = match.group(2)
        selected.append(block)
    require(set(selected_pins) == MINIMAL,
            "minimal_dependency_closure_missing:" +
            ",".join(sorted(MINIMAL - set(selected_pins))))
    require("fastapi" in selected_pins and "uvicorn" in selected_pins and
            not EXCLUDED.intersection(selected_pins),
            "unqualified_minimal_web_dependency")
    header = ("# Generated from audited source lock; never edit dependency hashes.\n"
              "# Original source lock SHA256: " + source_file_sha256 + "\n"
              "# Research-only loopback API; PyMuPDF/VTK are excluded.\n")
    output = header + "".join(selected)
    return output, selected_pins


def source_preflight(root: Path = ROOT) -> tuple[str, dict]:
    """Audit upstream dependency locks and web imports before any installation."""
    require(sys.version_info[:2] == PYTHON, "python_3_13_required")
    original = audit_all(root)
    import_scope = _source_imports(root / "tools/mesh_studio")
    target = _platform_profile()
    lock_path = root / "tools/mesh_studio/locks" / target
    raw = lock_path.read_bytes()
    require(_sha(raw) == original["python"][target]["lock_sha256"],
            "audited_runtime_source_lock_changed")
    out, pins = _project_hash_lock(raw.decode("utf-8"), _sha(raw))
    return out, {
        "classification": "LOCAL_READ_ONLY_DEV_ONLY_NOT_DISTRIBUTION",
        "source_lock": target,
        "source_lock_sha256": _sha(raw),
        "minimal_python_packages": pins,
        "minimal_python_count": len(pins),
        "excluded_scientific_packages": sorted(EXCLUDED),
        "original_cpp_r2_8_lod_qualified": False,
        "native_cpp_replayed": False,
        "source_modules_audited": import_scope["source_modules"],
        "source_external_imports": import_scope["external_imports"],
    }


def _binary(name: str, windows: bool = False) -> str:
    filename = name + ".cmd" if windows and os.name == "nt" else name
    found = shutil.which(filename)
    if not found:
        raise LocalStudioError("required_tool_missing:" + filename)
    return found


def _check_node() -> dict:
    node = _binary("node")
    npm = _binary("npm", windows=True)
    def run_version(binary: str) -> str:
        r = subprocess.run([binary, "--version"], check=True,
                           capture_output=True, text=True, timeout=15)
        return r.stdout.strip()
    node_version = run_version(node)
    npm_version = run_version(npm)
    require(re.fullmatch(r"v22\.\d+\.\d+", node_version) is not None and
            re.fullmatch(r"10\.\d+\.\d+", npm_version) is not None,
            "node_22_npm_10_required")
    return {"node_executable": node, "npm_executable": npm,
            "node_version": node_version, "npm_version": npm_version}


def _venv_python() -> Path:
    return VENV / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def _run_command(argv: list[str], cwd: Path = ROOT) -> None:
    subprocess.run(argv, cwd=cwd, check=True)


def setup() -> dict:
    lock, receipt = source_preflight()
    binaries = _check_node()
    python = _venv_python()
    if not python.is_file():
        _run_command([sys.executable, "-m", "venv", str(VENV)])
    require(python.is_file() and (VENV / "pyvenv.cfg").is_file(),
            "isolated_python_virtualenv_missing")
    cfg = (VENV / "pyvenv.cfg").read_text(encoding="utf-8").lower()
    require("include-system-site-packages = false" in cfg,
            "unsafe_virtualenv_inherits_unreviewed_site_packages")
    lock_path = VENV / "original-audited-runtime-requirements.lock"
    lock_path.write_text(lock, encoding="utf-8", newline="\n")
    _run_command([str(python), "-m", "pip", "install",
                  "--disable-pip-version-check", "--require-hashes",
                  "-r", str(lock_path)])
    _run_command([str(python), "-m", "pip", "check"])
    _run_command([binaries["npm_executable"], "ci", "--ignore-scripts",
                  "--no-audit", "--no-fund"], cwd=WEB)
    _verify_runtime_install(python)
    receipt["install"] = "SUCCESS_WITH_REQUIRE_HASHES_AND_NPM_CI_IGNORE_SCRIPTS"
    receipt["derived_runtime_lock_sha256"] = _sha(lock.encode("utf-8"))
    return receipt


def _verify_runtime_install(python: Path) -> None:
    require(python.is_file(), "missing_local_python_environment")
    assert_script = (
        "from importlib import metadata\n"
        "import sys\n"
        "from pathlib import Path\n"
        "from fastapi import FastAPI\n"
        "from uvicorn import Config\n"
        "def norm(name): return name.lower().replace('_','-').replace('.','-')\n"
        "installed = {norm(d.metadata['Name']) for d in metadata.distributions()}\n"
        f"expected = {sorted(MINIMAL)!r}\n"
        f"excluded = {sorted(EXCLUDED)!r}\n"
        "assert set(expected) <= installed, ('missing_runtime_packages', set(expected)-installed)\n"
        "assert not set(excluded) & installed, ('unsafe_scientific_dependency_in_local_api', set(excluded)&installed)\n"
        "assert sys.version_info[:2] == (3, 13)\n"
        "print('LOCAL_API_ISOLATED_PACKAGES=' + str(len(expected)))\n"
    )
    _run_command([str(python), "-c", assert_script])
    require((WEB / "node_modules/vite/bin/vite.js").is_file(),
            "source_locked_vite_install_missing")


def _available(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        return sock.connect_ex(("127.0.0.1", port)) != 0


def _get_json(url: str) -> dict:
    with urlopen(url, timeout=6) as response:
        require(response.status == 200 and
                response.headers.get("Content-Type", "").startswith("application/json"),
                "incorrect_local_json_response")
        return json.load(response)


def _await_http(url: str, process: subprocess.Popen, timeout: float) -> None:
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        if process.poll() is not None:
            raise LocalStudioError("local_server_exited_before_ready:" + str(process.returncode))
        try:
            with urlopen(url, timeout=1) as response:
                if response.status == 200:
                    return
        except (OSError, URLError, TimeoutError):
            pass
        time.sleep(.20)
    raise LocalStudioError("local_server_health_timeout:" + url)


def _spawn(args: list[str], cwd: Path) -> subprocess.Popen:
    settings = {}
    if os.name == "nt":
        settings["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        settings["start_new_session"] = True
    return subprocess.Popen(args, cwd=cwd, **settings)


def _terminate(proc: subprocess.Popen) -> None:
    if proc.poll() is not None:
        return
    if os.name != "nt":
        os.killpg(proc.pid, signal.SIGTERM)
    else:
        proc.terminate()
    try:
        proc.wait(timeout=6)
    except subprocess.TimeoutExpired:
        if os.name != "nt":
            os.killpg(proc.pid, signal.SIGKILL)
        else:
            proc.kill()
        proc.wait(timeout=6)


def launch(mode: str) -> dict:
    require(mode in ("smoke", "serve"), "invalid_launcher_mode")
    _, receipt = source_preflight()
    binaries = _check_node()
    python = _venv_python()
    _verify_runtime_install(python)
    require(_available(8765) and _available(5173),
            "loopback_ports_already_in_use")
    processes: list[subprocess.Popen] = []
    try:
        api = _spawn([str(python), "-m", "uvicorn", "tools.mesh_studio.web_api:app",
                      "--host", "127.0.0.1", "--port", "8765"], ROOT)
        processes.append(api)
        _await_http(API_ADDRESS + "/api/v1/health", api, 35)
        ui = _spawn([binaries["node_executable"],
                     str(WEB / "node_modules/vite/bin/vite.js"),
                     "--host", "127.0.0.1", "--port", "5173", "--strictPort"], WEB)
        processes.append(ui)
        _await_http(WEB_ADDRESS + "/", ui, 35)
        health = _get_json(API_ADDRESS + "/api/v1/health")
        require(health.get("status") == "READY" and
                health.get("mode") == "READ_ONLY_LOCAL_RESEARCH",
                "api_not_read_only_research")
        proxy_health = _get_json(WEB_ADDRESS + "/api/v1/health")
        require(proxy_health == health, "vite_proxy_not_same_local_readonly_api")
        models = _get_json(API_ADDRESS + "/api/v1/models")
        entries = models.get("models", [])
        require({m["id"] for m in entries} == {"p1","band","west","north","both"} and
                all(m["accepted_adaptive_epochs"] == 0 for m in entries) and
                next(m for m in entries if m["id"] == "p1")["source_status"] ==
                "CONTROLLED_PHYSICAL_GENERATION" and
                all(m["source_status"] == "STAGED_UNACCEPTED"
                    for m in entries if m["id"] != "p1"),
                "unsafe_or_modified_staged_catalog")
        _get_json(API_ADDRESS + "/api/v1/models/p1/quality")
        with urlopen(API_ADDRESS + "/api/v1/models/p1/publication.svg",
                     timeout=20) as response:
            svg = response.read()
            require(response.status == 200 and
                    response.headers.get("X-Vector-Figure-SHA256") == _sha(svg) and
                    b"<svg" in svg and b"<image" not in svg,
                    "source_vector_export_missing_or_raster")
        for bad, status in (("/api/v1/models/no-such-model/quality", 404),
                            ("/api/v1/models/p1/geometry?space=invalid", 422)):
            try:
                urlopen(API_ADDRESS + bad, timeout=6)
            except HTTPError as err:
                require(err.code == status, "invalid_request_not_rejected")
            else:
                raise LocalStudioError("invalid_source_request_not_rejected")
        receipt["local_health"] = "PASS"
        receipt["source_catalog_count"] = len(entries)
        receipt["source_svg_sha256"] = _sha(svg)
        receipt["vite_proxy"] = "PASS"
        receipt["invalid_request_rejections"] = [404, 422]
        if mode == "serve":
            print("Mesh Studio research interface: " + WEB_ADDRESS, flush=True)
            print("Research backend: " + API_ADDRESS, flush=True)
            print("Press Ctrl+C to stop both local processes.", flush=True)
            while all(p.poll() is None for p in processes):
                time.sleep(.35)
            raise LocalStudioError("one_local_server_exited_unexpectedly")
        receipt["mode"] = "SMOKE_COMPLETE_PROCESSES_TERMINATED"
        return receipt
    finally:
        for proc in reversed(processes):
            _terminate(proc)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("preflight", "setup", "smoke", "serve"))
    args = parser.parse_args()
    if args.mode == "preflight":
        lock, report = source_preflight()
        _check_node()
        report["derived_runtime_lock_sha256"] = _sha(lock.encode("utf-8"))
    elif args.mode == "setup":
        report = setup()
    else:
        report = launch(args.mode)
    print("V58_LOCAL_READONLY_STUDIO=" + json.dumps(report, sort_keys=True),
          flush=True)


if __name__ == "__main__":
    main()
