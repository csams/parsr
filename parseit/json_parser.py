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
                             Maybe,
                             Number,
                             RightBracket,
                             RightCurly,
                             QuotedString)


def to_object(res):
    return {k: v for k, v in res}


WS = Maybe(Many(AllWhitespace))
TRUE = Keyword("true", True)
FALSE = Keyword("false", False)
NULL = Keyword("null", None)
JsonArray = Forward()
JsonObject = Forward()
SimpleValue = (QuotedString | Number | JsonObject | JsonArray | TRUE | FALSE | NULL)
JsonValue = (WS >> SimpleValue << WS) % "Json Value"
Key = (QuotedString << Colon)
KeyValuePair = (WS >> Key) & JsonValue
JsonObject <= LeftCurly >> KeyValuePair.sep_by(WS >> Comma << WS).map(to_object) << RightCurly
JsonArray <= LeftBracket >> JsonValue.sep_by(WS >> Comma << WS) << RightBracket


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
