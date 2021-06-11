import operator

from rply import 分词器母机, 语法分析器母机

from .功用 import BoxInt


class TestBoth(object):
    def test_arithmetic(self):
        lg = 分词器母机()
        lg.add("NUMBER", r"\d+")
        lg.add("PLUS", r"\+")
        lg.add("TIMES", r"\*")

        pg = 语法分析器母机(["NUMBER", "PLUS", "TIMES"], precedence=[
            ("left", ["PLUS"]),
            ("left", ["TIMES"]),
        ])

        @pg.production("main : expr")
        def main(p):
            return p[0]

        @pg.production("expr : expr PLUS expr")
        @pg.production("expr : expr TIMES expr")
        def expr_binop(p):
            return BoxInt({
                "+": operator.add,
                "*": operator.mul
            }[p[1].getstr()](p[0].getint(), p[2].getint()))

        @pg.production("expr : NUMBER")
        def expr_num(p):
            return BoxInt(int(p[0].getstr()))

        lexer = lg.build()
        parser = pg.build()

        assert parser.parse(lexer.lex("3*4+5"))
