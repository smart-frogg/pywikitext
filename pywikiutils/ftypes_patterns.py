# -*- coding: utf-8 -*-
from pytextutils.token_splitter import TokenSplitter, POSTagger, TYPE_SIGN, TYPE_COMPLEX_TOKEN
from pytextutils.grammar_base import FormalLanguagesMatcher, SentenceSplitter 
from pytextutils.grammar_lexic import DefisWordsBuilder
from pywikiaccessor.wiki_core import WikiConfiguration, WikiFileIndex, TitleIndex, WikiBaseIndex
from pywikiaccessor.wiki_categories import CategoryIndex
from pywikiaccessor.document_type import DocumentTypeIndex
from pytextutils.text_stat import normalize, normalizeSum, TextStat, normalizeMaxMin, TEXT_STAT_KEYS
from pywikiutils.wiki_headers import HeadersFileIndex,HeadersFileBuilder
from pywikiutils.fragment import Fragment, calcHist

import numpy as np
import pickle
import json
import codecs
from collections import Counter
from math import log

class FragmentConfig:
    def __init__(self,directory, prefix=""):
        self.headersToFragmentType = {}
        self.fragmentTypesToHeaders= {}
        with open(directory + prefix+ 'FragmentConfig.json', encoding="utf8") as data_file:    
            self.fTypes = json.load(data_file,encoding="utf-8")
            for ftype in self.fTypes:
                ftype['name'] = ftype['name'].lower()
                if (ftype.get('headers',None)):
                    self.fragmentTypesToHeaders[ftype['name']] = [] 
                    for header in ftype['headers']:
                        header = header.lower()
                        self.fragmentTypesToHeaders[ftype['name']].append(header)
                        self.headersToFragmentType[header] = ftype['name'] 
    @staticmethod
    def getDocTypeByTemplate(template):
        return 1 #DocumentTypeConfig.templatesToDoctypes.get(template)
    
from abc import ABCMeta, abstractmethod

class AbstractFragmentIterator(metaclass=ABCMeta): 
    def __init__(self, accessor, headerIndexPrefix):
        self.accessor = accessor
        self.headerIndex = HeadersFileIndex(accessor,headerIndexPrefix)
        self.prefix = headerIndexPrefix
        self.tokenSplitter = TokenSplitter()
        self.posTagger = POSTagger()
        self.fragmentConfig = FragmentConfig(accessor.directory, headerIndexPrefix)

    @abstractmethod
    def preProcess(self):
        pass
    @abstractmethod
    def postProcess(self):
        pass
    @abstractmethod
    def processFragmentStart(self, fType):    
        pass
    @abstractmethod
    def processFragmentEnd(self, fType):    
        pass
    @abstractmethod
    def processDocument(self, fType, headerId, docId):
        pass  
    
    def build(self):
        self.preProcess()
        for fType in self.fragmentConfig.fragmentTypesToHeaders.keys():
            print("Process "+fType+". Need to process "+str(len(self.fragmentConfig.fragmentTypesToHeaders[fType]))+" unique headers.")
            self.processFragmentStart(fType)
            docCount = 0
            for header in self.fragmentConfig.fragmentTypesToHeaders[fType]:
                headerId = self.headerIndex.headerId(header)
                docs = self.headerIndex.documentsByHeader(header)
                print("Need to process "+str(len(docs))+" documents.")
                for docId in docs:
                    self.processDocument(fType, headerId, docId)
                    docCount+=1
                    if docCount%100 == 0:
                        print("\tProcess "+str(docCount)+" documents")    
            print("\tProcess "+str(docCount)+" documents")    
            self.processFragmentEnd(fType)
        self.postProcess()

