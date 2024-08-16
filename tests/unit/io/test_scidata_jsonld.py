"""Tests for io.scidata"""

import pathlib
import pytest

from ssm_client import io


@pytest.fixture
def outfile():
    outfile = pathlib.Path("output.jsonld")
    yield outfile
    outfile.unlink()


def test_write(scidata_nmr_jsonld, outfile):
    io.write(outfile.name, scidata_nmr_jsonld, ioformat="scidata-jsonld")
    assert outfile.is_file()


def test_read(scidata_nmr_jsonld, outfile):
    io.write(outfile.name, scidata_nmr_jsonld, ioformat="scidata-jsonld")
    output = io.read(outfile.name, ioformat="scidata-jsonld")
    assert "@context" in output
    assert "@id" in output
    assert "version" in output
    assert "generatedAt" in output
    assert output.get("version") == 2
    assert output.get("@id") == "https://stuchalk.github.io/scidata/examples/nmr/"  # noqa: E501
