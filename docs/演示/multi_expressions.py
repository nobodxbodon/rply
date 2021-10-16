from rply import LexerGenerator, ParserGenerator

lg = LexerGenerator()
lg.add('STATEMENT_END', r'\;')
lg.add('STRING', r'["][\w\s]+["]')
lg.ignore('\s+')

pg = ParserGenerator(["STRING", "STATEMENT_END"])

# just a demo, there are other ways
@pg.production("main : expr")
@pg.production("main : main expr")
def main(p):
    return p

@pg.production("expr : STRING STATEMENT_END")
def expr(p):
    return p[0].getstr()[1:-1]

lexer = lg.build()
parser = pg.build()

print(parser.parse(lexer.lex('"hi";"there";"buddy";')))