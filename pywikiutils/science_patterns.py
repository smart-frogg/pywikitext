# -*- coding: utf-8 -*-
from pytextutils.token_splitter import TokenSplitter, POSTagger, TYPE_SIGN, TYPE_COMPLEX_TOKEN
from pytextutils.grammar_base import FormalLanguagesMatcher, SentenceSplitter 
from pytextutils.grammar_lexic import DefisWordsBuilder
from pywikiaccessor.wiki_core import WikiConfiguration, WikiFileIndex, TitleIndex, WikiBaseIndex, WikiIterator
from pywikiaccessor.wiki_categories import CategoryIndex
from pywikiaccessor.document_type import DocumentTypeIndex
from pywikiaccessor.page_types_indexes import RedirectsIndex

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

class POSListBuilder(WikiIterator):
    
    def __init__(self, accessor, indexPrefix):
        super(POSListBuilder, self).__init__(accessor, indexPrefix)
    
    def preProcess(self):
        self.dictionaries = {'NOUN':Counter(),'VERB':Counter()}
        self.totalWords = {'NOUN':0,'VERB':0}
        self.idfData = {}
 
    def postProcess(self):
        with open(self.accessor.directory+self.prefix + 'hists_all.pcl', 'wb') as f:
            pickle.dump(self.dictionaries, f, pickle.HIGHEST_PROTOCOL)
        self.tfidf = {}
        self.tf = {}
        self.tfAll = {}
        for posKey in self.dictionaries:
            self.tfidf[posKey] = {}
            self.tf[posKey] = {}
            if not self.tfAll.get(posKey,None):
                self.tfAll[posKey] = {}
            for normForm in self.dictionaries[posKey]:
                count = self.dictionaries[posKey][normForm]
                tf = count/self.totalWords[posKey]
                idf = len(self.dictionaries)/len(self.idfData[normForm]) 
                self.tfidf[posKey][normForm] = tf * log(idf) 
                self.tf[posKey][normForm] = tf 
        with open(self.accessor.directory+self.prefix + 'tfidf_all.pcl', 'wb') as f:
            pickle.dump(self.tfidf, f, pickle.HIGHEST_PROTOCOL)
        with open(self.accessor.directory+self.prefix + 'tf_all.pcl', 'wb') as f:
            pickle.dump(self.tf, f, pickle.HIGHEST_PROTOCOL)
        with open(self.accessor.directory+self.prefix + 'tfAll.pcl', 'wb') as f:
            pickle.dump(self.tfAll, f, pickle.HIGHEST_PROTOCOL)
    
    def processDocument(self, docId):
        if self.redirects.isRedirect(docId):
            return
        if self.doctypeIndex.isDocType(docId,'wiki_stuff'):
            return
        text = self.wikiIndex.getTextArticleById(docId)
        self.tokenSplitter.split(text)
        tokens = self.tokenSplitter.getTokenArray()
        self.posTagger.posTagging(tokens)
        hists = calcHist(tokens)
        self.dictionaries["VERB"] += hists["VERB"] 
        self.dictionaries["NOUN"] += hists["NOUN"] 
        self.totalWords["VERB"] += len(list(hists["VERB"].elements()))
        self.totalWords["NOUN"] += len(list(hists["NOUN"].elements()))
        for f in hists["VERB"]: 
            if not self.idfData.get(f):
                self.idfData[f] = Counter()            
            self.idfData[f]+=hists["VERB"][f]
        for f in hists["NOUN"]: 
            if not self.idfData.get(f):
                self.idfData[f] = Counter()            
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

