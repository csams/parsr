import logging
from parseit.tree import Node

log = logging.getLogger(__name__)


class Parser(Node):
    def __init__(self):
        super(Parser, self).__init__()
        self.name = None
        self.code = None

    def __or__(self, other):
        return Or(self, other)

    def __lshift__(self, other):
        return KeepLeft(self, other)

    def __rshift__(self, other):
        return KeepRight(self, other)

    def __and__(self, other):
        return And(self, other)

    def __mod__(self, name):
        self.name = name
        return self

    def sep_by(self, p):
        return SepBy(p, self)

    def between(self, other):
        return Between(self, other)

    def map(self, func):
        return Map(func, self)

    def __call__(self, data):
        if not self.code:
            from parseit.compiler import comp
            self.code = comp(self)
        return self.code(data)

    def __repr__(self):
        return self.name or super(Parser, self).__repr__()


class SepBy(Parser):
    def __init__(self, sep, parser):
        super(SepBy, self).__init__()
        parser = Lift(self.accumulate) * Opt(parser) * Many(sep >> parser)
        parser.set_parent(self)
        sep.set_parent(self)

    @staticmethod
    def accumulate(first, rest):
        results = [first] if first else []
        if rest:
            results.extend(rest)
        return results


class Literal(Parser):
    def __init__(self, chars, ignore_case=False):
        super(Literal, self).__init__()
        self.ignore_case = ignore_case
        self.chars = chars if not ignore_case else chars.lower()


class Keyword(Literal):
    def __init__(self, chars, value, ignore_case=False):
        super(Keyword, self).__init__(chars, ignore_case=ignore_case)
        self.value = value


class Binary(Parser):
    def __init__(self, left, right):
        super(Binary, self).__init__()
        left.set_parent(self)
        right.set_parent(self)


class And(Binary):
    pass


class Or(Binary):
    pass


class KeepLeft(Binary):
    pass


class KeepRight(Binary):
    pass


class Forward(Parser):
    def __init__(self):
        super(Forward, self).__init__()

    def __le__(self, other):
        self.set_children([other])


class Lift(Parser):
    def __init__(self, func, args=None):
        super(Lift, self).__init__()
        self.func = func
        args = args or []
        for a in args:
            a.set_parent(self)

    def __mul__(self, other):
        other.set_parent(self)
        return self

    def __repr__(self):
        return self.name or f"Lift({self.func.__name__})"


class Choice(Parser):
    def add_predicates(self, preds):
        for p in preds:
            p.set_parent(self)
        return self


class Many(Parser):
    def __init__(self, parser):
        super(Many, self).__init__()
        parser.set_parent(self)


class Many1(Many):
    pass


class Opt(Parser):
    def __init__(self, parser):
        super(Opt, self).__init__()
        parser.set_parent(self)


class Between(Parser):
    def __init__(self, parser, envelope):
        super(Between, self).__init__()
        parser = (envelope >> parser << envelope)
        parser.set_parent(self)


class Map(Parser):
    """ lifts (a -> b) to (Parser<a> -> Parser<b>) """
    def __init__(self, func, parser):
        super(Map, self).__init__()
        self.func = func
        parser.set_parent(self)

    def __repr__(self):
        return self.name or f"Map({self.func.__name__})"


class Char(Parser):
    def __init__(self, c, ignore_case=False):
        super(Char, self).__init__()
        self.ignore_case = ignore_case
        self.c = c if not ignore_case else c.lower()

    def __repr__(self):
        return f"{self.__class__.__name__}({self.c})"


class EscapedChar(Char):
    pass


class InSet(Parser):
    def __init__(self, values, label):
        super(InSet, self).__init__()
        self.cache = set(values)
        self.name = label
        self.label = label

    def __repr__(self):
        return f"InSet({self.name})"


class StringBuilder(Parser):
    def __init__(self, anyChar=None, lower=0):
        super(StringBuilder, self).__init__()
        self.lower = lower
        self.cache = anyChar.cache if anyChar else set()
        self.echars = anyChar.echars if anyChar else set()

    def add_cache(self, cache):
        self.cache |= cache

    def add_echars(self, echars):
        self.echars |= echars

    def add_echar(self, echar):
        self.echars.add(echar)


class AnyChar(Parser):
    def __init__(self):
        super(AnyChar, self).__init__()
        self.cache = set()
        self.echars = set()

    def add_anychar(self, ac):
        self.cache |= ac.cache
        self.echars |= ac.echars
        return self

    def add_char(self, char):
        self.cache.add(char.c)
        return self

    def add_inset(self, s):
        self.cache |= s.cache

    def add_echar(self, echar):
        self.echars.add(echar.c)

    def __add__(self, other):
        res = AnyChar()
        res.cache = self.cache | other.cache
        res.echars = self.echars | other.echars
        res.name = " | ".join([self.name, other.name]) if self.name else other.name
        return res

    def __repr__(self):
        return f"AnyChar({self.name})"
