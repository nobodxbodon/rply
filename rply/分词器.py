from rply.报错 import 分词报错
from rply.词 import 字符位置, 词


class 分词器(object):
    def __init__(自身, 规则, 略过规则):
        自身.规则 = 规则
        自身.略过规则 = 略过规则

    def lex(自身, 源码):
        return 自身.分词(源码)

    def 分词(自身, 源码):
        return LexerStream(自身, 源码)


class LexerStream(object):
    def __init__(自身, lexer, 源码):
        自身.lexer = lexer
        自身.源码 = 源码
        自身.idx = 0

        自身._行号 = 1
        自身._列号 = 1

    def __iter__(自身):
        return 自身

    def _更新位置(自身, 匹配):
        自身.idx = 匹配.止
        自身._行号 += 自身.源码.count("\n", 匹配.起, 匹配.止)
        最近换行 = 自身.源码.rfind("\n", 0, 匹配.起)
        if 最近换行 < 0:
            return 匹配.起 + 1
        else:
            return 匹配.起 - 最近换行

    def _按字符更新位置(自身, 字符位置):
        自身._行号 += 1 if 自身.源码[字符位置] == "\n" else 0
        最近换行 = 自身.源码.rfind("\n", 0, 字符位置)
        if 最近换行 < 0:
            return 字符位置 + 1
        else:
            return 1

    def next(自身):
        while True:
            if 自身.idx >= len(自身.源码):
                raise StopIteration
            for rule in 自身.lexer.略过规则:
                匹配 = rule.matches(自身.源码, 自身.idx)
                if 匹配:
                    自身._更新位置(匹配)
                    break
            else:
                break

        for rule in 自身.lexer.规则:
            匹配 = rule.matches(自身.源码, 自身.idx)
            if 匹配:
                lineno = 自身._行号
                自身._列号 = 自身._更新位置(匹配)
                源码位置 = 字符位置(匹配.起, lineno, 自身._列号)
                token = 词(
                    rule.name, 自身.源码[匹配.起:匹配.止], 源码位置
                )
                return token
        else:
            # 如果无匹配，定位在上个匹配的下一字符
            自身._列号 = 自身._按字符更新位置(自身.idx)
            raise 分词报错(None, 字符位置(
                自身.idx, 自身._行号, 自身._列号))

    def __next__(自身):
        return 自身.next()