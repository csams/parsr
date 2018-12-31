from parseit import Char, Input


def test_and():
    p = Char("a") & Char("b")
    assert p(Input("ab")).value == ["a", "b"]


def test_or():
    p = Char("a") | Char("b")
    assert p(Input("a")).value == "a"
    assert p(Input("b")).value == "b"
