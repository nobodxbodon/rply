class ParserGeneratorError(Exception):
    pass


class 分词报错(Exception):
    """
    Raised by a Lexer, if no rule matches.
    """
    def __init__(自身, 信息, 源码位置):
        自身.信息 = 信息
        自身.source_pos = 源码位置

    def getsourcepos(自身):
        """
        Returns the position in the source, at which this error occurred.
        """
        return 自身.source_pos

    def __repr__(自身):
        return 'LexingError(%r, %r)' % (自身.信息, 自身.source_pos)


class 语法分析报错(Exception):
    """
    Raised by a Parser, if no production rule can be applied.
    """
    def __init__(自身, 信息, 源码位置):
        自身.信息 = 信息
        自身.source_pos = 源码位置

    def getsourcepos(自身):
        """
        Returns the position in the source, at which this error occurred.
        """
        return 自身.source_pos

    def __repr__(自身):
        return 'ParsingError(%r, %r)' % (自身.信息, 自身.source_pos)


class 按语法分词报错(Exception):
    """
    无法按语法规则进行分词时报错。给出最长搜索路径：各位置与对应词法规则名。
    """
    def __init__(自身, 最长路径):
        自身.最长路径 = 最长路径

    def __repr__(自身):
        return '此处不符语法规则：%r，' % (自身.最长路径)

class ParserGeneratorWarning(Warning):
    pass