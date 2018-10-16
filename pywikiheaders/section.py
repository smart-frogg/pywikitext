# -*- coding: utf-8 -*-
from pytextutils.token_splitter import TokenSplitter, POSTagger
from pytextutils.grammar_base import FormalLanguagesMatcher 
from pytextutils.grammar_lexic import DefisWordsBuilder
from pywikiaccessor.wiki_core import WikiConfiguration, WikiFileIndex, TitleIndex, WikiBaseIndex
from pywikiaccessor.wiki_categories import CategoryIndex
from pywikiaccessor.document_type import DocumentTypeIndex
from pywikiaccessor.wiki_tokenizer import WikiTokenizer
from pytextutils.text_stat import normalize, normalizeSum, TextStat, normalizeMaxMin, TEXT_STAT_KEYS
from pywikiutils.wiki_headers import HeadersFileIndex,HeadersFileBuilder
from pywikiutils.fragment import Fragment, calcHist

import numpy as np
import pickle
import json
import codecs
from collections import Counter
from math import log

from abc import ABCMeta, abstractmethod

class StopHeadersConfig:
    stopHeaders = None
    def __new__(cls,directory):
        if not StopHeadersConfig.stopHeaders:
            with open(directory + 'config/stopheaders.json', encoding="utf8") as data_file:
                StopHeadersConfig.stopHeaders = []    
                headers = json.load(data_file,encoding="utf-8")
                for header in headers:
                    StopHeadersConfig.stopHeaders.append(header.lower())
        return StopHeadersConfig.stopHeaders               
    
class AbstractSectionIterator(metaclass=ABCMeta): 
    def __init__(self, accessor, headerIndexPrefix):
        self.accessor = accessor
        self.headerIndex = HeadersFileIndex(accessor,headerIndexPrefix)
        self.prefix = headerIndexPrefix
        self.tokenSplitter = TokenSplitter()
        self.posTagger = POSTagger()

    @abstractmethod
    def preProcess(self):
        pass
    @abstractmethod
    def postProcess(self):
        pass
    @abstractmethod
    def processHeaderStart(self, headerId):    
        pass
    @abstractmethod
    def processHeaderEnd(self, headerId):    
        pass
    @abstractmethod
    def processFragment(self, headerId, docId):
        pass  
    
    def build(self):
        self.preProcess()
        stopHeaders = StopHeadersConfig(self.accessor.directory)
        fragmentCount = 0
        headerCount = 0
        for headerId in range(0, self.headerIndex.headerCount()):
            header = self.headerIndex.headerText(headerId)
            if not header in stopHeaders: 
                self.processHeaderStart(headerId)
                docs = self.headerIndex.documentsByHeaderId(headerId)
                if docs is None:
                    continue
                for docId in docs:
                    self.processFragment(headerId, docId)
                    fragmentCount+=1
                    if fragmentCount%1000 == 0:
                        print("\tProcess "+str(fragmentCount)+" fragments")
            headerCount+=1    
            self.processHeaderEnd(headerId)
            if headerCount%1000 == 0:
                print("\tProcess "+str(headerCount)+" headers")
            if headerCount == 2000:
                break;        
        self.postProcess()

