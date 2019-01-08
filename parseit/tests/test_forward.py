from parseit import Forward, Keyword


def test_forward():
    true = Forward()
    true <= Keyword("True", True)
    assert true("True")[1] is True
