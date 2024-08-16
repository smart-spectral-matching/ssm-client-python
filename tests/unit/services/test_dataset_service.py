#!/usr/bin/env python

"""Tests for DatasetService package."""

import pytest
import requests

from ssm_client.containers import CollectionContainer
from ssm_client.services import DatasetService
from ssm_client.services.dataset_service import MismatchedCollectionException


@pytest.fixture
def dataset_input():
    dataset_input = {
        "@context": "https://json-ld.org/contexts/person.jsonld",
        "@id": "http://dbpedia.org/resource/John_Lennon",
        "name": "John Lennon",
        "born": "1940-10-09",
        "spouse": "http://dbpedia.org/resource/Cynthia_Lennon",
    }
    return dataset_input


@pytest.fixture
def dataset_output():
    dataset_output = {
        "@context": {
            "birthDate": {
                "@id": "http://schema.org/birthDate",
                "@type": "http://www.w3.org/2001/XMLSchema#date",
            },
            "name": {"@id": "http://xmlns.com/foaf/0.1/name"},
            "spouse": {"@id": "http://schema.org/spouse", "@type": "@id"},
            "xsd": "http://www.w3.org/2001/XMLSchema#",
        },
        "@id": "http://dbpedia.org/resource/John_Lennon",
        "birthDate": "1940-10-09",
        "name": "John Lennon",
        "spouse": "http://dbpedia.org/resource/Cynthia_Lennon",
    }
    return dataset_output


@pytest.fixture
def dataset_uuid():
    return 64 * "Y"


@pytest.fixture
def collection():
    collection_title = 64 * "X"
    uri = "http://localhost/{}".format(collection_title)
    return CollectionContainer(title=collection_title, uri=uri)


@pytest.fixture
def dataset_service(collection):
    return DatasetService(collection=collection)


def test_construction(collection):
    """Tests construction of DatasetService object"""
    dataset = DatasetService(collection=collection)
    assert dataset.hostname == "http://localhost"
    assert dataset.collection_title == collection.title

    dataset = DatasetService(collection=collection, collection_title=collection.title)
    assert dataset.hostname == "http://localhost"
    assert dataset.collection_title == collection.title

    with pytest.raises(MismatchedCollectionException):
        DatasetService(collection=collection, collection_title=64 * "Z")


def test_create(
    dataset_input, dataset_output, dataset_uuid, dataset_service, requests_mock
):  # noqa: F811, E501
    """Test creating dataset"""
    json = {"uuid": dataset_uuid, "dataset": dataset_output}

    requests_mock.post(dataset_service._endpoint(), json=json)
    dataset = dataset_service.create(dataset_input)
    assert dataset.uuid == dataset_uuid
    assert dataset.dataset == dataset_output


def test_read(
    dataset_input, dataset_output, dataset_uuid, dataset_service, requests_mock
):  # noqa: F811, E501
    """Test read dataset"""
    json = {"uuid": dataset_uuid, "dataset": dataset_output}

    # Create a dataset first so we can read from it
    requests_mock.post(dataset_service._endpoint(), json=json)
    dataset = dataset_service.create(dataset_input)

    # Ensure the dataset we created and the one we get match
    requests_mock.get(dataset_service._endpoint(dataset_uuid), json=json)
    grabbed_dataset = dataset_service.get_by_uuid(dataset.uuid)
    assert dataset == grabbed_dataset


def test_replace_dataset_for_uuid(
    dataset_input, dataset_output, dataset_uuid, dataset_service, requests_mock
):  # noqa: F811, E501
    """Test replacing a dataset"""
    json = {"uuid": dataset_uuid, "dataset": dataset_output}

    # Create a dataset first so we can read from it
    requests_mock.post(dataset_service._endpoint(), json=json)
    dataset = dataset_service.create(dataset_input)

    # Replacement dataset: input and output
    new_dataset_input = {
        "@context": "https://json-ld.org/contexts/person.jsonld",
        "@id": "http://dbpedia.org/resource/Ringo_Starr",
        "name": "Ringo Starr",
    }

    new_dataset_output = {
        "@context": {
            "name": {"@id": "http://xmlns.com/foaf/0.1/name"},
            "xsd": "http://www.w3.org/2001/XMLSchema#",
        },
        "@id": "http://dbpedia.org/resource/Ringo_Starr",
        "name": "Ringo Starr",
    }

    json["dataset"] = new_dataset_output

    # Replace the dataset
    requests_mock.put(dataset_service._endpoint(dataset_uuid), json=json)
    new_dataset = dataset_service.replace_dataset_for_uuid(
        dataset.uuid, new_dataset_input
    )

    # Ensure the dataset we updated and the one we get back match
    requests_mock.get(dataset_service._endpoint(dataset_uuid), json=json)
    grabbed_dataset = dataset_service.get_by_uuid(dataset.uuid)
    assert new_dataset == grabbed_dataset
    assert dataset != grabbed_dataset


def test_update_dataset_for_uuid(
    dataset_input, dataset_output, dataset_uuid, dataset_service, requests_mock
):  # noqa: F811, E501
    """Test updating a dataset"""
    json = {"uuid": dataset_uuid, "dataset": dataset_output}

    # Create a dataset first so we can read from it
    requests_mock.post(dataset_service._endpoint(), json=json)
    dataset = dataset_service.create(dataset_input)

    # Updated dataset: input and output
    dataset_update_input = {"name": "Paul McCartney"}
    dataset_update_output = dataset_input.copy()
    dataset_update_output.update(dataset_update_input)
    json["dataset"] = dataset_update_output

    # Replace the dataset
    requests_mock.patch(dataset_service._endpoint(dataset_uuid), json=json)
    new_dataset = dataset_service.update_dataset_for_uuid(
        dataset.uuid, dataset_update_input
    )

    # Ensure the dataset we updated and the one we get back match
    requests_mock.get(dataset_service._endpoint(dataset_uuid), json=json)
    grabbed_dataset = dataset_service.get_by_uuid(dataset.uuid)
    assert new_dataset == grabbed_dataset
    assert dataset != grabbed_dataset


def test_delete(
    dataset_input, dataset_output, dataset_uuid, dataset_service, requests_mock
):  # noqa: F811, E501
    """Test deleting dataset"""
    json = {"uuid": dataset_uuid, "dataset": dataset_output}

    # Create a dataset first so we can read from it
    requests_mock.post(dataset_service._endpoint(), json=json)
    dataset = dataset_service.create(dataset_input)

    # Make sure it exists before we check for deletion
    requests_mock.get(dataset_service._endpoint(dataset.uuid), json=json)
    grabbed_dataset = dataset_service.get_by_uuid(dataset.uuid)
    assert dataset == grabbed_dataset

    # Delete the dataset
    requests_mock.delete(dataset_service._endpoint(dataset_uuid))
    dataset_service.delete_by_uuid(dataset.uuid)

    # Make sure we cannot get the dataset again, confirming deletion
    requests_mock.get(dataset_service._endpoint(dataset.uuid), status_code=404)
    with pytest.raises(requests.HTTPError):
        dataset_service.get_by_uuid(dataset.uuid)
