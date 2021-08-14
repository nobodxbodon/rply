from rply.报错 import 分词报错
from rply.词 import 字符位置, 词


class 分词器(object):
    def __init__(自身, 规则, 略过规则):
        自身.规则 = 规则
        自身.略过规则 = 略过规则

    def lex(自身, 源码):
        return 自身.分词(源码)

    def 分词(自身, 源码):
        return 词流(自身, 源码)


class 词流(object):
    def __init__(自身, 分词器, 源码):
        自身.分词器 = 分词器
        自身.源码 = 源码
        自身.位置 = 0

        自身._行号 = 1
        自身._列号 = 1

    def __iter__(自身):
        return 自身

    def _更新位置(自身, 匹配):
        自身.位置 = 匹配.止
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
            if 自身.位置 >= len(自身.源码):
                raise StopIteration
            for 规则 in 自身.分词器.略过规则:
                匹配 = 规则.matches(自身.源码, 自身.位置)
                if 匹配:
                    自身._更新位置(匹配)
                    break
            else:
                break

        for 规则 in 自身.分词器.规则:
            匹配 = 规则.matches(自身.源码, 自身.位置)
            if 匹配:
                行号 = 自身._行号
                自身._列号 = 自身._更新位置(匹配)
                源码位置 = 字符位置(匹配.起, 行号, 自身._列号)
                某词 = 词(
                    规则.词名, 自身.源码[匹配.起:匹配.止], 源码位置
                )
                return 某词
        else:
            # 如果无匹配，定位在上个匹配的下一字符
            自身._列号 = 自身._按字符更新位置(自身.位置)
            raise 分词报错(None, 字符位置(
                自身.位置, 自身._行号, 自身._列号))

    def __next__(自身):
        return 自身.next()