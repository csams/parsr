import copy
import operator
from functools import reduce
from itertools import groupby
from parseit import AnyChar, Char, Choice, EscapedChar, InSet, Or


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


def opt_character(choice):
    if all(isinstance(p, (AnyChar, Char, InSet)) for p in choice.children):
        ac = AnyChar()
        for p in choice.children:
            if isinstance(p, InSet):
                ac.add_inset(p)
            elif isinstance(p, EscapedChar):
                ac.add_echar(p)
            elif isinstance(p, Char):
                ac.add_char(p)
            elif isinstance(p, AnyChar):
                ac.add_anychar(p)

        ac.name = " | ".join([p.name or str(p) for p in choice.children])
        if choice.parent:
            choice.parent.replace_child(choice, ac)
        return ac
    return choice


def opt_choice(choice):
    choice = opt_inset(choice)
    choice = opt_character(choice)
    return choice


def optimize(tree):
    seen = set()
    tree = copy.deepcopy(tree)

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

        if isinstance(t, Choice):
            t = opt_choice(t)

        return t
    return inner(tree)
