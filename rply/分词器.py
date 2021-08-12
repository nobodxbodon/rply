from rply.报错 import 分词报错
from rply.词 import 字符位置, 词


class 分词器(object):
    def __init__(自身, rules, ignore_rules):
        自身.rules = rules
        自身.ignore_rules = ignore_rules

    def lex(自身, s):
        return 自身.分词(s)

    def 分词(自身, s):
        return LexerStream(自身, s)


class LexerStream(object):
    def __init__(自身, lexer, s):
        自身.lexer = lexer
        自身.s = s
        自身.idx = 0

        自身._行号 = 1
        自身._列号 = 1

    def __iter__(自身):
        return 自身

    def _更新位置(自身, match):
        自身.idx = match.end
        自身._行号 += 自身.s.count("\n", match.start, match.end)
        最近换行 = 自身.s.rfind("\n", 0, match.start)
        if 最近换行 < 0:
            return match.start + 1
        else:
            return match.start - 最近换行

    def _按字符更新位置(自身, 字符位置):
        自身._行号 += 1 if 自身.s[字符位置] == "\n" else 0
        最近换行 = 自身.s.rfind("\n", 0, 字符位置)
        if 最近换行 < 0:
            return 字符位置 + 1
        else:
            return 1

    def next(自身):
        while True:
            if 自身.idx >= len(自身.s):
                raise StopIteration
            for rule in 自身.lexer.ignore_rules:
                match = rule.matches(自身.s, 自身.idx)
                if match:
                    自身._更新位置(match)
                    break
            else:
                break

        for rule in 自身.lexer.rules:
            match = rule.matches(自身.s, 自身.idx)
            if match:
                lineno = 自身._行号
                自身._列号 = 自身._更新位置(match)
                源码位置 = 字符位置(match.start, lineno, 自身._列号)
                token = 词(
                    rule.name, 自身.s[match.start:match.end], 源码位置
                )
                return token
        else:
            # 如果无匹配，定位在上个匹配的下一字符
            自身._列号 = 自身._按字符更新位置(自身.idx)
            raise 分词报错(None, 字符位置(
                自身.idx, 自身._行号, 自身._列号))

    def __next__(自身):
        return 自身.next()
