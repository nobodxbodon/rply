import re

from rply.分词器 import 分词器


class 词模式(object):
    _attrs_ = ['词名', '匹配参数', '_模式']

    def __init__(自身, 词名, 模式, 匹配参数=0):
        自身.词名 = 词名
        自身.正则 = re.compile(模式, flags=匹配参数)

    def 匹配(自身, 源码, 起点, 终点 = None):
        m = 自身.正则.match(源码, 起点, 终点) if 终点 else 自身.正则.match(源码, 起点)
        return 范围(*m.span(0)) if m is not None else None

    def __repr__(自身):
        return "词名：{0}, 模式={1}".format(
            自身.词名, 自身.正则
        )

class 范围(object):
    _attrs_ = ["起", "止"]

    def __init__(自身, 起, 止):
        自身.起 = 起
        自身.止 = 止


class 分词器母机(object):
    r"""
    A LexerGenerator represents a set of 规则 that match pieces of text that
    should either be turned into tokens or ignored by the lexer.
    规则 are added using the :meth:`add` and :meth:`ignore` methods:
    >>> from rply import 分词器母机
    >>> lg = 分词器母机()
    >>> lg.添了('NUMBER', r'\d+')
    >>> lg.添了('ADD', r'\+')
    >>> lg.略过(r'\s+')
    The 规则 are passed to :func:`re.compile`. If you need additional flags,
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

    def __init__(自身):
        自身.规则 = []
        自身.略过规则 = []

    def 添了(自身, 词名, 模式, 匹配参数=0):
        """
        Adds a rule with the given `词名` and `模式`. In case of ambiguity,
        the first rule added wins.
        """
        自身.规则.append(词模式(词名, 模式, 匹配参数=匹配参数))

    def 略过(自身, 模式, 匹配参数=0):
        """
        Adds a rule whose matched value will be ignored. Ignored 规则 will be
        matched before regular ones.
        """
        自身.略过规则.append(词模式("", 模式, 匹配参数=匹配参数))

    def 产出(自身):
        """
        Returns a lexer instance, which provides a `lex` method that must be
        called with a string and returns an iterator yielding
        :class:`~rply.Token` instances.
        """
        return 分词器(自身.规则, 自身.略过规则)