
from rply import 语法分析器母机

class ParserGenerator(语法分析器母机):

    def __init__(self, 词表, precedence=[], cache_id=None):
        super().__init__(词表, precedence, cache_id)

    def production(self, 描述, precedence=None):
        return super().语法规则(描述, precedence)

    def build(self):
        return super().产出()

    def error(self, func):
        return super().报错(func)