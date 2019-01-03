import copy
import operator
from functools import reduce
from itertools import groupby
from parseit import (AnyChar,
                     Char,
                     Choice,
                     EscapedChar,
                     InSet,
                     Forward,
                     Many,
                     Many1,
                     Or,
                     StringBuilder)


class _Optimizer:
    def __init__(self, tree):
        self.tree = copy.deepcopy(tree)
        self.seen = set()

    def opt_char(self, p):
        """
        Converts InSet, Char, and EscapedChar to AnyChar.

        AnyChar is a general version of the above three and is a Monoid under
        set union of AnyChar.cache and set union of AnyChar.echars.

        Identity is AnyChar().
        Associative, so a + (b + c) == (a + b) + c.
        Closed since a + b also an AnyChar.
        """
        ac = AnyChar()
        if isinstance(p, InSet):
            ac.add_inset(p)
        elif isinstance(p, EscapedChar):
            ac.add_echar(p)
        elif isinstance(p, Char):
            ac.add_char(p)
        elif isinstance(p, AnyChar):
            ac.add_anychar(p)

        p.replace_with(ac)
        ac.name = p.name or str(p)
        return ac

    def opt_or(self, node):
        """
        Combines nested Or nodes into a single Choice.

        All Or instances are converted to Choices.
        """
        choice = Choice()

        for c in node.children:
            c = self.optimize(c)
            if isinstance(c, (Or, Choice)):
                choice.add_predicates(c.children)
            else:
                choice.add_predicates([c])

        choice = self.optimize(choice)
        node.replace_with(choice)
        return choice

    def fold_insets(self, choice):
        """
        Combines adjacent InSet instances into a single InSet.

        Insets are Monoids under set union of Inset.cache.
        """
        choice.set_children([self.optimize(c) for c in choice.children])
        children = []
        groups = groupby(choice.children, lambda x: x.__class__)
        for cls, objs in groups:
            if cls is not InSet:
                children.extend(objs)
            else:
                sets = list(objs)
                if len(sets) == 1:
                    children.extend(sets)
                else:
                    labels = [s.name for s in sets]
                    cache = reduce(operator.__or__, [s.cache for s in sets], set())
                    children.append(InSet(cache, " | ".join(labels)))
        choice.set_children(children)
        return choice

    def fold_anychars(self, choice):
        """
        Combines adjacent AnyChar instances into a single AnyChar.
        """
        choice.set_children([self.optimize(c) for c in choice.children])
        if all(isinstance(p, AnyChar) for p in choice.children):
            ac = sum(choice.children, AnyChar())
            choice.replace_with(ac)
            return ac
        return choice

    def opt_choice(self, choice):
        choice = self.fold_insets(choice)
        choice = self.fold_anychars(choice)
        return choice

    def opt_many(self, many, lower):
        many.set_children([self.optimize(many.children[0])])
        if isinstance(many.children[0], AnyChar):
            sb = StringBuilder(many.children[0], lower)
            many.replace_with(sb)
            return sb
        return many

    def optimize(self, t):
        if t in self.seen:
            return t

        if isinstance(t, Forward):
            # Don't recurse into Forward nodes, which are declarations of
            # recursive non terminals. Allow recursion into all other nodes
            # because optimization rules may need a chance to inspect them
            # several times.
            self.seen.add(t)

        if isinstance(t, Or):
            t = self.opt_or(t)
        elif isinstance(t, Choice):
            t = self.opt_choice(t)
        elif isinstance(t, Many1):
            t = self.opt_many(t, 1)
        elif isinstance(t, Many):
            t = self.opt_many(t, 0)
        elif isinstance(t, (InSet, Char, AnyChar)):
            t = self.opt_char(t)
        else:
            children = []
            for c in t.children:
                children.append(self.optimize(c))

            t.set_children(children)

        return t

    def __call__(self):
        return self.optimize(self.tree)


def optimize(tree):
    return _Optimizer(tree)()
