from parseit import Keyword, Literal


def test_literal():
    p = Literal("123")
    assert p("123")[1] == "123"


def test_keyword():
    p = Keyword("true", True)
    assert p("true")[1] is True


def test_ignore_case():
    p = Keyword("true", True, ignore_case=True)
    assert p("tRuE")[1] is True
