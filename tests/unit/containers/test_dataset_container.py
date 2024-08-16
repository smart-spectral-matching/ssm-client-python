#!/usr/bin/env python

"""Tests for DatasetContainer."""
import json
import pytest

from ssm_client.containers import DatasetContainer


@pytest.fixture
def dataset():
    dataset = {
        "@context": "https://json-ld.org/contexts/person.jsonld",
        "@id": "http://dbpedia.org/resource/John_Lennon",
        "name": "John Lennon",
        "born": "1940-10-09",
        "spouse": "http://dbpedia.org/resource/Cynthia_Lennon"
    }
    return dataset


def test_construction_default():
    """Test creating default dataset"""
    dataset = DatasetContainer()
    assert dataset.uuid is None
    assert dataset.dataset == dict()


def test_construction_just_uuid():
    """Test creating default dataset"""
    kwargs = {
        "uuid": "5D0DC5589FA2C1F5DE2AB19B47F3923E65B261FABD8ED0F9A9B57CBBE3799988"}  # noqa: E501
    dataset = DatasetContainer(**kwargs)
    assert dataset.uuid == kwargs['uuid']
    assert dataset.dataset == dict()


def test_construction_just_uri(dataset):
    """Test creating default dataset"""
    kwargs = {"dataset": dataset}
    dataset = DatasetContainer(**kwargs)
    assert dataset.uuid is None
    assert dataset.dataset == kwargs['dataset']


def test_dataset_str(dataset):
    """Testing string output of DatasetContainer"""
    dataset_container = DatasetContainer()
    target = "DatasetContainer(\nuuid={uuid},\ndataset={dataset}\n)"
    assert target.format(uuid=None, dataset=dict()) == dataset_container.__str__()

    uuid = "foo"
    dataset_container = DatasetContainer(uuid=uuid, dataset=dataset)
    pretty_dataset = json.dumps(dataset_container.dataset, sort_keys=True, indent=4)
    assert target.format(uuid=uuid, dataset=pretty_dataset) == dataset_container.__str__()


def test_dataset_repr():
    dataset = DatasetContainer()
    target = {"uuid": None, "dataset": dict()}
    assert json.dumps(target) == dataset.__repr__()


def test_datasets_equal(dataset):
    """Test datasets that are equal"""
    a = DatasetContainer()
    b = DatasetContainer()
    assert a == b

    uuid = "uuid"
    a = DatasetContainer(uuid=uuid, dataset=dataset)
    b = DatasetContainer(uuid=uuid, dataset=dataset)
    assert a == b


def test_datasets_not_equal(dataset):
    """Test datasets not equal"""
    a = DatasetContainer()
    b = DatasetContainer(uuid="uuid", dataset=dataset)
    assert a != b
