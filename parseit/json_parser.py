"""
This module handles primitive json parsing. It only vaguely conforms to the
spec.
"""
from parseit import Input
from parseit.grammar import (AllWhitespace,
                             Colon,
                             Comma,
                             Forward,
                             Keyword,
                             LeftBracket,
                             LeftCurly,
                             Many,
                             Number,
                             RightBracket,
                             RightCurly,
                             QuotedString)


WS = Many(AllWhitespace)
JsonArray = Forward()
JsonObject = Forward()

TRUE = Keyword("true", True)
FALSE = Keyword("false", False)
NULL = Keyword("null", None)
SimpleValue = (QuotedString | Number | JsonObject | JsonArray | TRUE | FALSE | NULL)
JsonValue = (WS >> SimpleValue << WS) % "Json Value"
Key = (QuotedString << Colon)
KVPairs = ((WS >> Key) & JsonValue).sep_by(Comma)
JsonObject <= LeftCurly >> KVPairs.map(lambda res: {k: v for (k, v) in res}) << RightCurly
JsonArray <= LeftBracket >> JsonValue.sep_by(Comma) << RightBracket


def loads(data):
    return JsonValue(Input(data)).value


def load(f):
    return loads(f.read())


if __name__ == "__main__":
    import sys
    from pprint import pprint

    if len(sys.argv) == 2:
        arg = sys.argv[1]
        if arg == "-":
            data = sys.stdin.read()
        else:
            with open(sys.argv[1]) as f:
                data = f.read()
        pprint(loads(data))
    else:
        print("Pass a file.")
