#!/usr/bin/env python

"""Tests for DatasetService package."""

import pytest
import requests
import requests_mock  # noqa: F401

from ssm_rest_python_client.services import DatasetService


@pytest.fixture
def dataset_service():
    return DatasetService()


def test_create(dataset_service, requests_mock):  # noqa: F811
    """Test creating dataset"""
    uuid = 64*"X"
    uri = "http://localhost/{}".format(uuid)
    json = {'uuid': uuid, 'uri': uri}

    requests_mock.post(dataset_service._endpoint(), json=json)
    dataset = dataset_service.create()
    assert len(dataset.uuid) == 64
    assert dataset.uri.__contains__(dataset.uuid)


def test_read(dataset_service, requests_mock):  # noqa: F811
    """Test read dataset"""
    uuid = "foo"
    uri = "bar"
    json = {'uuid': uuid, 'uri': uri}

    requests_mock.post(dataset_service._endpoint(), json=json)
    dataset = dataset_service.create()

    requests_mock.get(dataset_service._endpoint(uuid), json=json)
    grabbed_dataset = dataset_service.get_by_uuid(dataset.uuid)
    assert dataset == grabbed_dataset


def test_delete(dataset_service, requests_mock):  # noqa: F811
    """Test deleting dataset"""
    uuid = "foo"
    uri = "bar"
    json = {'uuid': uuid, 'uri': uri}

    requests_mock.post(dataset_service._endpoint(), json=json)
    dataset = dataset_service.create()

    requests_mock.get(dataset_service._endpoint(uuid), json=json)
    grabbed_dataset = dataset_service.get_by_uuid(dataset.uuid)
    assert dataset == grabbed_dataset

    requests_mock.delete(dataset_service._endpoint(uuid))
    dataset_service.delete_by_uuid(dataset.uuid)

    requests_mock.get(dataset_service._endpoint(uuid), status_code=404)
    with pytest.raises(requests.HTTPError):
        dataset_service.get_by_uuid(dataset.uuid)
