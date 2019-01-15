import string
from parsr import (Char, EOF, EOL, EndTagName, Forward, FS, GT, LT, Letters,
                   LineEnd, Many, Number, OneLineComment, QuotedString,
                   skip_none, StartTagName, String, WS, WSChar)


def loads(data):
    return Top(data)[0]


def load(f):
    return loads(f.read())


Complex = Forward()
Num = Number & (WSChar | LineEnd)
Cont = Char("\\") + EOL
StartName = WS >> StartTagName(Letters) << WS
EndName = WS >> EndTagName(Letters) << WS
Comment = (WS >> OneLineComment("#")).map(lambda x: None)
AttrStart = Many(WSChar)
AttrEnd = (Many(WSChar) + Cont) | Many(WSChar)
BareAttr = String(set(string.printable) - (set(string.whitespace) | set("#;{}<>\\'\"")))
Attr = AttrStart >> (Num | BareAttr | QuotedString) << AttrEnd
Attrs = Many(Attr)
StartTag = (WS + LT) >> (StartName + Attrs) << (GT + WS)
EndTag = (WS + LT + FS) >> EndName << (GT + WS)
Simple = WS >> (Letters + Attrs) << WS
Stanza = Simple | Complex | Comment
Complex <= StartTag + Many(Stanza).map(skip_none) << EndTag
Doc = Many(Stanza).map(skip_none)
Top = Doc + EOF