class POSListIndex(WikiFileIndex):
    def __init__(self, wikiAccessor,prefix):
        super(POSListIndex, self).__init__(wikiAccessor,prefix)
    
    def getDictionaryFiles(self): 
        return ['hists','tfidf','tf','tfAll']
    
    def getUniqueNounsCount(self):
        wordDict = self.dictionaries['hists']['NOUN']
        unoqueCount = len(list(wordDict.values()))
        return unoqueCount
    def getTotalNounsCount(self):
        wordDict = self.dictionaries['hists']['NOUN']
        fullCount = sum(list(wordDict.values()))
        return fullCount
    def getFunctionalNouns(self, part):
        wordDict = self.dictionaries['hists']['NOUN']
        fullCount = sum(list(wordDict.values()))
        count = 0
        goodWords = []
        for word in sorted(wordDict, key=wordDict.get, reverse=True):
            if count > part*fullCount:
                break
            count += wordDict[word]
            goodWords.append(word)
        return goodWords
    def getKeyNouns(self, part = 0.3):
        wordDict = self.dictionaries['hists']['NOUN']
        tfidfDict = self.dictionaries['tfidf']['NOUN']
        tfAll = self.dictionaries['tf']['NOUN']
        fullCount = sum(list(wordDict.values()))
        count = 0
        goodWords = []
        for word in sorted(wordDict, key=wordDict.get, reverse=True):
            if count > part*fullCount:
                break
            count += wordDict[word]
            goodWords.append(word)
        return goodWords
        
    def getKeyVerbs(self, weight, part):
        wordDict = self.dictionaries['hists']['VERB']
        tfidfDict = self.dictionaries['tfidf']['VERB']
        tfAll = self.dictionaries['tf']['VERB']
        fullCount = sum(list(wordDict.values()))
        count = 0
        goodWords = []
        for word in sorted(wordDict, key=wordDict.get, reverse=True):
            if count > part*fullCount:
                break
            count += wordDict[word]
            goodWords.append(word)
        return goodWords
    def getMostFreqVerbs(self, part):
        wordDict = self.dictionaries['hists']['VERB']
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
        return self.dictionaries['hists']['VERB']
    def getKeyNounsAsDict(self,fType):
        return self.dictionaries['hists']['NOUN']
    def getFunctionalTypes(self):
        return list(self.dictionaries['hists'].keys())
    def getBuilder(self):
        return POSListBuilder(self.accessor,self.prefix)
    def getName(self):
        return "pos_list_all"
                
class СollocationBuilder(WikiIterator):
    
    def __init__(self, accessor, indexPrefix):
        super(СollocationBuilder, self).__init__(accessor, indexPrefix)
        self.redirects = self.accessor.getIndex(RedirectsIndex) 
        self.doctypeIndex = DocumentTypeIndex(self.accessor)
        self.posListIndex = POSListIndex(accessor, indexPrefix)
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
                        'freq':self.totalCounts[fragment]/self.totalLen,
                        'grammar':fragment.genGrammar(),
                    })
        with open(self.accessor.directory+self.prefix + 'collocations_full.pcl', 'wb') as f:
            pickle.dump(grammars, f, pickle.HIGHEST_PROTOCOL)        

    def processDocument(self, docId):
        if self.redirects.isRedirect(docId):
            return
        if self.doctypeIndex.isDocType(docId,'wiki_stuff'):
            return
        text = self.wikiIndex.getTextArticleById(docId)
        self.tokenSplitter.split(text)
        tokens = self.tokenSplitter.getTokenArray() 
        self.posTagger.posTagging(tokens)
        self.flMatcher.combineTokens(tokens)
        self.defisWordsBuilder.combineTokens(tokens)
        fragmentStart = -1
        fragmentEnd = -1
        self.fragmentLen += len(tokens)
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
    

                
from pywikiaccessor.wiki_plain_text_index import WikiPlainTextIndex

