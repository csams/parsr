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
query of all child instances instead of a simple lookup.
"""
import operator
from functools import partial
from itertools import chain
from parsr.query.boolean import All, Any, Boolean, lift, lift2, TRUE


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
        while p.parent is not None and p.parent.parent is not None:
            p = p.parent
        return p

    @property
    def grandchildren(self):
        return list(chain.from_iterable(c.children for c in self.children))

    def find(self, *queries, roots=False):
        query = compile_queries(*queries)
        return find(query, self.children, roots=roots)

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
        return f"{self.name}: {self.string_value}"


class Result(Entry):
    def __init__(self, children=None):
        super().__init__()
        self.children = children or []

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

    def find(self, *queries, roots=False):
        query = compile_queries(*queries)
        return find(query, self.grandchildren, roots=roots)

    def __getitem__(self, query):
        if isinstance(query, (int, slice)):
            return self.children[query]
        query = desugar(query)
        return Result(children=[c for c in self.grandchildren if query.test(c)])

    def __repr__(self):
        return f"<Result>"


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


class EntryQuery:
    def __init__(self, expr):
        self.expr = expr

    def test(self, node):
        return self.expr.test(node)


class NameQuery(EntryQuery):
    def test(self, node):
        return self.expr.test(node.name)


class AttrQuery(EntryQuery):
    pass


class AllAttrQuery(AttrQuery):
    def test(self, n):
        return all(self.expr.test(a) for a in n.attrs)


class AnyAttrQuery(AttrQuery):
    def test(self, n):
        return any(self.expr.test(a) for a in n.attrs)


def any_(*exprs):
    return AnyAttrQuery(Any(*[desugar_attr(e) for e in exprs]))


def all_(*exprs):
    return AllAttrQuery(All(*[desugar_attr(e) for e in exprs]))


def desugar_name(q):
    if q is None:
        return NameQuery(TRUE)
    if isinstance(q, NameQuery):
        return q
    if isinstance(q, Boolean):
        return NameQuery(q)
    if callable(q):
        return NameQuery(lift(q))
    return NameQuery(lift(partial(operator.eq, q)))


def desugar_attr(q):
    if isinstance(q, Boolean):
        return q
    if callable(q):
        return lift(q)
    return lift(partial(operator.eq, q))


def desugar_attrs(q):
    if not q:
        return
    if len(q) == 1:
        q = q[0]
        return q if isinstance(q, AttrQuery) else AnyAttrQuery(desugar_attr(q))
    else:
        attr_queries = [desugar_attr(a) for a in q[1:]]
        return AnyAttrQuery(Any(*attr_queries))


def desugar(q):
    if isinstance(q, tuple):
        q = list(q)
        name_query = desugar_name(q[0])
        attrs_query = desugar_attrs(q[1:])
        if attrs_query:
            return All(name_query, attrs_query)
        return name_query
    return desugar_name(q)


def flatten(nodes):
    def inner(n):
        res = [n]
        res.extend(chain.from_iterable(inner(c) for c in n.children))
        return res
    return list(chain.from_iterable(inner(n) for n in nodes))


def compile_queries(*queries):
    def match(qs, nodes):
        q = desugar(qs[0])
        res = [n for n in nodes if q.test(n)]
        qs = qs[1:]
        if qs:
            gc = list(chain.from_iterable(n.children for n in res))
            return match(qs, gc)
        return res

    def inner(nodes):
        return Result(children=match(queries, nodes))
    return inner


def find(query, nodes, roots=False):
    results = []
    for n in flatten(nodes):
        results.extend(query([n]))
    if not roots:
        return Result(children=results)

    seen = set()
    top = []
    for r in results:
        root = r.root
        if root not in seen:
            seen.add(root)
            top.append(root)
    return Result(children=top)


lt = lift2(operator.lt)
le = lift2(operator.le)
eq = lift2(operator.eq)
gt = lift2(operator.gt)
ge = lift2(operator.ge)

contains = lift2(operator.contains)
startswith = lift2(str.startswith)
endswith = lift2(str.endswith)

ieq = lift2(operator.eq, ignore_case=True)
icontains = lift2(operator.contains, ignore_case=True)
istartswith = lift2(str.startswith, ignore_case=True)
iendswith = lift2(str.endswith, ignore_case=True)
