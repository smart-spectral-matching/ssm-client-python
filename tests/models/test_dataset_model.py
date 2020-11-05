#!/usr/bin/env python

"""Tests for DatasetModel."""

from ssm_rest_python_client.models import DatasetModel


def test_construction_default():
    """Test creating default dataset"""
    dataset = DatasetModel()
    assert dataset.uuid is None
    assert dataset.uri is None


def test_construction_just_uuid():
    """Test creating default dataset"""
    kwargs = {
        "uuid": "5D0DC5589FA2C1F5DE2AB19B47F3923E65B261FABD8ED0F9A9B57CBBE3799988"}  # noqa: E501
    dataset = DatasetModel(**kwargs)
    assert dataset.uuid == kwargs['uuid']
    assert dataset.uri is None


def test_construction_just_uri():
    """Test creating default dataset"""
    kwargs = {
        "uri": "http://fuseki:3030/5D0DC5589FA2C1F5DE2AB19B47F3923E65B261FABD8ED0F9A9B57CBBE3799988"}  # noqa: E501
    dataset = DatasetModel(**kwargs)
    assert dataset.uuid is None
    assert dataset.uri == kwargs['uri']


def test_dataset_repr():
    dataset = DatasetModel()
    target = "DatasetModel(uuid={uuid},uri={uri})"
    assert target.format(uuid=None, uri=None) == dataset.__str__()

    uuid = "bar"
    uri = "foo"
    dataset = DatasetModel(uuid=uuid, uri=uri)
    assert target.format(uuid=uuid, uri=uri) == dataset.__str__()


def test_datasets_equal():
    a = DatasetModel()
    b = DatasetModel()
    assert a == b


def test_datasets_equal_with_args():
    uri = "uri"
    uuid = "uuid"
    a = DatasetModel(uri=uri, uuid=uuid)
    b = DatasetModel(uri=uri, uuid=uuid)
    assert a == b


def test_datasets_not_equal():
    a = DatasetModel()
    b = DatasetModel(uuid="uuid", uri="uri")
    assert a != b