class StatBuilder(WikiIterator):
    
    def __init__(self, accessor, indexPrefix):
        super(StatBuilder, self).__init__(accessor, indexPrefix)
    
    def preProcess(self):
        self.fragments = []
        self.relativeStat = []
        self.docStats = {}
        self.plainTextIndex = WikiPlainTextIndex(self.accessor)

    def postProcess(self):
        with open(self.accessor.directory+self.prefix + 'stat_full.pcl', 'wb') as f:
            pickle.dump(self.fragments, f, pickle.HIGHEST_PROTOCOL)
        with open(self.accessor.directory+self.prefix + 'relativeStat_full.pcl', 'wb') as f:
            pickle.dump(self.relativeStat, f, pickle.HIGHEST_PROTOCOL)

    def __getStat(self,text):
        ts = TextStat(self.accessor.directory,text = text,clearWrap = False)
        rawStat = ts.buildPOSStat()
        for key in rawStat:
            rawStat[key] = rawStat[key][0] 
        stat = normalizeSum(rawStat,["DOTS","COMMAS","NOUNS","VERBS","ADJS","FUNC"])
        return stat
    def processDocument(self, docId):
        if self.redirects.isRedirect(docId):
            return
        if self.doctypeIndex.isDocType(docId,'wiki_stuff'):
            return
        text = self.wikiIndex.getTextArticleById(docId)
        stat = self.__getStat(text)
        self.fragments.append(stat)
        if not self.docStats.get(docId,None):
            docText = self.plainTextIndex.getTextById(docId)
            self.docStats[docId] = self.__getStat(docText)
        relativeStat = {k: float(stat[k])/self.docStats[docId][k] if self.docStats[docId][k] != 0 else 0 for k in stat}
        self.relativeStat.append(relativeStat)
                                
    def print(self):
        keys = TEXT_STAT_KEYS
        stat = np.empty((len(self.fragments),len(self.fragments[0])),dtype=np.float) 
        for row in range(len(self.fragments)):
            col = 0
            for key in keys:
                stat[row][col] = self.fragments[row][key]
                col+=1
        means = np.mean(stat, axis=0)        
        variances = np.var(stat, axis=0)        
        print (means)
        print (variances)             

class CollocationGrammars(WikiFileIndex):
    def __init__(self, wikiAccessor,prefix):
        super(CollocationGrammars, self).__init__(wikiAccessor,prefix)
    
    def getDictionaryFiles(self): 
        return ['collocations']

    def getGrammars(self,border=None):
        res = []
        
        patternList = self.dictionaries['collocations']
        if border: 
            i = 0
            while i < len(patternList):
                if patternList[i]['freq'] < border:
                    break
                i+=1
            res = res + patternList[:i]
        else:
            res = res + patternList
        return res
        
    def getFunctionalTypes(self):
        return list(self.dictionaries['collocations'].keys())
    def getBuilder(self):
        return СollocationBuilder(self.accessor,self.prefix)
    def getName(self):
        return "collocatoin_grammars"

def getArticles(categories,stopCategories,stopDocTypes,accessor):
    categoryIndex = accessor.getIndex(CategoryIndex)
    titleIndex = accessor.getIndex(TitleIndex)
    documentTypes = accessor.getIndex(DocumentTypeIndex)        
    
    stopCatsSet = set() 
    for cat in stopCategories:
        stopCatsSet.add(categoryIndex.getIdByTitle(cat))
        
    pages = set()
    for cat in categories:
        categoryId = categoryIndex.getIdByTitle(cat)
        catPages = categoryIndex.getAllPagesAsSet(categoryId, stopCatsSet)
        pages.update(catPages)
    
    stopDocTypesToCheck = list(stopDocTypes)
    stopDocTypesToCheck.append('category')
    stopDocTypesToCheck.append('template')    
    stopDocTypesToCheck.append('file')
    stopDocTypesToCheck.append('redirect')
    
    with codecs.open( accessor.directory+'titles.txt', 'w', 'utf-8' ) as f:
        for p in list(pages):
            if (documentTypes.haveDocType(p,stopDocTypesToCheck)):
                pages.discard(p)                
            else:
                # print(titleIndex.getTitleById(p))
               if titleIndex.getTitleById(p) is not None:
                   f.write(titleIndex.getTitleById(p)+'\n')
        f.close()
    return pages
    
def buildHeaders (categories,prefix,stopCategories=[],stopDocTypes=[]):
    directory = "C:/WORK/science/python-data/"
    accessor =  WikiConfiguration(directory)
    pages = getArticles(categories,stopCategories,stopDocTypes,accessor)
    print(len(pages))    
    hb = HeadersFileBuilder(accessor,list(pages),prefix) 
    hb.build()
    hi = HeadersFileIndex(accessor,prefix)
    stat = hi.getAllStat()
    with codecs.open( directory+'headers.txt', 'w', 'utf-8' ) as f:
        for item in stat:
            if item['cnt'] == 1:
                break
            print (item['text']+": "+str(item['cnt']))
            f.write(item['text']+": "+str(item['cnt'])+'\n')
        f.close()

def buildStat (prefix):
    directory = "C:/WORK/science/python-data/"
    accessor =  WikiConfiguration(directory)
    sb = StatBuilder(accessor,prefix)
    sb.build()
    sb.print()

