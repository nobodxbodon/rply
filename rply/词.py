class BaseBox(object):
    """
    A base class for polymorphic boxes that wrap parser results. Simply use
    this as a base class for anything you return in a production function of a
    parser. This is necessary because RPython unlike Python expects functions
    to always return objects of the same type.
    既然现在不支持 RPython，此数据结构应不需要。待清理。
    """
    _attrs_ = []


class 词(BaseBox):
    """
    Represents a syntactically relevant piece of text.
    :param name: A string describing the kind of text represented.
    :param value: The actual text represented.
    :param source_pos: A :class:`SourcePosition` object representing the
                       position of the first character in the source from which
                       this token was generated.
    """
    def __init__(自身, name, value, 源码位置=None):
        自身.name = name
        自身.value = value
        自身.source_pos = 源码位置

    def __repr__(自身):
        return "Token(%r, %r)" % (自身.name, 自身.value)

    def __eq__(自身, other):
        if not isinstance(other, 词):
            return NotImplemented
        return 自身.name == other.name and 自身.value == other.value

    def gettokentype(自身):
        """
        Returns the type or name of the token.
        """
        return 自身.name

    def getsourcepos(自身):
        """
        Returns a :class:`SourcePosition` instance, describing the position of
        this token's first character in the source.
        """
        return 自身.source_pos

    def getstr(自身):
        """
        Returns the string represented by this token.
        """
        return 自身.value


class 字符位置(object):
    """
    字符所在源码的位置。
    :param idx: The index of the character in the source.
    :param lineno: The number of the line in which the character occurs.
    :param colno: The number of the column in which the character occurs.
    The values passed to this object can be retrieved using the identically
    named attributes.
    """
    def __init__(自身, idx, lineno, colno):
        自身.idx = idx
        自身.lineno = lineno
        自身.colno = colno

    def __repr__(自身):
        return "SourcePosition(idx={0}, lineno={1}, colno={2})".format(
            自身.idx, 自身.lineno, 自身.colno
        )