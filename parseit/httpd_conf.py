import string
from parseit import (Char, EOF, EOL, Forward, Letters, Many, Number,
                     OneLineComment, Parser, QuotedString, String, WS, WSChar)


def skip_none(x):
    return [i for i in x if i is not None]


class StartName(Parser):
    def __init__(self, parser=Letters):
        super().__init__()
        self.add_child(parser)

    def process(self, pos, data, ctx):
        pos, res = self.children[0].process(pos, data, ctx)
        ctx.tags.append(res)
        return pos, res


class EndName(Parser):
    def __init__(self, parser=Letters):
        super().__init__()
        self.add_child(parser)

    def process(self, pos, data, ctx):
        pos, res = self.children[0].process(pos, data, ctx)
        expect = ctx.tags.pop()
        if res != expect:
            msg = f"Expected {expect}. Got {res}."
            ctx.set(pos, msg)
            raise Exception(msg)
        return pos, res


StartName = WS >> StartName() << WS
EndName = WS >> EndName() << WS
Comment = (WS >> OneLineComment("#")).map(lambda x: None)
Cont = Char("\\") + EOL

LT = Char("<")
GT = Char(">")
FS = Char("/")

Complex = Forward()

AttrStart = Many(WSChar)
AttrEnd = (Many(WSChar) + Cont) | Many(WSChar)
BareAttr = String(set(string.printable) - (set(string.whitespace) | set("#;{}<>\\'\"")))
Attr = AttrStart >> (Number | BareAttr | QuotedString) << AttrEnd
Attrs = Many(Attr)

StartTag = (WS + LT) >> (StartName + Attrs) << (GT + WS)
EndTag = (WS + LT + FS) >> EndName << (GT + WS)
Simple = WS >> (Letters + Attrs) << WS
Stanza = Simple | Complex | Comment
Complex <= StartTag + Many(Stanza).map(skip_none) << EndTag
Doc = Many(Stanza).map(skip_none)
Top = Doc + EOF


def loads(data):
    return Top(data)[0]


def load(f):
    return loads(f.read())
