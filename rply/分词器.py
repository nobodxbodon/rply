from rply.报错 import 分词报错
from rply.词 import 字符位置, 词


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
        自身.上个位置 = None
        自身.上个规则 = None
        # 同一位置可能多个词法规则无效，int->set。TODO: 添加终止位置，应付可变长模式（+或*)
        自身.不符语法词法规则 = {}
        自身.变长模式已试长度 = {}
        自身.回退点 = {}

        # 为调试回退之用
        自身.回退次数 = 0
        自身.退出 = False

    def __iter__(自身):
        return 自身

    def _更新位置(自身, 匹配):
        print("_更新位置: " + str(自身.位置) + "->" + str(匹配.止))
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
        print("变长模式已试长度: " + str(自身.变长模式已试长度))
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
            if 自身.位置 in 自身.不符语法词法规则 and 规则 in 自身.不符语法词法规则[自身.位置]:
                if 规则 in 自身.变长模式已试长度:
                    # if 自身.位置 not in 自身.变长模式已试长度[规则]:
                    #    print("变长模式" +  + str(规则) + " 在位置 " + str(自身.位置) + "未尝试过")
                        
                    if 自身.变长模式已试长度[规则][自身.位置] > 1:
                        再试长度 = 自身.变长模式已试长度[规则][自身.位置] - 1
                        print(str(自身.位置) + " 尝试：" + str(规则) + " 长度：" + str(再试长度))
                        匹配词 = 规则.匹配(自身.源码, 自身.位置, 自身.位置 + 再试长度)
                        if 匹配词:
                            # print("找到变长匹配词：" + 自身.源码[匹配词.起:匹配词.止])
                            自身.变长模式已试长度[规则][自身.位置] = 匹配词.止 - 匹配词.起
                        else:
                            print("未匹配变长：" + str(规则))
                    else:
                        print("跳过变长模式 " + str(规则))
                        continue
                else:
                    print("跳过！")
                    continue
            else:
                print(str(自身.位置) + " 尝试：" + str(规则))
                匹配词 = 规则.匹配(自身.源码, 自身.位置)
                # TODO: 待支持其他通配符或 {m,n} 等变长匹配
                if 匹配词:
                    if '\\' in 规则.正则.pattern:
                    #if '+' in 规则.正则.pattern or '*' in 规则.正则.pattern:
                        匹配长度 = 匹配词.止 - 匹配词.起
                        if 规则 not in 自身.变长模式已试长度:
                            自身.变长模式已试长度[规则] = {}
                        自身.变长模式已试长度[规则][自身.位置] = 匹配长度
                else:
                    print("未匹配：" + str(规则))
                
            自身.上个位置 = 自身.位置
            if 匹配词:
                print("找到匹配词：" + 自身.源码[匹配词.起:匹配词.止])
                自身.上个规则 = 规则
                行号 = 自身._行号
                自身._列号 = 自身._更新位置(匹配词)
                源码位置 = 字符位置(匹配词.起, 行号, 自身._列号)
                某词 = 词(
                    规则.词名, 自身.源码[匹配词.起:匹配词.止], 源码位置
                )
                return 某词
        else:
            print("完全无匹配")
            # 如果无匹配，定位在上个匹配的下一字符
            自身._列号 = 自身._按字符更新位置(自身.位置)
            raise 分词报错(None, 字符位置(
                自身.位置, 自身._行号, 自身._列号))

    # TODO：严重——应该按照状态记录，而非全局？
    # 比如：“整数”应该在4位置，但因为前部分词错误导致记录“‘整数’不可在4位置”
    def 标记不符语法词法规则(自身):
        print(f"标记不符语法词法规则: {自身.上个位置} -> {自身.上个规则}")
        #print(自身.上个规则)
        # 不记录固定模式？
        # if '\d' in 自身.上个规则.正则.pattern:
        if 自身.上个位置 in 自身.不符语法词法规则:
            自身.不符语法词法规则[自身.上个位置].add(自身.上个规则)
        else:
            自身.不符语法词法规则[自身.上个位置] = set([自身.上个规则])

        自身.回退()

        return 自身.位置

    def 记录状态(自身, 当前状态, 状态栈, 符号栈, 预读栈, 预读):
        自身.回退点[自身.位置] = (当前状态, 状态栈[:], 符号栈[:], 预读栈[:], 预读)
        print("记录状态: " + str(自身.回退点))


    # 返回：回退成功
    # 选取最近的的回退点
    def 回退(自身):
        print(f"回退前位置: {自身.位置}")
        print(f"当前回退点：{自身.回退点}")
        print(f"不符语法词法规则：{自身.不符语法词法规则}")
        已回退 = False
        最近位置 = -1
        for 回退位置 in 自身.回退点:
            if 回退位置 >= 自身.位置:
                continue
            # 若尚未经过变长模式匹配（肯定有），则继续尝试
            if 回退位置 not in 自身.不符语法词法规则:
                if 回退位置 > 最近位置:
                    最近位置 = 回退位置
                    print(f"不在不符语法词法规则：{最近位置}")
                continue
            for 规则 in 自身.不符语法词法规则[回退位置]:
                if 规则 not in 自身.变长模式已试长度:
                    if 回退位置 > 最近位置:
                        最近位置 = 回退位置
                        print(f"{规则} 不在变长模式已试长度：{最近位置}")
                elif 自身.变长模式已试长度[规则][回退位置] > 1:
                    if 回退位置 > 最近位置:
                        最近位置 = 回退位置
                        print(f"{规则} 变长匹配尚未彻底尝试于: {最近位置}")
        if 最近位置 > -1:
            自身.位置 = 最近位置
            已回退 = True
        if 已回退:
            自身.回退次数 += 1
            自身.不符语法词法规则 = 自身.清理后续问题规则(自身.位置)
        print(f"回退次数: {自身.回退次数}")
        if 自身.回退次数 >= 10000000: # 避免死循环
            已回退 = False
            自身.强制退出()
        return 已回退

    def 清理后续问题规则(自身, 当前位置):
        print(f"!!!!!!!!!!!!!!清理后续问题规则: {自身.不符语法词法规则}")
        新规则表 = {}
        for 位置 in 自身.不符语法词法规则:
            if 位置 <= 当前位置:
                新规则表[位置] = 自身.不符语法词法规则[位置].copy()
            else:
                print(f"清理后续问题规则：位置 {位置}，当前位置 {当前位置}")
        return 新规则表

    def 强制退出(自身):
        自身.退出 = True
        raise 分词报错(None, 字符位置(
                自身.位置, 自身._行号, 自身._列号))

    def __next__(自身):
        return 自身.next()