# -*- coding: utf-8 -*-
import pymorphy2
import WikiTokenizer
import WikiIndex
import TokenSplitter
import TextToken

from pprint import pprint
morph = pymorphy2.MorphAnalyzer()

# parse_result = morph.parse(u'стали')
# pprint (parse_result)

tokenizer = WikiTokenizer.WikiTokenizer()
directory = "C:\\WORK\\science\\onpositive_data\\python\\"
wikiIndex = WikiIndex.WikiIndex(directory)
cleanText = tokenizer.clean(wikiIndex.getTextArticleById(7))
wordSplitter = TokenSplitter.TokenSplitter()
wordSplitter.split(cleanText)
tokens = wordSplitter.getTokenArray()    
for token in tokens:
    if(token.tokenType == TextToken.TYPE_TOKEN):
        parse_result = morph.parse(token.token)
    pprint (parse_result) 
    


