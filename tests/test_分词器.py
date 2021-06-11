import re

from pytest import raises

from rply import 分词器母机, LexingError


class TestLexer(object):
    def test_simple(self):
        lg = 分词器母机()
        lg.add("NUMBER", r"\d+")
        lg.add("PLUS", r"\+")

        l = lg.build()

        stream = l.lex("2+3")
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
        lg.add("NUMBER", r"\d+")
        lg.add("PLUS", r"\+")
        lg.ignore(r"\s+")

        l = lg.build()

        stream = l.lex("2 + 3")
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
        lg.add("NUMBER", r"\d+")
        lg.add("PLUS", r"\+")
        lg.ignore(r"\s+")

        l = lg.build()

        stream = l.lex("2 + 3")
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

        stream = l.lex("2 +\n    37")
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
        lg.add("NEWLINE", r"\n")
        lg.add("SPACE", r" ")

        l = lg.build()

        stream = l.lex(" \n ")
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
        lg.add("ALL", r".*", re.DOTALL)

        l = lg.build()

        stream = l.lex("test\ndotall")
        t = stream.next()
        assert t.source_pos.lineno == 1
        assert t.source_pos.colno == 1
        assert t.getstr() == "test\ndotall"

        with raises(StopIteration):
            stream.next()

    def test_regex_flags_ignore(self):
        lg = 分词器母机()
        lg.add("ALL", r".*", re.DOTALL)
        lg.ignore(r".*", re.DOTALL)

        l = lg.build()

        stream = l.lex("test\ndotall")

        with raises(StopIteration):
            stream.next()

    def test_ignore_recursion(self):
        lg = 分词器母机()
        lg.ignore(r"\s")

        l = lg.build()

        assert list(l.lex(" " * 2000)) == []

    def test_error(self):
        lg = 分词器母机()
        lg.add("NUMBER", r"\d+")
        lg.add("PLUS", r"\+")

        l = lg.build()

        stream = l.lex('fail')
        with raises(LexingError) as excinfo:
            stream.next()

        assert 'SourcePosition(' in repr(excinfo.value)

    def test_error_line_number(self):
        lg = 分词器母机()
        lg.add("NEW_LINE", r"\n")
        l = lg.build()

        stream = l.lex("\nfail")
        stream.next()
        with raises(LexingError) as excinfo:
            stream.next()

        assert excinfo.value.source_pos.lineno == 2

    def test_error_column_number(self):
        lg = 分词器母机()
        lg.add("NUMBER", r"\d+")
        lg.add("PLUS", r"\+")
        l = lg.build()
        stream = l.lex("1+2+fail")
        stream.next()
        stream.next()
        stream.next()
        stream.next()
        with raises(LexingError) as excinfo:
            stream.next()

        assert excinfo.value.source_pos.colno == 4
