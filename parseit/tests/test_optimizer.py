from parseit import Char, Input
from parseit.grammar import String
from parseit.optimizer import optimize
from parseit.tree import render
from parseit.json_parser import JsonValue


def test_optimize_or():
    thing = Char("a") | Char("b") | Char("c")
    expected = thing(Input("c")).value
    actual = optimize(thing)(Input("c")).value
    assert expected == actual


def test_optimize_or_string():
    data = "abcde"
    expected = String(Input(data)).value
    actual = optimize(String)(Input(data)).value
    assert expected == actual


# def test_show_json():
#     print()
#     render(JsonValue)
