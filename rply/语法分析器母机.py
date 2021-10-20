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
from rply.功用 import 计数器, IdentityDict, iteritems, itervalues


LARGE_VALUE = sys.maxsize


class 语法分析器母机(object):
    """
    A ParserGenerator represents a set of production 规则, that define a
    sequence of terminals and non-terminals to be replaced with a non-terminal,
    which can be turned into a parser.

    :param 词表: A list of token (non-terminal) names.
    :param 优先级: A list of tuples defining the order of operation for
                       avoiding ambiguity, consisting of a string defining
                       associativity (left, right or nonassoc) and a list of
                       token names with the same associativity and 层级 of
                       precedence.
    :param cache_id: A string specifying an ID for caching.
    """
    VERSION = 1

    def __init__(自身, 词表, 优先级=[], cache_id=None):
        自身.词表 = 词表
        自身.productions = []
        自身.优先级 = 优先级
        自身.cache_id = cache_id
        自身.错误处理 = None

    def 语法规则(自身, 描述, 优先级=None):
        """
        A decorator that defines one or many production rules and registers
        the decorated function to be called with the terminals and
        non-terminals matched by those rules.

        A `rule` should consist of a name defining the non-terminal returned
        by the decorated function and one or more sequences of pipe-separated
        non-terminals and terminals that are supposed to be replaced::

            replacing_non_terminal : TERMINAL1 non_term1 | TERMINAL2 non_term2

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
        规则文本 = " ".join(部分[2:])
        所有规则 = 规则文本.split("|")

        def inner(func):
            for 规则 in 所有规则:
                各符号 = 规则.split()
                自身.productions.append((名称, 各符号, func, 优先级))
            return func
        return inner

    def 报错(自身, func):
        """
        Sets the error handler that is called with the state (if passed to the
        parser) and the token the parser errored on.

        Currently error handlers must raise an exception. If an error handler
        is not defined, a :exc:`rply.ParsingError` will be raised.
        """
        自身.错误处理 = func
        return func

    def compute_grammar_hash(自身, 语法):
        hasher = hashlib.sha1()
        hasher.update(语法.开头.encode())
        hasher.update(json.dumps(sorted(语法.各词所在语法表)).encode())
        for term, (结合性, 层级) in sorted(iteritems(语法.优先级)):
            hasher.update(term.encode())
            hasher.update(结合性.encode())
            hasher.update(bytes(层级))
        for 规则 in 语法.各规则:
            hasher.update(规则.名称.encode())
            hasher.update(json.dumps(规则.优先级).encode())
            hasher.update(json.dumps(规则.模式).encode())
        return hasher.hexdigest()

    def serialize_table(自身, 表):
        return {
            "lr_action": 表.lr_action,
            "lr_goto": 表.lr_goto,
            "取合不定": 表.取合不定,
            "不知咋合": 表.不知咋合,
            "default_reductions": 表.default_reductions,
            "start": 表.语法.开头,
            "terminals": sorted(表.语法.各词所在语法表),
            "precedence": 表.语法.优先级,
            "productions": [
                (规则.名称, 规则.模式, 规则.优先级) for 规则 in 表.语法.各规则
            ],
        }

    def 数据无误(自身, 语法, 数据):
        if 语法.开头 != 数据["start"]:
            return False
        if sorted(语法.各词所在语法表) != 数据["terminals"]:
            return False
        if sorted(语法.优先级) != sorted(数据["precedence"]):
            return False
        for key, (结合性, 层级) in iteritems(语法.优先级):
            if 数据["precedence"][key] != [结合性, 层级]:
                return False
        if len(语法.各规则) != len(数据["productions"]):
            return False
        for 规则, (规则名, 模式, (结合性, 层级)) in zip(语法.各规则, 数据["productions"]):
            if 规则.名称 != 规则名:
                return False
            if 规则.模式 != 模式:
                return False
            if 规则.优先级 != (结合性, 层级):
                return False
        return True

    def 产出(自身):
        语法细节 = 语法(自身.词表)

        for 层级, (结合性, terms) in enumerate(自身.优先级, 1):
            for term in terms:
                语法细节.设置优先级(term, 结合性, 层级)

        for 规则名, 各符号, func, 优先级 in 自身.productions:
            语法细节.添加规则(规则名, 各符号, func, 优先级)

        语法细节.牵头()

        for 词 in 语法细节.无用词():
            warnings.warn(
                "词 %r 无用" % 词,
                ParserGeneratorWarning,
                stacklevel=2
            )
        for 规则 in 语法细节.无用规则():
            warnings.warn(
                "规则 %r 无用" % 规则,
                ParserGeneratorWarning,
                stacklevel=2
            )

        语法细节.生成各lr项()
        语法细节.compute_first()
        语法细节.compute_follow()

        表 = None
        if 自身.cache_id is not None:
            cache_dir = AppDirs("rply").user_cache_dir
            cache_file = os.path.join(
                cache_dir,
                "%s-%s-%s.json" % (
                    自身.cache_id, 自身.VERSION, 自身.compute_grammar_hash(语法细节)
                )
            )

            if os.path.exists(cache_file):
                with open(cache_file) as f:
                    数据 = json.load(f)
                if 自身.数据无误(语法细节, 数据):
                    表 = LRTable.from缓存(语法细节, 数据)
        if 表 is None:
            表 = LRTable.from语法(语法细节)

            if 自身.cache_id is not None:
                自身._write_cache(cache_dir, cache_file, 表)

        if 表.取合不定:
            歧义 = 表.取合不定
            # 仅 shift2 有细节
            细节 = '\n\n'.join(['词' + str(i[1]) + '有歧义，默认进行 ' + i[2] + ('\n歧义序列：\n' + 输出序列(i[3]) if len(i) == 4 else "") for i in 歧义])
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
        return LRParser(表, 自身.错误处理)

    def _write_cache(自身, cache_dir, cache_file, 表):
        if not os.path.exists(cache_dir):
            try:
                os.makedirs(cache_dir, mode=0o0700)
            except OSError as e:
                if e.errno == errno.EROFS:
                    return
                raise

        with tempfile.NamedTemporaryFile(dir=cache_dir, delete=False, mode="w") as f:
            json.dump(自身.serialize_table(表), f)
        os.rename(f.name, cache_file)


def 输出序列(lr表):
    信息 = ""
    for 项 in lr表:
        信息 += '\t' + 项.规则名称 + ": " + " ".join(项.所在模式位置) + '\n'
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
    def __init__(自身, 语法, lr_action, lr_goto, default_reductions,
                 取合不定, 不知咋合):
        自身.语法 = 语法
        自身.lr_action = lr_action
        自身.lr_goto = lr_goto
        自身.default_reductions = default_reductions
        自身.取合不定 = 取合不定
        自身.不知咋合 = 不知咋合

    @classmethod
    def from缓存(本类, 语法, 数据):
        lr_action = [
            dict([(str(k), v) for k, v in iteritems(action)])
            for action in 数据["lr_action"]
        ]
        lr_goto = [
            dict([(str(k), v) for k, v in iteritems(goto)])
            for goto in 数据["lr_goto"]
        ]
        return LRTable(
            语法,
            lr_action,
            lr_goto,
            数据["default_reductions"],
            数据["取合不定"],
            数据["不知咋合"]
        )

    @classmethod
    def from语法(本类, 语法):
        cidhash = IdentityDict()
        goto_cache = {}
        计数 = 计数器()
        C = 本类.lr0各项(语法, 计数, cidhash, goto_cache)

        本类.添加lalr预读(语法, C, 计数, cidhash, goto_cache)

        lr_action = [None] * len(C)
        lr_goto = [None] * len(C)
        取合不定 = []
        不知咋合 = []
        for 状态号, I in enumerate(C):
            # 显示所有语法要素序列
            # print(str(状态号) + '\n' + 输出序列(I) + '')
            st_action = {}
            st_actionp = {}
            st_goto = {}
            for lr项 in I:
                if lr项.取长度() == lr项.索引 + 1:
                    if lr项.规则名称 == "S'":
                        # Start symbol. Accept!
                        st_action["$end"] = 0
                        st_actionp["$end"] = lr项
                    else:
                        laheads = lr项.预读[状态号]
                        for a in laheads:
                            if a in st_action:
                                r = st_action[a]
                                if r > 0:
                                    sprec, 取词层级 = 语法.各规则[st_actionp[a].规则序号].优先级
                                    合词优先方向, 合词层级 = 语法.优先级.get(a, ("right", 0))
                                    if (取词层级 < 合词层级) or (取词层级 == 合词层级 and 合词优先方向 == "left"):
                                        st_action[a] = -lr项.规则序号
                                        st_actionp[a] = lr项
                                        if not 取词层级 and not 合词层级:
                                            取合不定.append((状态号, repr(a), "reduce1"))
                                        语法.各规则[lr项.规则序号].reduced += 1
                                    elif not (取词层级 == 合词层级 and 合词优先方向 == "nonassoc"):
                                        if not 合词层级:
                                            取合不定.append((状态号, repr(a), "shift1"))
                                elif r < 0:
                                    oldp = 语法.各规则[-r]
                                    pp = 语法.各规则[lr项.规则序号]
                                    if oldp.序号 > pp.序号:
                                        st_action[a] = -lr项.规则序号
                                        st_actionp[a] = lr项
                                        chosenp, rejectp = pp, oldp
                                        语法.各规则[lr项.规则序号].reduced += 1
                                        语法.各规则[oldp.规则序号].reduced -= 1
                                    else:
                                        chosenp, rejectp = oldp, pp
                                    不知咋合.append((状态号, repr(chosenp), repr(rejectp)))
                                else:
                                    raise ParserGeneratorError("Unknown conflict in state %d" % 状态号)
                            else:
                                st_action[a] = -lr项.规则序号
                                st_actionp[a] = lr项
                                语法.各规则[lr项.规则序号].reduced += 1
                else:
                    i = lr项.索引
                    a = lr项.所在模式位置[i + 1]
                    if a in 语法.各词所在语法表:
                        g = 本类.lr0_goto(I, a, 计数, goto_cache)
                        j = cidhash.get(g, -1)
                        if j >= 0:
                            if a in st_action:
                                r = st_action[a]
                                if r > 0:
                                    if r != j:
                                        raise ParserGeneratorError("Shift/shift conflict in state %d" % 状态号)
                                elif r < 0:
                                    合词优先方向, 合词层级 = 语法.各规则[st_actionp[a].规则序号].优先级
                                    sprec, 取词层级 = 语法.优先级.get(a, ("right", 0))
                                    if (取词层级 > 合词层级) or (取词层级 == 合词层级 and 合词优先方向 == "right"):
                                        语法.各规则[st_actionp[a].规则序号].reduced -= 1
                                        st_action[a] = j
                                        st_actionp[a] = lr项
                                        if not 合词层级:
                                            取合不定.append((状态号, repr(a), "shift2", I))
                                    elif not (取词层级 == 合词层级 and 合词优先方向 == "nonassoc"):
                                        if not 取词层级 and not 合词层级:
                                            取合不定.append((状态号, repr(a), "reduce2"))
                                else:
                                    raise ParserGeneratorError("Unknown conflict in state %d" % 状态号)
                            else:
                                st_action[a] = j
                                st_actionp[a] = lr项
            nkeys = set()
            for ii in I:
                for s in ii.规则所含符号集合:
                    if s in 语法.各短语对应语法号:
                        nkeys.add(s)
            for n in nkeys:
                g = 本类.lr0_goto(I, n, 计数, goto_cache)
                j = cidhash.get(g, -1)
                if j >= 0:
                    st_goto[n] = j

            lr_action[状态号] = st_action
            lr_goto[状态号] = st_goto

        default_reductions = [0] * len(lr_action)
        for 状态号, actions in enumerate(lr_action):
            actions = set(itervalues(actions))
            if len(actions) == 1 and next(iter(actions)) < 0:
                default_reductions[状态号] = next(iter(actions))
        return LRTable(语法, lr_action, lr_goto, default_reductions, 取合不定, 不知咋合)

    @classmethod
    def lr0各项(本类, 语法, 计数, cidhash, goto_cache):
        C = [本类.lr0_closure([语法.各规则[0].lr_next], 计数)]
        for i, I in enumerate(C):
            cidhash[I] = i

        i = 0
        while i < len(C):
            I = C[i]
            i += 1

            asyms = set()
            for ii in I:
                asyms.update(ii.规则所含符号集合)
            for x in asyms:
                g = 本类.lr0_goto(I, x, 计数, goto_cache)
                if not g:
                    continue
                if g in cidhash:
                    continue
                cidhash[g] = len(C)
                C.append(g)
        return C

    @classmethod
    def lr0_closure(本类, I, 计数):
        计数.递增()

        J = I[:]
        added = True
        while added:
            added = False
            for j in J:
                for x in j.lr_after:
                    if x.lr0_added == 计数.值:
                        continue
                    J.append(x.lr_next)
                    x.lr0_added = 计数.值
                    added = True
        return J

    @classmethod
    def lr0_goto(本类, I, x, 计数, goto_cache):
        s = goto_cache.setdefault(x, IdentityDict())

        gs = []
        for 规则 in I:
            n = 规则.lr_next
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
                g = 本类.lr0_closure(gs, 计数)
                s["$end"] = g
            else:
                s["$end"] = gs
        return g

    @classmethod
    def 添加lalr预读(本类, 语法, C, 计数, cidhash, goto_cache):
        nullable = 本类.compute_nullable_nonterminals(语法)
        trans = 本类.find_nonterminal_transitions(语法, C)
        readsets = 本类.compute_read_sets(语法, C, trans, nullable, 计数, cidhash, goto_cache)
        lookd, included = 本类.compute_lookback_includes(语法, C, trans, nullable, 计数, cidhash, goto_cache)
        followsets = 本类.compute_follow_sets(trans, readsets, included)
        本类.添加预读(lookd, followsets)

    @classmethod
    def compute_nullable_nonterminals(本类, 语法):
        nullable = set()
        num_nullable = 0
        while True:
            for 规则 in 语法.各规则[1:]:
                if 规则.取长度() == 0:
                    nullable.add(规则.名称)
                    continue
                for 词 in 规则.模式:
                    if 词 not in nullable:
                        break
                else:
                    nullable.add(规则.名称)
            if len(nullable) == num_nullable:
                break
            num_nullable = len(nullable)
        return nullable

    @classmethod
    def find_nonterminal_transitions(本类, 语法, C):
        trans = []
        for idx, 状态 in enumerate(C):
            for lr项 in 状态:
                if lr项.索引 < lr项.取长度() - 1:
                    t = (idx, lr项.所在模式位置[lr项.索引 + 1])
                    if t[1] in 语法.各短语对应语法号 and t not in trans:
                        trans.append(t)
        return trans

    @classmethod
    def compute_read_sets(本类, 语法, C, ntrans, nullable, 计数, cidhash, goto_cache):
        return digraph(
            ntrans,
            R=lambda x: 本类.reads_relation(C, x, nullable, 计数, cidhash, goto_cache),
            FP=lambda x: 本类.dr_relation(语法, C, x, nullable, 计数, goto_cache)
        )

    @classmethod
    def compute_follow_sets(本类, ntrans, readsets, includesets):
        return digraph(
            ntrans,
            R=lambda x: includesets.get(x, []),
            FP=lambda x: readsets[x],
        )

    @classmethod
    def dr_relation(本类, 语法, C, trans, nullable, 计数, goto_cache):
        状态号, N = trans
        terms = []

        g = 本类.lr0_goto(C[状态号], N, 计数, goto_cache)
        for lr项 in g:
            if lr项.索引 < lr项.取长度() - 1:
                a = lr项.所在模式位置[lr项.索引 + 1]
                if a in 语法.各词所在语法表 and a not in terms:
                    terms.append(a)
        if 状态号 == 0 and N == 语法.各规则[0].模式[0]:
            terms.append("$end")
        return terms

    @classmethod
    def reads_relation(本类, C, trans, empty, 计数, cidhash, goto_cache):
        rel = []
        状态号, N = trans

        g = 本类.lr0_goto(C[状态号], N, 计数, goto_cache)
        j = cidhash.get(g, -1)
        for lr项 in g:
            if lr项.索引 < lr项.取长度() - 1:
                a = lr项.所在模式位置[lr项.索引 + 1]
                if a in empty:
                    rel.append((j, a))
        return rel

    @classmethod
    def compute_lookback_includes(本类, 语法, C, trans, nullable, 计数, cidhash, goto_cache):
        lookdict = {}
        includedict = {}

        dtrans = dict.fromkeys(trans, 1)

        for 状态号, N in trans:
            lookb = []
            includes = []
            for lr项 in C[状态号]:
                if lr项.规则名称 != N:
                    continue

                索引 = lr项.索引
                j = 状态号
                while 索引 < lr项.取长度() - 1:
                    索引 += 1
                    词 = lr项.所在模式位置[索引]

                    if (j, 词) in dtrans:
                        li = 索引 + 1
                        while li < lr项.取长度():
                            if lr项.所在模式位置[li] in 语法.各词所在语法表:
                                break
                            if lr项.所在模式位置[li] not in nullable:
                                break
                            li += 1
                        else:
                            includes.append((j, 词))

                    g = 本类.lr0_goto(C[j], 词, 计数, goto_cache)
                    j = cidhash.get(g, -1)

                for r in C[j]:
                    if r.规则名称 != lr项.规则名称:
                        continue
                    if r.取长度() != lr项.取长度():
                        continue
                    i = 0
                    while i < r.索引:
                        if r.所在模式位置[i] != lr项.所在模式位置[i + 1]:
                            break
                        i += 1
                    else:
                        lookb.append((j, r))

            for i in includes:
                includedict.setdefault(i, []).append((状态号, N))
            lookdict[状态号, N] = lookb
        return lookdict, includedict

    @classmethod
    def 添加预读(本类, lookbacks, followset):
        for trans, lb in iteritems(lookbacks):
            for 状态号, 规则 in lb:
                f = followset.get(trans, [])
                laheads = 规则.预读.setdefault(状态号, [])
                for a in f:
                    if a not in laheads:
                        laheads.append(a)
