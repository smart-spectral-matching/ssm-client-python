#!/usr/bin/env python

"""Tests for DatasetContainer."""
import json

from ssm_client.containers import CollectionContainer


def test_construction_default():
    """Test creating default dataset"""
    dataset = CollectionContainer()
    assert dataset.title is None
    assert dataset.uri is None


def test_construction_just_title():
    """Test creating default dataset"""
    kwargs = {
        "title": "5D0DC5589FA2C1F5DE2AB19B47F3923E65B261FABD8ED0F9A9B57CBBE3799988"}  # noqa: E501
    dataset = CollectionContainer(**kwargs)
    assert dataset.title == kwargs['title']
    assert dataset.uri is None


def test_construction_just_uri():
    """Test creating default dataset"""
    kwargs = {
        "uri": "http://fuseki:3030/5D0DC5589FA2C1F5DE2AB19B47F3923E65B261FABD8ED0F9A9B57CBBE3799988"}  # noqa: E501
    dataset = CollectionContainer(**kwargs)
    assert dataset.title is None
    assert dataset.uri == kwargs['uri']


def test_dataset_str():
    """Testing string output of DatasetContainer"""
    dataset = CollectionContainer()
    target = "DatasetContainer(title={title},uri={uri})"
    assert target.format(title=None, uri=None) == dataset.__str__()

    title = "bar"
    uri = "foo"
    dataset = CollectionContainer(title=title, uri=uri)
    assert target.format(title=title, uri=uri) == dataset.__str__()


def test_dataset_repr():
    dataset = CollectionContainer()
    target = {"title": None, "uri": None}
    assert json.dumps(target) == dataset.__repr__()


def test_datasets_equal():
    """Test datasets that are equal"""
    a = CollectionContainer()
    b = CollectionContainer()
    assert a == b

    uri = "uri"
    title = "title"
    a = CollectionContainer(title=title, uri=uri)
    b = CollectionContainer(title=title, uri=uri)
    assert a == b


def test_datasets_not_equal():
    """Test datasets not equal"""
    a = CollectionContainer()
    b = CollectionContainer(title="title", uri="uri")
    assert a != b
