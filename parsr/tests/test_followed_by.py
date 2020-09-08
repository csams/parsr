import pytest

from parsr import Char


def test_followed_by():
    ab = Char("a") & Char("b")
    assert ab("ab") == "a"


def test_followed_by_fail():
    ab = Char("a") & Char("b")
    with pytest.raises(Exception):
        ab("ac")
