import logging
from collections import namedtuple
from parseit import Input
from parseit.optimizer import optimize
from parseit import (And,
                     AnyChar,
                     Between,
                     Char,
                     Choice,
                     EscapedChar,
                     Forward,
                     InSet,
                     KeepLeft,
                     KeepRight,
                     Keyword,
                     Lift,
                     Literal,
                     Many,
                     Many1,
                     Map,
                     Opt,
                     Or,
                     SepBy,
                     StringBuilder)

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


def intersperse(lst, item):
    result = [item] * (len(lst) * 2 - 1)
    result[0::2] = lst
    return result


AND = 0
ANY_CHAR = 1
BETWEEN = 2
CHAR = 3
CHOICE = 4
ESCAPED_CHAR = 5
FORWARD = 6
IN_SET = 7
KEEP_LEFT = 8
KEEP_RIGHT = 9
KEYWORD = 10
LIFT = 11
LITERAL = 12
MANY = 13
MANY1 = 14
MAP = 15
OPT = 16
OR = 17
SEP_BY = 18
STRINGBUILDER = 19
PUSH_ACC = 22
STORE_ACC = 26
POP_STACK = 28
JUMPIFFAILURE = 23
JUMPIFSUCCESS = 24

OP_CODES = {
    And: AND,
    AnyChar: ANY_CHAR,
    Between: BETWEEN,
    Char: CHAR,
    Choice: CHOICE,
    EscapedChar: ESCAPED_CHAR,
    Forward: FORWARD,
    InSet: IN_SET,
    KeepLeft: KEEP_LEFT,
    KeepRight: KEEP_RIGHT,
    Keyword: KEYWORD,
    Lift: LIFT,
    Literal: LITERAL,
    Many: MANY,
    Many1: MANY1,
    Map: MAP,
    Opt: OPT,
    Or: OR,
    SepBy: SEP_BY,
    StringBuilder: STRINGBUILDER,
}

Op = namedtuple("Op", field_names="op data")


def comp(tree):
    seen = set()

    def inner(t):
        if t in seen:
            return

        if isinstance(t, Forward):
            seen.add(t)

        type_ = type(t)
        if type_ is InSet:
            return [Op(OP_CODES[type_], (t.cache, t.name))]

        elif type_ in (Char, EscapedChar):
            return [Op(OP_CODES[type_], t.c)]

        elif type_ in (AnyChar, StringBuilder):
            return [Op(OP_CODES[type_], (t.cache, t.echars, t.name))]

        elif type_ is Map:
            program = inner(t.children[0])
            program.append(Op(OP_CODES[type_], t.func))
            return program

        elif type_ is Opt:
            program = inner(t.children[0])
            program.append(Op(OP_CODES[type_], None))
            return program

        elif type_ is Or:
            left, right = t.children
            program = []
            left = inner(left)
            right = inner(right)
            program.extend(left)
            program.append(Op(JUMPIFSUCCESS, len(right) + 2))
            program.append(Op(POP_STACK, None))
            program.extend(right)
            return program

        elif type_ is Choice:
            program = []
            preds = [inner(c) for c in t.children]
            preds = intersperse(preds, [JUMPIFSUCCESS])
            length = sum(len(p) for p in preds)
            for p in preds:
                if p is JUMPIFSUCCESS:
                    offset = length - len(program)
                    program.append(Op(JUMPIFSUCCESS, offset))
                else:
                    program.extend(p)
            return program

        elif type_ is And:
            left, right = t.children
            program = []
            left = inner(left)
            right = inner(right)
            program.extend(left)
            program.extend(right)
            program.append(Op(OP_CODES[And], None))
            return program

    return Runner(inner(optimize(tree)))


class Runner(object):
    def __init__(self, program):
        self.program = program

    def __call__(self, data):
        data = Input(data)
        program = self.program
        ip = 0

        stack = []

        SUCCESS = True
        ERROR = False

        while ip < len(program):
            code, args = program[ip]

            if code is IN_SET:
                log.debug("InSet")
                cache, name = args
                c = data.peek()
                if c in cache:
                    _, c = data.next()
                    ret = (SUCCESS, c)
                else:
                    ret = (ERROR, f"Expected {name} at {data.pos}. Got {c}.")
                stack.append(ret)

            elif code is CHAR:
                log.debug("Char")
                c = data.peek()
                if c == args:
                    _, c = data.next()
                    ret = (SUCCESS, c)
                else:
                    ret = (ERROR, f"Expected {args} at {data.pos}. Got {c}.")
                stack.append(ret)

            elif code is ESCAPED_CHAR:
                log.debug("Escaped Char")
                ret = None
                e = data.peek()
                if e == "\\":
                    pos, e = data.next()
                    if data.peek() == args:
                        _, c = data.next()
                        ret = (SUCCESS, c)
                    else:
                        data.pos -= 1
                if not ret:
                    ret = (ERROR, f"Expected escaped {args} at {data.pos}. Got {e}.")
                stack.append(ret)

            elif code is ANY_CHAR:
                log.debug("AnyChar")
                cache, echars, name = args
                ret = None
                p = data.peek()
                if p == "\\":
                    pos, e = data.next()
                    if data.peek() in echars:
                        _, c = data.next()
                        ret = (SUCCESS, c)
                    else:
                        data.pos -= 1

                elif p in cache:
                    pos, c = data.next()
                    ret = (SUCCESS, c)
                else:
                    ret = (ERROR, f"Expected {name} at {data.pos}. Got {p} instead.")
                stack.append(ret)

            elif code is STRINGBUILDER:
                log.debug("StringBuilder")
                cache, echars, name = args
                ret = None
                p = data.peek()
                result = []
                while p == "\\" or p in cache:
                    if p == "\\":
                        pos, e = data.next()
                        if data.peek() in echars:
                            _, c = data.next()
                            result.append(c)
                        else:
                            data.pos -= 1

                    if p in cache:
                        pos, c = data.next()
                        result.append(c)
                    p = data.peek()
                stack.append((SUCCESS, "".join(result)))

            elif code is POP_STACK:
                log.debug("Pop Stack")
                stack.pop()

            elif code is JUMPIFSUCCESS:
                flag, _ = stack[-1]
                log.debug(f"Jump if success: {flag}. From {ip} to {ip + args}")
                if flag is SUCCESS:
                    ip += args
                    continue

            elif code is JUMPIFFAILURE:
                flag, _ = stack[-1]
                log.debug(f"Jump if failure: {flag}. From {ip} to {ip + args}")
                if flag is ERROR:
                    ip += args
                    continue

            elif code is AND:
                log.debug("And")
                (f0, r0) = stack.pop()
                (f1, r1) = stack.pop()
                if f0 and f1:
                    stack.append((SUCCESS, (r1, r0)))
                elif f1:
                    stack.append((f0, r0))
                else:
                    stack.append((f1, r1))

            elif code is MAP:
                log.debug("Map")
                flag, result = stack.pop()
                if flag:
                    stack.append((SUCCESS, args(result)))
                else:
                    stack.append((flag, result))

            elif code is OPT:
                log.debug("Opt")
                flag, result = stack.pop()
                if flag:
                    stack.append((SUCCESS, result))
                else:
                    stack.append((SUCCESS, None))

            ip += 1

        assert len(stack) == 1, stack
        return stack[0]
