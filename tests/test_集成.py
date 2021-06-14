import operator

from rply import 分词器母机, 语法分析器母机

from .功用 import BoxInt


class TestBoth(object):
    def test_arithmetic(self):
        lg = 分词器母机()
        lg.添了("NUMBER", r"\d+")
        lg.添了("PLUS", r"\+")
        lg.添了("TIMES", r"\*")

        pg = 语法分析器母机(["NUMBER", "PLUS", "TIMES"], 优先级=[
            ("left", ["PLUS"]),
            ("left", ["TIMES"]),
        ])

        @pg.语法规则("main : expr")
        def main(p):
            return p[0]

        @pg.语法规则("expr : expr PLUS expr")
        @pg.语法规则("expr : expr TIMES expr")
        def expr_binop(p):
            return BoxInt({
                "+": operator.add,
                "*": operator.mul
            }[p[1].getstr()](p[0].getint(), p[2].getint()))

        @pg.语法规则("expr : NUMBER")
        def expr_num(p):
            return BoxInt(int(p[0].getstr()))

        lexer = lg.产出()
        parser = pg.产出()

        assert parser.分析(lexer.分词("3*4+5"))
