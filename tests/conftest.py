"""Pytest configuration for the browser tests."""

import urllib.error
import urllib.request

import pytest
from test_common.common import BASE_URL


@pytest.fixture(scope="session", autouse=True)
def documentation_server() -> None:
    """Fail fast when the documentation server is not reachable."""
    try:
        urllib.request.urlopen(BASE_URL, timeout=5)  # noqa: S310
    except (urllib.error.URLError, OSError) as error:
        pytest.exit(
            f"Documentation is not served at {BASE_URL} ({error}). "
            "Build and serve the docs, or set the ANSYS_THEME_TEST_PORT ",
            "environment variable to the desired port.",
            returncode=2,
        )
