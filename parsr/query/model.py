from itertools import chain
from parsr.query.dsl import desugar


class Node:
    def __init__(self, name=None, attrs=None, children=None):
        self.name = name
        self.attrs = attrs or []
        self.children = children or []
        self.parent = None
        for c in self.children:
            c.parent = self

    @property
    def string_value(self):
        t = " ".join(["%s"] * len(self.attrs))
        return t % tuple(self.attrs)

    @property
    def value(self):
        if len(self.attrs) == 1:
            return self.attrs[0]
        return self.attrs or None

    @property
    def root(self):
        p = self
        while p and p.parent:
            p = p.parent
        return p

    @property
    def grandchildren(self):
        return list(chain.from_iterable(c.children for c in self.children))

    def __contains__(self, key):
        return len(self[key]) > 0

    def __len__(self):
        return len(self.children)

    def __getitem__(self, query):
        if isinstance(query, (int, slice)):
            return self.children[query]
        query = desugar(query)
        return Result(children=[c for c in self.children if query.test(c)])

    def __repr__(self):
        return f"Node('{self.name}')"


class Result(Node):
    @property
    def string_value(self):
        v = self.value
        t = " ".join(["%s"] * len(v))
        return t % tuple(v)

    @property
    def value(self):
        if len(self.children) == 1:
            return self.children[0].value
        raise Exception("More than one value to return.")

    def __getitem__(self, query):
        if isinstance(query, (int, slice)):
            return self.children[query]
        query = desugar(query)
        return Result(children=[c for c in self.grandchildren if query.test(c)])


def from_dict(orig):
    def inner(d):
        result = []
        for k, v in d.items():
            if isinstance(v, dict):
                result.append(Node(name=k, children=inner(v)))
            elif isinstance(v, list):
                res = [from_dict(i) if isinstance(i, dict) else i for i in v]
                if res:
                    if isinstance(res[0], Node):
                        result.append(Node(name=k, children=res))
                    else:
                        result.append(Node(name=k, attrs=res))
                else:
                    result.append(Node(name=k))
            else:
                result.append(Node(name=k, attrs=[v]))
        return result
    return Node(children=inner(orig))
