"""Offline local built reviewer checks; no synthetic C++ evidence admission."""

from __future__ import annotations

import asyncio
from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from .local_loopback_guard import LocalLoopbackGuard
from .local_static_site import (
    StaticResearchASGI, StaticReviewError, create_inventory,
    verify_inventory, validate_name, MANIFEST_NAME, WEB,
)
from .local_launcher import _source_imports


async def fake_local_api(scope, receive, send):
    await send({"type": "http.response.start", "status": 200,
                "headers": [(b"content-type", b"application/json")]})
    await send({"type": "http.response.body", "body": b'{"status":"READY"}'})


def _send_request(app, *, path="/", raw_path=None, method="GET",
                  headers=None):
    messages = []

    async def read():
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message):
        messages.append(message)

    scope = {
        "type": "http", "method": method, "path": path,
        "raw_path": raw_path if raw_path is not None else path.encode(),
        "headers": headers if headers is not None
        else [(b"host", b"127.0.0.1:8765")],
    }
    asyncio.run(app(scope, read, send))
    return messages


class StaticResearchPreviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory(prefix="v511-static-inventory-")
        self.root = Path(self.temp.name)
        (self.root / "assets").mkdir()
        (self.root / "index.html").write_bytes(
            b'<html><script src="/assets/app.js"></script></html>')
        (self.root / "bench.html").write_bytes(
            b'<html><script src="/assets/app.js"></script></html>')
        (self.root / "assets/app.js").write_bytes(b"/* built synthetic UI fixture */")
        (self.root / "assets/app.css").write_bytes(b"body { color: inherit; }")
        self.receipt = create_inventory(self.root)

    def tearDown(self):
        self.temp.cleanup()

    def make_app(self):
        return LocalLoopbackGuard(
            StaticResearchASGI(fake_local_api, self.root),
            allowed_origins=frozenset({b"http://127.0.0.1:8765"}),
        )

    def test_real_source_import_graph_of_static_app(self):
        result = _source_imports(entrypoint="local_review_asgi")
        self.assertEqual(result["external_imports"], ["fastapi"])
        self.assertIn("local_static_site", result["source_modules"])
        self.assertIn("web_api", result["source_modules"])

    def test_created_inventory_contains_only_exact_source_assets(self):
        self.assertEqual(self.receipt["static_asset_count"], 4)
        self.assertEqual(self.receipt["static_assets"]["assets/app.js"]["sha256"],
                         sha256(b"/* built synthetic UI fixture */").hexdigest())
        self.assertEqual(verify_inventory(self.root), self.receipt)
        self.assertFalse(self.receipt["native_cpp_recompiled"])
        self.assertFalse(self.receipt["scientific_lod_qualified"])

    def test_windows_vite_crcrlf_and_crlf_html_normalize_to_exact_lf(self):
        original_script_sha = self.receipt["static_assets"]["assets/app.js"]["sha256"]
        index = self.root / "index.html"
        bench = self.root / "bench.html"
        first, second = index.read_bytes(), bench.read_bytes()
        index.write_bytes(first + b"\r\r\n")
        bench.write_bytes(second + b"\r\n")
        canonical = create_inventory(self.root)
        self.assertEqual(index.read_bytes(), first + b"\n")
        self.assertEqual(bench.read_bytes(), second + b"\n")
        self.assertEqual(canonical["static_assets"]["assets/app.js"]["sha256"],
                         original_script_sha)
        self.assertEqual(verify_inventory(self.root), canonical)
        self.assertEqual(create_inventory(self.root), canonical)

    def test_malicious_path_names_fail_before_asset_read(self):
        for name in (".env", "../secret", "assets/../secret.js",
                     "assets//evil.js", "/root.js", "assets/evil.exe",
                     "assets/x%2f.js", "assets\\evil.js", "assets/.secrets.js"):
            with self.subTest(name=name), self.assertRaises(StaticReviewError):
                validate_name(name)

    def test_modified_asset_rejected_by_inventory_reaudit(self):
        (self.root / "assets/app.js").write_bytes(b"malicious")
        with self.assertRaisesRegex(StaticReviewError,
                                    "static_dist_asset_drift"):
            verify_inventory(self.root)

    def test_added_unindexed_file_rejected(self):
        (self.root / "assets/another.js").write_bytes(b"foreign")
        with self.assertRaisesRegex(StaticReviewError,
                                    "static_dist_asset_drift"):
            verify_inventory(self.root)

    def test_nested_symlink_rejected_even_with_matching_files(self):
        target = self.root / "assets" / "app.js"
        link = self.root / "assets" / "other.js"
        try:
            link.symlink_to(target)
        except (NotImplementedError, OSError):
            self.skipTest("host cannot create symlink")
        with self.assertRaisesRegex(StaticReviewError,
                                    "symlink_in_static_build"):
            verify_inventory(self.root)

    def test_inventory_lies_and_duplicate_json_keys_fail(self):
        manifest = self.root / MANIFEST_NAME
        payload = json.loads(manifest.read_bytes())
        payload["scientific_lod_qualified"] = True
        manifest.write_text(json.dumps(payload), encoding="utf-8")
        with self.assertRaisesRegex(StaticReviewError,
                                    "unsafe_static_inventory_claim"):
            verify_inventory(self.root)
        manifest.write_text('{"schema":1,"schema":2}', encoding="utf-8")
        with self.assertRaisesRegex(StaticReviewError,
                                    "duplicate_inventory_key"):
            verify_inventory(self.root)

    def test_same_origin_serves_exact_assets_and_api_only(self):
        app = self.make_app()
        page = _send_request(app)
        self.assertEqual(page[0]["status"], 200)
        self.assertIn(b"/assets/app.js", page[1]["body"])
        self.assertIn((b"x-frame-options", b"DENY"),
                      page[0]["headers"])
        asset = _send_request(app, path="/assets/app.js")
        self.assertEqual(asset[0]["status"], 200)
        self.assertEqual(asset[1]["body"], b"/* built synthetic UI fixture */")
        self.assertIn((b"content-type", b"text/javascript; charset=utf-8"),
                      asset[0]["headers"])
        api = _send_request(app, path="/api/v1/health")
        self.assertEqual(api[0]["status"], 200)
        self.assertIn(b"READY", api[1]["body"])
        head = _send_request(app, method="HEAD")
        self.assertEqual(head[0]["status"], 200)
        self.assertEqual(head[1]["body"], b"")

    def test_static_vite_hmr_and_unlisted_paths_rejected(self):
        app = self.make_app()
        for path in ("/@vite/client", "/src/main.tsx",
                     "/.apmesh-local-review-inventory.json",
                     "/node_modules/vite/bin/vite.js"):
            with self.subTest(path=path):
                self.assertEqual(_send_request(app, path=path)[0]["status"], 404)
        self.assertEqual(
            _send_request(app, path="/assets/../index.html")[0]["status"], 400)
        self.assertEqual(
            _send_request(app, path="/assets/%2e%2e/index.html",
                          raw_path=b"/assets/%2e%2e/index.html")[0]["status"], 400)

    def test_file_changed_after_server_instantiation_is_409(self):
        app = self.make_app()
        (self.root / "assets/app.js").write_bytes(b"forged")
        result = _send_request(app, path="/assets/app.js")
        self.assertEqual(result[0]["status"], 409)
        self.assertEqual(result[1]["body"], b"static_asset_integrity_failed")

    def test_static_reviewer_rejects_origin_from_dev_port(self):
        app = self.make_app()
        for origin in (b"http://127.0.0.1:5173",
                       b"https://untrusted.invalid", b"null"):
            with self.subTest(origin=origin):
                result = _send_request(app, headers=[
                    (b"host", b"127.0.0.1:8765"), (b"origin", origin)])
                self.assertEqual(result[0]["status"], 403)
        ok = _send_request(app, headers=[
            (b"host", b"127.0.0.1:8765"),
            (b"origin", b"http://127.0.0.1:8765")])
        self.assertEqual(ok[0]["status"], 200)


if __name__ == "__main__":
    unittest.main()
