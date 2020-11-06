#!/usr/bin/env python

"""Tests for DatasetContainer."""
import json

from ssm_rest_python_client.containers import DatasetContainer


def test_construction_default():
    """Test creating default dataset"""
    dataset = DatasetContainer()
    assert dataset.uuid is None
    assert dataset.uri is None


def test_construction_just_uuid():
    """Test creating default dataset"""
    kwargs = {
        "uuid": "5D0DC5589FA2C1F5DE2AB19B47F3923E65B261FABD8ED0F9A9B57CBBE3799988"}  # noqa: E501
    dataset = DatasetContainer(**kwargs)
    assert dataset.uuid == kwargs['uuid']
    assert dataset.uri is None


def test_construction_just_uri():
    """Test creating default dataset"""
    kwargs = {
        "uri": "http://fuseki:3030/5D0DC5589FA2C1F5DE2AB19B47F3923E65B261FABD8ED0F9A9B57CBBE3799988"}  # noqa: E501
    dataset = DatasetContainer(**kwargs)
    assert dataset.uuid is None
    assert dataset.uri == kwargs['uri']


def test_dataset_str():
    """Testing string output of DatasetContainer"""
    dataset = DatasetContainer()
    target = "DatasetContainer(uuid={uuid},uri={uri})"
    assert target.format(uuid=None, uri=None) == dataset.__str__()

    uuid = "bar"
    uri = "foo"
    dataset = DatasetContainer(uuid=uuid, uri=uri)
    assert target.format(uuid=uuid, uri=uri) == dataset.__str__()


def test_dataset_repr():
    dataset = DatasetContainer()
    target = {"uuid": None, "uri": None}
    assert json.dumps(target) == dataset.__repr__()


def test_datasets_equal():
    """Test datasets that are equal"""
    a = DatasetContainer()
    b = DatasetContainer()
    assert a == b

    uri = "uri"
    uuid = "uuid"
    a = DatasetContainer(uri=uri, uuid=uuid)
    b = DatasetContainer(uri=uri, uuid=uuid)
    assert a == b


def test_datasets_not_equal():
    """Test datasets not equal"""
    a = DatasetContainer()
    b = DatasetContainer(uuid="uuid", uri="uri")
    assert a != b
