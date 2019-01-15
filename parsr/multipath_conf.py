"""
multipath_conf parses multipath.conf configuration files into nested
dictionaries.
"""
import string
from parsr import (EOF, Forward, LeftCurly, Literal, LineEnd, RightCurly, Many,
                   Number, OneLineComment, skip_none, String, QuotedString, WS,
                   WSChar)


def loads(data):
    return Top(data)[0]


def load(f):
    return loads(f.read())


def to_dict(x):
    d = {}
    for k, v in x:
        if k in d:
            if not isinstance(d[k], list):
                d[k] = [d[k]]
            d[k].append(v)
        else:
            d[k] = v
    return d


Stmt = Forward()
Num = Number & (WSChar | LineEnd)
NULL = Literal("none", value=None)
Comment = (WS >> OneLineComment("#").map(lambda x: None))
BeginBlock = (WS >> LeftCurly << WS)
EndBlock = (WS >> RightCurly << WS)
Bare = String(set(string.printable) - (set(string.whitespace) | set("#{}'\"")))
Name = WS >> String(string.ascii_letters + "_") << WS
Value = WS >> (Num | NULL | QuotedString | Bare) << WS
Block = BeginBlock >> Many(Stmt).map(skip_none).map(to_dict) << EndBlock
Stanza = (Name + (Block | Value)) | Comment
Stmt <= WS >> Stanza << WS
Doc = Many(Stmt).map(skip_none).map(to_dict)
Top = Doc + EOF
