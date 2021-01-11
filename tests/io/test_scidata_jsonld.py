"""Tests for io.scidata"""
import pathlib
import pytest
import requests

from ssm_rest_python_client import io


@pytest.fixture
def scidata_nmr_jsonld():
    url = 'https://raw.githubusercontent.com/stuchalk/scidata/master/examples/nmr.jsonld'  # noqa: E501
    data = requests.get(url)
    return data.json()


@pytest.fixture
def outfile():
    outfile = pathlib.Path('output.jsonld')
    yield outfile
    outfile.unlink()


def test_write(scidata_nmr_jsonld, outfile):
    io.write(outfile.name, scidata_nmr_jsonld, ioformat='scidata-jsonld')
    assert outfile.is_file()


def test_read(scidata_nmr_jsonld, outfile):
    io.write(outfile.name, scidata_nmr_jsonld, ioformat='scidata-jsonld')
    output = io.read(outfile.name, ioformat='scidata-jsonld')
    assert '@context' in output
    assert '@id' in output
    assert 'version' in output
    assert 'generatedAt' in output
    assert output.get('version') == 2
    assert output.get('@id') == "https://stuchalk.github.io/scidata/examples/nmr/"  # noqa: E501
