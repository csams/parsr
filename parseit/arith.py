"""
Simple arithmetic with recursive definitions, operator precedence, and left
associativity.
"""
from parseit.grammar import Char, Forward, Many, Number


def reduce(args):
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
factor = (Number | (Char("(") >> expr << Char(")")))
term = (factor + Many((Char("*") | Char("/")) + factor)).map(reduce)
expr <= (term + Many((Char("+") | Char("-")) + term)).map(reduce)
