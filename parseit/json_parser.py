"""
This module handles primitive json parsing. It doesn't handle unicode or
numbers in scientific notation.
"""
from parseit import (Colon,
                     Comma,
                     Forward,
                     Keyword,
                     LeftBracket,
                     LeftCurly,
                     Number,
                     RightBracket,
                     RightCurly,
                     QuotedString,
                     WS)


JsonArray = Forward() % "Json Array"
JsonObject = Forward() % "Json Object"
TRUE = Keyword("true", True) % "TRUE"
FALSE = Keyword("false", False) % "FALSE"
NULL = Keyword("null", None) % "NULL"
SimpleValue = (QuotedString | Number | JsonObject | JsonArray | TRUE | FALSE | NULL) % "SimpleValue"
JsonValue = (WS >> SimpleValue << WS) % "Json Value"
Key = (QuotedString << Colon) % "Key"
KVPairs = (((WS >> Key) + JsonValue).sep_by(Comma)) % "KVPairs"
JsonArray <= (LeftBracket >> JsonValue.sep_by(Comma) << RightBracket) % "Json Array"
JsonObject <= (LeftCurly >> KVPairs.map(lambda res: {k: v for (k, v) in res}) << RightCurly) % "Json Object"


def loads(data):
    _, res = JsonValue(data)
    return res


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
        loads(data)
        pprint(loads(data))
    else:
        print("Pass a file.")
