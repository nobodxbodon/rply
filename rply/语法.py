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
        self.follow = {}
        self.优先级 = {}
        self.start = None

    def add_production(self, prod_name, syms, func, precedence):
        if prod_name in self.各词所在语法表:
            raise ParserGeneratorError("Illegal rule name %r" % prod_name)

        if precedence is None:
            precname = rightmost_terminal(syms, self.各词所在语法表)
            prod_prec = self.优先级.get(precname, ("right", 0))
        else:
            try:
                prod_prec = self.优先级[precedence]
            except KeyError:
                raise ParserGeneratorError(
                    "Precedence %r doesn't exist" % precedence
                )

        pnumber = len(self.各规则)
        self.各短语对应语法号.setdefault(prod_name, [])

        for t in syms:
            if t in self.各词所在语法表:
                self.各词所在语法表[t].append(pnumber)
            else:
                self.各短语对应语法号.setdefault(t, []).append(pnumber)

        p = Production(pnumber, prod_name, syms, prod_prec, func)
        self.各规则.append(p)

        self.各短语语法表.setdefault(prod_name, []).append(p)

    def set_precedence(self, term, assoc, level):
        if term in self.优先级:
            raise ParserGeneratorError(
                "Precedence already specified for %s" % term
            )
        if assoc not in ["left", "right", "nonassoc"]:
            raise ParserGeneratorError(
                "Precedence must be one of left, right, nonassoc; not %s" % (
                    assoc
                )
            )
        self.优先级[term] = (assoc, level)

    def set_start(self):
        start = self.各规则[1].name
        self.各规则[0] = Production(0, "S'", [start], ("right", 0), None)
        self.各短语对应语法号[start].append(0)
        self.start = start

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
        for p in self.各规则:
            lastlri = p
            i = 0
            lr_items = []
            while True:
                if i > p.getlength():
                    lri = None
                else:
                    try:
                        before = p.prod[i - 1]
                    except IndexError:
                        before = None
                    try:
                        after = self.各短语语法表[p.prod[i]]
                    except (IndexError, KeyError):
                        after = []
                    lri = LRItem(p, i, before, after)
                lastlri.lr_next = lri
                if lri is None:
                    break
                lr_items.append(lri)
                lastlri = lri
                i += 1
            p.lr_items = lr_items

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
                for p in self.各短语语法表[n]:
                    for f in self._first(p.prod):
                        if f not in self.first[n]:
                            self.first[n].append(f)
                            changed = True

    def compute_follow(self):
        for k in self.各短语对应语法号:
            self.follow[k] = []

        start = self.start
        self.follow[start] = ["$end"]

        added = True
        while added:
            added = False
            for p in self.各规则[1:]:
                for i, B in enumerate(p.prod):
                    if B in self.各短语对应语法号:
                        fst = self._first(p.prod[i + 1:])
                        has_empty = False
                        for f in fst:
                            if f != "<empty>" and f not in self.follow[B]:
                                self.follow[B].append(f)
                                added = True
                            if f == "<empty>":
                                has_empty = True
                        if has_empty or i == (len(p.prod) - 1):
                            for f in self.follow[p.name]:
                                if f not in self.follow[B]:
                                    self.follow[B].append(f)
                                    added = True


class Production(object):
    def __init__(self, num, name, prod, precedence, func):
        self.name = name
        self.prod = prod
        self.number = num
        self.func = func
        self.prec = precedence

        self.unique_syms = []
        for s in self.prod:
            if s not in self.unique_syms:
                self.unique_syms.append(s)

        self.lr_items = []
        self.lr_next = None
        self.lr0_added = 0
        self.reduced = 0

    def __repr__(self):
        return "Production(%s -> %s)" % (self.name, " ".join(self.prod))

    def getlength(self):
        return len(self.prod)


class LRItem(object):
    def __init__(self, p, n, before, after):
        self.name = p.name
        self.prod = p.prod[:]
        self.prod.insert(n, ".")
        self.number = p.number
        self.lr_index = n
        self.lookaheads = {}
        self.unique_syms = p.unique_syms
        self.lr_before = before
        self.lr_after = after

    def __repr__(self):
        return "LRItem(%s -> %s)" % (self.name, " ".join(self.prod))

    def getlength(self):
        return len(self.prod)
