from rply.报错 import 分词报错
from rply.词 import 字符位置, 词


class 分词器(object):
    def __init__(self, rules, ignore_rules):
        self.rules = rules
        self.ignore_rules = ignore_rules

    def 分词(self, s):
        return LexerStream(self, s)


class LexerStream(object):
    def __init__(self, lexer, s):
        self.lexer = lexer
        self.s = s
        self.idx = 0

        self._lineno = 1
        self._colno = 1

    def __iter__(self):
        return self

    def _update_pos(self, match):
        self.idx = match.end
        self._lineno += self.s.count("\n", match.start, match.end)
        last_nl = self.s.rfind("\n", 0, match.start)
        if last_nl < 0:
            return match.start + 1
        else:
            return match.start - last_nl

    def next(self):
        while True:
            if self.idx >= len(self.s):
                raise StopIteration
            for rule in self.lexer.ignore_rules:
                match = rule.matches(self.s, self.idx)
                if match:
                    self._update_pos(match)
                    break
            else:
                break

        for rule in self.lexer.rules:
            match = rule.matches(self.s, self.idx)
            if match:
                lineno = self._lineno
                self._colno = self._update_pos(match)
                source_pos = 字符位置(match.start, lineno, self._colno)
                token = 词(
                    rule.name, self.s[match.start:match.end], source_pos
                )
                return token
        else:
            raise 分词报错(None, 字符位置(
                self.idx, self._lineno, self._colno))

    def __next__(self):
        return self.next()
