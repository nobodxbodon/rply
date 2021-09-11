import operator
import pytest

from rply import LexerGenerator, ParserGenerator

from .功用 import BoxInt


class TestBoth(object):
    def test_arithmetic(self):
        lg = LexerGenerator()
        lg.add("NUMBER", r"\d+")
        lg.add("PLUS", r"\+")
        lg.add("TIMES", r"\*")

        pg = ParserGenerator(["NUMBER", "PLUS", "TIMES"], precedence=[
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

        assert parser.parse(lexer.lex("3*4+5")) == BoxInt(17)

    @pytest.mark.skip(reason="如按原始分词方法，无法解析")
    def test_按语法分词(self):
        lg = LexerGenerator()
        lg.add("关键词", r"5")
        lg.add("数", r"\d")

        pg = ParserGenerator(["数", "关键词"])

        @pg.production("main : 数 关键词")
        def main(p):
            return int(p[0].getstr())

        lexer = lg.build()
        parser = pg.build()

        assert parser.分析(lexer.分词('55')) == 5

    def test_无空格_单字(self):
        lg = LexerGenerator()
        lg.add("数", r"\d")

        pg = ParserGenerator(["数"])

        @pg.production("main : 数")
        def main(p):
            return int(p[0].getstr())

        lexer = lg.build()
        parser = pg.build()

        assert parser.无空格分析(lexer.lex('5')) == 5

    def test_无空格_多字(self):
        lg = LexerGenerator()
        lg.add("数", r"\d")
        lg.add("个", r"个")

        pg = ParserGenerator(["数", "个"])

        @pg.production("main : 数 个")
        def main(p):
            return int(p[0].getstr())

        lexer = lg.build()
        parser = pg.build()

        assert parser.无空格分析(lexer.lex('5个')) == 5

    def test_无空格_按语法分词(self):
        lg = LexerGenerator()
        lg.add("关键词", r"5")
        lg.add("数", r"\d")

        pg = ParserGenerator(["数", "关键词"])

        @pg.production("main : 数 关键词")
        def main(p):
            return int(p[0].getstr())

        lexer = lg.build()
        parser = pg.build()

        assert parser.无空格分析(lexer.分词('55')) == 5

    @pytest.mark.skip(reason="需逐个字尝试匹配，而非一味贪婪匹配")
    def test_无空格_需不贪婪匹配(self):
        lg = LexerGenerator()
        lg.add("关键词", r"5")
        lg.add("数", r"\d+")

        pg = ParserGenerator(["数", "五"])

        @pg.production("main : 数 关键词")
        def main(p):
            return int(p[0].getstr())

        lexer = lg.build()
        parser = pg.build()

        assert parser.无空格分析(lexer.分词('55')) == 5
