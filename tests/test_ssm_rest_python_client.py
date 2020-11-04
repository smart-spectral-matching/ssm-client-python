#!/usr/bin/env python

"""Tests for `ssm_rest_python_client` package."""

import pytest


from ssm_rest_python_client import SSMClient


@pytest.fixture
def ssm_client():
    return SSMClient()


def test_content(ssm_client):
    """Test creating dataset w/ client"""
    dataset = ssm_client.create_new_dataset()
    assert len(dataset) != 0
