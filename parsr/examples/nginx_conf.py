import string
from parsr import (EOF, Forward, LeftCurly, Lift, LineEnd, RightCurly, Many,
                   Number, OneLineComment, SemiColon, SingleQuotedString,
                   skip_none, String, WS, WSChar)
from parsr.query import Entry


def loads(data):
    return Top(data)[0]


def load(f):
    return loads(f.read())


def to_node(name, attrs, body):
    if body == ";":
        return Entry(name=name, attrs=attrs)
    return Entry(name=name, attrs=attrs, children=body)


Stmt = Forward()
Num = Number & (WSChar | LineEnd)
Comment = OneLineComment("#").map(lambda x: None)
BeginBlock = WS >> LeftCurly << WS
EndBlock = WS >> RightCurly << WS
Bare = String(set(string.printable) - (set(string.whitespace) | set("#;{}'\"")))
Name = WS >> String(string.ascii_letters + "_") << WS
Attr = WS >> (Num | Bare | SingleQuotedString) << WS
Attrs = Many(Attr)
Block = BeginBlock >> Many(Stmt).map(skip_none) << EndBlock
Stanza = (Lift(to_node) * Name * Attrs * (Block | SemiColon)) | Comment
Stmt <= WS >> Stanza << WS
Doc = Many(Stmt).map(skip_none)
Top = Doc + EOF
