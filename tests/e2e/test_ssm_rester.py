#!/usr/bin/env python

"""Tests for `ssm_client` package."""
import json
import tempfile
import requests
import pytest

import ssm_client

def test_collection_create(ssm_rester):
    """Test creating collection w/ client"""
    title = 64 * "X"

    collection = ssm_rester.collection.create(title)

    assert len(collection.title) == 64
    assert collection.title.__contains__(collection.title.lower())


def test_collection_read(ssm_rester):
    """Test read collection w/ client"""
    title = "foo"

    created_collection = ssm_rester.collection.create(title)
    read_collection = ssm_rester.collection.get_by_title(created_collection.title)

    assert created_collection == read_collection


def test_collection_delete(ssm_rester):
    """Test deleting collection w/ client"""
    title = "foo"

    created_collection = ssm_rester.collection.create(title)
    read_collection = ssm_rester.collection.get_by_title(created_collection.title)

    assert created_collection == read_collection

    ssm_rester.collection.delete_by_title(read_collection.title)

    with pytest.raises(requests.HTTPError):
        ssm_rester.collection.get_by_title(read_collection.title)


def test_initialize_dataset_for_collection(ssm_rester):
    """Test initializing the dataset for a collection"""
    collection_title = 64 * "X"
    uri = "http://localhost/{}".format(collection_title)
    collection = ssm_client.containers.CollectionContainer(
        title=collection_title,
        uri=uri
    )
    ssm_rester.initialize_dataset_for_collection(collection)
    assert ssm_rester.dataset.hostname == ssm_rester.hostname
    assert ssm_rester.dataset.collection_title == collection_title


def test_metazeunerite_dataset_jsonld_create(ssm_rester, metazeunerite_jsonld):
    collection = ssm_rester.collection.create("foo-collection-scidata-jsonld")
    ssm_rester.initialize_dataset_for_collection(collection)
    dataset = ssm_rester.dataset.create(metazeunerite_jsonld)
    assert dataset.uuid is not None
    assert dataset.dataset.get("@graph")[0].get("description") == metazeunerite_jsonld.get("@graph").get("description")


def test_metazeunerite_dataset_ssm_json_create(ssm_rester, metazeunerite_jsonld, metazeunerite_ssm_json):
    collection = ssm_rester.collection.create("foo-collection-ssm-json")
    ssm_rester.initialize_dataset_for_collection(collection)
    dataset = ssm_rester.dataset.create(metazeunerite_jsonld)
    dataset_ssm_json = ssm_rester.dataset.get_by_uuid(dataset.uuid, format="json")
    print(dataset.dataset.keys())
    assert dataset.dataset.get("@graph")[0].get("title") == dataset_ssm_json.dataset.get("title")
    assert dataset.dataset.get("@graph")[0].get("description") == metazeunerite_ssm_json.get("description")
        

def test_metazeunerite_dataset_ssm_json_update(ssm_rester, metazeunerite_jsonld):
    collection = ssm_rester.collection.create("foo-collection-ssm-json")
    ssm_rester.initialize_dataset_for_collection(collection)
    dataset = ssm_rester.dataset.create(metazeunerite_jsonld)
    dataset_ssm_json = ssm_rester.dataset.get_by_uuid(dataset.uuid, format="json")

    # Modify the 51st data entry for y-axis
    dataseries = dataset_ssm_json.dataset.get("scidata").get("dataseries")
    # x = 0, y = 1
    y = dataseries[1].get("y-axis").get("parameter").get("numericValueArray")[0].get("numberArray")
    y[50] -= 100.0

    ssm_json_filename = "temporary.json"
    with open(ssm_json_filename, "w") as f:
        json.dump(dataset_ssm_json.dataset, f)

    with open(ssm_json_filename, "r") as f:
        file_args = {"upload_file": (ssm_json_filename, f)}
        response = requests.post("http://localhost:8000/convert/jsonld", files=file_args)
        print(response.content)
        assert response.status_code == 200
