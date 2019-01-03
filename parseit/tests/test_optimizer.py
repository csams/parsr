from parseit import AnyChar, Char, Many, StringBuilder
from parseit.optimizer import optimize


def test_optimize_or_chars():
    raw = Char("a") | Char("b") | Char("c")
    optimized = optimize(raw)
    assert isinstance(optimized, AnyChar)


def test_optimized_string():
    raw = Many(Char("a") | Char("b") | Char("c"))
    optimized = optimize(raw)
    assert isinstance(optimized, StringBuilder)
