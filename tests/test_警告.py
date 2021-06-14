from rply import 语法分析器母机
from rply.报错 import ParserGeneratorWarning

from .基本 import BaseTests


class TestWarnings(BaseTests):
    def test_shift_reduce(self):
        pg = 语法分析器母机([
            "NAME", "NUMBER", "EQUALS", "PLUS", "MINUS", "TIMES", "DIVIDE",
            "LPAREN", "RPAREN"
        ])

        @pg.语法规则("statement : NAME EQUALS expression")
        def statement_assign(p):
            pass

        @pg.语法规则("statement : expression")
        def statement_expression(p):
            pass

        @pg.语法规则("expression : expression PLUS expression")
        @pg.语法规则("expression : expression MINUS expression")
        @pg.语法规则("expression : expression TIMES expression")
        @pg.语法规则("expression : expression DIVIDE expression")
        def expression_binop(p):
            pass

        @pg.语法规则("expression : MINUS expression")
        def expression_uminus(p):
            pass

        @pg.语法规则("expression : LPAREN expression RPAREN")
        def expression_group(p):
            pass

        @pg.语法规则("expression : NUMBER")
        def expression_number(p):
            pass

        @pg.语法规则("expression : NAME")
        def expression_name(p):
            pass

        with self.assert_warns(
            ParserGeneratorWarning, "如下 20 种情形取下个词还是合而为一？"
        ):
            pg.产出()

    def test_reduce_reduce(self):
        pg = 语法分析器母机(["NAME", "EQUALS", "NUMBER"])

        @pg.语法规则("main : assign")
        def main(p):
            pass

        @pg.语法规则("assign : NAME EQUALS expression")
        @pg.语法规则("assign : NAME EQUALS NUMBER")
        def assign(p):
            pass

        @pg.语法规则("expression : NUMBER")
        def expression(p):
            pass

        with self.assert_warns(
            ParserGeneratorWarning, "1 种情形不确定如何合而为一"
        ):
            pg.产出()

    def test_unused_tokens(self):
        pg = 语法分析器母机(["VALUE", "OTHER"])

        @pg.语法规则("main : VALUE")
        def main(p):
            return p[0]

        with self.assert_warns(
            ParserGeneratorWarning, "词 'OTHER' 无用"
        ):
            pg.产出()

    def test_unused_production(self):
        pg = 语法分析器母机(["VALUE", "OTHER"])

        @pg.语法规则("main : VALUE")
        def main(p):
            return p[0]

        @pg.语法规则("unused : OTHER")
        def unused(p):
            pass

        with self.assert_warns(
            ParserGeneratorWarning, "规则 'unused' 无用"
        ):
            pg.产出()

    def test_报警(self):
        pg = 语法分析器母机(["VALUE"])

        @pg.语法规则("main : VALUE")
        def main(p):
            return p[0]

        @pg.语法规则("无用 : main")
        def unused(p):
            pass

        # 待修：下例仅将规则顺序倒换，就不报警
        with self.assert_warns(
            ParserGeneratorWarning, "规则 '无用' 无用"
        ):
            pg.产出()

    def test_不报警(self):
        pg = 语法分析器母机(["VALUE"])

        @pg.语法规则("有用 : main")
        def unused(p):
            pass

        @pg.语法规则("main : VALUE")
        def main(p):
            return p[0]

        with self.应无报错():
            pg.产出()
