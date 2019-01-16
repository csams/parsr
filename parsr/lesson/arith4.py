import string


# A way of describing arithmetic:

# number = Many(digits)
# factor = ("(" + expr + ")") | number
# term = factor + Many("*/" + factor)
# expr = term + Many("+-" + term)


def oper(args):
    # externalize the operations to a function
    left, rest = args
    for op, right in rest:
        if op == "*":
            left *= right
        elif op == "/":
            left /= right
        elif op == "+":
            left += right
        else:
            left -= right
    return left


def number(pos, data):
    # number = Many(digits).map(to_int)

    # Many(string.digits)
    pos, res = many(pos, data, string.digits)
    # .map(lambda res: int("".join(res)))
    return pos, int("".join(res))


def factor(pos, data):
    # factor = ("(" + expr + ")") | number

    # (Char("(")
    if data[pos] == "(":
        # + expr
        pos, res = expr(pos + 1, data)
        # + Char(")"))
        assert data[pos] == ")", "Unmatched paren."
        return pos + 1, res
    # | number
    return number(pos, data)


def term(pos, data):
    # term = (factor + Many("*/" + factor)).map(oper)

    # factor
    pos, left = factor(pos, data)
    # + Many(Char("*/") + factor)
    pos, rest = many(pos, data, "*/", factor)
    # .map(oper)
    return pos, oper([left, rest])


def expr(pos, data):
    # expr = (term + Many("+-" + term)).map(oper)

    # term
    pos, left = term(pos, data)
    # + Many(Char("+-") + term)
    pos, rest = many(pos, data, "+-", term)
    # .map(oper)
    return pos, oper([left, rest])


def evaluate(data):
    data = list(data)
    data.append(None)
    return expr(0, data)[1]


def many(pos, data, cs, rhs=None):
    # ecapsulate the "build up a list" logic
    rest = []
    while data[pos] and data[pos] in cs:
        op = data[pos]
        if rhs:
            pos, right = rhs(pos + 1, data)
            rest.append([op, right])
        else:
            rest.append(op)
            pos += 1
    return pos, rest
