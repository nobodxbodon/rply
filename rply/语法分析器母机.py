import errno
import hashlib
import json
import os
import sys
import tempfile
import warnings

from appdirs import AppDirs

from rply.报错 import ParserGeneratorError, ParserGeneratorWarning
from rply.语法 import 语法
from rply.语法分析器 import LRParser
from rply.功用 import Counter, IdentityDict, iteritems, itervalues


LARGE_VALUE = sys.maxsize


class 语法分析器母机(object):
    """
    A ParserGenerator represents a set of production rules, that define a
    sequence of terminals and non-terminals to be replaced with a non-terminal,
    which can be turned into a parser.

    :param 词表: A list of token (non-terminal) names.
    :param 优先级: A list of tuples defining the order of operation for
                       avoiding ambiguity, consisting of a string defining
                       associativity (left, right or nonassoc) and a list of
                       token names with the same associativity and level of
                       precedence.
    :param cache_id: A string specifying an ID for caching.
    """
    VERSION = 1

    def __init__(self, 词表, 优先级=[], cache_id=None):
        self.词表 = 词表
        self.productions = []
        self.优先级 = 优先级
        self.cache_id = cache_id
        self.错误处理 = None

    def 语法规则(self, 描述, 优先级=None):
        """
        A decorator that defines a production rule and registers the decorated
        function to be called with the terminals and non-terminals matched by
        that rule.

        A `rule` should consist of a name defining the non-terminal returned
        by the decorated function and a sequence of non-terminals and terminals
        that are supposed to be replaced::

            replacing_non_terminal : ATERMINAL non_terminal

        The name of the non-terminal replacing the sequence is on the left,
        separated from the sequence by a colon. The whitespace around the colon
        is required.

        Knowing this we can define productions::

            pg = ParserGenerator(['NUMBER', 'ADD'])

            @pg.production('number : NUMBER')
            def expr_number(p):
                return BoxInt(int(p[0].getstr()))

            @pg.production('expr : number ADD number')
            def expr_add(p):
                return BoxInt(p[0].getint() + p[2].getint())

        If a state was passed to the parser, the decorated function is
        additionally called with that state as first argument.
        """
        部分 = 描述.split()
        名称 = 部分[0]
        if 部分[1] != ":":
            raise ParserGeneratorError("Expecting :")
        组成 = 部分[2:]

        def inner(func):
            self.productions.append((名称, 组成, func, 优先级))
            return func
        return inner

    def 报错(self, func):
        """
        Sets the error handler that is called with the state (if passed to the
        parser) and the token the parser errored on.

        Currently error handlers must raise an exception. If an error handler
        is not defined, a :exc:`rply.ParsingError` will be raised.
        """
        self.错误处理 = func
        return func

    def compute_grammar_hash(self, g):
        hasher = hashlib.sha1()
        hasher.update(g.start.encode())
        hasher.update(json.dumps(sorted(g.各词所在语法表)).encode())
        for term, (assoc, level) in sorted(iteritems(g.优先级)):
            hasher.update(term.encode())
            hasher.update(assoc.encode())
            hasher.update(bytes(level))
        for p in g.各规则:
            hasher.update(p.name.encode())
            hasher.update(json.dumps(p.优先级).encode())
            hasher.update(json.dumps(p.prod).encode())
        return hasher.hexdigest()

    def serialize_table(self, 表):
        return {
            "lr_action": 表.lr_action,
            "lr_goto": 表.lr_goto,
            "取合不定": 表.取合不定,
            "不知咋合": 表.不知咋合,
            "default_reductions": 表.default_reductions,
            "start": 表.语法.start,
            "terminals": sorted(表.语法.各词所在语法表),
            "precedence": 表.语法.优先级,
            "productions": [
                (p.name, p.prod, p.优先级) for p in 表.语法.各规则
            ],
        }

    def data_is_valid(self, g, data):
        if g.start != data["start"]:
            return False
        if sorted(g.各词所在语法表) != data["terminals"]:
            return False
        if sorted(g.优先级) != sorted(data["precedence"]):
            return False
        for key, (assoc, level) in iteritems(g.优先级):
            if data["precedence"][key] != [assoc, level]:
                return False
        if len(g.各规则) != len(data["productions"]):
            return False
        for p, (name, prod, (assoc, level)) in zip(g.各规则, data["productions"]):
            if p.name != name:
                return False
            if p.prod != prod:
                return False
            if p.优先级 != (assoc, level):
                return False
        return True

    def 产出(self):
        g = 语法(self.词表)

        for level, (assoc, terms) in enumerate(self.优先级, 1):
            for term in terms:
                g.set_precedence(term, assoc, level)

        for prod_name, syms, func, precedence in self.productions:
            g.add_production(prod_name, syms, func, precedence)

        g.牵头()

        for unused_term in g.unused_terminals():
            warnings.warn(
                "词 %r 无用" % unused_term,
                ParserGeneratorWarning,
                stacklevel=2
            )
        for unused_prod in g.无用规则():
            warnings.warn(
                "规则 %r 无用" % unused_prod,
                ParserGeneratorWarning,
                stacklevel=2
            )

        g.build_lritems()
        g.compute_first()
        g.compute_follow()

        表 = None
        if self.cache_id is not None:
            cache_dir = AppDirs("rply").user_cache_dir
            cache_file = os.path.join(
                cache_dir,
                "%s-%s-%s.json" % (
                    self.cache_id, self.VERSION, self.compute_grammar_hash(g)
                )
            )

            if os.path.exists(cache_file):
                with open(cache_file) as f:
                    data = json.load(f)
                if self.data_is_valid(g, data):
                    表 = LRTable.from缓存(g, data)
        if 表 is None:
            表 = LRTable.from语法(g)

            if self.cache_id is not None:
                self._write_cache(cache_dir, cache_file, 表)

        if 表.取合不定:
            歧义 = 表.取合不定
            细节 = '\n\n'.join(['词' + str(i[1]) + '有歧义，默认进行 ' + i[2] + '\n歧义序列：\n' + 输出序列(i[3]) for i in 歧义])
            warnings.warn(
                "如下 %d 种情形取下个词还是合而为一？\n%s" % (
                    len(歧义),
                    细节,
                ),
                ParserGeneratorWarning,
                stacklevel=2,
            )
        if 表.不知咋合:
            warnings.warn(
                "%d 种情形不确定如何合而为一" % (
                    len(表.不知咋合)
                ),
                ParserGeneratorWarning,
                stacklevel=2,
            )
        return LRParser(表, self.错误处理)

    def _write_cache(self, cache_dir, cache_file, 表):
        if not os.path.exists(cache_dir):
            try:
                os.makedirs(cache_dir, mode=0o0700)
            except OSError as e:
                if e.errno == errno.EROFS:
                    return
                raise

        with tempfile.NamedTemporaryFile(dir=cache_dir, delete=False, mode="w") as f:
            json.dump(self.serialize_table(表), f)
        os.rename(f.name, cache_file)


