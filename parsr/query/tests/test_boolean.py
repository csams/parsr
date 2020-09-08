from parsr.query.boolean import TRUE, FALSE, pred


def test_true():
    assert TRUE(None)


def test_false():
    assert not FALSE(None)


def test_bad_pred():
    def boom(v):
        raise Exception()

    boom = pred(boom)
    assert not boom(None)


def test_caseless_predicate():
    def is_blue(v):
        return v == "blue"

    is_blue = pred(is_blue, ignore_case=True)
    assert is_blue("BLUE")

    assert not is_blue(None)