#!/usr/bin/env python

"""Tests for DatasetService package."""

import pytest
import requests


def test_create(collection_service):
    """Test creating collection"""
    title = 64 * "X"

    collection = collection_service.create(title)
    assert len(collection.title) == 64
    assert collection.title.__contains__(title.lower())


def test_read(collection_service):
    """Test read collection"""
    title = "foo"

    collection = collection_service.create(title)
    grabbed_collection = collection_service.get_by_title(collection.title)
    assert collection == grabbed_collection


def test_delete(collection_service):  # noqa: F811
    """Test deleting collection"""
    title = "foo"

    collection = collection_service.create(title)
    grabbed_collection = collection_service.get_by_title(collection.title)
    assert collection == grabbed_collection

    collection_service.delete_by_title(collection.title)

    with pytest.raises(requests.HTTPError):
        collection_service.get_by_title(collection.title)
