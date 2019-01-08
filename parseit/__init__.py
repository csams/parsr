import string
from io import StringIO


class Node:
    def __init__(self):
        self.children = []

    def add_child(self, child):
        self.children.append(child)
        return self

    def set_children(self, children):
        self.children.clear()
        for c in children:
            self.add_child(c)
        return self

    def __repr__(self):
        return self.__class__.__name__


def text_format(tree):
    out = StringIO()
    tab = " " * 2
    seen = set()

    def inner(cur, prefix):
        print(prefix + str(cur), file=out)
        if cur in seen:
            return

        seen.add(cur)

        next_prefix = prefix + tab
        for c in cur.children:
            inner(c, next_prefix)

    inner(tree, "")
    out.seek(0)
    return out.read()


def render(tree):
    print(text_format(tree))


class Parser(Node):
    def __init__(self):
        super().__init__()
        self.name = None

    def map(self, func):
        return Map(self, func)

    @staticmethod
    def accumulate(first, rest):
        results = [first] if first else []
        if rest:
            results.extend(rest)
        return results

    def sep_by(self, sep):
        return Lift(self.accumulate) * Opt(self) * Many(sep >> self)

    def __or__(self, other):
        return Choice(self, other)

    def __and__(self, other):
        return FollowedBy(self, other)

    def __truediv__(self, other):
        return NotFollowedBy(self, other)

    def __add__(self, other):
        return Seq(self, other)

    def __lshift__(self, other):
        return KeepLeft(self, other)

    def __rshift__(self, other):
        return KeepRight(self, other)

    def __mod__(self, name):
        self.name = name
        return self

    def __call__(self, data):
        data = list(data)
        data.append(None)
        return self.process(0, data)

    def __repr__(self):
        return self.name or f"{self.__class__.__name__}"


class Choice(Parser):
    def __init__(self, left, right):
        super().__init__()
        self.set_children([left, right])

    def __or__(self, other):
        return self.add_child(other)

    def process(self, pos, data):
        ex = None
        for c in self.children:
            try:
                return c.process(pos, data)
            except Exception as e:
                ex = e
        raise ex


class Seq(Parser):
    def __init__(self, left, right):
        super().__init__()
        self.set_children([left, right])

    def __add__(self, other):
        return self.add_child(other)

    def process(self, pos, data):
        results = []
        for p in self.children:
            pos, res = p.process(pos, data)
            results.append(res)
        return pos, results


class Many(Parser):
    def __init__(self, p):
        super().__init__()
        self.add_child(p)

    def process(self, pos, data):
        results = []
        p = self.children[0]
        while True:
            try:
                pos, res = p.process(pos, data)
                results.append(res)
            except Exception:
                break
        return pos, results


class FollowedBy(Parser):
    def __init__(self, p, f):
        super().__init__()
        self.set_children([p, f])

    def process(self, pos, data):
        left, right = self.children
        new, res = left.process(pos, data)
        try:
            right.process(new, data)
        except Exception:
            raise
        else:
            return new, res


class NotFollowedBy(Parser):
    def __init__(self, p, f):
        super().__init__()
        self.set_children([p, f])

    def process(self, pos, data):
        left, right = self.children
        new, res = left.process(pos, data)
        try:
            right.process(new, data)
        except Exception:
            return new, res
        else:
            raise Exception(f"{right} can't follow {left} at {pos}")


class KeepLeft(Parser):
    def __init__(self, left, right):
        super().__init__()
        self.set_children([left, right])

    def process(self, pos, data):
        left, right = self.children
        pos, res = left.process(pos, data)
        pos, _ = right.process(pos, data)
        return pos, res


class KeepRight(Parser):
    def __init__(self, left, right):
        super().__init__()
        self.set_children([left, right])

    def process(self, pos, data):
        left, right = self.children
        pos, _ = left.process(pos, data)
        pos, res = right.process(pos, data)
        return pos, res


class Opt(Parser):
    def __init__(self, p, default=None):
        super().__init__()
        self.set_children([p])
        self.default = default

    def process(self, pos, data):
        try:
            return self.children[0].process(pos, data)
        except Exception:
            return pos, self.default


class Map(Parser):
    def __init__(self, p, func):
        super().__init__()
        self.add_child(p)
        self.func = func

    def process(self, pos, data):
        pos, res = self.children[0].process(pos, data)
        return pos, self.func(res)

    def __repr__(self):
        return f"Map({self.func})"


