import pytest

from parsr import Char


def test_not_followed_by():
    anb = Char("a") / Char("b")
    assert anb("ac") == "a"


def test_not_followed_by_fail():
    anb = Char("a") / Char("b")

    with pytest.raises(Exception):
        anb("ab")
