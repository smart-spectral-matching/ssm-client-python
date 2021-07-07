#!/usr/bin/env python

"""Tests for `ssm_rest_python_client` package."""

import pytest
import requests
import requests_mock  # noqa: F401

from ssm_rest_python_client import SSMRester
from ssm_rest_python_client.containers import DatasetContainer


@pytest.fixture
def ssm_rester():
    return SSMRester()


def test_dataset_create(ssm_rester, requests_mock):  # noqa: F811
    """Test creating dataset w/ client"""
    title = 64 * "X"
    uri = "http://localhost/{}".format(title)
    json = {'title': title, 'uri': uri}

    requests_mock.post(ssm_rester.dataset._endpoint(), json=json)
    dataset = ssm_rester.dataset.create(title)
    assert len(dataset.title) == 64
    assert dataset.uri.__contains__(dataset.title)


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


def test_dataset_delete(ssm_rester, requests_mock):  # noqa: F811
    """Test deleting dataset w/ client"""
    title = "foo"
    uri = "bar"
    json = {'title': title, 'uri': uri}

    requests_mock.post(ssm_rester.dataset._endpoint(), json=json)
    dataset = ssm_rester.dataset.create(title)

    requests_mock.get(ssm_rester.dataset._endpoint(title), json=json)
    grabbed_dataset = ssm_rester.dataset.get_by_title(dataset.title)
    assert dataset == grabbed_dataset

    requests_mock.delete(ssm_rester.dataset._endpoint(title))
    ssm_rester.dataset.delete_by_title(dataset.title)

    requests_mock.get(ssm_rester.dataset._endpoint(title), status_code=404)
    with pytest.raises(requests.HTTPError):
        ssm_rester.dataset.get_by_title(dataset.title)


def test_initialize_model_for_dataset(ssm_rester):
    """Test initializing the model for a dataset"""
    dataset_title = 64 * "X"
    uri = "http://localhost/{}".format(dataset_title)
    dataset = DatasetContainer(title=dataset_title, uri=uri)
    ssm_rester.initialize_model_for_dataset(dataset)
    assert ssm_rester.model.hostname == ssm_rester.hostname
    assert ssm_rester.model.dataset_title == dataset_title
