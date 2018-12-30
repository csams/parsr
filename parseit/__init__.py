import logging
import operator
from functools import reduce

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


class Parser(object):
    def __init__(self, name):
        self.name = name

    def __or__(self, other):
        return Or(self, other)

    def __rshift__(self, other):
        return KeepRight(self, other)

    def __lshift__(self, other):
        return KeepLeft(self, other)

    def __and__(self, other):
        return Accumulator(parsers=[self, other])

    def __mod__(self, name):
        self.name = name
        return self

    def between(self, other):
        return Between(self, other)

    def map(self, func):
        return Map(func, self)

    def sep_by(self, p):
        return SepBy(p, self)


class SepBy(Parser):
    @staticmethod
    def accumulate(first, rest):
        results = [first] if first else []
        if rest:
            results.extend(rest)
        return results

    def __init__(self, sep, parser):
        self.sep = sep
        self.parser = Lift(self.accumulate) * Opt(parser) * Many(sep >> parser)

    def __call__(self, data):
        return self.parser(data)


class Literal(Parser):
    def __init__(self, chars, ignore_case=False):
        self.chars = chars
        self.parser = reduce(operator.__and__, [Char(c, ignore_case=ignore_case) for c in chars])

    def get_literal(self, data):
        return "".join(self.parser(data).value)

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
        self.parsers = parsers or []

    def __and__(self, other):
        self.parsers.append(other)
        return self

    def __call__(self, data):
        pos = data.pos
        results = [p(data).value for p in self.parsers]
        return Result(pos, results)


class Binary(Parser):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return f"{self.__class__.__name__}({self.left}, {self.right})"


class KeepRight(Binary):
    def __call__(self, data):
        self.left(data)
        return self.right(data)


class KeepLeft(Binary):
    def __call__(self, data):
        res = self.left(data)
        self.right(data)
        return res


class Forward(Parser):
    def __init__(self):
        self.delegate = None

    def __le__(self, other):
        self.delegate = other

    def __call__(self, data):
        return self.delegate(data)


class Lift(Parser):
    def __init__(self, func, args=None):
        self.func = func
        self.bound_args = args or []

    def __mul__(self, other):
        args = list(self.bound_args)
        args.append(other)
        return Lift(self.func, args)

    def __call__(self, data):
        pos = data.pos
        results = [p(data).value for p in self.bound_args]
        res = self.func(*results)
        return Result(pos, res)


class Or(Parser):
    def __init__(self, left, right):
        self.predicates = [left, right]

    def __or__(self, other):
        self.predicates.append(other)
        return self

    def __call__(self, data):
        for p in self.predicates:
            try:
                return p(data)
            except Exception:
                pass
        raise Exception()

    def __repr__(self):
        return f"Or({self.predicates})"


class Many(Parser):
    def __init__(self, parser):
        self.parser = parser

    def __call__(self, data):
        results = []
        pos = data.pos
        try:
            while True:
                results.append(self.parser(data).value)
        except Exception:
            pass
        return Result(pos, results)

    def __repr__(self):
        return f"Many({self.parser})"


class Many1(Many):
    def __call__(self, data):
        pos = data.pos
        results = [self.parser(data).value]
        results.extend(super(Many1, self).__call__(data).value)
        return Result(pos, results)

    def __repr__(self):
        return f"Many1({self.parser})"


class Opt(Parser):
    def __init__(self, parser):
        self.parser = parser

    def __call__(self, data):
        pos = data.pos
        try:
            return self.parser(data)
        except Exception:
            data.pos = pos
        return Result(pos, None)


class Between(Parser):
    def __init__(self, parser, envelope):
        self.parser = parser
        self.envelope = envelope

    def __call__(self, data):
        self.envelope(data)
        r = self.parser(data)
        self.envelope(data)
        return r

    def __repr__(self):
        return f"Between({self.parser}, {self.envelope})"


class Map(Parser):
    """ lifts (a -> b) to (Parser<a> -> Parser<b>) """
    def __init__(self, func, parser):
        self.func = func
        self.parser = parser

    def __call__(self, data):
        pos = data.pos
        result = self.parser(data)
        return Result(pos, self.func(result.value))

    def __repr__(self):
        return f"Map({self.func}, {self.parser})"


class Char(Parser):
    def __init__(self, c, ignore_case=False):
        self.ignore_case = ignore_case
        self.c = c if not ignore_case else c.lower()

    def __call__(self, data):
        c = data.peek()
        if self.ignore_case:
            c = c.lower()
        if c == self.c:
            pos, n = data.next()
            return Result(pos, n)
        raise Exception(f"Expected {self.c} at offset {data.pos}")

    def __repr__(self):
        return f"{self.__class__.__name__}({self.c})"


class EscapedChar(Char):
    def __call__(self, data):
        e = data.peek()
        if e == "\\":
            pos, e = data.next()
            if data.peek() == self.c:
                _, c = data.next()
                return Result(pos - 1, str(f"{e}{c}"))
            data.pos -= 1
        raise Exception(f"Expected {self.c} at offset {data.pos}. Got {e} instead.")


class InSet(Parser):
    def __init__(self, values, label):
        self.cache = set(values)
        self.label = label

    def __call__(self, data):
        c = data.peek()
        if c in self.cache:
            pos, c = data.next()
            return Result(pos, c)
        raise Exception(f"Expected a {self.label} at offset {data.pos}. Got {c} instead.")

    def __repr__(self):
        return f"InSet({self.label})"
