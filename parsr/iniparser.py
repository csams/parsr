"""
iniparser parses ini files into a python dictionary of dictionaries. Duplicate
keys in a section convert the value to a list. Numbers are automatically
converted to python ints or floats. Line continuations based on hanging indents
are supported. Sections inherit keys from the `[DEFAULT]` section. All keys are
converted to lower case. Variable interpolation is not supported.
"""
import string
from parsr import (Char, EOF, EOL, LeftBracket, Many, Number, OneLineComment,
                   Opt, Parser, RightBracket, String, WithIndent, WS)


class HangingString(Parser):
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


def to_dict(x):
    x = dict([i for i in x if i is not None])
    d = {}
    for k, v in x.items():
        k = k.lower()
        if k in d:
            if not isinstance(d[k], list):
                d[k] = [d[k]]
            d[k].append(v)
        else:
            d[k] = v
    return d


header_chars = (set(string.printable) - set(string.whitespace) - set("[]"))
key_chars = header_chars - set("=:")
value_chars = set(string.printable) - set("\n\r")

LineEnd = EOL | EOF
LeftEnd = (WS + LeftBracket + WS)
RightEnd = (WS + RightBracket + WS)
Header = LeftEnd >> String(header_chars) << RightEnd
Key = WS >> String(key_chars) << WS
Sep = Char("=") | Char(":")
Value = WS >> ((Number << LineEnd) | HangingString(value_chars))
KVPair = WithIndent(Key + Opt(Sep + Value, default=[None, None])).map(lambda a: (a[0], a[1][1]))
Comment = (WS >> (OneLineComment("#") | OneLineComment(";")).map(lambda x: None))
Line = Comment | KVPair
Section = Header + (Many(Line).map(to_dict))
Doc = Many(Comment | Section).map(to_dict)
Top = Doc + EOF


def loads(s):
    res = Top(s)[0]
    default = res.get("default")
    if default:
        default_keys = set(default)
        for header, items in res.items():
            if header != "default":
                missing = default_keys - set(items)
                for m in missing:
                    items[m] = default[m]

    return res


def load(f):
    return loads(f.read())
