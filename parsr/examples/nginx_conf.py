import string
from parsr import (Char, EOF, Forward, LeftCurly, Lift, LineEnd, RightCurly,
        Many, Number, OneLineComment, Parser, PosMarker, SemiColon,
        SingleQuotedString, skip_none, String, WS, WSChar)
from parsr.query import Entry


def loads(data):
    return Top(data)[0]


def load(f):
    return loads(f.read())


def to_entry(name, attrs, body):
    if body == ";":
        return Entry(name=name.value, attrs=attrs, lineno=name.lineno)
    return Entry(name=name.value, attrs=attrs, children=body, lineno=name.lineno)


class EmptyQuotedString(Parser):
    def __init__(self, chars):
        super().__init__()
        parser = Char("'") >> String(set(chars) - set("'"), "'", 0) << Char("'")
        self.add_child(parser)

    def process(self, pos, data, ctx):
        return self.children[0].process(pos, data, ctx)


name_chars = string.ascii_letters + "_"
Stmt = Forward()
Num = Number & (WSChar | LineEnd)
Comment = OneLineComment("#").map(lambda x: None)
BeginBlock = WS >> LeftCurly << WS
EndBlock = WS >> RightCurly << WS
Bare = String(set(string.printable) - (set(string.whitespace) | set("#;{}'\"")))
Name = WS >> PosMarker(String(name_chars) | EmptyQuotedString(name_chars)) << WS
Attr = WS >> (Num | Bare | SingleQuotedString) << WS
Attrs = Many(Attr)
Block = BeginBlock >> Many(Stmt).map(skip_none) << EndBlock
Stanza = (Lift(to_entry) * Name * Attrs * (Block | SemiColon)) | Comment
Stmt <= WS >> Stanza << WS
Doc = Many(Stmt).map(skip_none)
Top = Doc + EOF
