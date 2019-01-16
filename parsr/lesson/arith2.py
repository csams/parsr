import string


# A way of describing arithmetic:

# number = Many(digits)
# factor = ("(" + expr + ")") | number
# term = factor + Many("*/" + factor)
# expr = term + Many("+-" + term)


def number(pos, data):
    # number = Many(digits).map(to_int)
    rest = []

    # first build up a list
    while data[pos] and data[pos] in string.digits:
        rest.append(data[pos])
        pos += 1

    # then perform the operation
    return pos, int("".join(rest))


def factor(pos, data):
    # factor = ("(" + expr + ")") | number
    if data[pos] == "(":
        pos, res = expr(pos + 1, data)
        assert data[pos] == ")", "Unmatched paren."
        return pos + 1, res
    return number(pos, data)


def term(pos, data):
    # term = factor + Many("*/" + factor)
    pos, left = factor(pos, data)

    # first build up a list
    rest = []
    while data[pos] and data[pos] in "*/":
        op = data[pos]
        pos, right = factor(pos + 1, data)
        rest.append([op, right])

    # then perform the operations
    for op, right in rest:
        if op == "*":
            left *= right
        else:
            left /= right

    return pos, left


def expr(pos, data):
    # expr = term + Many("+-" + term)
    pos, left = term(pos, data)

    # first build up a list
    rest = []
    while data[pos] and data[pos] in "+-":
        op = data[pos]
        pos, right = term(pos + 1, data)
        rest.append([op, right])

    # then perform the operations
    for op, right in rest:
        if op == "+":
            left += right
        else:
            left -= right

    return pos, left


def evaluate(data):
    data = list(data)
    data.append(None)
    return expr(0, data)[1]
