from parsr.query.dsl import all_, any_, lt, startswith, endswith
from parsr.query.model import from_dict, Node


simple_data = {
    "a": 3,
    "b": ["four", "five"],
    "c": [9, 15],
    "d": {"e": 9.7}
}


complex_tree = Node(name="root",
                    attrs=[1, 2, 3, 4],
                    children=[
                        Node(name="child", attrs=[1, 1, 2]),
                        Node(name="child", attrs=[1, 1, 2, 3, 5]),
                        Node(name="child", attrs=[1, 1, 3, 5, 9]),
                        Node(name="dog", attrs=["woof"], children=[
                            Node(name="puppy", attrs=["smol"]),
                            Node(name="puppy", attrs=["fluffy"]),
                            Node(name="kitten", attrs=["wut"]),
                        ])
                    ])


def test_from_dict():
    n = from_dict(simple_data)
    assert n
    assert len(n) == 4


def test_values():
    n = from_dict(simple_data)
    assert n["a"].value == 3

    assert n["b"].string_value == "four five"
    assert n["b"].value == ["four", "five"]

    assert n["c"].string_value == "9 15"
    assert n["c"].value == [9, 15]

    assert n["d"]["e"].value == 9.7


def test_complex():
    t = complex_tree
    assert len(t["child"]) == 3
    assert len(t["child", 3]) == 2
    assert len(t["child", all_(lt(3))]) == 1
    assert len(t["child", any_(1, 2)]) == 3
    assert len(t["child", any_(9)]) == 1
    assert len(t["child", any_(2, 5)]) == 3
    assert len(t["dog"]["puppy"]) == 2
    assert len(t[startswith("chi") & endswith("ld")]) == 3
    assert len(t[startswith("chi") | startswith("do")]) == 4
