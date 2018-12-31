import logging
from parseit.tree import Node

log = logging.getLogger(__name__)


class Input(list):
    def __init__(self, *args):
        super(Input, self).__init__(*args)
        self.pos = 0

    def peek(self):
        return self[self.pos]

    def next(self):
        p = self.pos
        self.pos += 1
        c = self[p]
        return (p, c)


class Result(object):
    # A class is actually more performant than a namedtuple.
    def __init__(self, pos, value):
        self.pos = pos
        self.value = value

    def __repr__(self):
        return f"Result(pos={self.pos}, value={self.value})"


class Parser(Node):
    def __init__(self):
        super(Parser, self).__init__()
        self.name = None

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

    def __call__(self, data):
        parser = self.children[0]
        return parser(data)


class Literal(Parser):
    def __init__(self, chars, ignore_case=False):
        super(Literal, self).__init__()
        self.chars = chars
        parser = Accumulator([Char(c, ignore_case=ignore_case) for c in chars])
        parser.set_parent(self)

    def get_literal(self, data):
        parser = self.children[0]
        return "".join(parser(data).value)

    def __call__(self, data):
        pos = data.pos
        result = self.get_literal(data)
        return Result(pos, result)


class Keyword(Literal):
    def __init__(self, chars, value, ignore_case=False):
        super(Keyword, self).__init__(chars, ignore_case=ignore_case)
        self.value = value

    def __call__(self, data):
        pos = data.pos
        self.get_literal(data)
        return Result(pos, self.value)


class Accumulator(Parser):
    def __init__(self, parsers=None):
        super(Accumulator, self).__init__()
        for p in parsers:
            p.set_parent(self)

    def __call__(self, data):
        pos = data.pos
        results = [p(data).value for p in self.children]
        return Result(pos, results)


class Binary(Parser):
    def __init__(self, left, right):
        super(Binary, self).__init__()
        left.set_parent(self)
        right.set_parent(self)


class And(Binary):
    def __call__(self, data):
        left, right = self.children
        val = [left(data).value, right(data).value]
        return Result(data.pos, val)


class Or(Binary):
    def __call__(self, data):
        left, right = self.children
        try:
            return left(data)
        except Exception:
            pass
        return right(data)


class KeepLeft(Binary):
    def __call__(self, data):
        left, right = self.children
        res = left(data)
        right(data)
        return res


class KeepRight(Binary):
    def __call__(self, data):
        left, right = self.children
        left(data)
        return right(data)


class Forward(Parser):
    def __init__(self):
        super(Forward, self).__init__()

    def __le__(self, other):
        self.set_children([other])

    def __call__(self, data):
        return self.children[0](data)


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

    def __call__(self, data):
        pos = data.pos
        results = [p(data).value for p in self.children]
        res = self.func(*results)
        return Result(pos, res)

    def __repr__(self):
        return self.name or f"Lift({self.func.__name__})"


class Choice(Parser):
    def add_predicates(self, preds):
        for p in preds:
            p.set_parent(self)
        return self

    def __call__(self, data):
        msgs = []
        for p in self.children:
            try:
                return p(data)
            except Exception as ex:
                msgs.append(str(ex))
        raise Exception("; ".join(msgs))


class Many(Parser):
    def __init__(self, parser):
        super(Many, self).__init__()
        parser.set_parent(self)

    def __call__(self, data):
        results = []
        pos = data.pos
        parser = self.children[0]
        try:
            while True:
                results.append(parser(data).value)
        except Exception:
            pass
        return Result(pos, results)


class Many1(Many):
    def __call__(self, data):
        parser = self.children[0]
        pos = data.pos
        results = [parser(data).value]
        results.extend(super(Many1, self).__call__(data).value)
        return Result(pos, results)


class Opt(Parser):
    def __init__(self, parser):
        super(Opt, self).__init__()
        parser.set_parent(self)

    def __call__(self, data):
        pos = data.pos
        parser = self.children[0]
        try:
            return parser(data)
        except Exception:
            data.pos = pos
        return Result(pos, None)


class Between(Parser):
    def __init__(self, parser, envelope):
        super(Between, self).__init__()
        parser.set_parent(self)
        envelope.set_parent(self)

    def __call__(self, data):
        parser, envelope = self.children
        envelope(data)
        r = parser(data)
        envelope(data)
        return r


class Map(Parser):
    """ lifts (a -> b) to (Parser<a> -> Parser<b>) """
    def __init__(self, func, parser):
        super(Map, self).__init__()
        self.func = func
        parser.set_parent(self)

    def __call__(self, data):
        parser = self.children[0]
        pos = data.pos
        result = parser(data)
        return Result(pos, self.func(result.value))

    def __repr__(self):
        return self.name or f"Map({self.func.__name__})"


class Char(Parser):
    def __init__(self, c, ignore_case=False):
        super(Char, self).__init__()
        self.ignore_case = ignore_case
        self.c = c if not ignore_case else c.lower()

    def __call__(self, data):
        c = data.peek()
        if self.ignore_case:
            c = c.lower()
        if c == self.c:
            pos, n = data.next()
            return Result(pos, n)
        raise Exception(f"Expected {self.c} at offset {data.pos} Got {c} instead.")

    def __repr__(self):
        return f"{self.__class__.__name__}({self.c})"


class EscapedChar(Char):
    def __call__(self, data):
        e = data.peek()
        if e == "\\":
            pos, e = data.next()
            if data.peek() == self.c:
                _, c = data.next()
                return Result(pos - 1, c)
            data.pos -= 1
        raise Exception(f"Expected {self.c} at offset {data.pos}. Got {e} instead.")


class InSet(Parser):
    def __init__(self, values, label):
        super(InSet, self).__init__()
        self.cache = set(values)
        self.name = label
        self.label = label

    def __call__(self, data):
        c = data.peek()
        if c in self.cache:
            pos, c = data.next()
            return Result(pos, c)
        raise Exception(f"Expected a {self.label} at offset {data.pos}. Got {c} instead.")

    def __repr__(self):
        return f"InSet({self.name})"


class StringBuilder(Parser):
    def __init__(self, cache=None, echars=None):
        super(StringBuilder, self).__init__()
        self.cache = cache or set()

    def __call__(self, data):
        pos = data.pos
        results = []
        try:
            while data.peek() in self.cache:
                _, c = data.next()
                results.append(c)
        except Exception:
            pass
        res = "".join(results)
        return Result(pos, res)


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

    def __call__(self, data):
        p = data.peek()
        if p == "\\":
            pos, e = data.next()
            if data.peek() in self.echars:
                _, c = data.next()
                return Result(pos - 1, c)
            data.pos -= 1

        if p in self.cache:
            pos, c = data.next()
            return Result(pos, c)
        raise Exception()

    def __repr__(self):
        return f"AnyChar({self.name})"
