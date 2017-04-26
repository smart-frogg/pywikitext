# -*- coding: utf-8 -*-
import pymorphy2
import pickle
#from pywikiaccessor import WikiTokenizer
#from pywikiaccessor import WikiIndex
import TokenSplitter
import TextToken

from pprint import pprint
morph = pymorphy2.MorphAnalyzer()

# parse_result = morph.parse(u'стали')
# pprint (parse_result)
wordSplitter = TokenSplitter.TokenSplitter()
str="Победа над фашизмом принесла долгожданный мир"
wordSplitter.split(str)
tokens = wordSplitter.getTokenArray()
for token in tokens:
    if (token.tokenType == TextToken.TYPE_TOKEN):
        parse_result = morph.parse(token.token)
        print(parse_result)
'''
tokenizer = WikiTokenizer.WikiTokenizer()
directory = "C:\\WORK\\science\\onpositive_data\\python\\"
wikiIndex = WikiIndex.WikiIndex(directory)
countVerbsDict = {}
countWordsDict = {}
countMultivalVerbsDict = {}    
countMultivalWordsDict = {}  
articlesCount = 0
for i in wikiIndex.getIds():
    countVerbs = 0
    countWords = 0
    countMultivalVerbs = 0    
    countMultivalWords = 0  
    articlesCount += 1
    if (articlesCount%10 == 0):
        pprint("Processed "+str(articlesCount))
    cleanText = tokenizer.clean(wikiIndex.getTextArticleById(i))
    wordSplitter = TokenSplitter.TokenSplitter()
    wordSplitter.split(cleanText)
    tokens = wordSplitter.getTokenArray()
  
    for token in tokens:
        if (token.tokenType == TextToken.TYPE_TOKEN):
            countWords += 1
            parse_result = morph.parse(token.token)
            count = len(parse_result)
            isVerb = False
            for res in parse_result:
                if (res.tag.POS == 'VERB'):
                    isVerb = True
            if(count > 1):
                countMultivalWords += 1
            if(isVerb):
                countVerbs += 1
                if(count > 1):
                    countMultivalVerbs += 1 
    countVerbsDict[i] = countVerbs
    countWordsDict[i] = countWordsDict
    countMultivalVerbsDict[i] = countMultivalVerbs    
    countMultivalWordsDict[i] = countMultivalWords     

with open(directory + 'countVerbs' + '.pkl', 'wb') as f:
    pickle.dump(countVerbsDict, f, pickle.HIGHEST_PROTOCOL)
with open(directory + 'countWords' + '.pkl', 'wb') as f:
    pickle.dump(countWordsDict, f, pickle.HIGHEST_PROTOCOL)
with open(directory + 'countMultivalVerbs' + '.pkl', 'wb') as f:
    pickle.dump(countMultivalVerbsDict, f, pickle.HIGHEST_PROTOCOL)
with open(directory + 'countMultivalWords' + '.pkl', 'wb') as f:
    pickle.dump(countMultivalWordsDict, f, pickle.HIGHEST_PROTOCOL)
 '''                   


