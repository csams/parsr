"""
json_parser handles primitive json parsing. It doesn't handle unicode or
numbers in scientific notation.
"""
from parsr import (Colon, Comma, EOF, Forward, Literal, LeftBracket, LeftCurly,
        Number, RightBracket, RightCurly, QuotedString, WS)


def loads(data):
    return Top(data)


def load(f):
    return loads(f.read())


JsonObject = Forward()
JsonArray = Forward()

TRUE = Literal("true", value=True)
FALSE = Literal("false", value=False)
NULL = Literal("null", value=None)

JsonValue = WS >> (Number | QuotedString | JsonObject | JsonArray | TRUE | FALSE | NULL) << WS
Key = QuotedString << WS << Colon
KVPairs = ((WS >> Key) + JsonValue).sep_by(Comma)
JsonArray <= (LeftBracket >> JsonValue.sep_by(Comma) << RightBracket)
JsonObject <= (LeftCurly >> KVPairs.map(dict) << RightCurly)
Top = JsonValue << EOF
