from parsr import EnclosedComment


def test_enclosed_comment():
    comment = EnclosedComment("/*", "*/")
    assert comment("/* howdy */")