class FTypePOSListBuilder(AbstractFragmentIterator):
    
    def __init__(self, accessor, indexPrefix):
        super(FTypePOSListBuilder, self).__init__(accessor, indexPrefix)
    
    def preProcess(self):
        self.dictionaries = {}
        self.idfData = {}
        self.totalWords = {}
        self.totalWords['_All'] =  {'NOUN':0,'VERB':0}
 
    def postProcess(self):
        with open(self.accessor.directory+self.prefix + 'hists.pcl', 'wb') as f:
            pickle.dump(self.dictionaries, f, pickle.HIGHEST_PROTOCOL)
        self.tfidf = {}
        self.tf = {}
        self.tfAll = {}
        for dType in self.dictionaries:
            self.tfidf[dType] = {}
            self.tf[dType] = {}
            for posKey in self.dictionaries[dType]:
                self.tfidf[dType][posKey] = {}
                self.tf[dType][posKey] = {}
                if not self.tfAll.get(posKey,None):
                    self.tfAll[posKey] = {}
                for normForm in self.dictionaries[dType][posKey]:
                    count = self.dictionaries[dType][posKey][normForm]
                    tf = count/self.totalWords[dType][posKey]
                    tfAll = len(list(self.idfData[normForm].elements()))/self.totalWords['_All'][posKey]
                    idf = len(self.dictionaries)/len(self.idfData[normForm]) 
                    self.tfidf[dType][posKey][normForm] = tf * log(idf) 
                    self.tf[dType][posKey][normForm] = tf 
                    self.tfAll[posKey][normForm] = tfAll
        with open(self.accessor.directory+self.prefix + 'tfidf.pcl', 'wb') as f:
            pickle.dump(self.tfidf, f, pickle.HIGHEST_PROTOCOL)
        with open(self.accessor.directory+self.prefix + 'tf.pcl', 'wb') as f:
            pickle.dump(self.tf, f, pickle.HIGHEST_PROTOCOL)
        with open(self.accessor.directory+self.prefix + 'tfAll.pcl', 'wb') as f:
            pickle.dump(self.tfAll, f, pickle.HIGHEST_PROTOCOL)

    def processFragmentStart(self, fType):    
        self.dictionaries[fType] = {'NOUN':Counter(),'VERB':Counter()}
        self.totalWords[fType] = {'NOUN':0,'VERB':0}
    def processFragmentEnd(self, fType):    
        pass
    
    def processDocument(self, fType, headerId, docId):
        text = self.headerIndex.getDocSection(docId, headerId)
        self.tokenSplitter.split(text)
        tokens = self.tokenSplitter.getTokenArray()
        self.posTagger.posTagging(tokens)
        hists = calcHist(tokens)
        self.dictionaries[fType]["VERB"] += hists["VERB"] 
        self.dictionaries[fType]["NOUN"] += hists["NOUN"] 
        self.totalWords[fType]["VERB"] += len(list(hists["VERB"].elements()))
        self.totalWords[fType]["NOUN"] += len(list(hists["NOUN"].elements()))
        self.totalWords["_All"]["VERB"] += len(list(hists["VERB"].elements()))
        self.totalWords["_All"]["NOUN"] += len(list(hists["NOUN"].elements()))
        for f in hists["VERB"]: 
            if not self.idfData.get(f):
                self.idfData[f] = Counter()            
            self.idfData[f][fType]+=hists["VERB"][f]
        for f in hists["NOUN"]: 
            if not self.idfData.get(f):
                self.idfData[f] = Counter()            
            self.idfData[f][fType]+=hists["NOUN"][f]
                                
    def printDict(self):
        for fType in self.dictionaries:
            print(fType)
            print (self.dictionaries[fType]["NOUN"].most_common(10))
            print (self.dictionaries[fType]["VERB"].most_common(10))

    def printTfIdf(self):
        for fType in self.dictionaries:
            print(fType)
            a = self.tfidf[fType]["NOUN"]
            i=0
            for key in sorted(a, key=a.get,reverse=False):
                if a[key] == 0:
                    continue
                print("\t{}: {}".format(key,a[key]))
                i+=1
                if i>10:
                    break
            a = self.tfidf[fType]["VERB"]
            i=0
            for key in sorted(a, key=a.get,reverse=False):
                if a[key] == 0:
                    continue
                print("\t{}: {}".format(key,a[key]))
                i+=1
                if i>10:
                    break

class FTypePOSListIndex(WikiFileIndex):
    def __init__(self, wikiAccessor,prefix):
        super(FTypePOSListIndex, self).__init__(wikiAccessor,prefix)
    
    def getDictionaryFiles(self): 
        return ['hists','tfidf','tf','tfAll']
    
    def getUniqueNounsCount(self,fType):
        wordDict = self.dictionaries['hists'][fType]['NOUN']
        unoqueCount = len(list(wordDict.values()))
        return unoqueCount
    def getTotalNounsCount(self,fType):
        wordDict = self.dictionaries['hists'][fType]['NOUN']
        fullCount = sum(list(wordDict.values()))
        return fullCount
    def getFunctionalNouns(self,fType, part):
        wordDict = self.dictionaries['hists'][fType]['NOUN']
        fullCount = sum(list(wordDict.values()))
        count = 0
        goodWords = []
        for word in sorted(wordDict, key=wordDict.get, reverse=True):
            if count > part*fullCount:
                break
            count += wordDict[word]
            goodWords.append(word)
        return goodWords
    def getKeyNouns(self,fType, part = 0.3):
        wordDict = self.dictionaries['hists'][fType]['NOUN']
        tfidfDict = self.dictionaries['tfidf'][fType]['NOUN']
        tfDict = self.dictionaries['tf'][fType]['NOUN']
        tfAll = self.dictionaries['tfAll']['NOUN']
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
        
    def getKeyVerbs(self,fType, weight, part):
        wordDict = self.dictionaries['hists'][fType]['VERB']
        tfidfDict = self.dictionaries['tfidf'][fType]['VERB']
        tfDict = self.dictionaries['tf'][fType]['VERB']
        tfAll = self.dictionaries['tfAll']['VERB']
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
    def getMostFreqVerbs(self,fType, part):
        wordDict = self.dictionaries['hists'][fType]['VERB']
        fullCount = sum(list(wordDict.values()))
        count = 0
        goodWords = []
        for word in sorted(wordDict, key=wordDict.get, reverse=True):
            if count > part*fullCount:
                break
            count += wordDict[word]
            goodWords.append(word)
        return goodWords
    def getKeyVerbsAsDict(self,fType):
        return self.dictionaries['hists'][fType]['VERB']
    def getKeyNounsAsDict(self,fType):
        return self.dictionaries['hists'][fType]['NOUN']
    def getVerbsHistsForAllTypes(self):
        res = {}
        for fType in self.getFunctionalTypes():
            res[fType] = self.getKeyVerbsAsDict(fType)
        return res
    def getFunctionalTypes(self):
        return list(self.dictionaries['hists'].keys())
    def getBuilder(self):
        return FTypePOSListBuilder(self.accessor,self.prefix)
    def getName(self):
        return "pos_list"
    

            
