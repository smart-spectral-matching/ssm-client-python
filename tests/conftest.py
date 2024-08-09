import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--base-url",
        default="http://localhost",
        help="Base url for Calatog API"
    )


@pytest.fixture
def base_url(request):
    return request.config.getoption("--base-url")
