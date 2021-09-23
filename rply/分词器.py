from rply.报错 import 分词报错, 按语法分词报错
from rply.词 import 字符位置, 词

调试细节 = 0
class 分词器(object):
    def __init__(自身, 词规则, 略过规则):
        自身.词规则 = 词规则
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

        # TODO：此三个表需合并或清理
        # 同一位置可能多个词法规则无效，位置:int->各规则:set
        自身.各位置失败规则 = {}

        # 规则->长度:int
        自身.变长模式已试长度 = {}

        # 位置:int->规则
        自身.当前路径各匹配词法 = {}

        # 位置:int->(当前状态, 状态栈[:], 符号栈[:], 预读栈[:], 预读)
        自身.回退点 = {} # 所有回退栈中的位置必有对应回退点

        # 位置:int
        自身.回退栈 = [] # 仅保存当前搜索路径相关位置

        # 为调试回退之用
        自身.回退次数 = 0
        自身.退出 = False

        自身.分词到达最远位置 = 0
        自身.最远位置对应路径 = []

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
        print("当前位置：" + str(自身.位置))
        while True:
            if 自身.位置 >= len(自身.源码):
                raise StopIteration
            for 规则 in 自身.分词器.略过规则:
                略过 = 规则.匹配(自身.源码, 自身.位置)
                if 略过:
                    自身._更新位置(略过)
                    break
            else:
                break

        for 规则 in 自身.分词器.词规则:
            if 自身.位置 in 自身.各位置失败规则 and 规则 in 自身.各位置失败规则[自身.位置]:
                匹配词 = 自身._匹配变长模式(规则)
            else:
                if 调试细节:
                    print(f"位置 {自身.位置} 第一次尝试：{规则}")
                匹配词 = 规则.匹配(自身.源码, 自身.位置)

            if 匹配词:
                if 自身._为变长匹配(规则):
                    匹配长度 = 匹配词.止 - 匹配词.起
                    print(f"变长模式匹配于 {自身.位置} ：规则：{规则}，长度：{匹配长度}")
                    if 规则 not in 自身.变长模式已试长度:
                        自身.变长模式已试长度[规则] = {}
                    自身.变长模式已试长度[规则][自身.位置] = 匹配长度
                自身.当前路径各匹配词法[自身.位置] = 规则
                
                行号 = 自身._行号
                自身._列号 = 自身._更新位置(匹配词)
                源码位置 = 字符位置(匹配词.起, 行号, 自身._列号)
                某词 = 词(
                    规则.词名, 自身.源码[匹配词.起:匹配词.止], 源码位置
                )
                if 调试细节:
                    print(f"找到匹配词：{某词.value}, 路径历史：{自身.当前路径各匹配词法}")

                return 某词
        else:
            print("完全无匹配")
            # 如果无匹配，定位在上个匹配的下一字符
            自身._列号 = 自身._按字符更新位置(自身.位置)
            raise 分词报错(None, 字符位置(
                自身.位置, 自身._行号, 自身._列号))


    # TODO: 待支持其他通配符或 {m,n} 等变长匹配
    def _为变长匹配(自身, 规则):
        return '\\' in 规则.正则.pattern

    def _匹配变长模式(自身, 规则):
        if 规则 in 自身.变长模式已试长度:
            已试长度 = 自身.变长模式已试长度[规则][自身.位置]
            if 已试长度 > 1:
                匹配词 = 规则.匹配(自身.源码, 自身.位置, 自身.位置 + 已试长度 - 1)
                return 匹配词
            else:
                print(f"变长模式已试完：{规则}")
        else:
            print(f"非变长模式已不符语法规则：{规则}")

    def _标记失败规则(自身):
        相关规则 = 自身.当前路径各匹配词法[自身.位置]
        print(f"标记失败规则: {自身.位置} -> {相关规则}")
        if 自身.位置 in 自身.各位置失败规则:
            自身.各位置失败规则[自身.位置].add(相关规则)
        else:
            自身.各位置失败规则[自身.位置] = set([相关规则])

    def 记录状态(自身, 当前状态, 状态栈, 符号栈, 预读栈, 预读):
        自身.回退点[自身.位置] = (当前状态, 状态栈[:], 符号栈[:], 预读栈[:], 预读)
        自身.回退栈.append(自身.位置)
        print(f"回退栈: {自身.回退栈}")


    # 返回：回退点的语法状态
    # 选取最近的回退点
    def 回退(自身, 最多回退数):
        if 自身.分词到达最远位置 < 自身.位置:
            自身.分词到达最远位置 = 自身.位置
            for 位置 in 自身.回退栈:
                # TODO: 为何有些位置无对应词法？
                自身.最远位置对应路径.append((位置, 自身.当前路径各匹配词法[位置].词名 if 位置 in 自身.当前路径各匹配词法 else None))

        if 自身.回退栈:
            回退位置 = 自身.回退栈.pop()
            while 回退位置 >= 自身.位置:
                if 自身.回退栈:
                    回退位置 = 自身.回退栈.pop()
                else:
                    print("栈已空！")
                    raise 按语法分词报错(自身.最远位置对应路径)
            print(f"回退位置: {回退位置}, 回退栈：{自身.回退栈}")
            自身.位置 = 回退位置
            自身.回退次数 += 1
            自身.各位置失败规则 = 自身.清理后续问题规则(自身.位置)
            自身._标记失败规则()
            if 自身.回退次数 >= 最多回退数: # 避免死循环
                print(f"回退过多：{自身.回退次数}")
                自身.强制退出()
            print(f"回退次数: {自身.回退次数}")
            return 自身.回退点[自身.位置]
        else:
            # TODO: 何时为空？
            print("栈为空！")
            return None

    def 清理后续问题规则(自身, 当前位置):
        if 调试细节:
            print(f"!!!!!各位置失败规则: {自身.各位置失败规则}")
            print(f"变长模式已试长度：{自身.变长模式已试长度}")
            print(f"当前路径各匹配词法: {自身.当前路径各匹配词法}")
        新规则表 = {}
        for 位置 in 自身.各位置失败规则:
            if 位置 <= 当前位置:
                新规则表[位置] = 自身.各位置失败规则[位置].copy()
            else:
                print(f"清理后续问题规则：位置 {位置}，当前位置 {当前位置}")
        return 新规则表

    def 强制退出(自身):
        自身.退出 = True
        raise 分词报错(None, 字符位置(
                自身.位置, 自身._行号, 自身._列号))

    def __next__(自身):
        return 自身.next()