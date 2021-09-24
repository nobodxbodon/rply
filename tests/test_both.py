import operator
import pytest

from rply import LexerGenerator, ParserGenerator
from rply import 分词器母机, 语法分析器母机

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

    @pytest.mark.skip(reason="如按原始分词方法，无法解析。此类用例汇集在 test_按语法分词.py")
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

    def test_读者表(self):
        分词母机 = 分词器母机()
        分词母机.添了('表', '表')
        分词母机.添了('标识符', r'[_a-zA-Z\u4e00-\u9fa5][_a-zA-Z0-9\u4e00-\u9fa5]*'
)

        分词母机.略过(r"\s+")
        分析器母机 = 语法分析器母机(['表', '标识符'])

        @分析器母机.语法规则("句 : 标识符 表")
        def 句(片段):
            return 片段[0].getstr()

        分词器 = 分词母机.产出()
        分析器 = 分析器母机.产出()

        assert 分析器.分析(分词器.分词('读者 表')) == '读者'