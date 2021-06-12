import re

from rply.分词器 import 分词器


class Rule(object):
    _attrs_ = ['name', 'flags', '_pattern']

    def __init__(self, name, pattern, flags=0):
        self.name = name
        self.re = re.compile(pattern, flags=flags)

    def matches(self, s, pos):
        m = self.re.match(s, pos)
        return Match(*m.span(0)) if m is not None else None


class Match(object):
    _attrs_ = ["start", "end"]

    def __init__(self, start, end):
        self.start = start
        self.end = end


class 分词器母机(object):
    r"""
    A LexerGenerator represents a set of rules that match pieces of text that
    should either be turned into tokens or ignored by the lexer.

    Rules are added using the :meth:`add` and :meth:`ignore` methods:

    >>> from rply import 分词器母机
    >>> lg = 分词器母机()
    >>> lg.添了('NUMBER', r'\d+')
    >>> lg.添了('ADD', r'\+')
    >>> lg.略过(r'\s+')

    The rules are passed to :func:`re.compile`. If you need additional flags,
    e.g. :const:`re.DOTALL`, you can pass them to :meth:`add` and
    :meth:`ignore` as an additional optional parameter:

    >>> import re
    >>> lg.添了('ALL', r'.*', flags=re.DOTALL)

    You can then build a lexer with which you can lex a string to produce an
    iterator yielding tokens:

    >>> lexer = lg.产出()
    >>> iterator = lexer.分词('1 + 1')
    >>> iterator.next()
    Token('NUMBER', '1')
    >>> iterator.next()
    Token('ADD', '+')
    >>> iterator.next()
    Token('NUMBER', '1')
    >>> iterator.next()
    Traceback (most recent call last):
    ...
    StopIteration
    """

    def __init__(self):
        self.rules = []
        self.ignore_rules = []

    def 添了(self, name, pattern, flags=0):
        """
        Adds a rule with the given `name` and `pattern`. In case of ambiguity,
        the first rule added wins.
        """
        self.rules.append(Rule(name, pattern, flags=flags))

    def 略过(self, pattern, flags=0):
        """
        Adds a rule whose matched value will be ignored. Ignored rules will be
        matched before regular ones.
        """
        self.ignore_rules.append(Rule("", pattern, flags=flags))

    def 产出(self):
        """
        Returns a lexer instance, which provides a `lex` method that must be
        called with a string and returns an iterator yielding
        :class:`~rply.Token` instances.
        """
        return 分词器(self.rules, self.ignore_rules)
