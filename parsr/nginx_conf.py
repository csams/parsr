import string
from parsr import (EOF, Forward, LeftCurly, Lift, RightCurly, Many, Number,
                   OneLineComment, SemiColon, SingleQuotedString, String, WS)


class Value:
    def __init__(self, name, attrs, body):
        self.name = name
        self.attrs = attrs
        self.body = body if body != ";" else []


def skip_none(x):
    return [i for i in x if i is not None]


Stmt = Forward()
Comment = OneLineComment("#").map(lambda x: None)
BeginBlock = WS >> LeftCurly << WS
EndBlock = WS >> RightCurly << WS
Bare = String(set(string.printable) - (set(string.whitespace) | set("#;{}'\"")))
Name = WS >> String(string.ascii_letters + "_") << WS
Attr = WS >> (Number | Bare | SingleQuotedString) << WS
Attrs = Many(Attr)
Block = BeginBlock >> Many(Stmt).map(skip_none) << EndBlock
Stanza = (Lift(Value) * Name * Attrs * (Block | SemiColon)) | Comment
Stmt <= WS >> Stanza << WS
Doc = Many(Stmt).map(skip_none)
Top = Doc + EOF


def loads(data):
    return Top(data)[0]


def load(f):
    return loads(f.read())
