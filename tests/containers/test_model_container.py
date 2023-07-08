#!/usr/bin/env python

"""Tests for ModelContainer."""
import json
import pytest

from ssm_client.containers import ModelContainer


@pytest.fixture
def model():
    model = {
        "@context": "https://json-ld.org/contexts/person.jsonld",
        "@id": "http://dbpedia.org/resource/John_Lennon",
        "name": "John Lennon",
        "born": "1940-10-09",
        "spouse": "http://dbpedia.org/resource/Cynthia_Lennon"
    }
    return model


def test_construction_default():
    """Test creating default dataset"""
    dataset = ModelContainer()
    assert dataset.uuid is None
    assert dataset.model == dict()


def test_construction_just_uuid():
    """Test creating default dataset"""
    kwargs = {
        "uuid": "5D0DC5589FA2C1F5DE2AB19B47F3923E65B261FABD8ED0F9A9B57CBBE3799988"}  # noqa: E501
    dataset = ModelContainer(**kwargs)
    assert dataset.uuid == kwargs['uuid']
    assert dataset.model == dict()


def test_construction_just_uri(model):
    """Test creating default dataset"""
    kwargs = {"model": model}
    dataset = ModelContainer(**kwargs)
    assert dataset.uuid is None
    assert dataset.model == kwargs['model']


def test_dataset_str(model):
    """Testing string output of ModelContainer"""
    dataset = ModelContainer()
    target = "ModelContainer(\nuuid={uuid},\nmodel={model}\n)"
    assert target.format(uuid=None, model=dict()) == dataset.__str__()

    uuid = "foo"
    dataset = ModelContainer(uuid=uuid, model=model)
    pretty_model = json.dumps(model, sort_keys=True, indent=4)
    assert target.format(uuid=uuid, model=pretty_model) == dataset.__str__()


def test_dataset_repr():
    dataset = ModelContainer()
    target = {"uuid": None, "model": dict()}
    assert json.dumps(target) == dataset.__repr__()


def test_datasets_equal(model):
    """Test datasets that are equal"""
    a = ModelContainer()
    b = ModelContainer()
    assert a == b

    uuid = "uuid"
    a = ModelContainer(uuid=uuid, model=model)
    b = ModelContainer(uuid=uuid, model=model)
    assert a == b


def test_datasets_not_equal(model):
    """Test datasets not equal"""
    a = ModelContainer()
    b = ModelContainer(uuid="uuid", model=model)
    assert a != b
