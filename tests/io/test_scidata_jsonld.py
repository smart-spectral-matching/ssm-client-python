"""Tests for io.scidata"""
import json
import pathlib
import pytest

from ssm_rest_python_client import io
from tests import TEST_DATA_DIR


@pytest.fixture
def scidata_nmr_jsonld():
    """
    NMR SciData JSON-LD file
    Retrieved on 1/12/2021 from:
        https://raw.githubusercontent.com/stuchalk/scidata/master/examples/nmr.jsonld
    """
    p = pathlib.Path(TEST_DATA_DIR, "scidata", "nmr.jsonld")
    return json.loads(p.read_text())


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
