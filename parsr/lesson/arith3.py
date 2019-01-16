import string


# A way of describing arithmetic:

# number = Many(digits)
# factor = ("(" + expr + ")") | number
# term = factor + Many("*/" + factor)
# expr = term + Many("+-" + term)


def oper(left, rest):
    # externalize the operations to a function
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
    rest = []

    # first build up a list
    while data[pos] and data[pos] in string.digits:
        rest.append(data[pos])
        pos += 1

    # then delegate to int to perform the operation
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

    # then delegate to oper to perform the operations
    return pos, oper(left, rest)


def expr(pos, data):
    # expr = term + Many("+-" + term)
    pos, left = term(pos, data)

    # first build up a list
    rest = []
    while data[pos] and data[pos] in "+-":
        op = data[pos]
        pos, right = term(pos + 1, data)
        rest.append([op, right])

    # then delegate to oper to perform the operations
    return pos, oper(left, rest)


def evaluate(data):
    data = list(data)
    data.append(None)
    return expr(0, data)[1]
