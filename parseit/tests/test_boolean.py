from parseit import Char


def test_and():
    p = Char("a") & Char("b")
    assert p("ab")[1] == ["a", "b"]


def test_or():
    p = Char("a") | Char("b")
    assert p("a")[1] == "a"
    assert p("b")[1] == "b"
