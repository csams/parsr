from parseit import Forward, Keyword


def test_forward():
    true = Forward()
    true <= Keyword("true", True, ignore_case=True)
    assert true("True")[1] is True
