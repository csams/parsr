import string
from parseit import Between, Char, Input, StringBuilder
from parseit.grammar import InSet, String, QuotedString
from parseit.optimizer import optimize


def test_inset():
    data = Input("a")
    assert InSet("abc", "thing")(data).value == "a"


def test_stringbuilder():
    sb = StringBuilder()
    sb.cache |= set(string.ascii_letters)
    data = Input("abcde")
    assert sb(data).value == "abcde"


def test_manual_quoted_string():
    sb = StringBuilder()
    sb.cache |= set(string.ascii_letters)
    p = Between(sb, Char('"'))
    data = Input('"abcde"')
    assert p(data).value == "abcde"


def test_string():
    data = Input("abcde")
    OString = optimize(String)
    assert OString(data).value == "abcde"


def test_quoted_string():
    data = Input("'abcde'")
    OString = optimize(QuotedString)
    print()
    assert OString(data).value == "abcde"
