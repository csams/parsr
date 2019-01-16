import string


# A way of describing arithmetic:

# number = Many(digits)
# factor = ("(" + expr + ")") | number
# term = factor + Many("*/" + factor)
# expr = term + Many("+-" + term)


class Parser:
    def __add__(self, other):
        return Seq(self, other)

    def __or__(self, other):
        return Choice(self, other)

    def map(self, func):
        return Map(self, func)

    def __call__(self, data):
        data = list(data)
        data.append(None)
        return self.process(0, data)[1]


# These classes correspond to functions of similar names in arith5.py. We use
# classes to take advantage of operator overloading.
class Char(Parser):
    # match a char
    def __init__(self, c):
        self.c = c

    def process(self, pos, data):
        if data[pos] == self.c:
            return pos + 1, self.c
        raise Exception()


class InSet(Parser):
    # match anything in a set
    def __init__(self, s):
        self.v = set(s)

    def process(self, pos, data):
        if data[pos] in self.v:
            return pos + 1, data[pos]
        raise Exception()


class Many(Parser):
    # continue matching until failure
    def __init__(self, p):
        self.p = p

    def process(self, pos, data):
        rest = []
        while True:
            try:
                pos, r = self.p.process(pos, data)
                rest.append(r)
            except Exception:
                break
        return pos, rest


class Seq(Parser):
    # match several things in a row
    def __init__(self, *args):
        self.args = list(args)

    def __add__(self, other):
        self.args.append(other)
        return self

    def process(self, pos, data):
        rest = []
        for p in self.args:
            pos, r = p.process(pos, data)
            rest.append(r)
        return pos, rest


class Choice(Parser):
    # match one of several alternatives
    def __init__(self, *args):
        self.args = list(args)

    def __or__(self, other):
        self.args.append(other)
        return self

    def process(self, pos, data):
        e = None
        for p in self.args:
            try:
                return p.process(pos, data)
            except Exception as ex:
                e = ex
        raise e


class Map(Parser):
    # apply a function to the result of a parser's match
    def __init__(self, p, func):
        self.p = p
        self.func = func

    def process(self, pos, data):
        pos, res = self.p.process(pos, data)
        return pos, self.func(res)


class Forward(Parser):
    # needed to "forward declare" some things since we're dealing with classes
    # and objects now instead of functions and can't just use them recursively.
    def __init__(self):
        self.p = None

    def __le__(self, other):
        self.p = other

    def process(self, pos, data):
        return self.p.process(pos, data)


def oper(args):
    left, rest = args
    for op, right in rest:
        if op == "*":
            left *= right
        elif op == "/":
            left /= right
        elif op == "+":
            left += right
        else:
            left -= right
    return left


expr = Forward()
number = Many(InSet(string.digits)).map(lambda x: int("".join(x)))
factor = (Char("(") + expr + Char(")")).map(lambda x: x[1]) | number
term = (factor + Many(InSet("*/") + factor)).map(oper)
expr <= (term + Many(InSet("+-") + term)).map(oper)


def evaluate(data):
    return expr(data)
