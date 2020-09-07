import pytest
from parsr import Regex


def test_simple_regex():
    Ident = Regex("[a-zA-Z]([a-zA-Z0-9])*")
    assert Ident("abcd1") == "abcd1"


def test_simple_regex_fail():
    Ident = Regex("[a-zA-Z]([a-zA-Z0-9])*")
    with pytest.raises(Exception):
        Ident("1abcd1")
