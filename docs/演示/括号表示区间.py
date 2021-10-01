from rply import ParserGenerator

### 分词器部分
from rply import LexerGenerator

分词器母机 = LexerGenerator()

分词器母机.add('数', r'\d+')
分词器母机.add('加', r'\+')
分词器母机.add('左括号', r'\(')
分词器母机.add('右括号', r'\)')
分词器母机.add('左中括号', r'\[')
分词器母机.add('逗号', r',')

分词器 = 分词器母机.build()

### 语法分析器部分

分析器母机 = ParserGenerator(
    # 所有词名
    ['数', '左括号', '右括号', '左中括号',
     '加', '逗号'
    ],
    precedence=[
        ('left', ['加'])
    ]
)

@分析器母机.production('表达式 : 数')
@分析器母机.production('表达式 : 区间')
def 数表达式(片段):
    # 匹配规则右部的片段列表
    if type(片段[0]) == str:
        return 片段[0]
    else:
        return int(片段[0].getstr())

@分析器母机.production('区间 : 左中括号 表达式 逗号 表达式 右括号')
@分析器母机.production('区间 : 左括号 表达式 逗号 表达式 右括号')
def 区间(片段):
    种类 = "左闭右开区间" if 片段[0].gettokentype()=='左中括号' else "闭区间"
    return f"{种类} {片段[1]}~{片段[3]}"

@分析器母机.production('表达式 : 左括号 表达式 右括号')
def 括号表达式(片段):
    return 片段[1]

@分析器母机.production('表达式 : 表达式 加 表达式')
def 二元运算表达式(片段):
    左 = 片段[0]
    右 = 片段[2]
    运算符 = 片段[1]
    if 运算符.gettokentype() == '加':
        return 左 + 右
    else:
        raise AssertionError('不应出现')

分析器 = 分析器母机.build()

print(分析器.parse(分词器.lex('[1,2)')))
print(分析器.parse(分词器.lex('(1+1)')))

print(分析器.parse(分词器.lex('[1,(1+1))')))
print(分析器.parse(分词器.lex('(1,(1+1))')))