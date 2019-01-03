from parseit import Char, Input
from parseit.optimizer import optimize


def test_optimize_or():
    thing = Char("a") | Char("b") | Char("c")
    expected = thing(Input("c")).value
    actual = optimize(thing)(Input("c")).value
    assert expected == actual