class Lift(Parser):
    def __init__(self, func):
        super().__init__()
        self.func = func

    def __mul__(self, other):
        return self.add_child(other)

    def process(self, pos, data):
        results = []
        for c in self.children:
            pos, res = c.process(pos, data)
            results.append(res)
        return pos, self.func(*results)


class Forward(Parser):
    def __init__(self):
        super().__init__()
        self.delegate = None

    def __le__(self, delegate):
        self.set_children([delegate])

    def process(self, pos, data):
        return self.children[0].process(pos, data)


class Char(Parser):
    def __init__(self, char):
        super().__init__()
        self.char = char

    def process(self, pos, data):
        if data[pos] == self.char:
            return (pos + 1, self.char)
        raise Exception(f"Require {self.char} at {pos}.")

    def __repr__(self):
        return f"Char('{self.char}')"


class InSet(Parser):
    def __init__(self, s, name=None):
        super().__init__()
        self.values = set(s)
        self.name = name

    def process(self, pos, data):
        c = data[pos]
        if c in self.values:
            return (pos + 1, c)
        raise Exception(f"Require {self} at {pos}.")


class Literal(Parser):
    def __init__(self, chars):
        super().__init__()
        self.chars = chars

    def process(self, pos, data):
        old = pos
        for c in self.chars:
            if data[pos] == c:
                pos += 1
            else:
                raise Exception(f"Expected {self.chars} at pos {old}.")
        return pos, self.chars


class Keyword(Literal):
    def __init__(self, chars, value):
        super().__init__(chars)
        self.value = value

    def process(self, pos, data):
        pos, _ = super().process(pos, data)
        return pos, self.value


class String(Parser):
    def __init__(self, chars, echars=None):
        super().__init__()
        self.chars = set(chars)
        self.echars = set(echars) if echars else set()

    def process(self, pos, data):
        results = []
        p = data[pos]
        while p in self.chars or p == "\\":
            if p == "\\" and data[pos + 1] in self.echars:
                results.append(data[pos + 1])
                pos += 2
            elif p in self.chars:
                results.append(p)
                pos += 1
            else:
                break
            p = data[pos]
        if not results:
            raise Exception(f"Expected one of {self.chars} at {pos}")
        return pos, "".join(results)


class EnclosedComment(Parser):
    def __init__(self, s, e):
        super().__init__()
        Start = Literal(s)
        End = Literal(e)
        p = (Start + Many(AnyChar / End) + AnyChar + End).map(self.combine)
        self.add_child(p)

    @staticmethod
    def combine(c):
        return c[0] + "".join(c[1]) + "".join(c[2:])

    def process(self, pos, data):
        return self.children[0].process(pos, data)


class OneLineComment(Parser):
    def __init__(self, s):
        super().__init__()
        Start = Literal(s)
        p = ((Start + Many(AnyChar / EOL) + AnyChar + EOL) | (Start + EOL)).map(self.combine)
        self.add_child(p)

    @staticmethod
    def combine(c):
        if len(c) == 2:
            return "".join(c)
        c[1] = "".join(c[1])
        return "".join(c)

    def process(self, pos, data):
        return self.children[0].process(pos, data)


def make_number(sign, int_part, frac_part):
    tmp = sign + int_part + ("".join(frac_part) if frac_part else "")
    return float(tmp) if "." in tmp else int(tmp)


LeftCurly = Char("{")
RightCurly = Char("}")
LeftBracket = Char("[")
RightBracket = Char("]")
LeftParen = Char("(")
RightParen = Char(")")
Colon = Char(":")
Comma = Char(",")

AnyChar = InSet(string.printable)
Digit = InSet(string.digits) % "Digit"
Digits = String(string.digits) % "Digits"
WSChar = InSet(set(string.whitespace) - set("\n\r")) % "Whitespace"
EOL = InSet("\n\r") % "EOL"
WS = Many(InSet(string.whitespace))
Number = Lift(make_number) * Opt(Char("-"), "") * Digits * Opt(Char(".") + Digits)

SingleQuotedString = Char("'") >> String(set(string.printable) - set("'"), "'") << Char("'")
DoubleQuotedString = Char('"') >> String(set(string.printable) - set('"'), '"') << Char('"')
QuotedString = (DoubleQuotedString | SingleQuotedString) % "Quoted String"
