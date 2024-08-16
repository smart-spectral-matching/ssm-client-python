#!/usr/bin/env python

"""Tests for DatasetService package."""

import pytest
import requests
import requests_mock  # noqa: F401

from ssm_client.services import CollectionService


@pytest.fixture
def collection_service():
    return CollectionService()


def test_create(collection_service, requests_mock):  # noqa: F811
    """Test creating collection"""
    title = 64*"X"
    uri = "http://localhost/{}".format(title)
    json = {'title': title, 'uri': uri}

    requests_mock.post(collection_service._endpoint(), json=json)
    collection = collection_service.create(title)
    assert len(collection.title) == 64
    assert collection.uri.__contains__(collection.title)


def test_read(collection_service, requests_mock):  # noqa: F811
    """Test read collection"""
    title = "foo"
    uri = "bar"
    json = {'title': title, 'uri': uri}

    requests_mock.post(collection_service._endpoint(), json=json)
    collection = collection_service.create(title)

    requests_mock.get(collection_service._endpoint(title), json=json)
    grabbed_collection = collection_service.get_by_title(collection.title)
    assert collection == grabbed_collection


def test_delete(collection_service, requests_mock):  # noqa: F811
    """Test deleting collection"""
    title = "foo"
    uri = "bar"
    json = {'title': title, 'uri': uri}

    requests_mock.post(collection_service._endpoint(), json=json)
    collection = collection_service.create(title)

    requests_mock.get(collection_service._endpoint(title), json=json)
    grabbed_collection = collection_service.get_by_title(collection.title)
    assert collection == grabbed_collection

    requests_mock.delete(collection_service._endpoint(title))
    collection_service.delete_by_title(collection.title)

    requests_mock.get(collection_service._endpoint(title), status_code=404)
    with pytest.raises(requests.HTTPError):
        collection_service.get_by_title(collection.title)
