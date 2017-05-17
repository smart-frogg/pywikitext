# -*- coding: utf-8 -*-
from pytextutils.token_splitter import TokenSplitter, SIGNS, TYPE_SIGN
from pywikiaccessor.wiki_tokenizer import WikiTokenizer
from pywikiaccessor.wiki_accessor import WikiAccessor
from pywikiaccessor.wiki_iterator import WikiIterator
from pywikiaccessor.wiki_file_index import WikiFileIndex
from pywikiaccessor.document_type import DocumentTypeIndex
import numpy as np

POS = ['VERB', 'INFN', 'PRTF', 'PRTS','GRND','NOUN','NPRO','ADJF','ADJS','COMP','ADVB','PRED','PREP','CONJ','PRCL','INTJ','NUMR']
WORD_POS = ['VERB', 'INFN', 'PRTF', 'PRTS','GRND','ADVB','PRED','PREP','CONJ','PRCL','INTJ']
DIAPASONS = {
    'CASE': [0,7],
    'NOM': [8,10],
    'GENDER': [11,14],
    'POS': [15,len(POS)+15],
    'SIGNS': [len(POS)+16,len(POS)+len(SIGNS)+16],
    'WORDS': [len(POS)+len(SIGNS)+17,0],
    }
'''
часть речи 16
падеж 7
число 2
род 3
конкретное слово
конкретный знак
'''  
class MorphBits:
    def __init__(self, words):
        self.arraySize = len(POS)+12+len(words)+len(SIGNS)
        self.words = words
    def getArray(self,tokens):
        res = np.zeros((self.arraySize,len(tokens)),dtype=np.int8)
        for i in range(0,len(tokens)-1):
            res[i] = self.__getOneToken(res[i],tokens[i])
        return res
    def __getOneToken(self,token):
        
        if token.tokenType == TYPE_SIGN:
            ind = SIGNS.index(token.token)
            
                

class RedirectsIndex (WikiFileIndex): 
    def __init__(self, wikiAccessor):
        super(RedirectsIndex, self).__init__(wikiAccessor)
        self.data = self.dictionaries["Redirects"]
    def getDictionaryFiles(self): 
        return ['Redirects']
    def getRedirectsIds(self):
        return list(self.data.keys());
    def getRedirectsCount(self):
        return len(self.data);
    def getRedirect(self, docId):
        return self.data[docId]; 
    def isRedirect(self, docId):
        return self.data.get(docId)
    def getBuilder(self):
        return RedirectsIndexBuilder(self.accessor)
    def getName(self):
        return "redirects"

from pywikiaccessor.title_index import TitleIndex
    
class RedirectsIndexBuilder (WikiIterator):
    
    def __init__(self, accessor):
        self.CODE = 'utf-8'
        self.simpleRedirect = re.compile('\#(redirect|перенаправление)([^\[])*\[\[([^\]]+)\]\]', re.VERBOSE)
        self.categoryTitle = re.compile('^Категория:(.+)', re.VERBOSE)
        self.complexRedirect = re.compile('\#(redirect|перенаправление)([^\[])\[\[([^\]\#]+)\#([^\]]+)\]\]', re.VERBOSE)  
        self.titleIndex = TitleIndex(accessor)
        super(RedirectsIndexBuilder, self).__init__(accessor, 10000)

    def processSave(self,articlesCount):
        return

    def postProcess(self):
        with open(self.accessor.directory + 'Redirects.pcl', 'wb') as f:
            pickle.dump(self.data, f, pickle.HIGHEST_PROTOCOL)

    def preProcess(self):
        self.data = {}
               
    def clear(self):
        return 
                                         
    def processDocument(self, docId):
        text = self.wikiIndex.getTextArticleById(docId).lower()
        res = self.complexRedirect.match(text)
        if res != None:
            self.data[docId] = RedirectPageFabric.createRedirectPage(self.titleIndex.findArticleId(res.group(3)),res.group(4))
            return
        res = self.simpleRedirect.match(text)
        if res != None:
            self.data[docId] = RedirectPageFabric.createRedirectPage(self.titleIndex.findArticleId(res.group(3)),"")

        
from pytextutils.cached_pymorphy_morph import CachedPymorphyMorph 
morph = CachedPymorphyMorph()
print(morph.parse("каждый"))
print(morph.parse("и"))

