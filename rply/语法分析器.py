from rply.报错 import 语法分析报错


class LRParser(object):
    def __init__(自身, lr_table, error_handler):
        自身.lr_table = lr_table
        自身.error_handler = error_handler

    def parse(自身, tokenizer, state=None):
        return 自身.分析(tokenizer, state)

    def 分析(自身, tokenizer, state=None):
        from rply.词 import 词

        预读 = None
        预读栈 = []

        状态栈 = [0]
        symstack = [词("$end", "$end")]

        当前状态 = 0
        while True:
            if 自身.lr_table.default_reductions[当前状态]:
                t = 自身.lr_table.default_reductions[当前状态]
                当前状态 = 自身._reduce_production(
                    t, symstack, 状态栈, state
                )
                continue

            if 预读 is None:
                if 预读栈:
                    预读 = 预读栈.pop()
                else:
                    try:
                        预读 = next(tokenizer)
                    except StopIteration:
                        预读 = None

                if 预读 is None:
                    预读 = 词("$end", "$end")

            ltype = 预读.gettokentype()
            if ltype in 自身.lr_table.lr_action[当前状态]:
                t = 自身.lr_table.lr_action[当前状态][ltype]
                if t > 0:
                    状态栈.append(t)
                    当前状态 = t
                    symstack.append(预读)
                    预读 = None
                    continue
                elif t < 0:
                    当前状态 = 自身._reduce_production(
                        t, symstack, 状态栈, state
                    )
                    continue
                else:
                    n = symstack[-1]
                    return n
            else:
                # TODO: actual error handling here
                if 自身.error_handler is not None:
                    if state is None:
                        自身.error_handler(预读)
                    else:
                        自身.error_handler(state, 预读)

                    # 此处原为 raise AssertionError，改为下面两行以支持空行，但代价是无视了某些语法错误？
                    预读 = None
                    continue
                else:
                    raise 语法分析报错(None, 预读.getsourcepos())

    def _reduce_production(自身, t, symstack, 状态栈, state):
        # reduce a symbol on the stack and emit a production
        规则 = 自身.lr_table.语法.各规则[-t]
        pname = 规则.名称
        plen = 规则.getlength()
        start = len(symstack) + (-plen - 1)
        assert start >= 0
        targ = symstack[start + 1:]
        start = len(symstack) + (-plen)
        assert start >= 0
        del symstack[start:]
        del 状态栈[start:]
        if state is None:
            value = 规则.func(targ)
        else:
            value = 规则.func(state, targ)
        symstack.append(value)
        当前状态 = 自身.lr_table.lr_goto[状态栈[-1]][pname]
        状态栈.append(当前状态)
        return 当前状态
