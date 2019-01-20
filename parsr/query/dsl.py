"""
"""
import operator
from functools import partial

from parsr.query.boolean import All, Any, Boolean, Lift, TRUE, lift2


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
        return NameQuery(Lift(q))
    return NameQuery(Lift(partial(operator.eq, q)))


def desugar_attr(q):
    if isinstance(q, Boolean):
        return q
    if callable(q):
        return Lift(q)
    return Lift(partial(operator.eq, q))


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
