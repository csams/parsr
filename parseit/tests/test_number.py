from parseit import Number


def test_zero():
    assert Number("0")[1] == 0.0


def test_positive_integer():
    assert Number("123")[1] == 123.0


def test_negative_integer():
    assert Number("-123")[1] == -123.0


def test_positive_float():
    assert Number("123.97")[1] == 123.97


def test_negative_float():
    assert Number("-123.97")[1] == -123.97
