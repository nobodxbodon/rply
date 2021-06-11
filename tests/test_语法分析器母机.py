import uuid

import py

from rply import 语法分析器母机, Token
from rply.报错 import ParserGeneratorError

from .基本 import BaseTests


class TestParserGenerator(BaseTests):
    def test_production_syntax_error(self):
        pg = 语法分析器母机([])
        with py.test.raises(ParserGeneratorError):
            pg.production("main VALUE")

    def test_production_terminal_overlap(self):
        pg = 语法分析器母机(["VALUE"])

        @pg.production("VALUE :")
        def x(p):
            pass

        with py.test.raises(ParserGeneratorError):
            pg.build()

    def test_duplicate_precedence(self):
        pg = 语法分析器母机([], precedence=[
            ("left", ["term", "term"])
        ])

        with py.test.raises(ParserGeneratorError):
            pg.build()

    def test_invalid_associativity(self):
        pg = 语法分析器母机([], precedence=[
            ("to-the-left", ["term"]),
        ])

        with py.test.raises(ParserGeneratorError):
            pg.build()

    def test_nonexistent_precedence(self):
        pg = 语法分析器母机(["VALUE"])

        @pg.production("main : VALUE", precedence="abc")
        def main(p):
            pass

        with py.test.raises(ParserGeneratorError):
            pg.build()

    def test_error_symbol(self):
        pg = 语法分析器母机(["VALUE"])

        @pg.production("main : VALUE")
        def main(p):
            pass

        @pg.production("main : error")
        def main_error(p):
            pass

        pg.build()


class TestParserCaching(object):
    def test_simple_caching(self):
        # Generate a random cache_id so that every test run does both the cache
        # write and read paths.
        pg = 语法分析器母机(["VALUE"], cache_id=str(uuid.uuid4()))

        @pg.production("main : VALUE")
        def main(p):
            return p[0]

        pg.build()
        parser = pg.build()

        assert parser.parse(iter([
            Token("VALUE", "3")
        ])) == Token("VALUE", "3")