class POSListSectionBuilder(AbstractSectionIterator):
    
    def __init__(self, accessor, indexPrefix):
        super(POSListSectionBuilder, self).__init__(accessor, indexPrefix)
    
    def preProcess(self):
        self.dictionaries = {'NOUN':Counter(),'VERB':Counter()}
        self.idfData = Counter()
        self.totalWords = Counter({'NOUN':0,'VERB':0})
 
    def postProcess(self):
        with open(self.accessor.directory+self.prefix + 'section_hists.pcl', 'wb') as f:
            pickle.dump(self.dictionaries, f, pickle.HIGHEST_PROTOCOL)
        self.tfidf = {}
        self.tf = {}
        self.tfidf = {}
        self.tf = {}
        for posKey in self.dictionaries:
            self.tfidf[posKey] = {}
            self.tf[posKey] = {}
            for normForm in self.dictionaries[posKey]:
                count = self.dictionaries[posKey][normForm]
                tf = count/self.totalWords[posKey]
                idf = len(self.dictionaries)/self.idfData[normForm] 
                self.tfidf[posKey][normForm] = tf * log(idf) 
                self.tf[posKey][normForm] = tf 
        with open(self.accessor.directory+self.prefix + 'section_tfidf.pcl', 'wb') as f:
            pickle.dump(self.tfidf, f, pickle.HIGHEST_PROTOCOL)
        with open(self.accessor.directory+self.prefix + 'section_tf.pcl', 'wb') as f:
            pickle.dump(self.tf, f, pickle.HIGHEST_PROTOCOL)

    def processHeaderStart(self, headerId):
        pass    
    def processHeaderEnd(self, headerId):    
        pass
    
    def processFragment(self, headerId, docId):
        text = self.headerIndex.getDocSection(docId, headerId)
        self.tokenSplitter.split(text)
        tokens = self.tokenSplitter.getTokenArray()
        self.posTagger.posTagging(tokens)
        hists = calcHist(tokens)
        self.dictionaries["VERB"] += hists["VERB"] 
        self.dictionaries["NOUN"] += hists["NOUN"] 
        self.totalWords["VERB"] += len(list(hists["VERB"].elements()))
        self.totalWords["NOUN"] += len(list(hists["NOUN"].elements()))
        for f in hists["VERB"]:           
            self.idfData[f]+=hists["VERB"][f]
        for f in hists["NOUN"]:            
            self.idfData[f]+=hists["NOUN"][f]
                                
    def printDict(self):
        print (self.dictionaries["NOUN"].most_common(10))
        print (self.dictionaries["VERB"].most_common(10))

    def printTfIdf(self):
        a = self.tfidf["NOUN"]
        i=0
        for key in sorted(a, key=a.get,reverse=False):
            if a[key] == 0:
                continue
            print("\t{}: {}".format(key,a[key]))
            i+=1
            if i>10:
                break
        a = self.tfidf["VERB"]
        i=0
        for key in sorted(a, key=a.get,reverse=False):
            if a[key] == 0:
                continue
            print("\t{}: {}".format(key,a[key]))
            i+=1
            if i>10:
                break

class POSListSectionIndex(WikiFileIndex):
    def __init__(self, wikiAccessor,prefix):
        super(POSListSectionIndex, self).__init__(wikiAccessor,prefix)
    
    def getDictionaryFiles(self): 
        return ['section_hists','section_tfidf','section_tf','section_tfAll']
    
    def getUniqueNounsCount(self):
        wordDict = self.dictionaries['section_hists']['NOUN']
        unoqueCount = len(list(wordDict.values()))
        return unoqueCount
    def getTotalNounsCount(self):
        wordDict = self.dictionaries['section_hists']['NOUN']
        fullCount = sum(list(wordDict.values()))
        return fullCount
    def getFunctionalNouns(self, part):
        wordDict = self.dictionaries['section_hists']['NOUN']
        fullCount = sum(list(wordDict.values()))
        count = 0
        goodWords = []
        for word in sorted(wordDict, key=wordDict.get, reverse=True):
            if count > part*fullCount:
                break
            count += wordDict[word]
            goodWords.append(word)
        return goodWords
    def getKeyNouns(self,part = 0.3):
        wordDict = self.dictionaries['section_hists']['NOUN']
        tfidfDict = self.dictionaries['section_tfidf']['NOUN']
        tfDict = self.dictionaries['section_tf']['NOUN']
        tfAll = self.dictionaries['section_tfAll']['NOUN']
        fullCount = sum(list(wordDict.values()))
        count = 0
        goodWords = []
        for word in sorted(wordDict, key=wordDict.get, reverse=True):
            if tfDict[word] < part * tfAll[word]: 
                continue
            if count > part*fullCount:
                break
            count += wordDict[word]
            goodWords.append(word)
        return goodWords
        
    def getKeyVerbs(self,weight, part):
        wordDict = self.dictionaries['section_hists']['VERB']
        tfidfDict = self.dictionaries['section_tfidf']['VERB']
        tfDict = self.dictionaries['section_tf']['VERB']
        tfAll = self.dictionaries['section_tfAll']['VERB']
        fullCount = sum(list(wordDict.values()))
        count = 0
        goodWords = []
        for word in sorted(wordDict, key=wordDict.get, reverse=True):
            if tfDict[word] < weight * tfAll[word]: 
                continue
            if count > part*fullCount:
                break
            count += wordDict[word]
            goodWords.append(word)
        return goodWords
    def getMostFreqVerbs(self, part):
        wordDict = self.dictionaries['section_hists']['VERB']
        fullCount = sum(list(wordDict.values()))
        count = 0
        goodWords = []
        for word in sorted(wordDict, key=wordDict.get, reverse=True):
            if count > part*fullCount:
                break
            count += wordDict[word]
            goodWords.append(word)
        return goodWords
    def getKeyVerbsAsDict(self):
        return self.dictionaries['section_hists']['VERB']
    def getKeyNounsAsDict(self):
        return self.dictionaries['section_hists']['NOUN']
    def getBuilder(self):
        return POSListSectionBuilder(self.accessor,self.prefix)
    def getName(self):
        return "pos_list_section"

