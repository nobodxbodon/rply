from rply import ParserGenerator
from rply.报错 import ParserGeneratorWarning

from .基本 import BaseTests


class TestWarnings(BaseTests):
    def test_shift_reduce(self):
        pg = ParserGenerator([
            "NAME", "NUMBER", "EQUALS", "PLUS", "MINUS", "TIMES", "DIVIDE",
            "LPAREN", "RPAREN"
        ])

        @pg.production("statement : NAME EQUALS expression")
        def statement_assign(p):
            pass

        @pg.production("statement : expression")
        def statement_expression(p):
            pass

        @pg.production("expression : expression PLUS expression")
        @pg.production("expression : expression MINUS expression")
        @pg.production("expression : expression TIMES expression")
        @pg.production("expression : expression DIVIDE expression")
        def expression_binop(p):
            pass

        @pg.production("expression : MINUS expression")
        def expression_uminus(p):
            pass

        @pg.production("expression : LPAREN expression RPAREN")
        def expression_group(p):
            pass

        @pg.production("expression : NUMBER")
        def expression_number(p):
            pass

        @pg.production("expression : NAME")
        def expression_name(p):
            pass

        with self.assert_warns(
            ParserGeneratorWarning, "如下 20 种情形 shift 还是 reduce？"
        ):
            pg.build()

    def test_reduce_reduce(self):
        pg = ParserGenerator(["NAME", "EQUALS", "NUMBER"])

        @pg.production("main : assign")
        def main(p):
            pass

        @pg.production("assign : NAME EQUALS expression")
        @pg.production("assign : NAME EQUALS NUMBER")
        def assign(p):
            pass

        @pg.production("expression : NUMBER")
        def expression(p):
            pass

        with self.assert_warns(
            ParserGeneratorWarning, "1 reduce/reduce conflict"
        ):
            pg.build()

    def test_unused_tokens(self):
        pg = ParserGenerator(["VALUE", "OTHER"])

        @pg.production("main : VALUE")
        def main(p):
            return p[0]

        with self.assert_warns(
            ParserGeneratorWarning, "Token 'OTHER' is unused"
        ):
            pg.build()

    def test_unused_production(self):
        pg = ParserGenerator(["VALUE", "OTHER"])

        @pg.production("main : VALUE")
        def main(p):
            return p[0]

        @pg.production("unused : OTHER")
        def unused(p):
            pass

        with self.assert_warns(
            ParserGeneratorWarning, "Production 'unused' is not reachable"
        ):
            pg.build()

    def test_报警(self):
        pg = ParserGenerator(["VALUE"])

        @pg.production("main : VALUE")
        def main(p):
            return p[0]

        @pg.production("无用 : main")
        def unused(p):
            pass

        with self.assert_warns(
            ParserGeneratorWarning, "Production '无用' is not reachable"
        ):
            pg.build()
'''
    上例仅将规则顺序倒换，就不报警
    def test_不报警(self):
        pg = ParserGenerator(["VALUE"])

        @pg.production("有用 : main")
        def unused(p):
            pass

        @pg.production("main : VALUE")
        def main(p):
            return p[0]

        with self.assert_warns(
            ParserGeneratorWarning, "Production 'main' is not reachable"
        ):
            pg.build()
'''