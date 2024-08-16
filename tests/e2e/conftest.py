import pytest

from ssm_client import SSMRester
from ssm_client.services import CollectionService


def pytest_addoption(parser):
    parser.addoption(
        "--base-url", default="http://localhost", help="Base url for Calatog API"
    )


@pytest.fixture
def base_url(request):
    return request.config.getoption("--base-url")


@pytest.fixture
def collection_service(base_url):
    collection_service = CollectionService(hostname=base_url)
    yield collection_service
    for collection in collection_service.get_collections():
        collection_service.delete_by_title(collection)


@pytest.fixture
def ssm_rester(base_url):
    ssm_rester = SSMRester(hostname=base_url)
    yield ssm_rester
    for collection in ssm_rester.collection.get_collections():
        ssm_rester.collection.delete_by_title(collection)
