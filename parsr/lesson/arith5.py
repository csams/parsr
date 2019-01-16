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
    digits = many(inset(string.digits))
    p = _map(digits, lambda x: int("".join(x)))
    return p(pos, data)


def factor(pos, data):
    # factor = ("(" + expr + ")") | number

    # the lambda plucks out the value between ( and )
    subexpr = _map(seq(char("("), expr, char(")")), lambda x: x[1])
    p = choice(subexpr, number)
    return p(pos, data)


def term(pos, data):
    # term = (factor + Many("*/" + factor)).map(oper)
    p = _map(seq(factor, many(seq(inset("*/"), factor))), oper)
    return p(pos, data)


def expr(pos, data):
    # expr = (term + Many("+-" + term)).map(oper)
    p = _map(seq(term, many(seq(inset("+-"), term))), oper)
    return p(pos, data)


def evaluate(data):
    data = list(data)
    data.append(None)
    return expr(0, data)[1]


def char(c):
    # match a char
    def process(pos, data):
        if data[pos] == c:
            return pos + 1, c
        raise Exception()
    return process


def inset(s):
    # match anything in a set
    def process(pos, data):
        v = set(s)
        if data[pos] in v:
            return pos + 1, data[pos]
        raise Exception()
    return process


def many(p):
    # continue matching until failure
    def process(pos, data):
        rest = []
        while True:
            try:
                pos, r = p(pos, data)
                rest.append(r)
            except Exception:
                break
        return pos, rest
    return process


def seq(*args):
    # match several things in a row
    def process(pos, data):
        rest = []
        for p in args:
            pos, r = p(pos, data)
            rest.append(r)
        return pos, rest
    return process


def choice(*args):
    # match one of several alternatives
    def process(pos, data):
        e = None
        for p in args:
            try:
                return p(pos, data)
            except Exception as ex:
                e = ex
        raise e
    return process


def _map(p, func):
    # apply a function to the result of a parser's match
    def process(pos, data):
        pos, res = p(pos, data)
        return pos, func(res)
    return process
