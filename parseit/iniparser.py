import string
from parseit import (Char, EOF, EOL, LeftBracket, Many, Number, OneLineComment,
                     Opt, Parser, RightBracket, String, WithIndent, WS)


class StringWithContinuation(Parser):
    def __init__(self, chars):
        super().__init__()
        self.add_child(String(chars) << (EOL | EOF))

    def process(self, pos, data, ctx):
        old = pos
        results = []
        while True:
            try:
                if ctx.col(pos) > ctx.indents[-1]:
                    pos, res = self.children[0].process(pos, data, ctx)
                    results.append(res)
                else:
                    pos = old
                    break
                old = pos
                pos, _ = WS.process(pos, data, ctx)
            except Exception:
                break
        ret = " ".join(results)
        return pos, ret


header_chars = (set(string.printable) - set(string.whitespace) - set("[]"))
key_chars = header_chars - set("=:")
value_chars = set(string.printable) - set("\n\r")

LineEnd = EOL | EOF

LeftEnd = (WS + LeftBracket + WS)
RightEnd = (WS + RightBracket + WS)
Header = LeftEnd >> String(header_chars) << RightEnd
Key = WS >> String(key_chars) << WS
Sep = Char("=") | Char(":")
Value = WS >> ((Number << LineEnd) | StringWithContinuation(value_chars))
KVPair = WithIndent(Key + Opt(Sep + Value, [None, None])).map(lambda a: (a[0], a[1][1]))
Comment = (WS >> (OneLineComment("#") | OneLineComment(";")).map(lambda x: None))
Line = Comment | KVPair
Section = Header + (Many(Line).map(lambda x: dict(filter(None, x))))
Doc = Many(Comment | Section).map(lambda x: dict(filter(None, x)))
Top = Doc + EOF


def loads(s):
    return Top(s)[0]


def load(f):
    return loads(f.read())
