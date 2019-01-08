from parseit import Char, Opt


def test_opt():
    a = Opt(Char("a"))
    assert a("a")[1] == "a"
    assert a("b")[1] is None


def test_opt_default():
    a = Opt(Char("a"), "Default")
    assert a("b")[1] == "Default"
