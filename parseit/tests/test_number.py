from parseit.grammar import Number
from parseit.compiler import comp


def test_zero():
    assert comp(Number)("0")[1] == 0.0


def test_positive_integer():
    assert comp(Number)("123")[1] == 123.0


def test_negative_integer():
    assert comp(Number)("-123")[1] == -123.0


def test_positive_float():
    assert comp(Number)("123.97")[1] == 123.97


def test_negative_float():
    assert comp(Number)("-123.97")[1] == -123.97
