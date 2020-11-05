#!/usr/bin/env python

"""Tests for `ssm_rest_python_client` package."""

import pytest


from ssm_rest_python_client import SSMRester
from ssm_rest_python_client.exceptions import DatasetNotFoundException


@pytest.fixture
def ssm_rester():
    return SSMRester()


def test_dataset_create(ssm_rester):
    """Test creating dataset w/ client"""
    dataset = ssm_rester.create_new_dataset()
    assert len(dataset.uuid) == 64
    assert dataset.uri.__contains__(dataset.uuid)


def test_dataset_read(ssm_rester):
    """Test read dataset w/ client"""
    dataset = ssm_rester.create_new_dataset()
    grabbed_dataset = ssm_rester.get_dataset_by_uuid(dataset.uuid)
    assert dataset == grabbed_dataset


def test_dataset_delete(ssm_rester):
    """Test deleting dataset w/ client"""
    dataset = ssm_rester.create_new_dataset()
    grabbed_dataset = ssm_rester.get_dataset_by_uuid(dataset.uuid)
    assert dataset == grabbed_dataset

    ssm_rester.delete_dataset_by_uuid(dataset.uuid)
    with pytest.raises(DatasetNotFoundException):
        ssm_rester.get_dataset_by_uuid(dataset.uuid)
