from parsr.query import Entry


complex_tree = Entry(name="root",
                    attrs=[1, 2, 3, 4],
                    children=[
                        Entry(name="child", attrs=[1, 1, 2]),
                        Entry(name="child", attrs=[1, 1, 2, 3, 5]),
                        Entry(name="child", attrs=[1, 1, 3, 5, 9]),
                        Entry(name="dog", attrs=["woof"], children=[
                            Entry(name="puppy", attrs=["smol"]),
                            Entry(name="puppy", attrs=["fluffy"]),
                            Entry(name="kitten", attrs=["wut"]),
                        ])
                    ])


def test_find_leaves():
    res = complex_tree.find("puppy")
    assert len(res) == 2
    assert res[0].name == "puppy"
    assert res[1].name == "puppy"


def test_find_roots():
    res = complex_tree.find("puppy", roots=True)
    assert len(res) == 1
    assert res[0].name == "root"


def test_find_chain():
    res = complex_tree.find("dog").find("puppy")
    assert len(res) == 2
