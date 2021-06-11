from rply.词 import 字符位置, 词


class TestTokens(object):
    def test_source_pos(self):
        t = 词("VALUE", "3", 字符位置(5, 2, 1))
        assert t.getsourcepos().lineno == 2

    def test_eq(self):
        t = 词("VALUE", "3", 字符位置(-1, -1, -1))
        assert not (t == 3)
        assert t != 3

    def test_repr(self):
        t = 词("VALUE", "3")
        assert repr(t) == "Token('VALUE', '3')"


class TestSourcePosition(object):
    def test_source_pos(self):
        sp = 字符位置(1, 2, 3)
        assert sp.idx == 1
        assert sp.lineno == 2
        assert sp.colno == 3

    def test_repr(self):
        t = 字符位置(1, 2, 3)
        assert repr(t) == "SourcePosition(idx=1, lineno=2, colno=3)"
