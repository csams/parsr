from parsr import Char, text_format


def test_text_format():
    ab = Char("a") + Char("b")
    assert text_format(ab)
