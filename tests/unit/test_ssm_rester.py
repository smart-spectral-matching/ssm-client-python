#!/usr/bin/env python

"""Tests for `ssm_client` package."""

import pytest
import requests
import requests_mock  # noqa: F401

from ssm_client import SSMRester
from ssm_client.containers import CollectionContainer


@pytest.fixture
def ssm_rester():
    yield SSMRester()


def test_collection_create(ssm_rester, requests_mock):  # noqa: F811
    """Test creating collection w/ client"""
    title = 64 * "X"
    json = {'title': title.lower()}

    requests_mock.post(ssm_rester.collection._endpoint(), json=json)
    print(ssm_rester.collection)
    collection = ssm_rester.collection.create(title)
    assert len(collection.title) == 64
    assert collection.title.__contains__(collection.title.lower())


def test_collection_read(ssm_rester, requests_mock):  # noqa: F811
    """Test read collection w/ client"""
    title = "foo"
    uri = "bar"
    json = {'title': title, 'uri': uri}

    requests_mock.post(ssm_rester.collection._endpoint(), json=json)
    collection = ssm_rester.collection.create(title)

    requests_mock.get(ssm_rester.collection._endpoint(title), json=json)
    grabbed_collection = ssm_rester.collection.get_by_title(collection.title)
    assert collection == grabbed_collection


def test_collection_delete(ssm_rester, requests_mock):  # noqa: F811
    """Test deleting collection w/ client"""
    title = "foo"
    uri = "bar"
    json = {'title': title, 'uri': uri}

    requests_mock.post(ssm_rester.collection._endpoint(), json=json)
    collection = ssm_rester.collection.create(title)

    requests_mock.get(ssm_rester.collection._endpoint(title), json=json)
    grabbed_collection = ssm_rester.collection.get_by_title(collection.title)
    assert collection == grabbed_collection

    requests_mock.delete(ssm_rester.collection._endpoint(title))
    ssm_rester.collection.delete_by_title(collection.title)

    requests_mock.get(ssm_rester.collection._endpoint(title), status_code=404)
    with pytest.raises(requests.HTTPError):
        ssm_rester.collection.get_by_title(collection.title)


def test_initialize_dataset_for_collection(ssm_rester):
    """Test initializing the dataset for a collection"""
    collection_title = 64 * "X"
    uri = "http://localhost/{}".format(collection_title)
    collection = CollectionContainer(title=collection_title, uri=uri)
    ssm_rester.initialize_dataset_for_collection(collection)
    assert ssm_rester.dataset.hostname == ssm_rester.hostname
    assert ssm_rester.dataset.collection_title == collection_title
