"""
Simple arithmetic with usual operator precedence and associativity.
"""
from parsr import Char, EOF, Forward, LeftParen, Many, Number, RightParen, WS


def op(args):
    ans, rest = args
    for op, arg in rest:
        if op == "+":
            ans += arg
        elif op == "-":
            ans -= arg
        elif op == "*":
            ans *= arg
        elif op == "/":
            ans /= arg
    return ans


expr = Forward()
factor = WS >> (Number | (LeftParen >> expr << RightParen)) << WS
term = (factor + Many((Char("*") | Char("/")) + factor)).map(op)
expr <= (term + Many((Char("+") | Char("-")) + term)).map(op)
Top = expr + EOF


def evaluate(e):
    return Top(e)[0]
