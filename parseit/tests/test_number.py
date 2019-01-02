from parseit import Input
from parseit.grammar import Number
from parseit.compiler import comp


def test_zero():
    assert comp(Number)("0") == 0.0
    assert Number(Input("0")).value == 0.0


def test_positive_integer():
    assert Number(Input("123")).value == 123.0
    assert comp(Number)("123") == 123.0


def test_negative_integer():
    assert Number(Input("-123")).value == -123.0
    assert comp(Number)("-123") == -123.0


def test_positive_float():
    assert Number(Input("123.97")).value == 123.97
    assert comp(Number)("123.97") == 123.97


def test_negative_float():
    assert Number(Input("-123.97")).value == -123.97
    assert comp(Number)("-123.97") == -123.97
