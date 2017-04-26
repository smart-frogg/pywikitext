# Generated from D:/Git/Парсер Викиразмертки\wiki_markup.g4 by ANTLR 4.7
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .wiki_markupParser import wiki_markupParser
else:
    from wiki_markupParser import wiki_markupParser

# This class defines a complete listener for a parse tree produced by wiki_markupParser.
class wiki_markupListener(ParseTreeListener):

    # Enter a parse tree produced by wiki_markupParser#wiki_article.
    def enterWiki_article(self, ctx:wiki_markupParser.Wiki_articleContext):
        pass

    # Exit a parse tree produced by wiki_markupParser#wiki_article.
    def exitWiki_article(self, ctx:wiki_markupParser.Wiki_articleContext):
        pass


    # Enter a parse tree produced by wiki_markupParser#elements_markup.
    def enterElements_markup(self, ctx:wiki_markupParser.Elements_markupContext):
        pass

    # Exit a parse tree produced by wiki_markupParser#elements_markup.
    def exitElements_markup(self, ctx:wiki_markupParser.Elements_markupContext):
        pass


    # Enter a parse tree produced by wiki_markupParser#tags.
    def enterTags(self, ctx:wiki_markupParser.TagsContext):
        pass

    # Exit a parse tree produced by wiki_markupParser#tags.
    def exitTags(self, ctx:wiki_markupParser.TagsContext):
        pass


    # Enter a parse tree produced by wiki_markupParser#comment.
    def enterComment(self, ctx:wiki_markupParser.CommentContext):
        pass

    # Exit a parse tree produced by wiki_markupParser#comment.
    def exitComment(self, ctx:wiki_markupParser.CommentContext):
        pass


    # Enter a parse tree produced by wiki_markupParser#text_comment.
    def enterText_comment(self, ctx:wiki_markupParser.Text_commentContext):
        pass

    # Exit a parse tree produced by wiki_markupParser#text_comment.
    def exitText_comment(self, ctx:wiki_markupParser.Text_commentContext):
        pass


    # Enter a parse tree produced by wiki_markupParser#nowiki.
    def enterNowiki(self, ctx:wiki_markupParser.NowikiContext):
        pass

    # Exit a parse tree produced by wiki_markupParser#nowiki.
    def exitNowiki(self, ctx:wiki_markupParser.NowikiContext):
        pass


    # Enter a parse tree produced by wiki_markupParser#code.
    def enterCode(self, ctx:wiki_markupParser.CodeContext):
        pass

    # Exit a parse tree produced by wiki_markupParser#code.
    def exitCode(self, ctx:wiki_markupParser.CodeContext):
        pass


    # Enter a parse tree produced by wiki_markupParser#syntaxhighlight.
    def enterSyntaxhighlight(self, ctx:wiki_markupParser.SyntaxhighlightContext):
        pass

    # Exit a parse tree produced by wiki_markupParser#syntaxhighlight.
    def exitSyntaxhighlight(self, ctx:wiki_markupParser.SyntaxhighlightContext):
        pass


    # Enter a parse tree produced by wiki_markupParser#pre.
    def enterPre(self, ctx:wiki_markupParser.PreContext):
        pass

    # Exit a parse tree produced by wiki_markupParser#pre.
    def exitPre(self, ctx:wiki_markupParser.PreContext):
        pass


    # Enter a parse tree produced by wiki_markupParser#math.
    def enterMath(self, ctx:wiki_markupParser.MathContext):
        pass

    # Exit a parse tree produced by wiki_markupParser#math.
    def exitMath(self, ctx:wiki_markupParser.MathContext):
        pass


    # Enter a parse tree produced by wiki_markupParser#tt.
    def enterTt(self, ctx:wiki_markupParser.TtContext):
        pass

    # Exit a parse tree produced by wiki_markupParser#tt.
    def exitTt(self, ctx:wiki_markupParser.TtContext):
        pass


    # Enter a parse tree produced by wiki_markupParser#ref.
    def enterRef(self, ctx:wiki_markupParser.RefContext):
        pass

    # Exit a parse tree produced by wiki_markupParser#ref.
    def exitRef(self, ctx:wiki_markupParser.RefContext):
        pass


    # Enter a parse tree produced by wiki_markupParser#ref_name.
    def enterRef_name(self, ctx:wiki_markupParser.Ref_nameContext):
        pass

    # Exit a parse tree produced by wiki_markupParser#ref_name.
    def exitRef_name(self, ctx:wiki_markupParser.Ref_nameContext):
        pass


    # Enter a parse tree produced by wiki_markupParser#ref_content.
    def enterRef_content(self, ctx:wiki_markupParser.Ref_contentContext):
        pass

    # Exit a parse tree produced by wiki_markupParser#ref_content.
    def exitRef_content(self, ctx:wiki_markupParser.Ref_contentContext):
        pass


    # Enter a parse tree produced by wiki_markupParser#other_tags.
    def enterOther_tags(self, ctx:wiki_markupParser.Other_tagsContext):
        pass

    # Exit a parse tree produced by wiki_markupParser#other_tags.
    def exitOther_tags(self, ctx:wiki_markupParser.Other_tagsContext):
        pass


    # Enter a parse tree produced by wiki_markupParser#content_other_tags.
    def enterContent_other_tags(self, ctx:wiki_markupParser.Content_other_tagsContext):
        pass

    # Exit a parse tree produced by wiki_markupParser#content_other_tags.
    def exitContent_other_tags(self, ctx:wiki_markupParser.Content_other_tagsContext):
        pass


    # Enter a parse tree produced by wiki_markupParser#template.
    def enterTemplate(self, ctx:wiki_markupParser.TemplateContext):
        pass

    # Exit a parse tree produced by wiki_markupParser#template.
    def exitTemplate(self, ctx:wiki_markupParser.TemplateContext):
        pass


    # Enter a parse tree produced by wiki_markupParser#template_element.
    def enterTemplate_element(self, ctx:wiki_markupParser.Template_elementContext):
        pass

    # Exit a parse tree produced by wiki_markupParser#template_element.
    def exitTemplate_element(self, ctx:wiki_markupParser.Template_elementContext):
        pass


    # Enter a parse tree produced by wiki_markupParser#ignore_element.
    def enterIgnore_element(self, ctx:wiki_markupParser.Ignore_elementContext):
        pass

    # Exit a parse tree produced by wiki_markupParser#ignore_element.
    def exitIgnore_element(self, ctx:wiki_markupParser.Ignore_elementContext):
        pass


    # Enter a parse tree produced by wiki_markupParser#ignore_content.
    def enterIgnore_content(self, ctx:wiki_markupParser.Ignore_contentContext):
        pass

    # Exit a parse tree produced by wiki_markupParser#ignore_content.
    def exitIgnore_content(self, ctx:wiki_markupParser.Ignore_contentContext):
        pass


    # Enter a parse tree produced by wiki_markupParser#table.
    def enterTable(self, ctx:wiki_markupParser.TableContext):
        pass

    # Exit a parse tree produced by wiki_markupParser#table.
    def exitTable(self, ctx:wiki_markupParser.TableContext):
        pass


    # Enter a parse tree produced by wiki_markupParser#link.
    def enterLink(self, ctx:wiki_markupParser.LinkContext):
        pass

    # Exit a parse tree produced by wiki_markupParser#link.
    def exitLink(self, ctx:wiki_markupParser.LinkContext):
        pass


    # Enter a parse tree produced by wiki_markupParser#link_element.
    def enterLink_element(self, ctx:wiki_markupParser.Link_elementContext):
        pass

    # Exit a parse tree produced by wiki_markupParser#link_element.
    def exitLink_element(self, ctx:wiki_markupParser.Link_elementContext):
        pass


    # Enter a parse tree produced by wiki_markupParser#url_or_email.
    def enterUrl_or_email(self, ctx:wiki_markupParser.Url_or_emailContext):
        pass

    # Exit a parse tree produced by wiki_markupParser#url_or_email.
    def exitUrl_or_email(self, ctx:wiki_markupParser.Url_or_emailContext):
        pass


    # Enter a parse tree produced by wiki_markupParser#content_url_or_email.
    def enterContent_url_or_email(self, ctx:wiki_markupParser.Content_url_or_emailContext):
        pass

    # Exit a parse tree produced by wiki_markupParser#content_url_or_email.
    def exitContent_url_or_email(self, ctx:wiki_markupParser.Content_url_or_emailContext):
        pass


    # Enter a parse tree produced by wiki_markupParser#lists.
    def enterLists(self, ctx:wiki_markupParser.ListsContext):
        pass

    # Exit a parse tree produced by wiki_markupParser#lists.
    def exitLists(self, ctx:wiki_markupParser.ListsContext):
        pass


    # Enter a parse tree produced by wiki_markupParser#list_element.
    def enterList_element(self, ctx:wiki_markupParser.List_elementContext):
        pass

    # Exit a parse tree produced by wiki_markupParser#list_element.
    def exitList_element(self, ctx:wiki_markupParser.List_elementContext):
        pass


    # Enter a parse tree produced by wiki_markupParser#assignment.
    def enterAssignment(self, ctx:wiki_markupParser.AssignmentContext):
        pass

    # Exit a parse tree produced by wiki_markupParser#assignment.
    def exitAssignment(self, ctx:wiki_markupParser.AssignmentContext):
        pass


    # Enter a parse tree produced by wiki_markupParser#accentuation.
    def enterAccentuation(self, ctx:wiki_markupParser.AccentuationContext):
        pass

    # Exit a parse tree produced by wiki_markupParser#accentuation.
    def exitAccentuation(self, ctx:wiki_markupParser.AccentuationContext):
        pass


    # Enter a parse tree produced by wiki_markupParser#logical_accentuation.
    def enterLogical_accentuation(self, ctx:wiki_markupParser.Logical_accentuationContext):
        pass

    # Exit a parse tree produced by wiki_markupParser#logical_accentuation.
    def exitLogical_accentuation(self, ctx:wiki_markupParser.Logical_accentuationContext):
        pass


    # Enter a parse tree produced by wiki_markupParser#structural_accentuation.
    def enterStructural_accentuation(self, ctx:wiki_markupParser.Structural_accentuationContext):
        pass

    # Exit a parse tree produced by wiki_markupParser#structural_accentuation.
    def exitStructural_accentuation(self, ctx:wiki_markupParser.Structural_accentuationContext):
        pass


    # Enter a parse tree produced by wiki_markupParser#text_accentuation.
    def enterText_accentuation(self, ctx:wiki_markupParser.Text_accentuationContext):
        pass

    # Exit a parse tree produced by wiki_markupParser#text_accentuation.
    def exitText_accentuation(self, ctx:wiki_markupParser.Text_accentuationContext):
        pass


    # Enter a parse tree produced by wiki_markupParser#headers.
    def enterHeaders(self, ctx:wiki_markupParser.HeadersContext):
        pass

    # Exit a parse tree produced by wiki_markupParser#headers.
    def exitHeaders(self, ctx:wiki_markupParser.HeadersContext):
        pass


    # Enter a parse tree produced by wiki_markupParser#contend_header.
    def enterContend_header(self, ctx:wiki_markupParser.Contend_headerContext):
        pass

    # Exit a parse tree produced by wiki_markupParser#contend_header.
    def exitContend_header(self, ctx:wiki_markupParser.Contend_headerContext):
        pass


    # Enter a parse tree produced by wiki_markupParser#header1.
    def enterHeader1(self, ctx:wiki_markupParser.Header1Context):
        pass

    # Exit a parse tree produced by wiki_markupParser#header1.
    def exitHeader1(self, ctx:wiki_markupParser.Header1Context):
        pass


    # Enter a parse tree produced by wiki_markupParser#header2.
    def enterHeader2(self, ctx:wiki_markupParser.Header2Context):
        pass

    # Exit a parse tree produced by wiki_markupParser#header2.
    def exitHeader2(self, ctx:wiki_markupParser.Header2Context):
        pass


    # Enter a parse tree produced by wiki_markupParser#header3.
    def enterHeader3(self, ctx:wiki_markupParser.Header3Context):
        pass

    # Exit a parse tree produced by wiki_markupParser#header3.
    def exitHeader3(self, ctx:wiki_markupParser.Header3Context):
        pass


    # Enter a parse tree produced by wiki_markupParser#header4.
    def enterHeader4(self, ctx:wiki_markupParser.Header4Context):
        pass

    # Exit a parse tree produced by wiki_markupParser#header4.
    def exitHeader4(self, ctx:wiki_markupParser.Header4Context):
        pass


    # Enter a parse tree produced by wiki_markupParser#header5.
    def enterHeader5(self, ctx:wiki_markupParser.Header5Context):
        pass

    # Exit a parse tree produced by wiki_markupParser#header5.
    def exitHeader5(self, ctx:wiki_markupParser.Header5Context):
        pass


    # Enter a parse tree produced by wiki_markupParser#header6.
    def enterHeader6(self, ctx:wiki_markupParser.Header6Context):
        pass

    # Exit a parse tree produced by wiki_markupParser#header6.
    def exitHeader6(self, ctx:wiki_markupParser.Header6Context):
        pass