def buildPOSList (prefix):
    directory = "C:/WORK/science/python-data/"
    accessor =  WikiConfiguration(directory)
    sb = POSListBuilder(accessor,prefix)
    sb.build()
    sb.printTfIdf()

def getStat():
    directory = "C:/WORK/science/python-data/"
    accessor =  WikiConfiguration(directory)
    bi = WikiBaseIndex(accessor)
    print('Articles in Wikipedia:' + str(bi.getCount()))
    pages = getArticles(['Математика','Информатика','Физика'],accessor)
    print('Articles in Subset:' + str(len(pages)))

def getStatByNouns():
    directory = "C:/WORK/science/python-data/"
    accessor =  WikiConfiguration(directory)
    pi = POSListIndex(accessor,'miph_')
    for fType in pi.getFunctionalTypes():
        print (fType)
        print("Total nouns: "+str(pi.getTotalNounsCount(fType)))
        print("Total nouns: "+str(pi.getUniqueNounsCount(fType)))
        print("Good nouns count: "+str(len(pi.getFunctionalNouns(fType, 0.5))))
        
    
if __name__ =="__main__":
    dTypes = ['person','location','entertainment','organization','event','device','substance']

    #buildHeaders(['Математика','Информатика','Физика'],'miph_'["Символы"],dTypes)
    buildHeaders(['Медицина'],'med_', [],dTypes)
    #buildPOSList ('miph_')
    #buildFragments('miph_')
    #getStatByNouns()
    #buildStat('miph_')
    '''
    directory = "C:/WORK/science/python-data/"
    accessor =  WikiConfiguration(directory)
    grammars = CollocationGrammars(accessor,'miph_')
    ftypes = grammars.getFunctionalTypes()
    collSets = {}
    for ftype in ftypes:
        collSets[ftype] = set() 
        coll = grammars.getGrammars(ftype)
        for c in coll:
            collSets[ftype].add(c['name'])
    totalIntersect = collSets["definition"]
    for type1 in ftypes:
        totalIntersect = totalIntersect.intersection(collSets[type1])
        for type2 in ftypes:         
            if (type1 != type2):
                intersect = collSets[type1].intersection(collSets[type2])
                intersectSize = len(intersect)
                print (type1+"\t"+type2+"\t"+str(intersectSize))
                print (str(intersectSize/len(collSets[type1]))+"\t"+str(intersectSize/len(collSets[type2]))+"\t")
                #for a in intersect: 
                #    print (a)
    print(len(totalIntersect))
    collection = {}
    
    #for a in totalIntersect: 
        #print (a)
    for type1 in ftypes:
        coll = grammars.getGrammars(type1)
        for c in coll:
            if c['name'] in totalIntersect:
                if not (c['name'] in collection):
                    collection[c['name']] = {}
                collection[c['name']][type1] = c['freq']
    for a in totalIntersect: 
        print (a)
        for type1 in ftypes:
            print (type1+"\t"+str(collection[a][type1]))
    '''        
'''
directory = "C:\\WORK\\science\\onpositive_data\\python\\"
accessor =  WikiAccessor(directory)
text = "быть или не быть - вот в чем вопрос когда-то был"
tokens = TokenSplitter().split(text)
FormalLanguagesMatcher().combineTokens(tokens)
DefisWordsBuilder().combineTokens(tokens)
POSTagger().posTagging(tokens)

f = Fragment(tokens)
print(f.genGrammar())

cg = CollocationGrammars(accessor,'math_')
for fType in cg.getFunctionalTypes():
    for gr in cg.getGrammars(fType, 1000):
        print (str(gr['name']))
'''

#pli = FTypePOSListIndex(accessor,'math_')
#for fType in pli.getFunctionalTypes(): 
#    print(fType)
#    goodWords = pli.getKeyNouns(fType)
#    print('\tKey nouns')
#    for word in goodWords:
#        print("\t\t"+word)
    #goodWords = pli.getFunctionalNouns(fType, 0.5)
    #print('\tFunctional nouns')
    #for word in goodWords:
    #    print("\t\t"+word)
    #goodWords = pli.getKeyVerbs(fType, 1.2,0.5)
    #goodWords = pli.getMostFreqVerbs(fType,0.5)
    #print('\tKey verbs')
    #for word in goodWords:
    #    print("\t\t"+word)
