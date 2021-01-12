import pytest
from ssm_rest_python_client.io import jcamp


def test_parse_duplicate_characters():
    assert jcamp._parse_duplicate_characters("9U") == "999"


def test_parse_line():
    target = [99.0, 98.0, 97.0, 96.0, 98.0, 93.0]

    line = "99 98 97 96 98 93"
    assert jcamp._parse_line(line) == target

    line = "99,98,97,96,98,93"
    assert jcamp._parse_line(line) == target

    line = "99+98+97+96+98+93"
    assert jcamp._parse_line(line) == target

    line = "99I8I7I6I8I3"
    assert jcamp._parse_line(line) == target

    line = "99jjjKn"
    assert jcamp._parse_line(line) == target

    line = "99jUKn"
    assert jcamp._parse_line(line) == target

    line = "99 98 *"
    with pytest.raises(jcamp.UnknownCharacterException):
        jcamp._parse_line(line)