from pytextutils.token_splitter import TYPE_SIGN            
class СollocationSectionIndexBuilder(AbstractSectionIterator):
    
    def __init__(self, accessor, indexPrefix):
        super(СollocationSectionIndexBuilder, self).__init__(accessor, indexPrefix)
        self.posListIndex = POSListSectionIndex(accessor, indexPrefix)
        self.flMatcher = FormalLanguagesMatcher()
        self.defisWordsBuilder = DefisWordsBuilder() 
        
    def preProcess(self):
        self.fragments = Counter()
        self.totalCounts = Counter()
        self.totalLen = 0
        self.goodWords = self.posListIndex.getFunctionalNouns(0.5)

    def postProcess(self):
        grammars = []
        for fragment in sorted(self.fragments, key=self.fragments.get, reverse=True):
            grammars.append({
                'name': str(fragment),
                'count': self.fragments[fragment],
                'freq': self.fragments[fragment]/self.totalLen,
                'grammar':fragment.genGrammar(),
            })
        with open(self.accessor.directory+self.prefix + 'section_collocations.pcl', 'wb') as f:
            pickle.dump(grammars, f, pickle.HIGHEST_PROTOCOL)        

    def processHeaderStart(self, headerId):    
        pass
        
    def processHeaderEnd(self, headerId):    
        pass
    
    def processFragment(self, headerId, docId):
        text = self.headerIndex.getDocSection(docId, headerId)
        self.tokenSplitter.split(text)
        tokens = self.tokenSplitter.getTokenArray() 
        self.posTagger.posTagging(tokens)
        self.flMatcher.combineTokens(tokens)
        self.defisWordsBuilder.combineTokens(tokens)
        fragmentStart = -1
        fragmentEnd = -1
        self.totalLen += len(tokens)
        signCount = 0
        for i in range(len(tokens)):
            if ((fragmentEnd - fragmentStart >=2 and signCount < fragmentEnd - fragmentStart) 
               or (fragmentEnd - fragmentStart == 1 and tokens[fragmentStart].tokenType !=TYPE_SIGN)):
                fragment = Fragment(tokens[fragmentStart:fragmentEnd],self.goodWords)
                self.fragments[fragment] += 1
                self.totalCounts[fragment] += 1
                signCount = 0
            if Fragment.isCommon(tokens[i],self.goodWords):
                fragmentStart = -1
                fragmentEnd = -1
                signCount = 0
            else:
                if fragmentStart == -1:
                    fragmentStart = i
                if tokens[i].tokenType == TYPE_SIGN:
                    signCount+=1
                fragmentEnd = i            
                        
    def printFragments(self, onlyGood = False):
        for fragment in sorted(self.fragments, key=self.fragments.get, reverse=True):
                if onlyGood and not fragment.isGood():
                    continue
                if self.fragments[fragment] < 10:
                    break
                print ("\t{}:{}".format(str(fragment),self.fragments[fragment]))      
def buildPOSSectionList (prefix):
    directory = "C:/WORK/science/python-data/"
    accessor =  WikiConfiguration(directory)
    sb = POSListSectionBuilder(accessor,prefix)
    sb.build()
    sb.printTfIdf()
def buildSectionCollocations (prefix):
    directory = "C:/WORK/science/python-data/"
    accessor =  WikiConfiguration(directory)
    fb = СollocationSectionIndexBuilder(accessor,prefix)
    fb.build()
    fb.printFragments(True)
if __name__ =="__main__":
    #buildPOSSectionList ('miph_')
    buildSectionCollocations('miph_')
                       