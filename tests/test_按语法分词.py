import pytest

from rply import 分词器母机, 语法分析器母机


标识符模式 = r'[_a-zA-Z\u4e00-\u9fa5][_a-zA-Z0-9\u4e00-\u9fa5]*'
class Test按语法分词(object):

    def test_无空格_单字(self):
        分词母机 = 分词器母机()
        分词母机.添了("数", r"\d")

        分析器母机 = 语法分析器母机(["数"])

        @分析器母机.语法规则("句 : 数")
        def 句(片段):
            return int(片段[0].getstr())

        分词器 = 分词母机.产出()
        分析器 = 分析器母机.产出()

        assert 分析器.按语法分词(分词器.lex('5')) == 5

    def test_无空格_多字(self):
        分词母机 = 分词器母机()
        分词母机.添了("数", r"\d")
        分词母机.添了("个", r"个")

        分析器母机 = 语法分析器母机(["数", "个"])

        @分析器母机.语法规则("句 : 数 个")
        def 句(片段):
            return int(片段[0].getstr())

        分词器 = 分词母机.产出()
        分析器 = 分析器母机.产出()

        assert 分析器.按语法分词(分词器.lex('5个')) == 5

    def test_无空格_按语法分词(self):
        分词母机 = 分词器母机()
        分词母机.添了("关键词", r"5")
        分词母机.添了("数", r"\d")

        分析器母机 = 语法分析器母机(["数", "关键词"])

        @分析器母机.语法规则("句 : 数 关键词")
        def 句(片段):
            return int(片段[0].getstr())

        分词器 = 分词母机.产出()
        分析器 = 分析器母机.产出()

        assert 分析器.按语法分词(分词器.分词('55')) == 5

    def test_逐个尝试不贪婪匹配(self):
        分词母机 = 分词器母机()
        分词母机.添了("关键词", r"5")
        分词母机.添了("数", r"\d+")

        分析器母机 = 语法分析器母机(["数", "关键词"])

        @分析器母机.语法规则("句 : 数 关键词")
        def 句(片段):
            return int(片段[0].getstr())

        分词器 = 分词母机.产出()
        分析器 = 分析器母机.产出()

        assert 分析器.按语法分词(分词器.分词('55')) == 5

    def test_读者表(self):
        分词母机 = 分词器母机()
        分词母机.添了('表', '表')
        分词母机.添了('标识符', 标识符模式)

        分析器母机 = 语法分析器母机(['表', '标识符'])

        @分析器母机.语法规则("句 : 标识符 表")
        def 句(片段):
            return 片段[0].getstr()

        分词器 = 分词母机.产出()
        分析器 = 分析器母机.产出()

        assert 分析器.按语法分词(分词器.分词('读者表')) == '读者'

    def test_删除读者表(self):
        分词母机 = 分词器母机()
        分词母机.添了('删除', '删除')
        分词母机.添了('表', '表')
        分词母机.添了('标识符', 标识符模式)

        分析器母机 = 语法分析器母机(['删除', '表', '标识符'])

        @分析器母机.语法规则("句 : 删除 标识符 表")
        def 句(片段):
            return 片段[1].getstr()

        分词器 = 分词母机.产出()
        分析器 = 分析器母机.产出()

        assert 分析器.按语法分词(分词器.分词('删除读者表')) == '读者'

    def test_删读者表格(self):
        分词母机 = 分词器母机()
        分词母机.添了('删', '删')
        分词母机.添了('表', '表格')
        分词母机.添了('标识符', 标识符模式)

        分析器母机 = 语法分析器母机(['删', '表', '标识符'])

        @分析器母机.语法规则("句 : 删 标识符 表")
        def 句(片段):
            return 片段[1].getstr()

        分词器 = 分词母机.产出()
        分析器 = 分析器母机.产出()

        assert 分析器.按语法分词(分词器.分词('删读者表格'), 4) == '读者'

    def test_创建钟表表(self):
        分词母机 = 分词器母机()
        分词母机.添了('创建', '创建')
        分词母机.添了('表', '表')
        分词母机.添了('标识符', 标识符模式)

        分析器母机 = 语法分析器母机(['创建', '表', '标识符'])

        @分析器母机.语法规则("句 : 创建 标识符 表")
        def 句(片段):
            return 片段[1].getstr()

        分词器 = 分词母机.产出()
        分析器 = 分析器母机.产出()

        assert 分析器.按语法分词(分词器.分词('创建钟表表'), 2) == '钟表'
        assert 分析器.按语法分词(分词器.分词('创建表表表表表表')) == '表表表表表'
        assert 分析器.按语法分词(分词器.分词('创建钟表表表表表')) == '钟表表表表'
        assert 分析器.按语法分词(分词器.分词('创建钟表')) == '钟'

    def test_出生年为整数(self):
        分词母机 = 分词器母机()
        分词母机.添了('为', '为')
        分词母机.添了('整数', '整数')
        分词母机.添了('标识符', 标识符模式)

        分析器母机 = 语法分析器母机(['为', '整数', '标识符'])

        @分析器母机.语法规则("句 : 标识符 为 整数")
        def 句(片段):
            return 片段[0].getstr()

        分词器 = 分词母机.产出()
        分析器 = 分析器母机.产出()

        assert 分析器.按语法分词(分词器.分词('出生年为整数')) == '出生年'

    def test_昵称为空的文本(self):
        分词母机 = 分词器母机()
        分词母机.添了('为', '为')
        分词母机.添了('文本', '文本')
        分词母机.添了('空', '空')
        分词母机.添了('的', '的')
        分词母机.添了('标识符', 标识符模式)

        分析器母机 = 语法分析器母机(['为', '文本', '标识符', '空', '的'])

        @分析器母机.语法规则("句 : 标识符 为 空 的 文本")
        def 句(片段):
            return 片段[0].getstr()

        分词器 = 分词母机.产出()
        分析器 = 分析器母机.产出()

        assert 分析器.按语法分词(分词器.分词('昵称为空的文本'), 最多回退数=19) == '昵称'

    def test_昵称为不空文本(self):
        分词母机 = 分词器母机()
        分词母机.添了('为', '为')
        分词母机.添了('文本', '文本')
        分词母机.添了('不空', '不空')
        分词母机.添了('标识符', 标识符模式)

        分析器母机 = 语法分析器母机(['为', '文本', '标识符', '不空'])

        @分析器母机.语法规则("句 : 标识符 为 不空 文本")
        def 句(片段):
            return 片段[0].getstr()

        分词器 = 分词母机.产出()
        分析器 = 分析器母机.产出()

        assert 分析器.按语法分词(分词器.分词('昵称为不空文本'), 18) == '昵称'

    def test_昵称为不为空文本(self):
        分词母机 = 分词器母机()
        分词母机.添了('为', '为')
        分词母机.添了('文本', '文本')
        分词母机.添了('不为空', '不为空')
        分词母机.添了('标识符', 标识符模式)

        分析器母机 = 语法分析器母机(['为', '文本', '标识符', '不为空'])

        @分析器母机.语法规则("句 : 标识符 为 不为空 文本")
        def 句(片段):
            return 片段[0].getstr()

        分词器 = 分词母机.产出()
        分析器 = 分析器母机.产出()

        assert 分析器.按语法分词(分词器.分词('昵称为不为空文本'), 28) == '昵称'

    def test_昵称为不为空的文本(self):
        分词母机 = 分词器母机()
        分词母机.添了('为', '为')
        分词母机.添了('文本', '文本')
        分词母机.添了('不为空', '不为空')
        分词母机.添了('的', '的')
        分词母机.添了('标识符', 标识符模式)

        分析器母机 = 语法分析器母机(['为', '文本', '标识符', '不为空', '的'])

        @分析器母机.语法规则("句 : 标识符 为 不为空 的 文本")
        def 句(片段):
            return 片段[0].getstr()

        分词器 = 分词母机.产出()
        分析器 = 分析器母机.产出()

        assert 分析器.按语法分词(分词器.分词('昵称为不为空的文本'), 37) == '昵称'

    def test_按出生年排列(self):
        分词母机 = 分词器母机()
        分词母机.添了('按', '按')
        分词母机.添了('排列', '排列')
        分词母机.添了('标识符', 标识符模式)

        分析器母机 = 语法分析器母机(['按', '排列', '标识符'])

        @分析器母机.语法规则("句 : 按 标识符 排列")
        def 句(片段):
            return 片段[1].getstr()

        分词器 = 分词母机.产出()
        分析器 = 分析器母机.产出()

        assert 分析器.按语法分词(分词器.分词('按出生年排列')) == '出生年'

    def test_按出生年倒序排列(self):
        分词母机 = 分词器母机()
        分词母机.添了('按', '按')
        分词母机.添了('倒序', '倒序')
        分词母机.添了('排列', '排列')
        分词母机.添了('标识符', 标识符模式)

        分析器母机 = 语法分析器母机(['按', '倒序', '排列', '标识符'])

        @分析器母机.语法规则("句 : 按 标识符 倒序 排列")
        def 句(片段):
            return 片段[1].getstr()

        分词器 = 分词母机.产出()
        分析器 = 分析器母机.产出()

        assert 分析器.按语法分词(分词器.分词('按出生年倒序排列')) == '出生年'

    def test_多语法规则_删除某条件的读者记录(self):
        分词母机 = 分词器母机()
        分词母机.添了('删除', '删除')
        分词母机.添了('记录', '记录')
        分词母机.添了('小于', '小于')
        分词母机.添了('的', '的')
        分词母机.添了('数', r'\d+')
        分词母机.添了('标识符', 标识符模式)

        分析器母机 = 语法分析器母机(['删除', '记录', '的', '小于', '数', '标识符'])

        @分析器母机.语法规则("句 : 删除 条件 的 标识符 记录")
        def 句(片段):
            return 片段[3].getstr() + ":" + 片段[1]

        @分析器母机.语法规则("条件 : 标识符 小于 数")
        def 条件(片段):
            return 片段[0].getstr() + "<" + 片段[2].getstr()

        分词器 = 分词母机.产出()
        分析器 = 分析器母机.产出()

        assert 分析器.按语法分词(分词器.分词('删除出生年小于2000的读者记录'), 52) == '读者:出生年<2000'

    def test_创建单列表(self):
        分词母机 = 分词器母机()
        分词母机.添了('创建', '创建')
        分词母机.添了('表', '表')
        分词母机.添了('为', '为')
        分词母机.添了('整数', '整数')
        分词母机.添了('逗号', ',') # 暂且英文逗号，以避开标识符模式
        分词母机.添了('标识符', 标识符模式)

        分析器母机 = 语法分析器母机(['创建', '表', '为', '整数', '逗号', '标识符'])

        @分析器母机.语法规则("建表 : 表声明 逗号 列声明")
        def 建表(片段):
            return 片段[0] + ": " +片段[2]

        @分析器母机.语法规则("表声明 : 创建 标识符 表")
        def 表声明(片段):
            return 片段[1].getstr()

        @分析器母机.语法规则("列声明 : 标识符 为 整数")
        def 列声明(片段):
            return 片段[0].getstr()

        分词器 = 分词母机.产出()
        分析器 = 分析器母机.产出()

        assert 分析器.按语法分词(分词器.分词('创建读者表,出生年为整数'), 10) == '读者: 出生年'


    def test_创建多列表(self):
        分词母机 = 分词器母机()
        分词母机.添了('创建', '创建')
        分词母机.添了('表', '表')
        分词母机.添了('为', '为')
        分词母机.添了('整数', '整数')
        分词母机.添了('文本', '文本')
        分词母机.添了('逗号', ',') # 暂且英文逗号，以避开标识符模式
        分词母机.添了('标识符', 标识符模式)

        分析器母机 = 语法分析器母机(['创建', '表', '为', '整数', '文本', '逗号', '标识符'])

        @分析器母机.语法规则("建表 : 表声明")
        @分析器母机.语法规则("建表 : 建表 逗号 列声明")
        def 建表(片段):
            if len(片段) == 1:
                return f"{片段[0]}"
            if len(片段) == 3:
                return f"{片段[0]}-{片段[2]}"

        @分析器母机.语法规则("表声明 : 创建 标识符 表")
        def 表声明(片段):
            return 片段[1].getstr()

        @分析器母机.语法规则("列声明 : 标识符 为 列类型")
        def 列声明(片段):
            return 片段[0].getstr() + " " + 片段[2]

        @分析器母机.语法规则("列类型 : 整数 | 文本")
        def 列类型(片段):
            return 片段[0].getstr()

        分词器 = 分词母机.产出()
        分析器 = 分析器母机.产出()

        assert 分析器.按语法分词(分词器.分词('创建读者表,编号为整数,出生年为文本'), 18) == '读者-编号 整数-出生年 文本'

    def test_六规则创建多列表(self):
        分词母机 = 分词器母机()
        分词母机.添了('创建', '创建')
        分词母机.添了('表', '表')
        分词母机.添了('为', '为')
        分词母机.添了('整数', '整数')
        分词母机.添了('文本', '文本')
        分词母机.添了('逗号', ',')
        分词母机.添了('标识符', 标识符模式)

        分析器母机 = 语法分析器母机(['创建', '表', '为', '整数', '文本', '逗号', '标识符'])

        @分析器母机.语法规则("建表 : 表声明 逗号 各列声明") # https://zhuanlan.zhihu.com/p/412465957
        def 建表(片段):
            return f"{片段[0]} 各列为 {片段[2]}"

        @分析器母机.语法规则("各列声明 : 列声明")
        @分析器母机.语法规则("各列声明 : 各列声明 逗号 列声明")
        def 各列声明(片段):
            if len(片段) == 1:
                return f"{片段[0]}"
            if len(片段) == 3:
                return f"{片段[0]} {片段[2]}"

        @分析器母机.语法规则("表声明 : 创建 标识符 表")
        def 表声明(片段):
            return 片段[1].getstr()

        @分析器母机.语法规则("列声明 : 标识符 为 列类型")
        def 列声明(片段):
            return 片段[0].getstr() + " " + 片段[2]

        @分析器母机.语法规则("列类型 : 整数 | 文本")
        def 列类型(片段):
            return 片段[0].getstr()

        分词器 = 分词母机.产出(); 分析器 = 分析器母机.产出()

        assert 分析器.按语法分词(分词器.分词('创建读者表,编号为整数,出生年为文本'), 18) == '读者 各列为 编号 整数 出生年 文本'

    def test_两句(self):
        分词母机 = 分词器母机()
        分词母机.添了('删除', '删除')
        分词母机.添了('表', '表')
        分词母机.添了('句号', '。')
        分词母机.添了('标识符', 标识符模式)

        分析器母机 = 语法分析器母机(['删除', '表', '标识符', '句号'])

        @分析器母机.语法规则("代码 : 各句 句号")
        def 各句(片段):
            return 片段[0]

        @分析器母机.语法规则("各句 : 句")
        @分析器母机.语法规则("各句 : 各句 句号 句")
        def 各句(片段):
            if len(片段) == 1:
                return f"{片段[0]}"
            if len(片段) == 3:
                return f"{片段[0]} {片段[2]}"

        @分析器母机.语法规则("句 : 删除 标识符 表")
        def 句(片段):
            return 片段[1].getstr()

        分词器 = 分词母机.产出()
        分析器 = 分析器母机.产出()

        assert 分析器.按语法分词(分词器.分词('删除读者表。删除顾客表。')) == '读者 顾客'


    def test_两句创建删除(self):
        分词母机 = 分词器母机()
        分词母机.添了('删除', '删除')
        分词母机.添了('创建', '创建')
        分词母机.添了('不为空', '不为空')
        分词母机.添了('不重复', '不重复')
        分词母机.添了('为', '为')
        分词母机.添了('的', '的')
        分词母机.添了('整数', '整数')
        分词母机.添了('文本', '文本')
        分词母机.添了('表', '表')
        分词母机.添了('句号', '。')
        分词母机.添了('逗号', '，')
        分词母机.添了('标识符', 标识符模式)

        # TODO: 如果忘了加 '的', 会报错 KeyError: '的' 与 “for 规则 in 自身.各短语语法表[n]:”
        分析器母机 = 语法分析器母机(['删除', '创建', '为', '的', '整数', '不为空', '不重复', '文本', '表', '标识符', '句号', '逗号'])

        @分析器母机.语法规则("代码 : 各句 句号")
        def 代码(片段):
            return 片段[0]

        @分析器母机.语法规则("各句 : 句 | 各句 句号 句")
        def 各句(片段):
            return f"{片段[0]}" if len(片段) == 1 else f"{片段[0]}；{片段[2]}"

        @分析器母机.语法规则("句 : 删表 | 建表")
        def 句(片段):
            return 片段[0]

        @分析器母机.语法规则("删表 : 删除 标识符 表")
        def 删表声明(片段):
            return f"删除 {片段[1].getstr()}"

        @分析器母机.语法规则("建表 : 表声明 逗号 各列声明") # https://zhuanlan.zhihu.com/p/412465957
        def 建表(片段):
            return f"{片段[0]} 各列为 {片段[2]}"

        @分析器母机.语法规则("各列声明 : 列声明 | 各列声明 逗号 列声明")
        def 各列声明(片段):
            return f"{片段[0]}" if len(片段) == 1 else f"{片段[0]} {片段[2]}"

        @分析器母机.语法规则("表声明 : 创建 标识符 表")
        def 表声明(片段):
            return 片段[1].getstr()

        @分析器母机.语法规则("列声明 : 标识符 为 列类型 | 标识符 为 全部列特性 的 列类型")
        def 列声明(片段):
            return 片段[0].getstr() + ' ' + 片段[2] if len(片段) == 3 else 片段[0].getstr() + ' ' + 片段[2]+ ' ' + 片段[4]

        @分析器母机.语法规则("全部列特性 : 列特性 | 全部列特性 列特性")
        def 列特性(片段):
            return 片段[0] if len(片段) == 1 else 片段[0] + " " + 片段[1]

        @分析器母机.语法规则("列特性 : 不为空 | 不重复")
        def 列特性(片段):
            return 片段[0].getstr()

        @分析器母机.语法规则("列类型 : 整数 | 文本")
        def 列类型(片段):
            return 片段[0].getstr()

        分词器 = 分词母机.产出(); 分析器 = 分析器母机.产出()

        assert 分析器.按语法分词(分词器.分词('创建读者表，编号为整数，邮箱为不为空不重复的文本，出生年为整数。删除读者表。'), 89) == '读者 各列为 编号 整数 邮箱 不为空 不重复 文本 出生年 整数；删除 读者'


    def test_两句创建删除_生成SQL(self):
        分词母机 = 分词器母机()
        分词母机.添了('删除', '删除')
        分词母机.添了('创建', '创建')
        分词母机.添了('不为空', '不为空')
        分词母机.添了('不重复', '不重复')
        分词母机.添了('自动递增', '自动递增')
        分词母机.添了('主键', '主键')
        分词母机.添了('为', '为')
        分词母机.添了('的', '的')
        分词母机.添了('整数', '整数')
        分词母机.添了('文本', '文本')
        分词母机.添了('表', '表')
        分词母机.添了('句号', '。')
        分词母机.添了('逗号', '，')
        分词母机.添了('标识符', 标识符模式)

        分析器母机 = 语法分析器母机(['删除', '创建', '为', '的', '整数', '不为空', '不重复', '自动递增', '主键', '文本', '表', '标识符', '句号', '逗号'])

        @分析器母机.语法规则("代码 : 各句 句号")
        def 代码(片段):
            return f"{片段[0]};"

        @分析器母机.语法规则("各句 : 句 | 各句 句号 句")
        def 各句(片段):
            return f"{片段[0]}" if len(片段) == 1 else f"{片段[0]}; {片段[2]}"

        @分析器母机.语法规则("句 : 删表 | 建表")
        def 句(片段):
            return 片段[0]

        @分析器母机.语法规则("删表 : 删除 标识符 表")
        def 删表声明(片段):
            return f"DROP TABLE {片段[1].getstr()}"

        @分析器母机.语法规则("建表 : 表声明 逗号 各列声明")
        def 建表(片段):
            return f"{片段[0]} ( {片段[2]} )"

        @分析器母机.语法规则("各列声明 : 列声明 | 各列声明 逗号 列声明")
        def 各列声明(片段):
            return f"{片段[0]}" if len(片段) == 1 else f"{片段[0]}, {片段[2]}"

        @分析器母机.语法规则("表声明 : 创建 标识符 表")
        def 表声明(片段):
            return f"CREATE TABLE {片段[1].getstr()}"

        @分析器母机.语法规则("列声明 : 标识符 为 列类型 | 标识符 为 全部列特性 的 列类型 | 标识符 为 全部列特性 的 列类型 键属性")
        def 列声明(片段):
            词数 = len(片段)
            if 词数 == 3:
                return f"{片段[0].getstr()} {片段[2]}"
            elif 词数 == 5:
                return f"{片段[0].getstr()} {片段[4]} {片段[2]}"
            elif 词数 == 6:
                return f"{片段[0].getstr()} {片段[4]} {片段[5]} {片段[2]}"

        @分析器母机.语法规则("全部列特性 : 列特性 | 全部列特性 列特性")
        def 列特性(片段):
            return f"{片段[0]}" if len(片段) == 1 else f"{片段[0]} {片段[1]}"

        @分析器母机.语法规则("键属性 : 主键")
        def 键属性(片段):
            属性 = 片段[0].getstr()
            if 属性=="主键":
                return "PRIMARY KEY"

        @分析器母机.语法规则("列特性 : 不为空 | 不重复 | 自动递增")
        def 列特性(片段):
            特性 = 片段[0].getstr()
            if 特性=="不为空":
                return "NOT NULL"
            elif 特性=="不重复":
                return "UNIQUE"
            elif 特性=="自动递增":
                return "AUTOINCREMENT"

        @分析器母机.语法规则("列类型 : 整数 | 文本")
        def 列类型(片段):
            return "INTEGER" if 片段[0].getstr()=="整数" else "TEXT"

        分词器 = 分词母机.产出(); 分析器 = 分析器母机.产出()

        assert 分析器.按语法分词(分词器.分词('创建读者表，编号为自动递增的整数主键，邮箱为不重复不为空的文本，出生年为整数。删除读者表。'), 138) == 'CREATE TABLE 读者 ( 编号 INTEGER PRIMARY KEY AUTOINCREMENT, 邮箱 TEXT UNIQUE NOT NULL, 出生年 INTEGER ); DROP TABLE 读者;'
