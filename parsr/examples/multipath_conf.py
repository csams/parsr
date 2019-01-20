"""
multipath_conf parses multipath.conf configuration files into nested
dictionaries.
"""
import string
from parsr import (EOF, Forward, LeftCurly, Lift, Literal, LineEnd, RightCurly,
                   Many, Number, OneLineComment, skip_none, String,
                   QuotedString, WS, WSChar)
from parsr.query.model import Node


def loads(data):
    return Node(children=Top(data)[0])


def load(f):
    return loads(f.read())


def to_node(name, rest):
    if isinstance(rest, list):
        return Node(name=name, children=rest)
    return Node(name=name, attrs=rest)


Stmt = Forward()
Num = Number & (WSChar | LineEnd)
NULL = Literal("none", value=None)
Comment = (WS >> OneLineComment("#").map(lambda x: None))
BeginBlock = (WS >> LeftCurly << WS)
EndBlock = (WS >> RightCurly << WS)
Bare = String(set(string.printable) - (set(string.whitespace) | set("#{}'\"")))
Name = WS >> String(string.ascii_letters + "_") << WS
Value = WS >> (Num | NULL | QuotedString | Bare) << WS
Block = BeginBlock >> Many(Stmt).map(skip_none) << EndBlock
Stanza = (Lift(to_node) * Name * (Block | Value)) | Comment
Stmt <= WS >> Stanza << WS
Doc = Many(Stmt).map(skip_none)
Top = Doc + EOF
