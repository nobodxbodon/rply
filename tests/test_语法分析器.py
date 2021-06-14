import operator

import py

from rply import 语法分析器母机, 语法分析报错, 词
from rply.报错 import ParserGeneratorWarning
from rply.词 import 字符位置

from .基本 import BaseTests
from .功用 import BoxInt, ParserState, RecordingLexer


class TestParser(BaseTests):
    def test_simple(self):
        pg = 语法分析器母机(["VALUE"])

        @pg.语法规则("main : VALUE")
        def main(p):
            return p[0]

        parser = pg.产出()

        token = parser.分析(iter([词("VALUE", "abc")]))
        assert token == 词("VALUE", "abc")

    def test_arithmetic(self):
        pg = 语法分析器母机(["NUMBER", "PLUS"])

        @pg.语法规则("main : expr")
        def main(p):
            return p[0]

        @pg.语法规则("expr : expr PLUS expr")
        def expr_op(p):
            return BoxInt(p[0].getint() + p[2].getint())

        @pg.语法规则("expr : NUMBER")
        def expr_num(p):
            return BoxInt(int(p[0].getstr()))

        with self.assert_warns(
            ParserGeneratorWarning, "如下 1 种情形取下个词还是合而为一？"
        ):
            parser = pg.产出()

        assert parser.分析(iter([
            词("NUMBER", "1"),
            词("PLUS", "+"),
            词("NUMBER", "4")
        ])) == BoxInt(5)

    def test_null_production(self):
        pg = 语法分析器母机(["VALUE", "SPACE"])

        @pg.语法规则("main : values")
        def main(p):
            return p[0]

        @pg.语法规则("values : none")
        def values_empty(p):
            return []

        @pg.语法规则("values : VALUE")
        def values_value(p):
            return [p[0].getstr()]

        @pg.语法规则("values : values SPACE VALUE")
        def values_values(p):
            return p[0] + [p[2].getstr()]

        @pg.语法规则("none :")
        def none(p):
            return None

        parser = pg.产出()
        assert parser.分析(iter([
            词("VALUE", "abc"),
            词("SPACE", " "),
            词("VALUE", "def"),
            词("SPACE", " "),
            词("VALUE", "ghi"),
        ])) == ["abc", "def", "ghi"]

        assert parser.分析(iter([])) == []

    def test_precedence(self):
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

        parser = pg.产出()

        assert parser.分析(iter([
            词("NUMBER", "3"),
            词("TIMES", "*"),
            词("NUMBER", "4"),
            词("PLUS", "+"),
            词("NUMBER", "5")
        ])) == BoxInt(17)

    def test_per_rule_precedence(self):
        pg = 语法分析器母机(["NUMBER", "MINUS"], 优先级=[
            ("right", ["UMINUS"]),
        ])

        @pg.语法规则("main : expr")
        def main_expr(p):
            return p[0]

        @pg.语法规则("expr : expr MINUS expr")
        def expr_minus(p):
            return BoxInt(p[0].getint() - p[2].getint())

        @pg.语法规则("expr : MINUS expr", 优先级="UMINUS")
        def expr_uminus(p):
            return BoxInt(-p[1].getint())

        @pg.语法规则("expr : NUMBER")
        def expr_number(p):
            return BoxInt(int(p[0].getstr()))

        with self.assert_warns(
            ParserGeneratorWarning, "如下 1 种情形取下个词还是合而为一？"
        ):
            parser = pg.产出()

        assert parser.分析(iter([
            词("MINUS", "-"),
            词("NUMBER", "4"),
            词("MINUS", "-"),
            词("NUMBER", "5"),
        ])) == BoxInt(-9)

    def test_parse_error(self):
        pg = 语法分析器母机(["VALUE"])

        @pg.语法规则("main : VALUE")
        def main(p):
            return p[0]

        parser = pg.产出()

        with py.test.raises(语法分析报错) as exc_info:
            parser.分析(iter([
                词("VALUE", "hello"),
                词("VALUE", "world", 字符位置(5, 10, 2)),
            ]))

        assert exc_info.value.getsourcepos().lineno == 10
        assert 'SourcePosition' in repr(exc_info.value)

    def test_parse_error_handler(self):
        pg = 语法分析器母机(["VALUE"])

        @pg.语法规则("main : VALUE")
        def main(p):
            return p[0]

        @pg.报错
        def error_handler(token):
            raise ValueError(token)

        parser = pg.产出()

        token = 词("VALUE", "world")

        with py.test.raises(ValueError) as exc_info:
            parser.分析(iter([
                词("VALUE", "hello"),
                token
            ]))

        assert exc_info.value.args[0] is token

    def test_空行(self):
        pg = 语法分析器母机(["空行"])
        记录 = []

        @pg.语法规则("main : 空行")
        def main(p):
            记录.append("一行")
            return p[0]

        @pg.报错
        def error_handler(词):
            if 词.getstr() == '\n':
                return

        parser = pg.产出()

        parser.分析(iter([
            词("空行", "\n"),
            词("空行", "\n")
        ]))

        assert 记录 == [
            "一行",
        ]

    def test_state(self):
        pg = 语法分析器母机(["NUMBER", "PLUS"], 优先级=[
            ("left", ["PLUS"]),
        ])

        @pg.语法规则("main : expression")
        def main(state, p):
            state.count += 1
            return p[0]

        @pg.语法规则("expression : expression PLUS expression")
        def expression_plus(state, p):
            state.count += 1
            return BoxInt(p[0].getint() + p[2].getint())

        @pg.语法规则("expression : NUMBER")
        def expression_number(state, p):
            state.count += 1
            return BoxInt(int(p[0].getstr()))

        parser = pg.产出()

        state = ParserState()
        assert parser.分析(iter([
            词("NUMBER", "10"),
            词("PLUS", "+"),
            词("NUMBER", "12"),
            词("PLUS", "+"),
            词("NUMBER", "-2"),
        ]), state=state) == BoxInt(20)
        assert state.count == 6

    def test_error_handler_state(self):
        pg = 语法分析器母机([])

        @pg.语法规则("main :")
        def main(state, p):
            pass

        @pg.报错
        def error(state, token):
            raise ValueError(state, token)

        parser = pg.产出()

        state = ParserState()
        token = 词("VALUE", "")
        with py.test.raises(ValueError) as exc_info:
            parser.分析(iter([token]), state=state)

        assert exc_info.value.args[0] is state
        assert exc_info.value.args[1] is token

    def test_default_reductions(self):
        pg = 语法分析器母机(
            ["INTEGER_START", "INTEGER_VALUE", "COMPARE"],
            优先级=[
                ("nonassoc", ["COMPARE"])
            ]
        )
        record = []

        @pg.语法规则("main : expr")
        def main(p):
            record.append("main")
            return p[0]

        @pg.语法规则("expr : expr COMPARE expr")
        def expr_compare(p):
            record.append("expr:compare")
            return BoxInt(p[0].getint() - p[2].getint())

        @pg.语法规则("expr : INTEGER_START INTEGER_VALUE")
        def expr_int(p):
            record.append("expr:int")
            return BoxInt(int(p[1].getstr()))

        parser = pg.产出()

        assert parser.分析(RecordingLexer(record, [
            词("INTEGER_START", ""),
            词("INTEGER_VALUE", "10"),
            词("COMPARE", "-"),
            词("INTEGER_START", ""),
            词("INTEGER_VALUE", "5")
        ])) == BoxInt(5)

        assert record == [
            "token:INTEGER_START",
            "token:INTEGER_VALUE",
            "expr:int",
            "token:COMPARE",
            "token:INTEGER_START",
            "token:INTEGER_VALUE",
            "expr:int",
            "expr:compare",
            "token:None",
            "main",
        ]
