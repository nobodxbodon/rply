import re

import pytest
from pytest import raises

from rply import 分词器母机, 分词报错


class TestLexer(object):
    def test_simple(self):
        lg = 分词器母机()
        lg.添了("NUMBER", r"\d+")
        lg.添了("PLUS", r"\+")

        l = lg.产出()

        stream = l.分词("2+3")
        t = stream.next()
        assert t.name == "NUMBER"
        assert t.value == "2"
        t = stream.next()
        assert t.name == "PLUS"
        assert t.value == "+"
        t = stream.next()
        assert t.name == "NUMBER"
        assert t.value == "3"
        assert t.source_pos.idx == 2

        with raises(StopIteration):
            stream.next()

    def test_ignore(self):
        lg = 分词器母机()
        lg.添了("NUMBER", r"\d+")
        lg.添了("PLUS", r"\+")
        lg.略过(r"\s+")

        l = lg.产出()

        stream = l.分词("2 + 3")
        t = stream.next()
        assert t.name == "NUMBER"
        assert t.value == "2"
        t = stream.next()
        assert t.name == "PLUS"
        assert t.value == "+"
        t = stream.next()
        assert t.name == "NUMBER"
        assert t.value == "3"
        assert t.source_pos.idx == 4

        with raises(StopIteration):
            stream.next()

    def test_position(self):
        lg = 分词器母机()
        lg.添了("NUMBER", r"\d+")
        lg.添了("PLUS", r"\+")
        lg.略过(r"\s+")

        l = lg.产出()

        stream = l.分词("2 + 3")
        t = stream.next()
        assert t.source_pos.lineno == 1
        assert t.source_pos.colno == 1
        t = stream.next()
        assert t.source_pos.lineno == 1
        assert t.source_pos.colno == 3
        t = stream.next()
        assert t.source_pos.lineno == 1
        assert t.source_pos.colno == 5
        with raises(StopIteration):
            stream.next()

        stream = l.分词("2 +\n    37")
        t = stream.next()
        assert t.source_pos.lineno == 1
        assert t.source_pos.colno == 1
        t = stream.next()
        assert t.source_pos.lineno == 1
        assert t.source_pos.colno == 3
        t = stream.next()
        assert t.source_pos.lineno == 2
        assert t.source_pos.colno == 5
        with raises(StopIteration):
            stream.next()

    def test_newline_position(self):
        lg = 分词器母机()
        lg.添了("NEWLINE", r"\n")
        lg.添了("SPACE", r" ")

        l = lg.产出()

        stream = l.分词(" \n ")
        t = stream.next()
        assert t.source_pos.lineno == 1
        assert t.source_pos.colno == 1
        t = stream.next()
        assert t.source_pos.lineno == 1
        assert t.source_pos.colno == 2
        t = stream.next()
        assert t.source_pos.lineno == 2
        assert t.source_pos.colno == 1

    def test_regex_flags(self):
        lg = 分词器母机()
        lg.添了("ALL", r".*", re.DOTALL)

        l = lg.产出()

        stream = l.分词("test\ndotall")
        t = stream.next()
        assert t.source_pos.lineno == 1
        assert t.source_pos.colno == 1
        assert t.getstr() == "test\ndotall"

        with raises(StopIteration):
            stream.next()

    def test_regex_flags_ignore(self):
        lg = 分词器母机()
        lg.添了("ALL", r".*", re.DOTALL)
        lg.略过(r".*", re.DOTALL)

        l = lg.产出()

        stream = l.分词("test\ndotall")

        with raises(StopIteration):
            stream.next()

    def test_ignore_recursion(self):
        lg = 分词器母机()
        lg.略过(r"\s")

        l = lg.产出()

        assert list(l.分词(" " * 2000)) == []

    def test_error(self):
        lg = 分词器母机()
        lg.添了("NUMBER", r"\d+")
        lg.添了("PLUS", r"\+")

        l = lg.产出()

        stream = l.分词('fail')
        with raises(分词报错) as excinfo:
            stream.next()

        assert 'SourcePosition(' in repr(excinfo.value)
        assert excinfo.value.source_pos.colno == 1

    def test_error_line_number(self):
        lg = 分词器母机()
        lg.添了("NEW_LINE", r"\n")
        l = lg.产出()

        stream = l.分词("\nfail")
        stream.next()
        with raises(分词报错) as excinfo:
            stream.next()

        assert excinfo.value.source_pos.lineno == 2
        assert excinfo.value.source_pos.colno == 1

    def test_error_column_number(self):
        lg = 分词器母机()
        lg.添了("NUMBER", r"\d+")
        lg.添了("PLUS", r"\+")
        l = lg.产出()
        stream = l.分词("1+2+fail")
        stream.next()
        stream.next()
        stream.next()
        stream.next()
        with raises(分词报错) as excinfo:
            stream.next()

        assert excinfo.value.source_pos.colno == 5

    def test_error_换行列号(self):
        lg = 分词器母机()
        lg.添了("换行", r"\n")
        lg.添了("数", r"\d+")
        l = lg.产出()
        stream = l.分词("12\nfail")
        stream.next()
        stream.next()
        with raises(分词报错) as excinfo:
            stream.next()

        assert excinfo.value.source_pos.lineno == 2
        assert excinfo.value.source_pos.colno == 1