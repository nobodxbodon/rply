from rply.报错 import ParserGeneratorError
from rply.功用 import iteritems


def 最右侧词(各符号, 各词):
    for 符号 in reversed(各符号):
        if 符号 in 各词:
            return 符号
    return None


class 语法(object):
    def __init__(自身, 各词):
        自身.各规则 = [None]
        自身.各短语语法表 = {}
        自身.各词所在语法表 = dict((词, []) for 词 in 各词)
        自身.各词所在语法表["error"] = []
        # A dictionary mapping names of nonterminals to a list of rule numbers
        # where they are used
        自身.各短语对应语法号 = {}
        自身.first = {}
        自身.各规则后续 = {}
        自身.优先级 = {}
        自身.开头 = None

    def 添加规则(自身, 名称, 各符号, func, 优先级):
        if 名称 in 自身.各词所在语法表:
            raise ParserGeneratorError("Illegal rule name %r" % 名称)

        if 优先级 is None:
            precname = 最右侧词(各符号, 自身.各词所在语法表)
            规则优先级 = 自身.优先级.get(precname, ("right", 0))
        else:
            try:
                规则优先级 = 自身.优先级[优先级]
            except KeyError:
                raise ParserGeneratorError(
                    "优先级 %r 不存在" % 优先级
                )

        序号 = len(自身.各规则)
        自身.各短语对应语法号.setdefault(名称, [])

        for 词 in 各符号:
            if 词 in 自身.各词所在语法表:
                自身.各词所在语法表[词].append(序号)
            else:
                自身.各短语对应语法号.setdefault(词, []).append(序号)

        某规则 = 规则(序号, 名称, 各符号, 规则优先级, func)
        自身.各规则.append(某规则)

        自身.各短语语法表.setdefault(名称, []).append(某规则)

    def 设置优先级(自身, term, 结合性, 层级):
        if term in 自身.优先级:
            raise ParserGeneratorError(
                "%s 的优先级已指定" % term
            )
        if 结合性 not in ["left", "right", "nonassoc"]:
            raise ParserGeneratorError(
                "优先级只能是左、右或非链（left, right, nonassoc），现为 %s" % (结合性)
            )
        自身.优先级[term] = (结合性, 层级)

    '''注意：将首个语法规则作为"根"，因此添加语法规则的顺序影响结果'''
    def 牵头(自身):
        规则名 = 自身.各规则[1].名称
        自身.各规则[0] = 规则(0, "S'", [规则名], ("right", 0), None)
        自身.各短语对应语法号[规则名].append(0)
        自身.开头 = 规则名

    def 无用词(自身):
        return [
            词
            for 词, prods in iteritems(自身.各词所在语法表)
            if not prods and 词 != "error"
        ]

    def 无用规则(自身):
        # for 短语 in 自身.各短语对应语法号:
        #     print(短语 + ' -> ' + str(自身.各短语对应语法号[短语]))
        return [p for p, 各规则 in iteritems(自身.各短语对应语法号) if not 各规则]

    def 生成各lr项(自身):
        """
        Walks the list of productions and builds a complete set of the LR
        items.
        """
        for 规则 in 自身.各规则:
            # print(repr(规则))
            lastlri = 规则
            i = 0
            lr_items = []
            while True:
                if i > 规则.取长度():
                    lri = None
                else:
                    try:
                        前 = 规则.模式[i - 1]
                    except IndexError:
                        前 = None
                    try:
                        后 = 自身.各短语语法表[规则.模式[i]]
                    except (IndexError, KeyError):
                        后 = []
                    lri = LR项(规则, i, 前, 后)
                lastlri.lr_next = lri
                if lri is None:
                    break
                lr_items.append(lri)
                lastlri = lri
                i += 1
            规则.lr_items = lr_items

    def _first(自身, beta):
        result = []
        for x in beta:
            x_produces_empty = False
            for f in 自身.first[x]:
                if f == "<empty>":
                    x_produces_empty = True
                else:
                    if f not in result:
                        result.append(f)
            if not x_produces_empty:
                break
        else:
            result.append("<empty>")
        return result

    def compute_first(自身):
        for 词 in 自身.各词所在语法表:
            自身.first[词] = [词]

        自身.first["$end"] = ["$end"]

        for n in 自身.各短语对应语法号:
            自身.first[n] = []

        changed = True
        while changed:
            changed = False
            for n in 自身.各短语对应语法号:
                for 规则 in 自身.各短语语法表[n]:
                    for f in 自身._first(规则.模式):
                        if f not in 自身.first[n]:
                            自身.first[n].append(f)
                            changed = True

    def compute_follow(自身):
        for k in 自身.各短语对应语法号:
            自身.各规则后续[k] = []

        开头 = 自身.开头
        自身.各规则后续[开头] = ["$end"]

        added = True
        while added:
            added = False
            for 规则 in 自身.各规则[1:]:
                for i, B in enumerate(规则.模式):
                    if B in 自身.各短语对应语法号:
                        fst = 自身._first(规则.模式[i + 1:])
                        has_empty = False
                        for f in fst:
                            if f != "<empty>" and f not in 自身.各规则后续[B]:
                                自身.各规则后续[B].append(f)
                                added = True
                            if f == "<empty>":
                                has_empty = True
                        if has_empty or i == (len(规则.模式) - 1):
                            for f in 自身.各规则后续[规则.名称]:
                                if f not in 自身.各规则后续[B]:
                                    自身.各规则后续[B].append(f)
                                    added = True


class 规则(object):
    def __init__(自身, 序号, 名称, 模式, 优先级, func):
        自身.名称 = 名称
        自身.模式 = 模式
        自身.序号 = 序号
        自身.func = func
        自身.优先级 = 优先级

        自身.符号集合 = []
        for s in 自身.模式:
            if s not in 自身.符号集合:
                自身.符号集合.append(s)

        自身.lr_items = []
        自身.lr_next = None
        自身.lr0_added = 0
        自身.reduced = 0

    def __repr__(自身):
        return "[%s] 规则(%s -> %s)，优先级：%s" % (自身.序号, 自身.名称, " ".join(自身.模式), 自身.优先级)

    def 取长度(自身):
        return len(自身.模式)


class LR项(object):
    def __init__(自身, 规则, n, 前, 后):
        自身.规则名称 = 规则.名称
        自身.所在模式位置 = 规则.模式[:]
        自身.所在模式位置.insert(n, ".")
        自身.规则序号 = 规则.序号
        自身.索引 = n
        自身.预读 = {}
        自身.规则所含符号集合 = 规则.符号集合
        自身.lr_before = 前
        自身.lr_after = 后

    def __repr__(自身):
        return "LR项(%s -> %s)" % (自身.规则名称, " ".join(自身.所在模式位置))

    def 取长度(自身):
        return len(自身.所在模式位置)
