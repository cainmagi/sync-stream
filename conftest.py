"""
Pytest configurations
=====================
@ Sync-stream

Author
------
Yuchen Jin
- cainmagi@gmail.com
- yjin4@uh.edu
"""

import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--slow",
        action="store_true",
        help=(
            "Enable the slow mode for tests. Some tests may require this mode for "
            "getting run correctly with Github Actions."
        ),
    )


@pytest.fixture(scope="session")
def is_slow(request):
    return request.config.getoption("--slow")
