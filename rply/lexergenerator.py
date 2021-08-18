from rply import 分词器母机
from rply.分词器母机 import 词模式
from rply.分词器 import 分词器

class LexerGenerator(分词器母机):

    def __init__(自身):
        super().__init__()

    def add(自身, 词名, 模式, flags=0):
        super().添了(词名, 模式, 匹配参数=flags)

    def ignore(自身, 模式, flags=0):
        super().略过(模式, 匹配参数=flags)

    def build(自身):
        return super().产出()
