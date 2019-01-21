from parsr.examples.kvpairs import loads

DATA = """
# this is a config file
a = 15
b = a string
valueless
d = 1.14

# another section
+valueless  # no value
e = hello   # a value
#
"""


def test_kvpairs():
    d = loads(DATA)
    assert d
    assert d["a"] == 15
    assert d["b"] == "a string"
    assert d["valueless"] is None
    assert d["d"] == 1.14
    assert d["+valueless"] is None
    assert d["e"] == "hello"
