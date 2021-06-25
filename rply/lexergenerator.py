from rply import 分词器母机
from rply.分词器母机 import Rule
from rply.分词器 import 分词器

class LexerGenerator(分词器母机):

    def __init__(self):
        super().__init__()

    def add(self, name, pattern, flags=0):
        super().添了(name, pattern, flags=flags)

    def ignore(self, pattern, flags=0):
        super().略过(pattern, flags=flags)

    def build(self):
        return super().产出()
