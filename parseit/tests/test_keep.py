from parseit import Colon, QuotedString


def test_keepleft():
    key = QuotedString << Colon
    assert key('"key":')[1] == "key"

    key = Colon << QuotedString
    assert key(':"key"')[1] == ":"


def test_keepright():
    key = QuotedString >> Colon
    assert key('"key":')[1] == ":"

    key = Colon >> QuotedString
    assert key(':"key"')[1] == "key"


def test_middle():
    key = Colon >> QuotedString << Colon
    assert key(':"key":')[1] == "key"
