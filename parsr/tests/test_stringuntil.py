import pytest
from parsr import Char, StringUntil


DATA = "abcde ="


def test_success():
    assert StringUntil(Char("="))(DATA) == "abcde "


def test_fail():
    with pytest.raises(Exception):
        StringUntil(Char("?"))(DATA) == ""


def test_empty():
    assert StringUntil(Char("="))("=") == ""


def test_lower():
    assert StringUntil(Char("="), lower=1)("a=") == "a"

    with pytest.raises(Exception):
        StringUntil(Char("="), lower=2)("a=")


def test_upper():
    assert StringUntil(Char("="), upper=1)("a=") == "a"

    with pytest.raises(Exception):
        StringUntil(Char("="), upper=1)("ab=")
