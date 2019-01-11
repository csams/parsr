"""
Simple arithmetic with recursive definitions, operator precedence, and left
associativity.
"""
from parseit import Char, EOF, Forward, LeftParen, Many, Number, RightParen


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
factor = (Number | (LeftParen >> expr << RightParen))
term = (factor + Many((Char("*") | Char("/")) + factor)).map(op)
expr <= (term + Many((Char("+") | Char("-")) + term)).map(op)
Top = expr + EOF
