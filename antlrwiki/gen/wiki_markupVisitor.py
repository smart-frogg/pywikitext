# Generated from D:/Git/Парсер Викиразмертки\wiki_markup.g4 by ANTLR 4.7
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .wiki_markupParser import wiki_markupParser
else:
    from wiki_markupParser import wiki_markupParser

# This class defines a complete generic visitor for a parse tree produced by wiki_markupParser.

class wiki_markupVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by wiki_markupParser#wiki_article.
    def visitWiki_article(self, ctx:wiki_markupParser.Wiki_articleContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by wiki_markupParser#elements_markup.
    def visitElements_markup(self, ctx:wiki_markupParser.Elements_markupContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by wiki_markupParser#tags.
    def visitTags(self, ctx:wiki_markupParser.TagsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by wiki_markupParser#comment.
    def visitComment(self, ctx:wiki_markupParser.CommentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by wiki_markupParser#text_comment.
    def visitText_comment(self, ctx:wiki_markupParser.Text_commentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by wiki_markupParser#nowiki.
    def visitNowiki(self, ctx:wiki_markupParser.NowikiContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by wiki_markupParser#code.
    def visitCode(self, ctx:wiki_markupParser.CodeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by wiki_markupParser#syntaxhighlight.
    def visitSyntaxhighlight(self, ctx:wiki_markupParser.SyntaxhighlightContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by wiki_markupParser#pre.
    def visitPre(self, ctx:wiki_markupParser.PreContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by wiki_markupParser#math.
    def visitMath(self, ctx:wiki_markupParser.MathContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by wiki_markupParser#tt.
    def visitTt(self, ctx:wiki_markupParser.TtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by wiki_markupParser#ref.
    def visitRef(self, ctx:wiki_markupParser.RefContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by wiki_markupParser#ref_name.
    def visitRef_name(self, ctx:wiki_markupParser.Ref_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by wiki_markupParser#ref_content.
    def visitRef_content(self, ctx:wiki_markupParser.Ref_contentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by wiki_markupParser#other_tags.
    def visitOther_tags(self, ctx:wiki_markupParser.Other_tagsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by wiki_markupParser#content_other_tags.
    def visitContent_other_tags(self, ctx:wiki_markupParser.Content_other_tagsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by wiki_markupParser#template.
    def visitTemplate(self, ctx:wiki_markupParser.TemplateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by wiki_markupParser#template_element.
    def visitTemplate_element(self, ctx:wiki_markupParser.Template_elementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by wiki_markupParser#ignore_element.
    def visitIgnore_element(self, ctx:wiki_markupParser.Ignore_elementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by wiki_markupParser#ignore_content.
    def visitIgnore_content(self, ctx:wiki_markupParser.Ignore_contentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by wiki_markupParser#table.
    def visitTable(self, ctx:wiki_markupParser.TableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by wiki_markupParser#link.
    def visitLink(self, ctx:wiki_markupParser.LinkContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by wiki_markupParser#link_element.
    def visitLink_element(self, ctx:wiki_markupParser.Link_elementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by wiki_markupParser#url_or_email.
    def visitUrl_or_email(self, ctx:wiki_markupParser.Url_or_emailContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by wiki_markupParser#content_url_or_email.
    def visitContent_url_or_email(self, ctx:wiki_markupParser.Content_url_or_emailContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by wiki_markupParser#lists.
    def visitLists(self, ctx:wiki_markupParser.ListsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by wiki_markupParser#list_element.
    def visitList_element(self, ctx:wiki_markupParser.List_elementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by wiki_markupParser#assignment.
    def visitAssignment(self, ctx:wiki_markupParser.AssignmentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by wiki_markupParser#accentuation.
    def visitAccentuation(self, ctx:wiki_markupParser.AccentuationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by wiki_markupParser#logical_accentuation.
    def visitLogical_accentuation(self, ctx:wiki_markupParser.Logical_accentuationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by wiki_markupParser#structural_accentuation.
    def visitStructural_accentuation(self, ctx:wiki_markupParser.Structural_accentuationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by wiki_markupParser#text_accentuation.
    def visitText_accentuation(self, ctx:wiki_markupParser.Text_accentuationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by wiki_markupParser#headers.
    def visitHeaders(self, ctx:wiki_markupParser.HeadersContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by wiki_markupParser#contend_header.
    def visitContend_header(self, ctx:wiki_markupParser.Contend_headerContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by wiki_markupParser#header1.
    def visitHeader1(self, ctx:wiki_markupParser.Header1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by wiki_markupParser#header2.
    def visitHeader2(self, ctx:wiki_markupParser.Header2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by wiki_markupParser#header3.
    def visitHeader3(self, ctx:wiki_markupParser.Header3Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by wiki_markupParser#header4.
    def visitHeader4(self, ctx:wiki_markupParser.Header4Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by wiki_markupParser#header5.
    def visitHeader5(self, ctx:wiki_markupParser.Header5Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by wiki_markupParser#header6.
    def visitHeader6(self, ctx:wiki_markupParser.Header6Context):
        return self.visitChildren(ctx)



del wiki_markupParser