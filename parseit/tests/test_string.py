import string
from parseit import Between, Char, StringBuilder
from parseit.grammar import InSet, String, QuotedString


def test_inset():
    assert InSet("abc", "set of abc")("a")[1] == "a"


def test_stringbuilder():
    sb = StringBuilder()
    sb.add_cache(set(string.ascii_letters))
    data = "abcde"
    assert sb(data)[1] == "abcde"


def test_manual_quoted_string():
    sb = StringBuilder()
    sb.add_cache(set(string.ascii_letters))
    p = Between(sb, Char('"'))
    data = '"abcde"'
    assert p(data)[1] == "abcde"


def test_manual_escaped_string():
    sb = StringBuilder()
    sb.add_cache(set(string.ascii_letters))
    sb.add_echar("'")
    p = Between(sb, Char("'"))
    data = r"""'a\'bcde'"""
    assert p(data)[1] == "a\'bcde"


def test_string():
    data = "abcde"
    assert String(data)[1] == "abcde"


def test_quoted_string():
    data = "'abcde'"
    assert QuotedString(data)[1] == "abcde"


def test_escaped_string():
    data = r"""'a\'bcde'"""
    assert QuotedString(data)[1] == "a\'bcde"
