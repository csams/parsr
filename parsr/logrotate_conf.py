import string
from parsr import (AnyChar, Choice, EOF, EOL, Forward, LeftCurly, LineEnd, Literal, Many,
                   Number, OneLineComment, Opt, QuotedString, RightCurly,
                   String, WS, WSChar)


scripts = set("postrotate prerotate firstaction lastaction preremove".split())


def skip_none(x):
    return [i for i in x if i is not None]


def to_dict(x):
    d = {}
    for i in x:
        name, attrs, body = i
        if body:
            for n in [name] + attrs:
                d[n] = body
        else:
            d[name] = attrs[0] if attrs else None
    return d


Spaces = Many(WSChar)
Bare = String(set(string.printable) - (set(string.whitespace) | set("#{}'\"")))
Num = Number & (WSChar | LineEnd)
Comment = OneLineComment("#").map(lambda x: None)

ScriptStart = WS >> Choice([Literal(s) for s in scripts]) << WS
ScriptEnd = Literal("endscript")
Line = (WS >> AnyChar.until(EOL) << WS).map(lambda x: "".join(x))
Lines = Line.until(ScriptEnd).map(lambda x: "\n".join(x))
Script = ScriptStart + Lines << ScriptEnd
Script = Script.map(lambda x: (x[0], [], x[1]))

Stanza = Forward()
BeginBlock = WS >> LeftCurly << WS
EndBlock = WS >> RightCurly
First = (Bare | QuotedString) << Spaces
Attr = Spaces >> (Num | Bare | QuotedString) << Spaces
Rest = Many(Attr)
Block = BeginBlock >> Many(Stanza).map(skip_none).map(to_dict) << EndBlock
Stmt = WS >> (Script | (First + Rest + Opt(Block))) << WS
Stanza <= WS >> (Stmt | Comment) << WS
Doc = Many(Stanza).map(skip_none).map(to_dict)
Top = Doc + EOF


def loads(data):
    return Top(data)[0]


def load(f):
    return loads(f.read())
