"""Fail-closed ASGI boundary for the opt-in local research launcher.

Legacy FastAPI tests still use the ordinary app. Only the V5.8+ launcher
serves local_app. This does not provide production authentication or hardening.
"""

from __future__ import annotations

from typing import Callable, Awaitable, Any

API_HOST = b"127.0.0.1:8765"
ALLOWED_ORIGINS = frozenset({
    b"http://127.0.0.1:5173",
    b"http://127.0.0.1:8765",
})
SAFE_FETCH_SITES = frozenset({b"same-origin", b"same-site", b"none"})
READ_ONLY_METHODS = frozenset({"GET", "HEAD", "OPTIONS"})
HARDENED_HEADERS = (
    (b"x-content-type-options", b"nosniff"),
    (b"x-frame-options", b"DENY"),
    (b"referrer-policy", b"no-referrer"),
    (b"cross-origin-resource-policy", b"same-origin"),
    (b"cache-control", b"no-store"),
)


def header_values(scope: dict, name: bytes) -> list[bytes]:
    """Return every raw occurrence to reject ambiguous proxy headers."""
    return [value for key, value in scope.get("headers", [])
            if key.lower() == name]


def rejection(status: int, message: bytes):
    """Return a fixed-size error without reflecting user input."""
    async def sender(send):
        headers = list(HARDENED_HEADERS)
        headers.extend(((b"content-type", b"text/plain; charset=utf-8"),
                        (b"content-length", str(len(message)).encode("ascii"))))
        await send({"type": "http.response.start",
                    "status": status, "headers": headers})
        await send({"type": "http.response.body", "body": message})
    return sender


class LocalLoopbackGuard:
    """Permit only the launcher-owned host, origins and read-only HTTP verbs."""

    def __init__(self, app: Callable[..., Awaitable[Any]]):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "websocket":
            await send({"type": "websocket.close", "code": 1008})
            return
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        hosts = header_values(scope, b"host")
        if hosts != [API_HOST]:
            await rejection(400, b"invalid_local_host")(send)
            return
        origins = header_values(scope, b"origin")
        if len(origins) > 1 or (origins and origins[0] not in ALLOWED_ORIGINS):
            await rejection(403, b"untrusted_local_origin")(send)
            return
        fetch_sites = header_values(scope, b"sec-fetch-site")
        if len(fetch_sites) > 1 or (fetch_sites and
                                   fetch_sites[0] not in SAFE_FETCH_SITES):
            await rejection(403, b"untrusted_fetch_site")(send)
            return
        if scope.get("method") not in READ_ONLY_METHODS:
            await rejection(405, b"local_research_api_is_read_only")(send)
            return

        async def protected_send(message):
            if message["type"] == "http.response.start":
                existing = {key.lower() for key, _ in message.get("headers", [])}
                message = {**message, "headers": list(message.get("headers", [])) +
                           [(key, value) for key, value in HARDENED_HEADERS
                            if key not in existing]}
            await send(message)

        await self.app(scope, receive, protected_send)
