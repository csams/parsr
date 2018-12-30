import string
from parseit import (Many,  # noqa 401
                     Many1,
                     Maybe,
                     Char,
                     EscapedChar,
                     InSet,
                     Lift,
                     Forward,
                     Keyword,
                     Literal)


def make_string(results):
    return "".join(results)


def make_float(sign, int_part, dec_part):
    if dec_part:
        res = ".".join([int_part, dec_part[1]])
    else:
        res = int_part
    res = float(res)
    return -res if sign else res


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
Colon = Char(":")
Comma = Char(",")

DoubleQuote = Char("\"")
EscapedDoubleQuote = EscapedChar("\"")
SingleQuote = Char("'")
EscapedSingleQuote = EscapedChar("'")
Backslash = Char("\\")
String = Many1(Letter | Digit | Punctuation | Whitespace).map(make_string)
DoubleQuoteString = Many1(Letter | Digit | Whitespace | NonDoubleQuotePunctuation | EscapedDoubleQuote | Backslash)
SingleQuoteString = Many1(Letter | Digit | Whitespace | NonSingleQuotePunctuation | EscapedSingleQuote | Backslash)
QuotedString = (DoubleQuoteString.between(DoubleQuote) | SingleQuoteString.between(SingleQuote)).map(make_string)

_Float = Lift(make_float)
Number = _Float * Maybe(Char("-")) * Many1(Digit).map(make_string) * (Maybe(Char(".") & Many(Digit).map(make_string)))
