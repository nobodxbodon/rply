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

        assert parser.按语法分词(lexer.lex('5')) == 5

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

        assert parser.按语法分词(lexer.lex('5个')) == 5

    #@pytest.mark.skip(reason="")
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

        assert parser.按语法分词(lexer.分词('55')) == 5

    #@pytest.mark.skip(reason="")
    def test_逐个尝试不贪婪匹配(self):
        lg = LexerGenerator()
        lg.add("关键词", r"5")
        lg.add("数", r"\d+")

        pg = ParserGenerator(["数", "关键词"])

        @pg.production("main : 数 关键词")
        def main(p):
            return int(p[0].getstr())

        lexer = lg.build()
        parser = pg.build()

        assert parser.按语法分词(lexer.分词('55')) == 5

    #@pytest.mark.skip(reason="")
    def test_读者表(self):
        lg = LexerGenerator()
        lg.添了('表', '表')
        lg.添了('标识符', r'[_a-zA-Z\u4e00-\u9fa5][_a-zA-Z0-9\u4e00-\u9fa5]*')

        pg = ParserGenerator(['表', '标识符'])

        @pg.production("main : 标识符 表")
        def main(p):
            return p[0].getstr()

        lexer = lg.build()
        parser = pg.build()

        assert parser.按语法分词(lexer.分词('读者表')) == '读者'

    #@pytest.mark.skip(reason="")
    def test_删除读者表(self):
        lg = LexerGenerator()
        lg.添了('删除', '删除')
        lg.添了('表', '表')
        lg.添了('标识符', r'[_a-zA-Z\u4e00-\u9fa5][_a-zA-Z0-9\u4e00-\u9fa5]*')

        pg = ParserGenerator(['删除', '表', '标识符'])

        @pg.production("main : 删除 标识符 表")
        def main(p):
            return p[1].getstr()

        lexer = lg.build()
        parser = pg.build()

        assert parser.按语法分词(lexer.分词('删除读者表')) == '读者'

    #@pytest.mark.skip(reason="")
    def test_出生年为整数(self):
        lg = LexerGenerator()
        lg.添了('为', '为')
        lg.添了('整数', '整数')
        lg.添了('标识符', r'[_a-zA-Z\u4e00-\u9fa5][_a-zA-Z0-9\u4e00-\u9fa5]*')

        pg = ParserGenerator(['为', '整数', '标识符'])

        @pg.production("main : 标识符 为 整数")
        def main(p):
            return p[0].getstr()

        lexer = lg.build()
        parser = pg.build()

        assert parser.按语法分词(lexer.分词('出生年为整数')) == '出生年'

    def test_昵称为空的文本(self):
        lg = LexerGenerator()
        lg.添了('为', '为')
        lg.添了('文本', '文本')
        lg.添了('空', '空')
        lg.添了('的', '的')
        lg.添了('标识符', r'[_a-zA-Z\u4e00-\u9fa5][_a-zA-Z0-9\u4e00-\u9fa5]*')

        pg = ParserGenerator(['为', '文本', '标识符', '空', '的'])

        @pg.production("main : 标识符 为 空 的 文本")
        def main(p):
            return p[0].getstr()

        lexer = lg.build()
        parser = pg.build()

        assert parser.按语法分词(lexer.分词('昵称为空的文本')) == '昵称'
