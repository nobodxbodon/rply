from rply import 分词器母机, 语法分析器母机

分词母机 = 分词器母机()
分词母机.添了('标识符', r'[\u4e00-\u9fa5]+')

分析器母机 = 语法分析器母机(['标识符'])

@分析器母机.语法规则("句 : 标识符")
def 句(片段):
    return 片段[0].getstr()

分词器 = 分词母机.产出()
分析器 = 分析器母机.产出()

print(分析器.按语法分词(分词器.分词('读者')))