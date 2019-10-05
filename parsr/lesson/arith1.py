# A way of describing arithmetic:
# number = Many(digits)
# factor = ("(" + expr + ")") | number
# term = factor + Many("*/" + factor)
# expr = term + Many("+-" + term)


def number(pos, data):
    # number = Many(digits).map(to_int)
    rest = []
    while data[pos] and data[pos].isdigit():
        rest.append(data[pos])
        pos += 1
    return pos, int("".join(rest))


def factor(pos, data):
    # factor = ("(" + expr + ")") | number
    if data[pos] == "(":
        pos, res = expr(pos + 1, data)  # don't forget to jump the "("
        assert data[pos] == ")", "Unmatched paren."
        return pos + 1, res  # don't forget to jump the ")"
    return number(pos, data)


def term(pos, data):
    # term = factor + Many("*/" + factor)
    pos, left = factor(pos, data)
    while data[pos] and data[pos] in "*/":
        op = data[pos]
        pos, right = factor(pos + 1, data)
        left = left * right if op == "*" else left / right
    return pos, left


def expr(pos, data):
    # expr = term + Many("+-" + term)
    pos, left = term(pos, data)
    while data[pos] and data[pos] in "+-":
        op = data[pos]
        pos, right = term(pos + 1, data)
        left = left + right if op == "+" else left - right
    return pos, left


def evaluate(data):
    data = list(data)
    data.append(None)
    return expr(0, data)[1]
