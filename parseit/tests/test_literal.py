from parseit import Keyword, Literal


def test_literal():
    p = Literal("123")
    assert p("123") == "123"


def test_keyword():
    p = Keyword("true", True)
    assert p("true") is True


def test_literal_ignore_case():
    p = Literal("true", ignore_case=True)
    assert p("TrUe") == "TrUe"


def test_keyword_ignore_case():
    p = Keyword("true", True, ignore_case=True)
    assert p("TRUE") is True