def 输出序列(lr表):
    信息 = ""
    for 项 in lr表:
        信息 += '\t' + 项.name + ": " + " ".join(项.prod) + '\n'
    return 信息

def digraph(X, R, FP):
    N = dict.fromkeys(X, 0)
    stack = []
    F = {}
    for x in X:
        if N[x] == 0:
            traverse(x, N, stack, F, X, R, FP)
    return F


def traverse(x, N, stack, F, X, R, FP):
    stack.append(x)
    d = len(stack)
    N[x] = d
    F[x] = FP(x)

    rel = R(x)
    for y in rel:
        if N[y] == 0:
            traverse(y, N, stack, F, X, R, FP)
        N[x] = min(N[x], N[y])
        for a in F.get(y, []):
            if a not in F[x]:
                F[x].append(a)
    if N[x] == d:
        N[stack[-1]] = LARGE_VALUE
        F[stack[-1]] = F[x]
        element = stack.pop()
        while element != x:
            N[stack[-1]] = LARGE_VALUE
            F[stack[-1]] = F[x]
            element = stack.pop()


class LRTable(object):
    def __init__(self, 语法, lr_action, lr_goto, default_reductions,
                 取合不定, 不知咋合):
        self.语法 = 语法
        self.lr_action = lr_action
        self.lr_goto = lr_goto
        self.default_reductions = default_reductions
        self.取合不定 = 取合不定
        self.不知咋合 = 不知咋合

    @classmethod
    def from缓存(cls, 语法, data):
        lr_action = [
            dict([(str(k), v) for k, v in iteritems(action)])
            for action in data["lr_action"]
        ]
        lr_goto = [
            dict([(str(k), v) for k, v in iteritems(goto)])
            for goto in data["lr_goto"]
        ]
        return LRTable(
            语法,
            lr_action,
            lr_goto,
            data["default_reductions"],
            data["取合不定"],
            data["不知咋合"]
        )

    @classmethod
    def from语法(cls, 语法):
        cidhash = IdentityDict()
        goto_cache = {}
        add_count = Counter()
        C = cls.lr0_items(语法, add_count, cidhash, goto_cache)

        cls.添加lalr预读(语法, C, add_count, cidhash, goto_cache)

        lr_action = [None] * len(C)
        lr_goto = [None] * len(C)
        取合不定 = []
        不知咋合 = []
        for st, I in enumerate(C):
            # 显示所有语法要素序列
            # print(str(st) + '\n' + 输出序列(I) + '')
            st_action = {}
            st_actionp = {}
            st_goto = {}
            for p in I:
                if p.getlength() == p.lr_index + 1:
                    if p.name == "S'":
                        # Start symbol. Accept!
                        st_action["$end"] = 0
                        st_actionp["$end"] = p
                    else:
                        laheads = p.预读[st]
                        for a in laheads:
                            if a in st_action:
                                r = st_action[a]
                                if r > 0:
                                    sprec, 取词层级 = 语法.各规则[st_actionp[a].number].优先级
                                    合词优先方向, 合词层级 = 语法.优先级.get(a, ("right", 0))
                                    if (取词层级 < 合词层级) or (取词层级 == 合词层级 and 合词优先方向 == "left"):
                                        st_action[a] = -p.number
                                        st_actionp[a] = p
                                        if not 取词层级 and not 合词层级:
                                            取合不定.append((st, repr(a), "reduce1"))
                                        语法.各规则[p.number].reduced += 1
                                    elif not (取词层级 == 合词层级 and 合词优先方向 == "nonassoc"):
                                        if not 合词层级:
                                            取合不定.append((st, repr(a), "shift1"))
                                elif r < 0:
                                    oldp = 语法.各规则[-r]
                                    pp = 语法.各规则[p.number]
                                    if oldp.number > pp.number:
                                        st_action[a] = -p.number
                                        st_actionp[a] = p
                                        chosenp, rejectp = pp, oldp
                                        语法.各规则[p.number].reduced += 1
                                        语法.各规则[oldp.number].reduced -= 1
                                    else:
                                        chosenp, rejectp = oldp, pp
                                    不知咋合.append((st, repr(chosenp), repr(rejectp)))
                                else:
                                    raise ParserGeneratorError("Unknown conflict in state %d" % st)
                            else:
                                st_action[a] = -p.number
                                st_actionp[a] = p
                                语法.各规则[p.number].reduced += 1
                else:
                    i = p.lr_index
                    a = p.prod[i + 1]
                    if a in 语法.各词所在语法表:
                        g = cls.lr0_goto(I, a, add_count, goto_cache)
                        j = cidhash.get(g, -1)
                        if j >= 0:
                            if a in st_action:
                                r = st_action[a]
                                if r > 0:
                                    if r != j:
                                        raise ParserGeneratorError("Shift/shift conflict in state %d" % st)
                                elif r < 0:
                                    合词优先方向, 合词层级 = 语法.各规则[st_actionp[a].number].优先级
                                    sprec, 取词层级 = 语法.优先级.get(a, ("right", 0))
                                    if (取词层级 > 合词层级) or (取词层级 == 合词层级 and 合词优先方向 == "right"):
                                        语法.各规则[st_actionp[a].number].reduced -= 1
                                        st_action[a] = j
                                        st_actionp[a] = p
                                        if not 合词层级:
                                            取合不定.append((st, repr(a), "shift2", I))
                                    elif not (取词层级 == 合词层级 and 合词优先方向 == "nonassoc"):
                                        if not 取词层级 and not 合词层级:
                                            取合不定.append((st, repr(a), "reduce2"))
                                else:
                                    raise ParserGeneratorError("Unknown conflict in state %d" % st)
                            else:
                                st_action[a] = j
                                st_actionp[a] = p
            nkeys = set()
            for ii in I:
                for s in ii.unique_syms:
                    if s in 语法.各短语对应语法号:
                        nkeys.add(s)
            for n in nkeys:
                g = cls.lr0_goto(I, n, add_count, goto_cache)
                j = cidhash.get(g, -1)
                if j >= 0:
                    st_goto[n] = j

            lr_action[st] = st_action
            lr_goto[st] = st_goto

        default_reductions = [0] * len(lr_action)
        for state, actions in enumerate(lr_action):
            actions = set(itervalues(actions))
            if len(actions) == 1 and next(iter(actions)) < 0:
                default_reductions[state] = next(iter(actions))
        return LRTable(语法, lr_action, lr_goto, default_reductions, 取合不定, 不知咋合)

    @classmethod
    def lr0_items(cls, 语法, add_count, cidhash, goto_cache):
        C = [cls.lr0_closure([语法.各规则[0].lr_next], add_count)]
        for i, I in enumerate(C):
            cidhash[I] = i

        i = 0
        while i < len(C):
            I = C[i]
            i += 1

            asyms = set()
            for ii in I:
                asyms.update(ii.unique_syms)
            for x in asyms:
                g = cls.lr0_goto(I, x, add_count, goto_cache)
                if not g:
                    continue
                if g in cidhash:
                    continue
                cidhash[g] = len(C)
                C.append(g)
        return C

    @classmethod
    def lr0_closure(cls, I, add_count):
        add_count.incr()

        J = I[:]
        added = True
        while added:
            added = False
            for j in J:
                for x in j.lr_after:
                    if x.lr0_added == add_count.value:
                        continue
                    J.append(x.lr_next)
                    x.lr0_added = add_count.value
                    added = True
        return J

    @classmethod
    def lr0_goto(cls, I, x, add_count, goto_cache):
        s = goto_cache.setdefault(x, IdentityDict())

        gs = []
        for p in I:
            n = p.lr_next
            if n and n.lr_before == x:
                s1 = s.get(n)
                if not s1:
                    s1 = {}
                    s[n] = s1
                gs.append(n)
                s = s1
        g = s.get("$end")
        if not g:
            if gs:
                g = cls.lr0_closure(gs, add_count)
                s["$end"] = g
            else:
                s["$end"] = gs
        return g

    @classmethod
    def 添加lalr预读(cls, 语法, C, add_count, cidhash, goto_cache):
        nullable = cls.compute_nullable_nonterminals(语法)
        trans = cls.find_nonterminal_transitions(语法, C)
        readsets = cls.compute_read_sets(语法, C, trans, nullable, add_count, cidhash, goto_cache)
        lookd, included = cls.compute_lookback_includes(语法, C, trans, nullable, add_count, cidhash, goto_cache)
        followsets = cls.compute_follow_sets(trans, readsets, included)
        cls.添加预读(lookd, followsets)

    @classmethod
    def compute_nullable_nonterminals(cls, 语法):
        nullable = set()
        num_nullable = 0
        while True:
            for p in 语法.各规则[1:]:
                if p.getlength() == 0:
                    nullable.add(p.name)
                    continue
                for t in p.prod:
                    if t not in nullable:
                        break
                else:
                    nullable.add(p.name)
            if len(nullable) == num_nullable:
                break
            num_nullable = len(nullable)
        return nullable

    @classmethod
    def find_nonterminal_transitions(cls, 语法, C):
        trans = []
        for idx, state in enumerate(C):
            for p in state:
                if p.lr_index < p.getlength() - 1:
                    t = (idx, p.prod[p.lr_index + 1])
                    if t[1] in 语法.各短语对应语法号 and t not in trans:
                        trans.append(t)
        return trans

    @classmethod
    def compute_read_sets(cls, 语法, C, ntrans, nullable, add_count, cidhash, goto_cache):
        return digraph(
            ntrans,
            R=lambda x: cls.reads_relation(C, x, nullable, add_count, cidhash, goto_cache),
            FP=lambda x: cls.dr_relation(语法, C, x, nullable, add_count, goto_cache)
        )

    @classmethod
    def compute_follow_sets(cls, ntrans, readsets, includesets):
        return digraph(
            ntrans,
            R=lambda x: includesets.get(x, []),
            FP=lambda x: readsets[x],
        )

    @classmethod
    def dr_relation(cls, 语法, C, trans, nullable, add_count, goto_cache):
        state, N = trans
        terms = []

        g = cls.lr0_goto(C[state], N, add_count, goto_cache)
        for p in g:
            if p.lr_index < p.getlength() - 1:
                a = p.prod[p.lr_index + 1]
                if a in 语法.各词所在语法表 and a not in terms:
                    terms.append(a)
        if state == 0 and N == 语法.各规则[0].prod[0]:
            terms.append("$end")
        return terms

    @classmethod
    def reads_relation(cls, C, trans, empty, add_count, cidhash, goto_cache):
        rel = []
        state, N = trans

        g = cls.lr0_goto(C[state], N, add_count, goto_cache)
        j = cidhash.get(g, -1)
        for p in g:
            if p.lr_index < p.getlength() - 1:
                a = p.prod[p.lr_index + 1]
                if a in empty:
                    rel.append((j, a))
        return rel

    @classmethod
    def compute_lookback_includes(cls, 语法, C, trans, nullable, add_count, cidhash, goto_cache):
        lookdict = {}
        includedict = {}

        dtrans = dict.fromkeys(trans, 1)

        for state, N in trans:
            lookb = []
            includes = []
            for p in C[state]:
                if p.name != N:
                    continue

                lr_index = p.lr_index
                j = state
                while lr_index < p.getlength() - 1:
                    lr_index += 1
                    t = p.prod[lr_index]

                    if (j, t) in dtrans:
                        li = lr_index + 1
                        while li < p.getlength():
                            if p.prod[li] in 语法.各词所在语法表:
                                break
                            if p.prod[li] not in nullable:
                                break
                            li += 1
                        else:
                            includes.append((j, t))

                    g = cls.lr0_goto(C[j], t, add_count, goto_cache)
                    j = cidhash.get(g, -1)

                for r in C[j]:
                    if r.name != p.name:
                        continue
                    if r.getlength() != p.getlength():
                        continue
                    i = 0
                    while i < r.lr_index:
                        if r.prod[i] != p.prod[i + 1]:
                            break
                        i += 1
                    else:
                        lookb.append((j, r))

            for i in includes:
                includedict.setdefault(i, []).append((state, N))
            lookdict[state, N] = lookb
        return lookdict, includedict

    @classmethod
    def 添加预读(cls, lookbacks, followset):
        for trans, lb in iteritems(lookbacks):
            for state, p in lb:
                f = followset.get(trans, [])
                laheads = p.预读.setdefault(state, [])
                for a in f:
                    if a not in laheads:
                        laheads.append(a)
