from parseit import Forward, Input, Keyword


def test_forward():
    true = Forward()
    true <= Keyword("true", True, ignore_case=True)
    assert true(Input("True")).value is True
