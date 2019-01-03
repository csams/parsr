import logging
from collections import namedtuple
from parseit import Input
from parseit.optimizer import optimize
from parseit import (And,
                     AnyChar,
                     Between,
                     Choice,
                     Forward,
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

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def intersperse(lst, item):
    result = [item] * (len(lst) * 2 - 1)
    result[0::2] = lst
    return result


ANY_CHAR = 1  # DONE
FORWARD = 2  # DONE
KEEP_LEFT = 3  # DONE
KEEP_RIGHT = 4  # DONE
KEYWORD = 5  # DONE
LIFT = 6  # DONE
LITERAL = 7  # DONE
MAP = 8  # DONE
OPT = 9  # DONE
STRINGBUILDER = 10  # DONE
PUSH = 11  # DONE
POP = 12  # DONE
LOAD_ACC = 13  # DONE
JUMPIFFAILURE = 14  # DONE
JUMPIFSUCCESS = 15  # DONE
JUMP = 16  # DONE
CREATE_ACC = 17  # DONE
DELETE_ACC = 18  # DONE
PRINT = 19
PUSH_POS = 20
POP_POS = 21
CLEAR_POS = 22
POP_PUSH_POS = 23

CODE_OPS = {
    ANY_CHAR: "ANY_CHAR",
    FORWARD: "FORWARD",
    KEEP_LEFT: "KEEP_LEFT",
    KEEP_RIGHT: "KEEP_RIGHT",
    KEYWORD: "KEYWORD",
    LIFT: "LIFT",
    LITERAL: "LITERAL",
    MAP: "MAP",
    OPT: "OPT",
    STRINGBUILDER: "STRINGBUILDER",
    PUSH: "PUSH",
    POP: "POP",
    LOAD_ACC: "LOAD_ACC",
    JUMPIFFAILURE: "JUMPIFFAILURE",
    JUMPIFSUCCESS: "JUMPIFSUCCESS",
    JUMP: "JUMP",
    CREATE_ACC: "CREATE_ACC",
    DELETE_ACC: "DELETE_ACC",
    PRINT: "PRINT",
    PUSH_POS: "PUSH_POS",
    POP_POS: "POP_POS",
    CLEAR_POS: "CLEAR_POS",
    POP_PUSH_POS: "POP_PUSH_POS",
}

OP_CODES = {
    AnyChar: ANY_CHAR,
    Forward: FORWARD,
    KeepLeft: KEEP_LEFT,
    KeepRight: KEEP_RIGHT,
    Keyword: KEYWORD,
    Lift: LIFT,
    Literal: LITERAL,
    Map: MAP,
    Opt: OPT,
    StringBuilder: STRINGBUILDER,
}


Op = namedtuple("Op", field_names="op data")


def comp(tree):
    seen = set()
    future_table = {}

    def inner(t):
        type_ = type(t)
        if type_ in (AnyChar, StringBuilder):
            return [Op(OP_CODES[type_], (t.cache, t.echars, t.name))]

        elif type_ is Opt:
            program = [Op(PUSH_POS, None)]
            program.extend(inner(t.children[0]))
            program.append(Op(JUMPIFSUCCESS, 2))
            program.append(Op(POP_POS, None))
            program.append(Op(OP_CODES[type_], None))
            return program

        elif type_ is KeepLeft:
            left, right = t.children
            left = inner(left)
            right = inner(right)

            program = []
            program.append(Op(CREATE_ACC, None))
            program.append(Op(PUSH_POS, None))
            program.extend(left)
            program.append(Op(JUMPIFFAILURE, len(right) + 6))
            program.append(Op(PUSH, None))
            program.extend(right)
            program.append(Op(JUMPIFFAILURE, 4))
            program.append(Op(POP, None))
            program.append(Op(CLEAR_POS, None))
            program.append(Op(JUMP, 2))
            program.append(Op(POP_POS, None))
            program.append(Op(DELETE_ACC, None))
            return program

        elif type_ is KeepRight:
            left, right = t.children
            program = []
            program.append(Op(PUSH_POS, None))
            program.extend(inner(left))
            right = inner(right)
            program.append(Op(JUMPIFFAILURE, len(right) + 3))
            program.extend(right)
            program.append(Op(CLEAR_POS, None))
            program.append(Op(JUMP, 2))
            program.append(Op(POP_POS, None))
            return program

        elif type_ is And:
            left, right = t.children
            program = []
            chunks = []

            left = inner(left)
            right = inner(right)

            chunks.append([Op(CREATE_ACC, None), Op(PUSH_POS, None)])
            chunks.append(left)
            chunks.append(JUMPIFFAILURE)
            chunks.append([Op(PUSH, None)])
            chunks.append(right)
            chunks.append(JUMPIFFAILURE)
            chunks.append([Op(PUSH, None)])
            chunks.append([Op(LOAD_ACC, (2, t.name or str(t)))])
            chunks.append([Op(CLEAR_POS, None)])
            chunks.append([Op(JUMP, 3)])

            length = sum(len(c) if isinstance(c, list) else 1 for c in chunks)
            for p in chunks:
                if p is JUMPIFFAILURE:
                    offset = length - len(program)
                    program.append(Op(JUMPIFFAILURE, offset))
                else:
                    program.extend(p)

            program.append(Op(POP_POS, None))
            program.append(Op(DELETE_ACC, None))
            return program

        elif type_ is Or:
            left, right = t.children
            left = inner(left)
            right = inner(right)

            program = [Op(PUSH_POS, None)]
            program.extend(left)
            program.append(Op(JUMPIFSUCCESS, len(right) + 5))
            program.append(Op(POP_PUSH_POS, None))
            program.extend(right)
            program.append(Op(JUMPIFSUCCESS, 3))
            program.append(Op(POP_POS, None))
            program.append(Op(JUMP, 2))
            program.append(Op(CLEAR_POS, None))
            return program

        elif type_ is Choice:
            program = []
            tmp = [Op(PUSH_POS, None)]
            for c in t.children:
                tmp.extend(inner(c))
                tmp.append(JUMPIFSUCCESS)
                tmp.append(Op(POP_PUSH_POS, None))

            tmp.pop()
            tmp.append(Op(POP_POS, None))

            length = len(tmp)
            for p in tmp:
                if p == JUMPIFSUCCESS:
                    offset = length - len(program) + 1
                    program.append(Op(JUMPIFSUCCESS, offset))
                else:
                    program.append(p)

            program.append(Op(JUMP, 2))
            program.append(Op(CLEAR_POS, None))
            return program

        elif type_ is Many:
            child = t.children[0]
            program = [Op(CREATE_ACC, None)]
            program.append(Op(PUSH_POS, None))
            program.extend(inner(child))
            program.append(Op(JUMPIFFAILURE, 4))
            program.append(Op(PUSH, None))
            program.append(Op(CLEAR_POS, None))
            program.append(Op(JUMP, -len(program) + 1))
            program.append(Op(POP_POS, None))
            program.append(Op(LOAD_ACC, (0, child.name or str(child))))
            return program

        elif type_ is Many1:
            child = t.children[0]
            program = [Op(CREATE_ACC, None)]
            program.append(Op(PUSH_POS, None))
            program.extend(inner(child))
            program.append(Op(JUMPIFFAILURE, 4))
            program.append(Op(PUSH, None))
            program.append(Op(CLEAR_POS, None))
            program.append(Op(JUMP, -len(program) + 1))
            program.append(Op(POP_POS, None))
            program.append(Op(LOAD_ACC, (1, child.name or str(child))))
            return program

        elif type_ is Map:
            program = inner(t.children[0])
            program.append(Op(OP_CODES[type_], t.func))
            return program

        elif type_ is Lift:
            program = [Op(CREATE_ACC, None), Op(PUSH_POS, None)]
            tmp = []
            for c in t.children:
                tmp.extend(inner(c))
                tmp.append(JUMPIFFAILURE)
                tmp.append(Op(PUSH, None))
                tmp.append(Op(CLEAR_POS, None))
                tmp.append(Op(PUSH_POS, None))

            tmp.pop()

            length = len(tmp) + 1
            for p in tmp:
                if p == JUMPIFFAILURE:
                    offset = length - len(program) + 4
                    program.append(Op(JUMPIFFAILURE, offset))
                else:
                    program.append(p)

            program.append(Op(LOAD_ACC, (len(t.children), str(t))))
            program.append(Op(OP_CODES[type_], t.func))
            program.append(Op(JUMP, 3))
            program.append(Op(POP_POS, None))  # ERROR
            program.append(Op(DELETE_ACC, None))  # DONE
            return program

        elif type_ is Literal:
            program = [Op(OP_CODES[type_], (t.chars, t.ignore_case))]
            return program

        elif type_ is Keyword:
            program = [Op(OP_CODES[type_], (t.chars, t.value, t.ignore_case))]
            return program

        elif type_ in (Between, SepBy):
            return inner(t.children[0])

        elif type_ is Forward:
            if t in seen:
                return [Op(FORWARD, t)]
            seen.add(t)
            program = inner(t.children[0])
            future_table[t] = program
            return program

    return Runner(inner(optimize(tree)), future_table)


class Runner(object):
    def __init__(self, program, future_table):
        self.program = program
        self.future_table = future_table

    def __repr__(self):
        results = []
        for idx, i in enumerate(self.program):
            if i.op in (JUMPIFSUCCESS, JUMPIFFAILURE, JUMP):
                msg = f"{idx:3}| {CODE_OPS[i.op]} to {i.data + idx}"
            else:
                msg = f"{idx:3}| {CODE_OPS[i.op]}: {i.data}"
            results.append(msg)
        return "\n".join(results)

    def __call__(self, data):
        data = Input(data)
        return self.process(data, self.program, self.future_table)

    def process(self, data, program, future_table):
        ip = 0
        acc = []
        pos_stack = []
        reg = None

        SUCCESS = True
        ERROR = False
        status = SUCCESS

        while ip < len(program):
            code, args = program[ip]

            if code is STRINGBUILDER:
                cache, echars, name = args
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
                status = SUCCESS
                reg = "".join(result)

            elif code == JUMPIFFAILURE:
                if status is ERROR:
                    ip += args
                    continue

            elif code == PUSH_POS:
                pos_stack.append(data.pos)

            elif code == CLEAR_POS:
                pos_stack.pop()

            elif code == POP_POS:
                data.pos = pos_stack.pop()

            elif code == JUMP:
                ip += args
                continue

            elif code == POP_PUSH_POS:
                a = pos_stack.pop()
                data.pos = a
                pos_stack.append(a)

            elif code == JUMPIFSUCCESS:
                if status is SUCCESS:
                    ip += args
                    continue

            elif code == PUSH:
                acc[-1].append(reg)
                status = True

            elif code == POP:
                reg = acc[-1].pop()
                status = True

            elif code == LOAD_ACC:
                lower, label = args
                lacc = acc.pop()
                if len(lacc) >= lower:
                    status = SUCCESS
                    reg = lacc
                else:
                    status = ERROR
                    reg = f"Expected at least {lower} {label} at {data.pos}."

            elif code == CREATE_ACC:
                acc.append([])

            elif code == DELETE_ACC:
                acc.pop()

            elif code == ANY_CHAR:
                cache, echars, name = args
                p = data.peek()
                if p == "\\":
                    pos, e = data.next()
                    if data.peek() in echars:
                        _, c = data.next()
                        status = SUCCESS
                        reg = c
                    else:
                        data.pos -= 1
                elif p in cache:
                    pos, c = data.next()
                    status = SUCCESS
                    reg = c
                else:
                    status = ERROR
                    reg = f"Expected {name} at {data.pos}. Got {p} instead."

            elif code == MAP:
                if status is SUCCESS:
                    try:
                        reg = args(reg)
                    except Exception as ex:
                        status = ERROR
                        reg = str(ex)

            elif code == LIFT:
                func = args
                try:
                    reg = func(*reg)
                    status = SUCCESS
                except Exception as ex:
                    status = ERROR
                    reg = str(ex)

            elif code == OPT:
                if status is ERROR:
                    status = SUCCESS
                    reg = None

            elif code == LITERAL:
                chars, ignore_case = args
                pos = data.pos
                if ignore_case:
                    for c in chars:
                        if data.peek().lower() != c:
                            msg = f"Expected {c} at {data.pos}. Got {data.peek()}"
                            status = ERROR
                            reg = msg
                            data.pos = pos
                            break
                        data.next()
                    else:
                        status = SUCCESS
                        reg = chars
                else:
                    for c in chars:
                        if data.peek() != c:
                            msg = f"Expected {c} at {data.pos}. Got {data.peek()}"
                            status = ERROR
                            reg = msg
                            data.pos = pos
                            break
                        data.next()
                    else:
                        status = SUCCESS
                        reg = chars

            elif code == KEYWORD:
                chars, value, ignore_case = args
                pos = data.pos
                if ignore_case:
                    for c in chars:
                        if data.peek().lower() != c:
                            msg = f"Expected {c} at {data.pos}. Got {data.peek()}"
                            status = ERROR
                            reg = msg
                            data.pos = pos
                            break
                        data.next()
                    else:
                        status = SUCCESS
                        reg = value
                else:
                    for c in chars:
                        if data.peek() != c:
                            msg = f"Expected {c} at {data.pos}. Got {data.peek()}"
                            status = ERROR
                            reg = msg
                            data.pos = pos
                            break
                        data.next()
                    else:
                        status = SUCCESS
                        reg = value

            elif code == FORWARD:
                pos = data.pos
                status, reg = self.process(data, future_table[args], future_table)
                if status == ERROR:
                    data.pos = pos

            elif code == PRINT:
                log.info(args)

            else:
                log.warn(f"Unrecognized code: ({code}, {args})")

            ip += 1

        return (status, reg)
