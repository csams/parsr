from parseit import Input
from parseit.grammar import Number


def test_zero():
    assert Number(Input("0")).value == 0.0


def test_positive_integer():
    assert Number(Input("123")).value == 123.0


def test_negative_integer():
    assert Number(Input("-123")).value == -123.0


def test_positive_float():
    assert Number(Input("123.97")).value == 123.97


def test_negative_float():
    assert Number(Input("-123.97")).value == -123.97
