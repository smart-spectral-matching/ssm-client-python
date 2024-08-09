#!/usr/bin/env python

"""Tests for `ssm_client` package."""

import pytest
import requests
import requests_mock  # noqa: F401

from ssm_client import SSMRester
from ssm_client.containers import CollectionContainer


@pytest.fixture
def ssm_rester(base_url):
    ssm_rester = SSMRester(hostname=base_url)
    yield ssm_rester
    for collection in ssm_rester.collection.get_collections():
        ssm_rester.collection.delete_by_title(collection)


def test_collection_create(ssm_rester, base_url,): #requests_mock):  # noqa: F811
    """Test creating collection w/ client"""
    title = 64 * "X"
    uri = f"{base_url}/{title}"
    json = {'title': title}

    #requests_mock.post(ssm_rester.collection._endpoint(), json=json)
    collection = ssm_rester.collection.create(title)
    assert len(collection.title) == 64
    assert collection.title.__contains__(collection.title.lower())


def test_dataset_read(ssm_rester, requests_mock):  # noqa: F811
    """Test read dataset w/ client"""
    title = "foo"
    uri = "bar"
    json = {'title': title, 'uri': uri}

    requests_mock.post(ssm_rester.dataset._endpoint(), json=json)
    dataset = ssm_rester.dataset.create(title)

    requests_mock.get(ssm_rester.dataset._endpoint(title), json=json)
    grabbed_dataset = ssm_rester.dataset.get_by_title(dataset.title)
    assert dataset == grabbed_dataset


def test_collection_delete(ssm_rester,): #requests_mock):  # noqa: F811
    """Test deleting dataset w/ client"""
    title = "foo"
    uri = "bar"
    json = {'title': title, 'uri': uri}

    #requests_mock.post(ssm_rester.dataset._endpoint(), json=json)
    collection = ssm_rester.collection.create(title)

    #requests_mock.get(ssm_rester.dataset._endpoint(title), json=json)
    grabbed_collection = ssm_rester.dataset.get_by_title(collection.title)
    assert collection == grabbed_collection

    #requests_mock.delete(ssm_rester.collection._endpoint(title))
    ssm_rester.collection.delete_by_title(collection.title)

    requests_mock.get(ssm_rester.collection._endpoint(title), status_code=404)
    with pytest.raises(requests.HTTPError):
        ssm_rester.collection.get_by_title(collection.title)


def test_initialize_model_for_dataset(ssm_rester):
    """Test initializing the model for a dataset"""
    dataset_title = 64 * "X"
    uri = "http://localhost/{}".format(dataset_title)
    dataset = CollectionContainer(title=dataset_title, uri=uri)
    ssm_rester.initialize_model_for_dataset(dataset)
    assert ssm_rester.model.hostname == ssm_rester.hostname
    assert ssm_rester.model.dataset_title == dataset_title
