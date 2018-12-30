from parseit.grammar import (QuotedString,
                             Number,
                             Colon,
                             Comma,
                             Forward,
                             Keyword,
                             LeftBracket,
                             LeftCurly,
                             RightBracket,
                             RightCurly)


def to_object(res):
    return {k: v for k, v in res}


TRUE = Keyword("true", True)
FALSE = Keyword("false", False)
NULL = Keyword("null", None)
JsonArray = Forward()
JsonObject = Forward()
JsonValue = QuotedString | Number | JsonObject | JsonArray | TRUE | FALSE | NULL % "Json Value"

KeyValuePair = (QuotedString << Colon) & JsonValue
JsonObject <= LeftCurly >> KeyValuePair.sep_by(Comma).map(to_object) << RightCurly
JsonArray <= LeftBracket >> JsonValue.sep_by(Comma) << RightBracket
