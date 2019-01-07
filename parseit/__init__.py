"""
parseit is a project I'm using to learn about parser combinators.
"""
import logging
import string
from parseit.tree import Node

log = logging.getLogger(__name__)


class Parser(Node):
    def __init__(self):
        super(Parser, self).__init__()
        self.name = None
        self._code = None
        self._tree = None

    @property
    def code(self):
        if not self._code:
            from parseit.compiler import comp
            self._code = comp(self)
        return self._code

    @property
    def optimized_tree(self):
        if not self._tree:
            from parseit.optimizer import optimize
            self._tree = optimize(self)
        return self._tree

    def __truediv__(self, other):
        return NotFollowedBy(self, other)

    def __or__(self, other):
        return Or(self, other)

    def __lshift__(self, other):
        return KeepLeft(self, other)

    def __rshift__(self, other):
        return KeepRight(self, other)

    def __add__(self, other):
        return Concat(self, other)

    def __and__(self, other):
        return FollowedBy(self, other)

    def __mod__(self, name):
        self.name = name
        return self

    def sep_by(self, p):
        return SepBy(p, self)

    def until(self, p):
        pass

    def between(self, other):
        return Between(self, other)

    def map(self, func):
        return Map(func, self)

    def __call__(self, data):
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


class NotFollowedBy(Parser):
    def __init__(self, parser, end):
        super(NotFollowedBy, self).__init__()
        parser.set_parent(self)
        end.set_parent(self)


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


class Concat(Binary):
    pass


class FollowedBy(Binary):
    pass


class Or(Binary):
    pass


class KeepLeft(Binary):
    pass


class KeepRight(Binary):
    pass


class Forward(Parser):
    """
    Forward declaration of a recursive non-terminal.

    .. code-block:: python
       expr = Forward()
       term = Forward()

       factor = (Number | (Char("(") >> expr << Char(")")))
       term <= ((factor + (Char("*") | Char("/")) + term) | factor)
       expr <= ((term + (Char("+") | Char("-")) + expr) | term)

    """
    def __init__(self):
        super(Forward, self).__init__()

    def __le__(self, other):
        self.set_children([other])


class Lift(Parser):
    """
    Parse several things in a row and then pass them to the positional
    arguments of Lift.

    .. code-block:: python
       def f(a, b, c):
           return a + b + c

    `Lift(f) * Number * Number * Number` will parse three numbers and then
    call f with them. The result of the entire expression is the result of f.

    `*` is meant to evoke applicative functor syntax:
    `pure(f) <*> Number <*> Number <*> Number`
    """
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
    """ Optimization of nested Or nodes. """
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


class OrUntil(Parser):
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


class EnclosedComment(Parser):
    def __init__(self, s, e):
        super(EnclosedComment, self).__init__()
        p = Literal(s) + Many(OneChar / Literal(e)) + OneChar + Literal(e)
        p.set_parent(self)


def make_string(results):
    if isinstance(results, list):
        return "".join(results)
    return results


def make_float(sign, int_part, dec_part):
    if dec_part:
        res = ".".join([int_part, dec_part[1]])
    else:
        res = int_part
    res = float(res)
    return -res if sign else res


def make_int(sign, num):
    res = int(num)
    return res if not sign else -res


_punc_set = set(string.punctuation)
Digit = InSet(string.digits, "digit")
NonZeroDigit = InSet(set(string.digits) - set(["0"]), "Non zero digit")
Letter = InSet(string.ascii_letters, "letter")
NonSingleQuotePunctuation = InSet(_punc_set - set("'\\"), "non single quote punctuation character")
NonDoubleQuotePunctuation = InSet(_punc_set - set("\"\\"), "non double quote punctuation character")
Punctuation = InSet(_punc_set, "punctuation character")
Printable = InSet(string.printable, "printable character")
OneChar = Printable
Whitespace = InSet(set(string.whitespace) - set("\n\r"), "whitespace except newlines")
EOL = InSet("\n\r", "newline")
AllWhitespace = (Whitespace | EOL)
LeftCurly = Char("{")
RightCurly = Char("}")
LeftBracket = Char("[")
RightBracket = Char("]")
LeftParen = Char("(")
RightParen = Char(")")
Colon = Char(":")
Comma = Char(",")
DoubleQuote = Char("\"")
EscapedDoubleQuote = EscapedChar('"')
SingleQuote = Char("'")
EscapedSingleQuote = EscapedChar("'")
Backslash = Char("\\")
String = Many(Letter | Digit | Punctuation | Whitespace) % "String"
DoubleQuoteString = Many(Letter | Digit | Whitespace | NonDoubleQuotePunctuation | EscapedDoubleQuote | Backslash) % "Double Quoted String"
SingleQuoteString = Many(Letter | Digit | Whitespace | NonSingleQuotePunctuation | EscapedSingleQuote | Backslash) % "Single Quoted String"
QuotedString = ((DoubleQuoteString.between(DoubleQuote) | SingleQuoteString.between(SingleQuote))) % "QuotedString"
_Float = Lift(make_float)
Number = (_Float * Opt(Char("-")) * Many1(Digit) * (Opt(Char(".") + Many(Digit)))) % "Number"
Integer = (Lift(make_int) * Opt(Char("-")) * Many1(Digit)) % "Integer"
