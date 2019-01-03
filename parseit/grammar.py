import string
from parseit import (Many,  # noqa 401
                     Many1,
                     Opt,
                     Char,
                     EscapedChar,
                     InSet,
                     Lift,
                     Forward,
                     Keyword,
                     Literal)


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
