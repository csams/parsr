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
