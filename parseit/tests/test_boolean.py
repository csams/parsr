from parseit import Char, Input


def test_and():
    p = Char("a") & Char("b") & Char("c")
    assert p(Input("abc")).value == ["a", "b", "c"]


def test_or():
    p = Char("a") | Char("b")
    assert p(Input("a")).value == "a"
    assert p(Input("b")).value == "b"
