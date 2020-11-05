#!/usr/bin/env python

"""Tests for `ssm_rest_python_client` package."""

import pytest
import requests
import requests_mock  # noqa: F401

from ssm_rest_python_client import SSMRester


@pytest.fixture
def ssm_rester():
    return SSMRester()


def test_dataset_create(ssm_rester, requests_mock):  # noqa: F811
    """Test creating dataset w/ client"""
    uuid = 64*"X"
    uri = "http://localhost/{}".format(uuid)
    json = {'uuid': uuid, 'uri': uri}

    requests_mock.post(ssm_rester._dataset_endpoint(), json=json)
    dataset = ssm_rester.create_new_dataset()
    assert len(dataset.uuid) == 64
    assert dataset.uri.__contains__(dataset.uuid)


def test_dataset_read(ssm_rester, requests_mock):  # noqa: F811
    """Test read dataset w/ client"""
    uuid = "foo"
    uri = "bar"
    json = {'uuid': uuid, 'uri': uri}

    requests_mock.post(ssm_rester._dataset_endpoint(), json=json)
    dataset = ssm_rester.create_new_dataset()

    requests_mock.get(ssm_rester._dataset_endpoint(uuid), json=json)
    grabbed_dataset = ssm_rester.get_dataset_by_uuid(dataset.uuid)
    assert dataset == grabbed_dataset


def test_dataset_delete(ssm_rester, requests_mock):  # noqa: F811
    """Test deleting dataset w/ client"""
    uuid = "foo"
    uri = "bar"
    json = {'uuid': uuid, 'uri': uri}

    requests_mock.post(ssm_rester._dataset_endpoint(), json=json)
    dataset = ssm_rester.create_new_dataset()

    requests_mock.get(ssm_rester._dataset_endpoint(uuid), json=json)
    grabbed_dataset = ssm_rester.get_dataset_by_uuid(dataset.uuid)
    assert dataset == grabbed_dataset

    requests_mock.delete(ssm_rester._dataset_endpoint(uuid))
    ssm_rester.delete_dataset_by_uuid(dataset.uuid)

    requests_mock.get(ssm_rester._dataset_endpoint(uuid), status_code=404)
    with pytest.raises(requests.HTTPError):
        ssm_rester.get_dataset_by_uuid(dataset.uuid)
