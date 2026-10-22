"""Pytest configuration for the browser tests."""

from collections.abc import Iterator
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading

import pytest

DOCS_DIR = Path(__file__).resolve().parents[1] / "doc" / "_build" / "html"


class _QuietHandler(SimpleHTTPRequestHandler):
    """Serve files without logging every request."""

    def log_message(self, format: str, *args: object) -> None:
        """Silence the request log."""


@pytest.fixture(scope="session")
def base_url() -> Iterator[str]:
    """Serve the built documentation on a free port and return its URL.

    Overrides the ``base_url`` fixture of ``pytest-playwright``, so ``page.goto("/path")``
    resolves against the served documentation.
    """
    if not (DOCS_DIR / "index.html").is_file():
        pytest.exit(
            f"Documentation not found in {DOCS_DIR}. Build it with 'make -C doc html'.",
            returncode=2,
        )

    # Port 0 lets the operating system pick any free port.
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(_QuietHandler, directory=str(DOCS_DIR)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        server.server_close()
