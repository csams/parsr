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
FORWARD = 4
KEEP_LEFT = 5
KEEP_RIGHT = 6
KEYWORD = 7  # DONE
LIFT = 8  # DONE
LITERAL = 9  # DONE
MAP = 11  # DONE
OPT = 12  # DONE
STRINGBUILDER = 14  # DONE
PUSH_ACC = 15  # DONE
LOAD_ACC = 16  # DONE
POP_STACK = 17  # DONE
JUMPIFFAILURE = 18  # DONE
JUMPIFSUCCESS = 19  # DONE
JUMP = 20  # DONE
CREATE_ACC = 22  # DONE
DELETE_ACC = 23  # DONE

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
    PUSH_ACC: "PUSH_ACC",
    LOAD_ACC: "LOAD_ACC",
    POP_STACK: "POP_STACK",
    JUMPIFFAILURE: "JUMPIFFAILURE",
    JUMPIFSUCCESS: "JUMPIFSUCCESS",
    JUMP: "JUMP",
    CREATE_ACC: "CREATE_ACC",
    DELETE_ACC: "DELETE_ACC",
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
    func_table = {}

    def inner(t):
#        if t in seen:
#            return

#        if isinstance(t, Forward):
#            seen.add(t)

        type_ = type(t)
        if type_ in (AnyChar, StringBuilder):
            return [Op(OP_CODES[type_], (t.cache, t.echars, t.name))]

        elif type_ is Opt:
            program = inner(t.children[0])
            program.append(Op(OP_CODES[type_], None))
            return program

        elif type_ is And:
            left, right = t.children
            program = []
            chunks = []
            left = inner(left)
            right = inner(right)

            chunks.append([Op(CREATE_ACC, None)])
            chunks.append(left)
            chunks.append(JUMPIFFAILURE)
            chunks.append([Op(PUSH_ACC, None)])
            chunks.append(right)
            chunks.append(JUMPIFFAILURE)
            chunks.append([Op(PUSH_ACC, None)])
            chunks.append([Op(LOAD_ACC, (2, t.name or str(t)))])
            chunks.append([Op(JUMP, 2)])

            length = len(left) + len(right) + 7
            for p in chunks:
                if p is JUMPIFFAILURE:
                    offset = length - len(program)
                    program.append(Op(JUMPIFFAILURE, offset))
                else:
                    program.extend(p)

            program.append(Op(DELETE_ACC, None))
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
            length = sum(len(p) for p in preds) + (2 * len(t.children)) - 1
            preds = intersperse(preds, [JUMPIFSUCCESS, Op(POP_STACK, None)])

            tmp = []
            for p in preds:
                tmp.extend(p)

            for t in tmp:
                if t is JUMPIFSUCCESS:
                    offset = length - len(program)
                    program.append(Op(JUMPIFSUCCESS, offset))
                else:
                    program.append(t)
            return program

        elif type_ is Many:
            child = t.children[0]
            program = [Op(CREATE_ACC, None)]
            program.extend(inner(child))
            program.append(Op(JUMPIFFAILURE, 3))
            program.append(Op(PUSH_ACC, None))
            program.append(Op(JUMP, -len(program) + 1))
            program.append(Op(POP_STACK, None))
            program.append(Op(LOAD_ACC, (0, child.name or str(child))))
            return program

        elif type_ is Many1:
            child = t.children[0]
            program = [Op(CREATE_ACC, None)]
            program.extend(inner(child))
            program.append(Op(JUMPIFFAILURE, 3))
            program.append(Op(PUSH_ACC, None))
            program.append(Op(JUMP, -len(program) + 1))
            program.append(Op(POP_STACK, None))
            program.append(Op(LOAD_ACC, (1, child.name or str(child))))
            return program

        elif type_ is Map:
            program = inner(t.children[0])
            program.append(Op(OP_CODES[type_], t.func))
            return program

        elif type_ is Lift:
            program = []
            chunks = [[Op(CREATE_ACC, None)]]

            for c in t.children:
                chunks.append(inner(c))
                chunks.append(JUMPIFFAILURE)
                chunks.append([Op(PUSH_ACC, None)])

            chunks.append([Op(LOAD_ACC, (len(t.children), t.name or str(t)))])

            length = sum(len(c) if isinstance(c, list) else 1 for c in chunks)
            for p in chunks:
                if p is JUMPIFFAILURE:
                    offset = length - len(program)
                    program.append(Op(JUMPIFFAILURE, offset))
                else:
                    program.extend(p)
            program.append(Op(OP_CODES[type_], (t.func, len(t.children))))
            return program

        elif type_ is Literal:
            program = [Op(OP_CODES[type_], (t.chars, t.ignore_case))]
            return program

        elif type_ is Keyword:
            program = [Op(OP_CODES[type_], (t.chars, t.value, t.ignore_case))]
            return program

        elif type_ is SepBy:
            program = inner(t.children[0])
            return program

        elif type_ is Between:
            program = inner(t.children[0])
            return program

        elif type_ is KeepLeft:
            program = inner(t.children[0])
            return program

        elif type_ is KeepRight:
            program = inner(t.children[0])
            return program

        elif type_ is Forward:
            if t in seen:
                return [Op(FORWARD, t)]
            seen.add(t)
            program = inner(t.children[0])
            func_table[t] = program
            return program

    return Runner(inner(optimize(tree)), func_table)


