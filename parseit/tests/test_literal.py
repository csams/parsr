from parseit import Keyword, Literal


def test_literal():
    p = Literal("123")
    assert p("123") == "123"


def test_keyword():
    p = Keyword("true", True)
    assert p("true") is True
