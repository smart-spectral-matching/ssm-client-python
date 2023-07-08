#!/usr/bin/env python

"""Tests for DatasetService package."""

import pytest
import requests
import requests_mock  # noqa: F401

from ssm_client.services import DatasetService


@pytest.fixture
def dataset_service():
    return DatasetService()


def test_create(dataset_service, requests_mock):  # noqa: F811
    """Test creating dataset"""
    title = 64*"X"
    uri = "http://localhost/{}".format(title)
    json = {'title': title, 'uri': uri}

    requests_mock.post(dataset_service._endpoint(), json=json)
    dataset = dataset_service.create(title)
    assert len(dataset.title) == 64
    assert dataset.uri.__contains__(dataset.title)


def test_read(dataset_service, requests_mock):  # noqa: F811
    """Test read dataset"""
    title = "foo"
    uri = "bar"
    json = {'title': title, 'uri': uri}

    requests_mock.post(dataset_service._endpoint(), json=json)
    dataset = dataset_service.create(title)

    requests_mock.get(dataset_service._endpoint(title), json=json)
    grabbed_dataset = dataset_service.get_by_title(dataset.title)
    assert dataset == grabbed_dataset


def test_delete(dataset_service, requests_mock):  # noqa: F811
    """Test deleting dataset"""
    title = "foo"
    uri = "bar"
    json = {'title': title, 'uri': uri}

    requests_mock.post(dataset_service._endpoint(), json=json)
    dataset = dataset_service.create(title)

    requests_mock.get(dataset_service._endpoint(title), json=json)
    grabbed_dataset = dataset_service.get_by_title(dataset.title)
    assert dataset == grabbed_dataset

    requests_mock.delete(dataset_service._endpoint(title))
    dataset_service.delete_by_title(dataset.title)

    requests_mock.get(dataset_service._endpoint(title), status_code=404)
    with pytest.raises(requests.HTTPError):
        dataset_service.get_by_title(dataset.title)
