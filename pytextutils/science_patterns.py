# -*- coding: utf-8 -*-
from pytextutils.token_splitter import TokenSplitter, POSTagger, SIGNS, TYPE_SIGN
from pywikiaccessor.wiki_accessor import WikiAccessor
from pywikiaccessor.wiki_iterator import WikiIterator
from pywikiaccessor.wiki_file_index import WikiFileIndex
from pywikiaccessor.wiki_categories import CategoryIndex
from pywikiaccessor.title_index import TitleIndex
from pywikiaccessor.document_type import DocumentTypeIndex
from experiments.wiki_headers import HeadersFileBuilder
from pywikiaccessor.wiki_tokenizer import WikiTokenizer
from pywikiaccessor.wiki_base_index import WikiBaseIndex
import numpy as np
import pickle
import json
import codecs
from wiki_headers import HeadersFileIndex,HeadersFileBuilder
from collections import Counter

WORD_POS = ['VERB', 'INFN', 'PRTF', 'PRTS','GRND','ADVB','PRED','PREP','CONJ','PRCL','INTJ']
NAME_GROUP = "@NAME_GROUP@"

class Fragment:
    def __init__(self,tokens):
        self.tokens = []
        for t in tokens:
            if t.tokenType == TYPE_SIGN:
                self.tokens.append(t.token)
            elif t.getBestPOS() in WORD_POS:
                self.tokens.append(t.POS[0]['normalForm'])
            else:
                self.tokens.append(NAME_GROUP)    
    def __str__(self):
        return '|'.join(self.tokens)
             
    def __hash__(self):
        return hash('|'.join(self.tokens))

    def __eq__(self, other):
        return self.tokens == other.tokens
     
class FragmentConfig:
    headersToFragmentType = {}
    fragmentTypesToHeaders= {}
    fTypes = None
    def __new__(cls,directory):
        if not FragmentConfig.fTypes:
            with open(directory + 'FragmentConfig.json', encoding="utf8") as data_file:    
                fTypes = json.load(data_file,encoding="utf-8")
                for ftype in fTypes:
                    ftype['name'] = ftype['name'].lower()
                    if (ftype.get('headers',None)):
                        FragmentConfig.fragmentTypesToHeaders[ftype['name']] = [] 
                        for header in ftype['headers']:
                            header = header.lower()
                            FragmentConfig.fragmentTypesToHeaders[ftype['name']].append(header)
                            FragmentConfig.headersToFragmentType[header] = ftype['name'] 
        return FragmentConfig.fTypes               
    @staticmethod
    def getDocTypeByTemplate(template):
        return 1 #DocumentTypeConfig.templatesToDoctypes.get(template)

    
class FragmentBuilder:
    
    def __init__(self, accessor, headerIndexPrefix):
        self.headerIndex = HeadersFileIndex(accessor,headerIndexPrefix)
        self.wikiTokenizer = WikiTokenizer()
        self.tokenSplitter = TokenSplitter()
        fTypes = FragmentConfig(accessor.directory)
        self.wikiIndex = accessor.getIndex(WikiBaseIndex)
        self.posTagger = POSTagger()

    def getDocSection(self,docId,headerId):
        text = self.wikiIndex.getTextArticleById(docId)
        headers = self.headerIndex.headersByDoc(docId)
        headerN = [i for i, h in enumerate(headers) if h['header'] == headerId][0]
        start = headers[headerN]["position_match"]
        if headerN == len(headers)-1:
            finish = len(text)
        else:
            finish = headers[headerN+1]["position_start"]
        return self.wikiTokenizer.clean(text[start:finish])
               
    def build(self,windowSize):
        self.fragments = {}
        for fType in FragmentConfig.fragmentTypesToHeaders.keys():
            self.fragments[fType] = Counter()
            for header in FragmentConfig.fragmentTypesToHeaders[fType]:
                headerId = self.headerIndex.headerId(header)
                docs = self.headerIndex.documentsByHeader(header)
                for docId in docs:
                    text = self.getDocSection(docId, headerId)
                    self.tokenSplitter.split(text)
                    tokens = self.tokenSplitter.getTokenArray() 
                    self.posTagger.posTagging(tokens)
                    for i in range(len(tokens)-windowSize):
                        fragment = Fragment(tokens[i:i+windowSize])
                        self.fragments[fType][fragment] += 1
                        
    def print(self):
        for fType in self.fragments:
            print(fType)
            
            for fragment in sorted(self.fragments[fType], key=self.fragments[fType].get, reverse=True):
                if self.fragments[fType][fragment] < 10:
                    break
                print ("\t{}:{}".format(str(fragment),self.fragments[fType][fragment]))
                                                     


def buildHeaders (categories,prefix):
    directory = "C:\\WORK\\science\\onpositive_data\\python\\"
    accessor =  WikiAccessor(directory)
    categoryIndex = accessor.getIndex(CategoryIndex)
    titleIndex = accessor.getIndex(TitleIndex)
    documentTypes = accessor.getIndex(DocumentTypeIndex)        
    
    pages = set()
    for cat in categories:
        categoryId = categoryIndex.getIdByTitle(cat)
        catPages = categoryIndex.getAllPagesAsSet(categoryId)
        pages.update(catPages)
    with codecs.open( directory+'titles.txt', 'w', 'utf-8' ) as f:
        for p in list(pages):
            if (documentTypes.isDocType(p,'person') or 
                documentTypes.isDocType(p,'location') or 
                documentTypes.isDocType(p,'entertainment') or 
                documentTypes.isDocType(p,'organization')):
                pages.discard(p)
            else:
                # print(titleIndex.getTitleById(p))
                f.write(titleIndex.getTitleById(p)+'\n')
        f.close()
    print(len(pages))    
    hb = HeadersFileBuilder(accessor,list(pages),prefix) 
    hb.build()
    hi = HeadersFileIndex(accessor,prefix)
    stat = hi.getAllStat()
    for item in stat:
        if item['cnt'] == 1:
            break
        print (item['text']+": "+str(item['cnt']))

buildHeaders(['Информатика','Математика'],'math_')
#directory = "C:\\WORK\\science\\onpositive_data\\python\\"
#accessor =  WikiAccessor(directory)
#fb = FragmentBuilder(accessor,'math_')
#fb.build(3)
#fb.print()
