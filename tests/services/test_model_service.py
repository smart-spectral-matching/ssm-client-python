#!/usr/bin/env python

"""Tests for ModelService package."""

import pytest
import requests
import requests_mock  # noqa: F401

from ssm_rest_python_client.containers import DatasetContainer
from ssm_rest_python_client.services import ModelService
from ssm_rest_python_client.services.model_service import \
    MismatchedDatasetException


@pytest.fixture
def model_input():
    model_input = {
        "@context": "https://json-ld.org/contexts/person.jsonld",
        "@id": "http://dbpedia.org/resource/John_Lennon",
        "name": "John Lennon",
        "born": "1940-10-09",
        "spouse": "http://dbpedia.org/resource/Cynthia_Lennon"
    }
    return model_input


@pytest.fixture
def model_output():
    model_output = {
        "@context": {
            "birthDate": {
                "@id": "http://schema.org/birthDate",
                "@type": "http://www.w3.org/2001/XMLSchema#date"
            },
            "name": {
                "@id": "http://xmlns.com/foaf/0.1/name"
            },
            "spouse": {
                "@id": "http://schema.org/spouse",
                "@type": "@id"
            },
            "xsd": "http://www.w3.org/2001/XMLSchema#"
        },
        "@id": "http://dbpedia.org/resource/John_Lennon",
        "birthDate": "1940-10-09",
        "name": "John Lennon",
        "spouse": "http://dbpedia.org/resource/Cynthia_Lennon"
    }
    return model_output


@pytest.fixture
def model_uuid():
    return 64 * "Y"


@pytest.fixture
def dataset():
    dataset_uuid = 64 * "X"
    uri = "http://localhost/{}".format(dataset_uuid)
    return DatasetContainer(uuid=dataset_uuid, uri=uri)


@pytest.fixture
def model_service(dataset):
    return ModelService(dataset=dataset)


def test_construction(dataset):
    """Tests construction of ModelService object"""
    model = ModelService(dataset=dataset)
    assert model.hostname == "http://localhost"
    assert model.dataset_uuid == dataset.uuid

    model = ModelService(dataset=dataset, dataset_uuid=dataset.uuid)
    assert model.hostname == "http://localhost"
    assert model.dataset_uuid == dataset.uuid

    with pytest.raises(MismatchedDatasetException):
        ModelService(dataset=dataset, dataset_uuid=64*"Z")


def test_create(model_input, model_output, model_uuid, model_service, requests_mock):  # noqa: F811, E501
    """Test creating model"""
    json = {"uuid": model_uuid, "model": model_output}

    requests_mock.post(model_service._endpoint(), json=json)
    model = model_service.create(model_input)
    assert model.uuid == model_uuid
    assert model.model == model_output


def test_read(model_input, model_output, model_uuid, model_service, requests_mock):  # noqa: F811, E501
    """Test read model"""
    json = {"uuid": model_uuid, "model": model_output}

    # Create a model first so we can read from it
    requests_mock.post(model_service._endpoint(), json=json)
    model = model_service.create(model_input)

    # Ensure the model we created and the one we get match
    requests_mock.get(model_service._endpoint(model_uuid), json=json)
    grabbed_model = model_service.get_by_uuid(model.uuid)
    assert model == grabbed_model


def test_replace_model_for_uuid(model_input, model_output, model_uuid, model_service, requests_mock):  # noqa: F811, E501
    """Test replacing a model"""
    json = {"uuid": model_uuid, "model": model_output}

    # Create a model first so we can read from it
    requests_mock.post(model_service._endpoint(), json=json)
    model = model_service.create(model_input)

    # Replacement model: input and output
    new_model_input = {
        "@context": "https://json-ld.org/contexts/person.jsonld",
        "@id": "http://dbpedia.org/resource/Ringo_Starr",
        "name": "Ringo Starr",
    }

    new_model_output = {
        "@context": {
            "name": {
                "@id": "http://xmlns.com/foaf/0.1/name"
            },
            "xsd": "http://www.w3.org/2001/XMLSchema#"
        },
        "@id": "http://dbpedia.org/resource/Ringo_Starr",
        "name": "Ringo Starr"
    }

    json["model"] = new_model_output

    # Replace the model
    requests_mock.put(model_service._endpoint(model_uuid), json=json)
    new_model = model_service.replace_model_for_uuid(
        model.uuid, new_model_input)

    # Ensure the model we updated and the one we get back match
    requests_mock.get(model_service._endpoint(model_uuid), json=json)
    grabbed_model = model_service.get_by_uuid(model.uuid)
    assert new_model == grabbed_model
    assert model != grabbed_model


def test_update_model_for_uuid(model_input, model_output, model_uuid, model_service, requests_mock):  # noqa: F811, E501
    """Test updating a model"""
    json = {"uuid": model_uuid, "model": model_output}

    # Create a model first so we can read from it
    requests_mock.post(model_service._endpoint(), json=json)
    model = model_service.create(model_input)

    # Updated model: input and output
    model_update_input = {"name": "Paul McCartney"}
    model_update_output = model_input.copy()
    model_update_output.update(model_update_input)
    json["model"] = model_update_output

    # Replace the model
    requests_mock.patch(model_service._endpoint(model_uuid), json=json)
    new_model = model_service.update_model_for_uuid(
        model.uuid, model_update_input)

    # Ensure the model we updated and the one we get back match
    requests_mock.get(model_service._endpoint(model_uuid), json=json)
    grabbed_model = model_service.get_by_uuid(model.uuid)
    assert new_model == grabbed_model
    assert model != grabbed_model


def test_delete(model_input, model_output, model_uuid, model_service, requests_mock):  # noqa: F811, E501
    """Test deleting dataset"""
    json = {"uuid": model_uuid, "model": model_output}

    # Create a model first so we can read from it
    requests_mock.post(model_service._endpoint(), json=json)
    model = model_service.create(model_input)

    # Make sure it exists before we check for deletion
    requests_mock.get(model_service._endpoint(model.uuid), json=json)
    grabbed_model = model_service.get_by_uuid(model.uuid)
    assert model == grabbed_model

    # Delete the model
    requests_mock.delete(model_service._endpoint(model_uuid))
    model_service.delete_by_uuid(model.uuid)

    # Make sure we cannot get the model again, confirming deletion
    requests_mock.get(model_service._endpoint(model.uuid), status_code=404)
    with pytest.raises(requests.HTTPError):
        model_service.get_by_uuid(model.uuid)
