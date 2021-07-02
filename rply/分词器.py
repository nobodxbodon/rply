from rply.报错 import 分词报错
from rply.词 import 字符位置, 词


class 分词器(object):
    def __init__(self, rules, ignore_rules):
        self.rules = rules
        self.ignore_rules = ignore_rules

    def lex(self, s):
        return self.分词(s)

    def 分词(self, s):
        return LexerStream(self, s)


class LexerStream(object):
    def __init__(self, lexer, s):
        self.lexer = lexer
        self.s = s
        self.idx = 0

        self._行号 = 1
        self._列号 = 1

    def __iter__(self):
        return self

    def _更新位置(self, match):
        self.idx = match.end
        self._行号 += self.s.count("\n", match.start, match.end)
        最近换行 = self.s.rfind("\n", 0, match.start)
        if 最近换行 < 0:
            return match.start + 1
        else:
            return match.start - 最近换行

    def _按字符更新位置(self, 字符位置):
        self._行号 += 1 if self.s[字符位置] == "\n" else 0
        最近换行 = self.s.rfind("\n", 0, 字符位置)
        if 最近换行 < 0:
            return 字符位置 + 1
        else:
            return 1

    def next(self):
        while True:
            if self.idx >= len(self.s):
                raise StopIteration
            for rule in self.lexer.ignore_rules:
                match = rule.matches(self.s, self.idx)
                if match:
                    self._更新位置(match)
                    break
            else:
                break

        for rule in self.lexer.rules:
            match = rule.matches(self.s, self.idx)
            if match:
                lineno = self._行号
                self._列号 = self._更新位置(match)
                源码位置 = 字符位置(match.start, lineno, self._列号)
                token = 词(
                    rule.name, self.s[match.start:match.end], 源码位置
                )
                return token
        else:
            # 如果无匹配，定位在上个匹配的下一字符
            self._列号 = self._按字符更新位置(self.idx)
            raise 分词报错(None, 字符位置(
                self.idx, self._行号, self._列号))

    def __next__(self):
        return self.next()
