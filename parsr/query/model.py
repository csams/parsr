"""
This module allows parsers to construct data with a common representation that
is compatible with parsr.query.dsl.

The model allows duplicate keys, and it allows values with *unnamed* attributes
and recursive substructure. This is a common model for many kinds of
configuration.

Simple key/value pairs can be represented as a key with a value that has a
single attribute. Most dictionary shapes used to represent configuration are
made of keys with simple values (key/single attr), lists of simple values
(key/multiple attrs), or nested dictionaries (key/substructure).

Something like XML allows duplicate keys, and it allows values to have named
attributes and substructure. This module doesn't cover that case.

`Entry` and `Result` have overloaded __getitem__ functions that respond to
queries from the parsr.query.dsl module. This allows their instances to be
accessed like simple dictionaries, but the key passed to `[]` is converted to a
query of all child instances instead of a simple lookup. See `parsr.query.dsl`
for more details.
"""
from itertools import chain
from parsr.query.dsl import desugar


class Entry:
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
        return f"Entry('{self.name}')"


class Result(Entry):
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
                result.append(Entry(name=k, children=inner(v)))
            elif isinstance(v, list):
                res = [from_dict(i) if isinstance(i, dict) else i for i in v]
                if res:
                    if isinstance(res[0], Entry):
                        result.append(Entry(name=k, children=res))
                    else:
                        result.append(Entry(name=k, attrs=res))
                else:
                    result.append(Entry(name=k))
            else:
                result.append(Entry(name=k, attrs=[v]))
        return result
    return Entry(children=inner(orig))
