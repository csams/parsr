"""
corosync_conf parses corosync configuration files into nested dictionaries.
"""
import string
from parsr import (Char, EOF, Forward, LeftCurly, LineEnd, Literal, RightCurly,
                   Many, Number, OneLineComment, String, QuotedString, WS,
                   WSChar)


def skip_none(x):
    return [i for i in x if i is not None]


Stmt = Forward()
Num = (Number & (WSChar | LineEnd))
NULL = Literal("none", value=None)
Sep = (Char(":") | Char("="))
Comment = (WS >> OneLineComment("#").map(lambda x: None))
BeginBlock = (WS >> LeftCurly << WS)
EndBlock = (WS >> RightCurly << WS)
Bare = String(set(string.printable) - (set(string.whitespace) | set("#{}'\"")))
Name = WS >> String(string.ascii_letters + "_") << WS
Value = WS >> (Num | NULL | QuotedString | Bare) << WS
Block = BeginBlock >> Many(Stmt).map(skip_none).map(dict) << EndBlock
Stanza = (Name + (Block | (Sep >> Value))) | Comment
Stmt <= WS >> Stanza << WS
Doc = Many(Stmt).map(skip_none).map(dict)
Top = Doc + EOF


def loads(data):
    return Top(data)[0]


def load(f):
    return loads(f.read())
