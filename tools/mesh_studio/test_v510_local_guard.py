"""Pure stdlib protocol tests for the local-only ASGI boundary.

These tests do not equate localhost header checks with production security.
"""

from __future__ import annotations

import asyncio
import unittest

from .local_loopback_guard import LocalLoopbackGuard, HARDENED_HEADERS


async def bare_asgi(scope, receive, send):
    """A deliberately generic downstream endpoint to inspect admission."""
    await send({"type": "http.response.start", "status": 200,
                "headers": [(b"content-type", b"application/json")]})
    await send({"type": "http.response.body", "body": b'{"status":"READY"}'})


def request(headers=None, method="GET", scope_type="http"):
    """Drive actual ASGI application with byte-faithful untrusted headers."""
    result = []
    scope = {
        "type": scope_type,
        "method": method,
        "headers": headers if headers is not None
        else [(b"host", b"127.0.0.1:8765")],
        "path": "/api/v1/health",
    }

    async def read():
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message):
        result.append(message)

    asyncio.run(LocalLoopbackGuard(bare_asgi)(scope, read, send))
    return result


class LocalGuardProtocolTests(unittest.TestCase):
    def test_real_launch_address_and_cors_origin_are_allowed(self):
        result = request([
            (b"host", b"127.0.0.1:8765"),
            (b"origin", b"http://127.0.0.1:5173"),
            (b"sec-fetch-site", b"same-origin"),
        ])
        self.assertEqual(result[0]["status"], 200)
        self.assertEqual(result[1]["body"], b'{"status":"READY"}')
        self.assertTrue(set(HARDENED_HEADERS) <=
                        set(result[0]["headers"]))

    def test_default_nonbrowser_cli_get_succeeds_without_origin(self):
        self.assertEqual(request()[0]["status"], 200)

    def test_wrong_or_missing_host_is_rejected_before_source_endpoint(self):
        for headers in (
            [],
            [(b"host", b"attacker.invalid:8765")],
            [(b"host", b"127.0.0.1:5173")],
            [(b"host", b"localhost:8765")],
            [(b"host", b"127.0.0.1:8765"),
             (b"host", b"attacker.invalid:8765")],
            [(b"host", b"127.0.0.1:8765"),
             (b"Host", b"127.0.0.1:8765")],
        ):
            with self.subTest(headers=headers):
                result = request(headers)
                self.assertEqual(result[0]["status"], 400)
                self.assertEqual(result[1]["body"], b"invalid_local_host")

    def test_external_or_duplicate_origin_rejected(self):
        for origins in (
            [b"https://attacker.invalid"],
            [b"null"],
            [b"http://localhost:5173"],
            [b"http://127.0.0.1:5173", b"http://127.0.0.1:5173"],
        ):
            with self.subTest(origins=origins):
                headers = [(b"host", b"127.0.0.1:8765")]
                headers.extend((b"origin", o) for o in origins)
                self.assertEqual(request(headers)[0]["status"], 403)

    def test_cross_site_fetch_metadata_rejected(self):
        for values in ([b"cross-site"], [b"cross-site", b"same-site"],
                       [b"unexpected"]):
            headers = [(b"host", b"127.0.0.1:8765")]
            headers.extend((b"sec-fetch-site", value) for value in values)
            self.assertEqual(request(headers)[0]["status"], 403)

    def test_post_put_patch_delete_never_reach_downstream(self):
        for method in ("POST", "PUT", "PATCH", "DELETE", "TRACE", "CONNECT"):
            with self.subTest(method=method):
                self.assertEqual(request(method=method)[0]["status"], 405)

    def test_guard_does_not_break_allowed_options_for_read_only_cors(self):
        self.assertEqual(request(method="OPTIONS")[0]["status"], 200)

    def test_websocket_is_not_an_available_local_backend(self):
        result = request(scope_type="websocket")
        self.assertEqual(result[0]["type"], "websocket.close")
        self.assertEqual(result[0]["code"], 1008)


if __name__ == "__main__":
    unittest.main()
