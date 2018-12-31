import operator
from functools import reduce
from itertools import groupby
from parseit import Choice, InSet, Or


def opt_or(tree):
    """ Combines nested Or trees into a single Choice """
    choice = Choice()

    for c in tree.children:
        if isinstance(c, (Or, Choice)):
            choice.add_predicates(c.children)
        else:
            choice.add_predicates([c])

    if tree.parent:
        tree.parent.replace_child(tree, choice)
    return choice


def opt_inset(choice):
    """ Combines adjacent InSet instances into a single InSet """
    children = []
    groups = groupby(choice.children, lambda x: x.__class__)
    for cls, objs in groups:
        if cls is not InSet:
            children.extend(objs)
        else:
            sets = [o for o in objs]
            if len(sets) == 1:
                children.extend(sets)
            else:
                labels = [s.label for s in sets]
                cache = reduce(operator.__or__, [s.cache for s in sets], set())
                children.append(InSet(cache, " | ".join(labels)))
    choice.set_children(children)
    return choice


def optimize(tree):
    seen = set()

    def inner(t):
        if t in seen:
            return t
        seen.add(t)
        children = []
        for c in t.children:
            children.append(inner(c))

        t.set_children(children)

        if isinstance(t, (Or, Choice)):
            t = opt_or(t)

        t = opt_inset(t)
        return t
    return inner(tree)
