from rply.报错 import 语法分析报错, 分词报错


class LRParser(object):
    def __init__(自身, lr_table, error_handler):
        自身.lr_table = lr_table
        自身.error_handler = error_handler

    def parse(自身, 分词器, state=None):
        return 自身.分析(分词器, state)

    def 分析(自身, 分词器, state=None):
        from rply.词 import 词

        预读 = None
        预读栈 = []

        状态栈 = [0]
        符号栈 = [词("$end", "$end")]

        当前状态 = 0
        while True:
            if 自身.lr_table.default_reductions[当前状态]:
                t = 自身.lr_table.default_reductions[当前状态]
                当前状态 = 自身._reduce_production(
                    t, 符号栈, 状态栈, state
                )
                continue

            if 预读 is None:
                if 预读栈:
                    预读 = 预读栈.pop()
                else:
                    try:
                        预读 = next(分词器)
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
                    符号栈.append(预读)
                    预读 = None
                    continue
                elif t < 0:
                    当前状态 = 自身._reduce_production(
                        t, 符号栈, 状态栈, state
                    )
                    continue
                else:
                    n = 符号栈[-1]
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

    # TODO：尚未兼容带空格分析的所有测试用例
    def 按语法分词(自身, 分词器, state=None):
        from rply.词 import 词

        预读 = None
        上个预读 = None

        预读栈 = []
        上个预读栈 = 预读栈

        状态栈 = [0]
        上个状态栈 = 状态栈

        符号栈 = [词("$end", "$end")]
        上个符号栈 = 符号栈

        当前状态 = 0
        上个状态 = 当前状态
        print('lr_action: ' + str(自身.lr_table.lr_action))
        print('lr_goto: ' + str(自身.lr_table.lr_goto))
        while True:
            print("入循环，当前状态： " + str(当前状态))
            上个状态 = 当前状态
            上个状态栈 = 状态栈
            上个符号栈 = 符号栈
            上个预读栈 = 预读栈
            上个预读 = 预读
            print("状态栈：" + str(状态栈))
            if 自身.lr_table.default_reductions[当前状态]:
                t = 自身.lr_table.default_reductions[当前状态]
                当前状态 = 自身._reduce_production(
                    t, 符号栈, 状态栈, state
                )
                continue

            if 预读 is None:
                if 预读栈:
                    预读 = 预读栈.pop()
                else:
                    try:
                        print('取下一词')
                        分词器.记录状态(当前状态, 状态栈, 符号栈, 预读栈, 预读)
                        预读 = next(分词器)
                    except StopIteration:
                        预读 = None
                    except 分词报错:
                        if 分词器.退出 or not 分词器.回退():
                            raise 语法分析报错(None, 预读.getsourcepos())

                if 预读 is None:
                    预读 = 词("$end", "$end")

            ltype = 预读.gettokentype()
            print('预读词：' + str(预读) + ' 类型: ' + ltype + ' 当前状态：' + str(当前状态))
            print('当前分词位置：' + str(分词器.位置))
            if ltype in 自身.lr_table.lr_action[当前状态]:
                print('在状态')
                t = 自身.lr_table.lr_action[当前状态][ltype]
                if t > 0:
                    print('大于0')
                    状态栈.append(t)
                    当前状态 = t
                    符号栈.append(预读)
                    预读 = None
                    continue
                elif t < 0:
                    print('小于0')
                    当前状态 = 自身._reduce_production(
                        t, 符号栈, 状态栈, state
                    )
                    continue
                else:
                    print('为0')
                    n = 符号栈[-1]
                    return n
            else:
                print('不在状态')
                # TODO: actual error handling here
                if 自身.error_handler is not None:
                    print("错误处理")
                    if state is None:
                        自身.error_handler(预读)
                    else:
                        自身.error_handler(state, 预读)

                    # 此处原为 raise AssertionError，改为下面两行以支持空行，但代价是无视了某些语法错误？
                    预读 = None
                    continue
                else:
                    print(预读)
                    上个位置 = 分词器.标记不符语法词法规则()
                    上个状态 = 分词器.回退点[上个位置][0] if 上个位置 in 分词器.回退点 else -1
                    上个状态栈 = 分词器.回退点[上个位置][1] if 上个位置 in 分词器.回退点 else [0]
                    上个符号栈 = 分词器.回退点[上个位置][2] if 上个位置 in 分词器.回退点 else [词("$end", "$end")]
                    上个预读栈 = 分词器.回退点[上个位置][3] if 上个位置 in 分词器.回退点 else []
                    上个预读 = 分词器.回退点[上个位置][4] if 上个位置 in 分词器.回退点 else None
                    print("上个位置：" + str(上个位置))
                    print("上个状态：" + str(上个状态))
                    print("上个状态栈" + str(上个状态栈))
                    print("查找回退位置：" + str(分词器.不符语法词法规则))
                    print("回退点: " + str(分词器.回退点))
                    当前状态 = 上个状态
                    状态栈 = 上个状态栈
                    符号栈 = 上个符号栈
                    预读栈 = 上个预读栈
                    预读 = 上个预读

    def _reduce_production(自身, t, 符号栈, 状态栈, 状态):
        # reduce a symbol on the stack and emit a production
        规则 = 自身.lr_table.语法.各规则[-t]
        规则名 = 规则.名称
        规则长度 = 规则.取长度()
        起始位置 = len(符号栈) + (-规则长度 - 1)
        assert 起始位置 >= 0
        targ = 符号栈[起始位置 + 1:]
        起始位置 = len(符号栈) + (-规则长度)
        assert 起始位置 >= 0
        del 符号栈[起始位置:]
        del 状态栈[起始位置:]
        if 状态 is None:
            value = 规则.func(targ)
        else:
            value = 规则.func(状态, targ)
        符号栈.append(value)
        当前状态 = 自身.lr_table.lr_goto[状态栈[-1]][规则名]
        状态栈.append(当前状态)
        return 当前状态
