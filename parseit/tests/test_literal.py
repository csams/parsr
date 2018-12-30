from parseit import Keyword, Literal, Input


def test_literal():
    p = Literal("123")
    assert p(Input("123")).value == "123"


def test_keyword():
    p = Keyword("true", True)
    assert p(Input("true")).value is True


def test_ignore_case():
    p = Keyword("true", True, ignore_case=True)
    assert p(Input("tRuE")).value is True
