"""
multipath_conf parses multipath.conf configuration files into nested
dictionaries.
"""
import string
from parsr import (EOF, EOL, Forward, LeftCurly, Literal, RightCurly, Many,
                   Number, OneLineComment, String, QuotedString, WS)


def skip_none(x):
    return [i for i in x if i is not None]


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
LineEnd = (EOL | EOF) % "LineEnd"
Num = (Number << LineEnd) % "Num"
NULL = Literal("none", value=None) % "none"
Comment = (WS >> OneLineComment("#").map(lambda x: None)) % "Comment"
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


def loads(data):
    return Top(data)[0]


def load(f):
    return loads(f.read())
