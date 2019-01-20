class Boolean:
    def __and__(self, other):
        return All(self, other)

    def __or__(self, other):
        return Any(self, other)

    def __invert__(self):
        return Not(self)

    def test(self, value):
        return True

    def __call__(self, value):
        return self.test(value)


class TRUE(Boolean):
    pass


class FALSE(Boolean):
    def test(self, value):
        return False


class Any(Boolean):
    def __init__(self, *exprs):
        self.exprs = list(exprs)

    def __or__(self, other):
        self.exprs.append(other)
        return self

    def test(self, value):
        return any(q.test(value) for q in self.exprs)


class All(Boolean):
    def __init__(self, *exprs):
        self.exprs = list(exprs)

    def __and__(self, other):
        self.exprs.append(other)
        return self

    def test(self, value):
        return all(q.test(value) for q in self.exprs)


class Not(Boolean):
    def __init__(self, query):
        self.query = query

    def test(self, value):
        return not self.query.test(value)


class Lift(Boolean):
    def __init__(self, func):
        self.func = func

    def test(self, value):
        return self.func(value)


class CaseQuery(Lift):
    def __init__(self, func, rhs=None, ignore_case=False):
        super().__init__(func)
        self.rhs = rhs
        self.ignore_case = ignore_case

    def test(self, lhs):
        if self.ignore_case and isinstance(lhs, str):
            if self.rhs is not None:
                return self.func(lhs.lower(), self.rhs)
            return self.func(lhs.lower())
        if self.rhs is not None:
            return self.func(lhs, self.rhs)
        return self.func(lhs)


def lift(func, ignore_case=False):
    return CaseQuery(func, ignore_case=ignore_case)


def lift2(func, ignore_case=False):
    def inner(val):
        if ignore_case and isinstance(val, str):
            val = val.lower()
        return CaseQuery(func, rhs=val, ignore_case=ignore_case)
    return inner


Or = Any
And = All