class СollocationFragmentTypeBuilder(AbstractFragmentIterator):
    
    def __init__(self, accessor, indexPrefix):
        super(СollocationFragmentTypeBuilder, self).__init__(accessor, indexPrefix)
        self.posListIndex = FTypePOSListIndex(accessor, indexPrefix)
        self.flMatcher = FormalLanguagesMatcher()
        self.defisWordsBuilder = DefisWordsBuilder() 
        
    def preProcess(self):
        self.fragments = {}
        self.totalCounts = Counter()
        self.totalLen = 0
        self.fragmentLen = {}

    def postProcess(self):
        grammars = {}
        for fType in self.fragments:
            grammars[fType] = []
            for fragment in sorted(self.fragments[fType], key=self.fragments[fType].get, reverse=True):
                grammars[fType].append({
                        'name': str(fragment),
                        'count': self.fragments[fType][fragment],
                        'freq': self.fragments[fType][fragment]/self.fragmentLen[fType],
                        'total_freq':self.totalCounts[fragment]/self.totalLen,
                        'grammar':fragment.genGrammar(),
                    })
        with open(self.accessor.directory+self.prefix + 'collocations.pcl', 'wb') as f:
            pickle.dump(grammars, f, pickle.HIGHEST_PROTOCOL)        

    def processFragmentStart(self, fType):    
        self.fragments[fType] = Counter()
        self.fragmentLen[fType] = 0
        self.goodWords = self.posListIndex.getFunctionalNouns(fType,0.5)
        
    def processFragmentEnd(self, fType):    
        pass
    
    def processDocument(self, fType, headerId, docId):
        text = self.headerIndex.getDocSection(docId, headerId)
        self.tokenSplitter.split(text)
        tokens = self.tokenSplitter.getTokenArray() 
        self.posTagger.posTagging(tokens)
        self.flMatcher.combineTokens(tokens)
        self.defisWordsBuilder.combineTokens(tokens)
        fragmentStart = -1
        fragmentEnd = -1
        self.fragmentLen[fType] += len(tokens)
        self.totalLen += len(tokens)
        signCount = 0
        for i in range(len(tokens)):
            if ((fragmentEnd - fragmentStart >=2 and signCount < fragmentEnd - fragmentStart) 
               or (fragmentEnd - fragmentStart == 1 and tokens[fragmentStart].tokenType !=TYPE_SIGN)):
                fragment = Fragment(tokens[fragmentStart:fragmentEnd],self.goodWords)
                self.fragments[fType][fragment] += 1
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
        for fType in self.fragments:
            print(fType)
            for fragment in sorted(self.fragments[fType], key=self.fragments[fType].get, reverse=True):
                if onlyGood and not fragment.isGood():
                    continue
                if self.fragments[fType][fragment] < 10:
                    break
                print ("\t{}:{}".format(str(fragment),self.fragments[fType][fragment]))
                
def buildFragments (prefix):
    directory = "C:/WORK/science/python-data/"
    accessor =  WikiConfiguration(directory)
    fb = СollocationFragmentTypeBuilder(accessor,prefix)
    fb.build()
    fb.printFragments(True)
    
#def buildStat (prefix):
#    directory = "C:/WORK/science/python-data/"
#    accessor =  WikiConfiguration(directory)
#    sb = StatBuilder(accessor,prefix)
#    sb.build()
#    sb.print()

def buildPOSList (prefix):
    directory = "C:/WORK/science/python-data/"
    accessor =  WikiConfiguration(directory)
    sb = FTypePOSListBuilder(accessor,prefix)
    sb.build()
    sb.printTfIdf()    