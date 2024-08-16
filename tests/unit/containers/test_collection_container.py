#!/usr/bin/env python

"""Tests for CollectionContainer."""

import json

from ssm_client.containers import CollectionContainer


def test_construction_default():
    """Test creating default collection"""
    collection = CollectionContainer()
    assert collection.title is None
    assert collection.uri is None


def test_construction_just_title():
    """Test creating default collection"""
    kwargs = {
            "title": "5D0DC5589FA2C1F5DE2AB19B47F3923E65B261FABD8ED0F9A9B57CBBE3799988"  # noqa: E501
    }
    collection = CollectionContainer(**kwargs)
    assert collection.title == kwargs["title"]
    assert collection.uri is None


def test_construction_just_uri():
    """Test creating default collection"""
    kwargs = {
        "uri": "http://fuseki:3030/5D0DC5589FA2C1F5DE2AB19B47F3923E65B261FABD8ED0F9A9B57CBBE3799988"  # noqa: E501
    }
    collection = CollectionContainer(**kwargs)
    assert collection.title is None
    assert collection.uri == kwargs["uri"]


def test_collection_str():
    """Testing string output of CollectionContainer"""
    collection = CollectionContainer()
    target = "CollectionContainer(title={title},uri={uri})"
    assert target.format(title=None, uri=None) == collection.__str__()

    title = "bar"
    uri = "foo"
    collection = CollectionContainer(title=title, uri=uri)
    assert target.format(title=title, uri=uri) == collection.__str__()


def test_collection_repr():
    collection = CollectionContainer()
    target = {"title": None, "uri": None}
    assert json.dumps(target) == collection.__repr__()


def test_collections_equal():
    """Test collections that are equal"""
    a = CollectionContainer()
    b = CollectionContainer()
    assert a == b

    uri = "uri"
    title = "title"
    a = CollectionContainer(title=title, uri=uri)
    b = CollectionContainer(title=title, uri=uri)
    assert a == b


def test_collections_not_equal():
    """Test collections not equal"""
    a = CollectionContainer()
    b = CollectionContainer(title="title", uri="uri")
    assert a != b