class Runner(object):
    def __init__(self, program, func_table):
        self.program = program
        self.func_table = func_table

    def __repr__(self):
        results = []
        for idx, i in enumerate(self.program):
            print(i)
            if i.op in (JUMPIFSUCCESS, JUMPIFFAILURE, JUMP):
                msg = f"{idx:3}| {CODE_OPS[i.op]}: {i.data} to {i.data + idx}"
            else:
                msg = f"{idx:3}| {CODE_OPS[i.op]}: {i.data}"
            results.append(msg)
        return "\n".join(results)

    def __call__(self, data):
        data = Input(data)
        return self.process(data, self.program, self.func_table)

    def process(self, data, program, func_table):

        ip = 0
        acc = []
        stack = []

        SUCCESS = True
        ERROR = False

        while ip < len(program):
            code, args = program[ip]
            log.info(f"Stack  : {stack}")
            log.info(f"Acc    : {acc}")
            log.info("")
            log.info(f"Op Code: {CODE_OPS[code]}({args})")
            log.info(f"Data   : {data.peek()}")

            if code is ANY_CHAR:
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

            elif code is JUMP:
                ip += args
                continue

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

            elif code is PUSH_ACC:
                log.debug("Push Acc")
                flag, result = stack.pop()
                acc[-1].append(result)

            elif code is LOAD_ACC:
                log.debug("Load Acc")
                lower, label = args
                lacc = acc[-1]
                if len(lacc) >= lower:
                    stack.append((SUCCESS, lacc))
                else:
                    stack.append((ERROR, f"Expected at least {lower} {label} at {data.pos}."))
                acc.pop()

            elif code is CREATE_ACC:
                log.debug("Create Acc")
                acc.append([])

            elif code is DELETE_ACC:
                log.debug("Delete Acc")
                acc.pop()

            elif code is MAP:
                log.debug("Map")
                flag, result = stack.pop()
                if flag:
                    stack.append((SUCCESS, args(result)))
                else:
                    stack.append((ERROR, result))

            elif code is LIFT:
                func, num_args = args
                log.debug(f"Lift({func})")
                flag, params = stack.pop()
                if len(params) == num_args:
                    stack.append((SUCCESS, func(*params)))
                else:
                    stack.append((ERROR, result))

            elif code is OPT:
                log.debug("Opt")
                flag, result = stack.pop()
                if flag:
                    stack.append((SUCCESS, result))
                else:
                    stack.append((SUCCESS, None))

            elif code is LITERAL:
                log.debug("Literal")
                flag, result = stack.pop()
                chars, ignore_case = result
                if ignore_case:
                    for c in chars:
                        if data.peek().lower() != c:
                            msg = f"Expected {c} at {data.pos}. Got {data.peek()}"
                            stack.append((ERROR, msg))
                            break
                    else:
                        stack.append((SUCCESS, chars))
                else:
                    for c in chars:
                        if data.peek().lower() != c:
                            msg = f"Expected {c} at {data.pos}. Got {data.peek()}"
                            stack.append((ERROR, msg))
                            break
                    else:
                        stack.append((SUCCESS, chars))

            elif code is KEYWORD:
                log.debug("Keyword")
                flag, result = stack.pop()
                chars, value, ignore_case = result
                if ignore_case:
                    for c in chars:
                        if data.peek().lower() != c:
                            msg = f"Expected {c} at {data.pos}. Got {data.peek()}"
                            stack.append((ERROR, msg))
                            break
                    else:
                        stack.append((SUCCESS, value))
                else:
                    for c in chars:
                        if data.peek().lower() != c:
                            msg = f"Expected {c} at {data.pos}. Got {data.peek()}"
                            stack.append((ERROR, msg))
                            break
                    else:
                        stack.append((SUCCESS, value))

            elif code is FORWARD:
                result = self.process(data, func_table[args], func_table)
                stack.append(result)

            ip += 1

        assert len(stack) == 1, stack
        return stack[0]
