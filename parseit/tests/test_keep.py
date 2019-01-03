from parseit.compiler import comp
from parseit.grammar import Colon, QuotedString


def test_keepleft():
    key = comp(QuotedString << Colon)
    assert key('"key":')[1] == "key"

    key = comp(Colon << QuotedString)
    assert key(':"key"')[1] == ":"


def test_keepright():
    key = comp(QuotedString >> Colon)
    assert key('"key":')[1] == ":"

    key = comp(Colon >> QuotedString)
    assert key(':"key"')[1] == "key"


def test_middle():
    key = comp(Colon >> QuotedString << Colon)
    assert key(':"key":')[1] == "key"
