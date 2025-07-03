import functools
import z3

from rply import 分词器母机, 语法分析器母机

标识符模式 = r'[_a-zA-Z\u4e00-\u9fa5][_a-zA-Z0-9\u4e00-\u9fa5]*'

class Test辩证(object):

    def 或者(self, x, y):
        return x == True or y == True

    def test_两句(self):
        s = z3.Solver()
        各值 = {}

        分词母机 = 分词器母机()
        分词母机.添了('有问题', '有问题')
        分词母机.添了('或者', '或')
        分词母机.添了('句号', '。')
        分词母机.添了('标识符', 标识符模式)

        分析器母机 = 语法分析器母机(['有问题', '或者', '标识符', '句号'])

        @分析器母机.语法规则("代码 : 各句 句号")
        def 代码(片段):
            # 2. 如甲有问题，则乙有问题
            s.add(z3.If(
                    各值['甲'] == True,
                    各值['乙'] == True,
                    True,
                ))

            if s.check() != z3.sat:
                raise ValueError("有误")
            
            结果 = s.model()
            for 某项 in 结果:
                if 结果[某项]:
                    return str(某项) + '有问题'

        @分析器母机.语法规则("各句 : 结构句")
        @分析器母机.语法规则("各句 : 各句 句号 结构句")
        def 各句(片段):
            if len(片段) == 1:
                return f"{片段[0]}"
            if len(片段) == 3:
                return f"{片段[0]} {片段[2]}"

        @分析器母机.语法规则("结构句 : 句 或者 句")
        def 或者(片段):
            新布尔量 = z3.Bools(
                [片段[0], 片段[2]]
            )
            各值[片段[0]] = 新布尔量[0]
            各值[片段[2]] = 新布尔量[1]

            # 1. 甲有问题或乙有问题
            s.add(functools.reduce(self.或者, list(各值.values()))) # 新布尔量))
            
        @分析器母机.语法规则("句 : 标识符 有问题")
        def 句(片段):
            return 片段[0].getstr()

        分词器 = 分词母机.产出()
        分析器 = 分析器母机.产出()

        assert 分析器.按语法分词(分词器.分词('甲有问题或乙有问题。'), 50) == '乙有问题'
