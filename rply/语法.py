from rply.报错 import ParserGeneratorError
from rply.功用 import iteritems


def rightmost_terminal(symbols, terminals):
    for sym in reversed(symbols):
        if sym in terminals:
            return sym
    return None


class 语法(object):
    def __init__(self, 各词):
        self.各规则 = [None]
        self.各短语语法表 = {}
        self.各词所在语法表 = dict((t, []) for t in 各词)
        self.各词所在语法表["error"] = []
        # A dictionary mapping names of nonterminals to a list of rule numbers
        # where they are used
        self.各短语对应语法号 = {}
        self.first = {}
        self.各规则后续 = {}
        self.优先级 = {}
        self.开头 = None

    def 添加规则(self, 名称, syms, func, 优先级):
        if 名称 in self.各词所在语法表:
            raise ParserGeneratorError("Illegal rule name %r" % 名称)

        if 优先级 is None:
            precname = rightmost_terminal(syms, self.各词所在语法表)
            规则优先级 = self.优先级.get(precname, ("right", 0))
        else:
            try:
                规则优先级 = self.优先级[优先级]
            except KeyError:
                raise ParserGeneratorError(
                    "优先级 %r 不存在" % 优先级
                )

        序号 = len(self.各规则)
        self.各短语对应语法号.setdefault(名称, [])

        for t in syms:
            if t in self.各词所在语法表:
                self.各词所在语法表[t].append(序号)
            else:
                self.各短语对应语法号.setdefault(t, []).append(序号)

        某规则 = 规则(序号, 名称, syms, 规则优先级, func)
        self.各规则.append(某规则)

        self.各短语语法表.setdefault(名称, []).append(某规则)

    def 设置优先级(self, term, 结合性, 层级):
        if term in self.优先级:
            raise ParserGeneratorError(
                "%s 的优先级已指定" % term
            )
        if 结合性 not in ["left", "right", "nonassoc"]:
            raise ParserGeneratorError(
                "优先级只能是左、右或非链（left, right, nonassoc），现为 %s" % (结合性)
            )
        self.优先级[term] = (结合性, 层级)

    '''注意：将首个语法规则作为"根"，因此添加语法规则的顺序影响结果'''
    def 牵头(self):
        规则名 = self.各规则[1].名称
        self.各规则[0] = 规则(0, "S'", [规则名], ("right", 0), None)
        self.各短语对应语法号[规则名].append(0)
        self.开头 = 规则名

    def unused_terminals(self):
        return [
            t
            for t, prods in iteritems(self.各词所在语法表)
            if not prods and t != "error"
        ]

    def 无用规则(self):
        # for 短语 in self.各短语对应语法号:
        #     print(短语 + ' -> ' + str(self.各短语对应语法号[短语]))
        return [p for p, 各规则 in iteritems(self.各短语对应语法号) if not 各规则]

    def build_lritems(self):
        """
        Walks the list of productions and builds a complete set of the LR
        items.
        """
        for 规则 in self.各规则:
            print(repr(规则))
            lastlri = 规则
            i = 0
            lr_items = []
            while True:
                if i > 规则.getlength():
                    lri = None
                else:
                    try:
                        前 = 规则.模式[i - 1]
                    except IndexError:
                        前 = None
                    try:
                        后 = self.各短语语法表[规则.模式[i]]
                    except (IndexError, KeyError):
                        后 = []
                    lri = LRItem(规则, i, 前, 后)
                lastlri.lr_next = lri
                if lri is None:
                    break
                lr_items.append(lri)
                lastlri = lri
                i += 1
            规则.lr_items = lr_items

    def _first(self, beta):
        result = []
        for x in beta:
            x_produces_empty = False
            for f in self.first[x]:
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

    def compute_first(self):
        for t in self.各词所在语法表:
            self.first[t] = [t]

        self.first["$end"] = ["$end"]

        for n in self.各短语对应语法号:
            self.first[n] = []

        changed = True
        while changed:
            changed = False
            for n in self.各短语对应语法号:
                for 规则 in self.各短语语法表[n]:
                    for f in self._first(规则.模式):
                        if f not in self.first[n]:
                            self.first[n].append(f)
                            changed = True

    def compute_follow(self):
        for k in self.各短语对应语法号:
            self.各规则后续[k] = []

        开头 = self.开头
        self.各规则后续[开头] = ["$end"]

        added = True
        while added:
            added = False
            for 规则 in self.各规则[1:]:
                for i, B in enumerate(规则.模式):
                    if B in self.各短语对应语法号:
                        fst = self._first(规则.模式[i + 1:])
                        has_empty = False
                        for f in fst:
                            if f != "<empty>" and f not in self.各规则后续[B]:
                                self.各规则后续[B].append(f)
                                added = True
                            if f == "<empty>":
                                has_empty = True
                        if has_empty or i == (len(规则.模式) - 1):
                            for f in self.各规则后续[规则.名称]:
                                if f not in self.各规则后续[B]:
                                    self.各规则后续[B].append(f)
                                    added = True


class 规则(object):
    def __init__(self, 序号, 名称, 模式, 优先级, func):
        self.名称 = 名称
        self.模式 = 模式
        self.序号 = 序号
        self.func = func
        self.优先级 = 优先级

        self.符号集合 = []
        for s in self.模式:
            if s not in self.符号集合:
                self.符号集合.append(s)

        self.lr_items = []
        self.lr_next = None
        self.lr0_added = 0
        self.reduced = 0

    def __repr__(self):
        return "[%s] 规则(%s -> %s)，优先级：%s" % (self.序号, self.名称, " ".join(self.模式), self.优先级)

    def getlength(self):
        return len(self.模式)


class LRItem(object):
    def __init__(self, 规则, n, 前, 后):
        self.规则名称 = 规则.名称
        self.所在模式位置 = 规则.模式[:]
        self.所在模式位置.insert(n, ".")
        self.规则序号 = 规则.序号
        self.索引 = n
        self.预读 = {}
        self.规则所含符号集合 = 规则.符号集合
        self.lr_before = 前
        self.lr_after = 后

    def __repr__(self):
        return "LRItem(%s -> %s)" % (self.规则名称, " ".join(self.所在模式位置))

    def getlength(self):
        return len(self.所在模式位置)
