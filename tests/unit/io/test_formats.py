"""Tests for io.formats"""
import pytest
from ssm_client import io


def test_get_ioformat_scidata_jsonld():
    fmt = io.formats._get_ioformat('scidata-jsonld')
    assert fmt.__name__ == 'ssm_client.io.scidata_jsonld'


def test_get_ioformat_jcamp():
    fmt = io.formats._get_ioformat('jcamp')
    assert fmt.__name__ == 'ssm_client.io.jcamp'


def test_get_ioformat_raise_exception():
    with pytest.raises(io.formats.UnknownFileTypeError):
        io.formats._get_ioformat('cat')
