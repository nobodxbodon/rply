# 验证不用 「」标示变量
from rply import 分词器母机, 语法分析器母机

分词母机 = 分词器母机()
分词母机.添了('除', '除')
分词母机.添了('乘', '乘')
分词母机.添了('以', '以')
分词母机.添了('标识符', r'[\u4e00-\u9fa5]+')

分析器母机 = 语法分析器母机(['除', '乘', '以', '标识符'])

@分析器母机.语法规则("表达式 : 除 标识符 以 标识符 | 乘 标识符 以 标识符")
def 表达式(片段):
    运算符 = '*' if 片段[0].getstr() == '乘' else '/'
    return f"{片段[1].getstr()} {运算符} {片段[3].getstr()}"

分词器 = 分词母机.产出()
分析器 = 分析器母机.产出()

print(分析器.按语法分词(分词器.分词('除觚冪以半徑平方')))
print(分析器.按语法分词(分词器.分词('乘移位數以二之對數上')))
print(分析器.按语法分词(分词器.分词('除以下金额以除夕人数')))
print(分析器.按语法分词(分词器.分词('除不以三开头的数以去除末尾零的数'), 38))
print(分析器.按语法分词(分词器.分词('除除夕余额以以上人数'))) # 有歧义
