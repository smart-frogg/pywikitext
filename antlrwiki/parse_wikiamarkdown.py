import sys
from antlr4 import *
from gen.wiki_markupLexer import wiki_markupLexer
from gen.wiki_markupParser import wiki_markupParser


def main(argv):
    input = FileStream(argv[1], encoding='utf-8')
    lexer = wiki_markupLexer(input)
    stream = CommonTokenStream(lexer)
    parser = wiki_markupParser(stream)
    tree = parser.wiki_article()
    '''
    for c in tree.children:
        print(type(c))
        if str(type(c)) != "<class 'antlr4.tree.Tree.TerminalNodeImpl'>":
            for c1 in c.children:
                if str(type(c1)) == "<class 'gen.wiki_markupParser.wiki_markupParser.TemplateContext'>":
                    for c2 in c1.children:
                        if str(type(c2)) == "<class 'gen.wiki_markupParser.wiki_markupParser.Template_elementContext'>":
                            print(c2.getText())
                            return
    '''
    print(tree.toStringTree(ruleNames=[''], recog=parser))


if __name__ == '__main__':
    main(sys.argv)