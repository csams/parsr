"""
json_parser handles primitive json parsing. It doesn't handle unicode or
numbers in scientific notation.
"""
from parsr import (Colon, Comma, EOF, Forward, Literal, LeftBracket, LeftCurly,
                   Number, RightBracket, RightCurly, QuotedString, WS)


JsonArray = Forward()
JsonObject = Forward()
TRUE = Literal("true", value=True) % "true"
FALSE = Literal("false", value=False) % "false"
NULL = Literal("null", value=None) % "null"
SimpleValue = (Number | QuotedString | JsonObject | JsonArray | TRUE | FALSE | NULL)
JsonValue = (WS >> SimpleValue << WS)
Key = (QuotedString << Colon)
KVPairs = (((WS >> Key) + JsonValue).sep_by(Comma))
JsonArray <= (LeftBracket >> JsonValue.sep_by(Comma) << RightBracket)
JsonObject <= (LeftCurly >> KVPairs.map(lambda res: {k: v for (k, v) in res}) << RightCurly)
Top = JsonValue + EOF


def loads(data):
    return Top(data)[0]


def load(f):
    return loads(f.read())
