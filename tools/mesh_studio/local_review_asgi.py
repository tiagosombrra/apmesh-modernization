"""Standalone, single-port static research reviewer (not a release server).

Only this ASGI entrypoint is used by V5.11; neither Vite dev/HMR nor the
unprotected legacy FastAPI entrypoint is exposed by the reviewer launcher.
"""

from .local_loopback_guard import LocalLoopbackGuard
from .local_static_site import StaticResearchASGI
from .web_api import app

local_review_app = LocalLoopbackGuard(
    StaticResearchASGI(app),
    allowed_origins=frozenset({b"http://127.0.0.1:8765"}),
)
