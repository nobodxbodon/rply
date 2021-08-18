
from rply import 语法分析器母机

class ParserGenerator(语法分析器母机):

    def __init__(自身, 词表, precedence=[], cache_id=None):
        super().__init__(词表, precedence, cache_id)

    def production(自身, 描述, precedence=None):
        return super().语法规则(描述, precedence)

    def build(自身):
        return super().产出()

    def error(自身, func):
        return super().报错(func)