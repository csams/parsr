import string
from parseit import InSet, String, QuotedString


def test_inset():
    assert InSet("abc", "set of abc")("a")[1] == "a"


def test_string():
    sb = String(string.ascii_letters)
    data = "abcde"
    assert sb(data)[1] == "abcde"


def test_quoted_string():
    data = "'abcde'"
    assert QuotedString(data)[1] == "abcde"


def test_escaped_string():
    data = r"""'a\'bcde'"""
    assert QuotedString(data)[1] == "a\'bcde"
