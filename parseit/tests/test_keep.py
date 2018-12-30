from parseit import Input
from parseit.grammar import Colon, QuotedString


def test_keepleft():
    key = QuotedString << Colon
    assert key(Input('"key":')).value == "key"

    key = Colon << QuotedString
    assert key(Input(':"key"')).value == ":"


def test_keepright():
    key = QuotedString >> Colon
    assert key(Input('"key":')).value == ":"

    key = Colon >> QuotedString
    assert key(Input(':"key"')).value == "key"


def test_middle():
    key = Colon >> QuotedString << Colon
    assert key(Input(':"key":')).value == "key"
