from parseit import Forward, Literal


def test_forward():
    true = Forward()
    true <= Literal("True", value=True)
    assert true("True")
