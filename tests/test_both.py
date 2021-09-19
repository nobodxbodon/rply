import operator
import pytest

from rply import LexerGenerator, ParserGenerator, 分词器母机, 语法分析器母机

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
        分词母机 = 分词器母机()
        分词母机.添了("数", r"\d")

        分析器母机 = 语法分析器母机(["数"])

        @分析器母机.语法规则("句 : 数")
        def 句(片段):
            return int(片段[0].getstr())

        分词器 = 分词母机.产出()
        分析器 = 分析器母机.产出()

        assert 分析器.按语法分词(分词器.lex('5')) == 5

    def test_无空格_多字(self):
        分词母机 = 分词器母机()
        分词母机.添了("数", r"\d")
        分词母机.添了("个", r"个")

        分析器母机 = 语法分析器母机(["数", "个"])

        @分析器母机.语法规则("句 : 数 个")
        def 句(片段):
            return int(片段[0].getstr())

        分词器 = 分词母机.产出()
        分析器 = 分析器母机.产出()

        assert 分析器.按语法分词(分词器.lex('5个')) == 5

    def test_无空格_按语法分词(self):
        分词母机 = 分词器母机()
        分词母机.添了("关键词", r"5")
        分词母机.添了("数", r"\d")

        分析器母机 = 语法分析器母机(["数", "关键词"])

        @分析器母机.语法规则("句 : 数 关键词")
        def 句(片段):
            return int(片段[0].getstr())

        分词器 = 分词母机.产出()
        分析器 = 分析器母机.产出()

        assert 分析器.按语法分词(分词器.分词('55')) == 5

    def test_逐个尝试不贪婪匹配(self):
        分词母机 = 分词器母机()
        分词母机.添了("关键词", r"5")
        分词母机.添了("数", r"\d+")

        分析器母机 = 语法分析器母机(["数", "关键词"])

        @分析器母机.语法规则("句 : 数 关键词")
        def 句(片段):
            return int(片段[0].getstr())

        分词器 = 分词母机.产出()
        分析器 = 分析器母机.产出()

        assert 分析器.按语法分词(分词器.分词('55')) == 5

    def test_读者表(self):
        分词母机 = 分词器母机()
        分词母机.添了('表', '表')
        分词母机.添了('标识符', r'[_a-zA-Z\u4e00-\u9fa5][_a-zA-Z0-9\u4e00-\u9fa5]*')

        分析器母机 = 语法分析器母机(['表', '标识符'])

        @分析器母机.语法规则("句 : 标识符 表")
        def 句(片段):
            return 片段[0].getstr()

        分词器 = 分词母机.产出()
        分析器 = 分析器母机.产出()

        assert 分析器.按语法分词(分词器.分词('读者表')) == '读者'

    def test_删除读者表(self):
        分词母机 = 分词器母机()
        分词母机.添了('删除', '删除')
        分词母机.添了('表', '表')
        分词母机.添了('标识符', r'[_a-zA-Z\u4e00-\u9fa5][_a-zA-Z0-9\u4e00-\u9fa5]*')

        分析器母机 = 语法分析器母机(['删除', '表', '标识符'])

        @分析器母机.语法规则("句 : 删除 标识符 表")
        def 句(片段):
            return 片段[1].getstr()

        分词器 = 分词母机.产出()
        分析器 = 分析器母机.产出()

        assert 分析器.按语法分词(分词器.分词('删除读者表')) == '读者'

    def test_创建钟表表(self):
        分词母机 = 分词器母机()
        分词母机.添了('创建', '创建')
        分词母机.添了('表', '表')
        分词母机.添了('标识符', r'[_a-zA-Z\u4e00-\u9fa5][_a-zA-Z0-9\u4e00-\u9fa5]*')

        分析器母机 = 语法分析器母机(['创建', '表', '标识符'])

        @分析器母机.语法规则("句 : 创建 标识符 表")
        def 句(片段):
            return 片段[1].getstr()

        分词器 = 分词母机.产出()
        分析器 = 分析器母机.产出()

        assert 分析器.按语法分词(分词器.分词('创建钟表表')) == '钟表'

    def test_出生年为整数(self):
        分词母机 = 分词器母机()
        分词母机.添了('为', '为')
        分词母机.添了('整数', '整数')
        分词母机.添了('标识符', r'[_a-zA-Z\u4e00-\u9fa5][_a-zA-Z0-9\u4e00-\u9fa5]*')

        分析器母机 = 语法分析器母机(['为', '整数', '标识符'])

        @分析器母机.语法规则("句 : 标识符 为 整数")
        def 句(片段):
            return 片段[0].getstr()

        分词器 = 分词母机.产出()
        分析器 = 分析器母机.产出()

        assert 分析器.按语法分词(分词器.分词('出生年为整数')) == '出生年'

    def test_昵称为空的文本(self):
        分词母机 = 分词器母机()
        分词母机.添了('为', '为')
        分词母机.添了('文本', '文本')
        分词母机.添了('空', '空')
        分词母机.添了('的', '的')
        分词母机.添了('标识符', r'[_a-zA-Z\u4e00-\u9fa5][_a-zA-Z0-9\u4e00-\u9fa5]*')

        分析器母机 = 语法分析器母机(['为', '文本', '标识符', '空', '的'])

        @分析器母机.语法规则("句 : 标识符 为 空 的 文本")
        def 句(片段):
            return 片段[0].getstr()

        分词器 = 分词母机.产出()
        分析器 = 分析器母机.产出()

        assert 分析器.按语法分词(分词器.分词('昵称为空的文本')) == '昵称'

    def test_昵称为不为空的文本(self):
        分词母机 = 分词器母机()
        分词母机.添了('为', '为')
        分词母机.添了('文本', '文本')
        分词母机.添了('不为空', '不为空')
        分词母机.添了('的', '的')
        分词母机.添了('标识符', r'[_a-zA-Z\u4e00-\u9fa5][_a-zA-Z0-9\u4e00-\u9fa5]*')

        分析器母机 = 语法分析器母机(['为', '文本', '标识符', '不为空', '的'])

        @分析器母机.语法规则("句 : 标识符 为 不为空 的 文本")
        def 句(片段):
            return 片段[0].getstr()

        分词器 = 分词母机.产出()
        分析器 = 分析器母机.产出()

        assert 分析器.按语法分词(分词器.分词('昵称为不为空的文本')) == '昵称'

    @pytest.mark.skip(reason="无限回退")
    def test_按出生年倒序排列(self):
        分词母机 = 分词器母机()
        分词母机.添了('按', '按')
        分词母机.添了('倒序', '倒序')
        分词母机.添了('排列', '排列')
        分词母机.添了('标识符', r'[_a-zA-Z\u4e00-\u9fa5][_a-zA-Z0-9\u4e00-\u9fa5]*')

        分析器母机 = 语法分析器母机(['按', '倒序', '排列', '标识符'])

        @分析器母机.语法规则("句 : 按 标识符 倒序 排列")
        def 句(片段):
            return 片段[1].getstr()

        分词器 = 分词母机.产出()
        分析器 = 分析器母机.产出()

        assert 分析器.按语法分词(分词器.分词('按出生年倒序排列')) == '出生年'
