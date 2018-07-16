# -*- coding: utf-8 -*-
from pytextutils.token_splitter import TokenSplitter, POSTagger, TYPE_SIGN, TYPE_COMPLEX_TOKEN
from pytextutils.grammar_base import FormalLanguagesMatcher 
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

from abc import ABCMeta, abstractmethod
            
class AbstractFragmentIterator(metaclass=ABCMeta): 
    def __init__(self, accessor, headerIndexPrefix):
        self.accessor = accessor
        self.headerIndex = HeadersFileIndex(accessor,headerIndexPrefix)
        self.prefix = headerIndexPrefix
        self.tokenSplitter = TokenSplitter()
        self.posTagger = POSTagger()
        FragmentConfig(accessor.directory)

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
        for fType in FragmentConfig.fragmentTypesToHeaders.keys():
            print("Process "+fType+". Need to process "+str(len(FragmentConfig.fragmentTypesToHeaders[fType]))+" unique headers.")
            self.processFragmentStart(fType)
            docCount = 0
            for header in FragmentConfig.fragmentTypesToHeaders[fType]:
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
    
class СollocationBuilder(AbstractFragmentIterator):
    
    def __init__(self, accessor, indexPrefix):
        super(СollocationBuilder, self).__init__(accessor, indexPrefix)
        self.posListIndex = POSListIndex(accessor, indexPrefix)
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
from pywikiaccessor.wiki_plain_text_index import WikiPlainTextIndex

class StatBuilder(AbstractFragmentIterator):
    
    def __init__(self, accessor, indexPrefix):
        super(StatBuilder, self).__init__(accessor, indexPrefix)
    
    def preProcess(self):
        self.fragments = {}
        self.relativeStat = {}
        self.docStats = {}
        self.plainTextIndex = WikiPlainTextIndex(self.accessor)

    def postProcess(self):
        with open(self.accessor.directory+self.prefix + 'stat.pcl', 'wb') as f:
            pickle.dump(self.fragments, f, pickle.HIGHEST_PROTOCOL)
        with open(self.accessor.directory+self.prefix + 'relativeStat.pcl', 'wb') as f:
            pickle.dump(self.relativeStat, f, pickle.HIGHEST_PROTOCOL)

    def processFragmentStart(self, fType):    
        self.fragments[fType] = []
        self.relativeStat[fType] = []
        
    def processFragmentEnd(self, fType):    
        pass
    
    def __getStat(self,text):
        ts = TextStat(self.accessor.directory,text = text,clearWrap = False)
        rawStat = ts.buildPOSStat()
        for key in rawStat:
            rawStat[key] = rawStat[key][0] 
        stat = normalizeSum(rawStat,["DOTS","COMMAS","NOUNS","VERBS","ADJS","FUNC"])
        return stat
    def processDocument(self, fType, headerId, docId):
        text = self.headerIndex.getDocSection(docId, headerId)
        stat = self.__getStat(text)
        self.fragments[fType].append(stat)
        if not self.docStats.get(docId,None):
            docText = self.plainTextIndex.getTextById(docId)
            self.docStats[docId] = self.__getStat(docText)
        relativeStat = {k: float(stat[k])/self.docStats[docId][k] if self.docStats[docId][k] != 0 else 0 for k in stat}
        self.relativeStat[fType].append(relativeStat)
                                
    def print(self):
        keys = TEXT_STAT_KEYS
        for fType in self.fragments:
            print(fType)
            stat = np.empty((len(self.fragments[fType]),len(self.fragments[fType][0])),dtype=np.float) 
            for row in range(len(self.fragments[fType])):
                col = 0
                for key in keys:
                    stat[row][col] = self.fragments[fType][row][key]
                    col+=1
            means = np.mean(stat, axis=0)        
            variances = np.var(stat, axis=0)        
            print (means)
            print (variances)

       
             
class POSListBuilder(AbstractFragmentIterator):
    
    def __init__(self, accessor, indexPrefix):
        super(POSListBuilder, self).__init__(accessor, indexPrefix)
    
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

class POSListIndex(WikiFileIndex):
    def __init__(self, wikiAccessor,prefix):
        super(POSListIndex, self).__init__(wikiAccessor,prefix)
    
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
        return POSListBuilder(self.accessor,self.prefix)
    def getName(self):
        return "pos_list"

class CollocationGrammars(WikiFileIndex):
    def __init__(self, wikiAccessor,prefix):
        super(CollocationGrammars, self).__init__(wikiAccessor,prefix)
    
    def getDictionaryFiles(self): 
        return ['collocations']
    
    def getGrammars(self,fType,count = None,border=None):
        if count:
            return self.dictionaries['collocations'][fType][:count]
        if border:
            i = 0
            while i < len(self.dictionaries['collocations'][fType]):
                if self.dictionaries['collocations'][fType][i]['freq'] < border:
                    break
                i+=1
            return self.dictionaries['collocations'][fType][:i]
        return self.dictionaries['collocations'][fType]
    def getFunctionalTypes(self):
        return list(self.dictionaries['collocations'].keys())
    def getBuilder(self):
        return СollocationBuilder(self.accessor,self.prefix)
    def getName(self):
        return "collocatoin_grammars"

def getArticles(categories,stopCategories,accessor):
    categoryIndex = accessor.getIndex(CategoryIndex)
    titleIndex = accessor.getIndex(TitleIndex)
    documentTypes = accessor.getIndex(DocumentTypeIndex)        
    
    stopCatsSet = set() 
    for cat in categories:
        stopCatsSet.add(categoryIndex.getIdByTitle(cat))
        
    pages = set()
    for cat in categories:
        categoryId = categoryIndex.getIdByTitle(cat)
        catPages = categoryIndex.getAllPagesAsSet(categoryId, stopCatsSet)
        pages.update(catPages)
    with codecs.open( accessor.directory+'titles.txt', 'w', 'utf-8' ) as f:
        for p in list(pages):
            if (documentTypes.isDocType(p,'person') or 
                documentTypes.isDocType(p,'location') or
                documentTypes.isDocType(p,'template') or  
                documentTypes.isDocType(p,'entertainment') or 
                documentTypes.isDocType(p,'organization') or 
                documentTypes.isDocType(p,'event') or 
                documentTypes.isDocType(p,'category') or 
                documentTypes.isDocType(p,'device') or
                documentTypes.isDocType(p,'redirect') or
                documentTypes.isDocType(p,'file') or    
                documentTypes.isDocType(p,'substance')):
                pages.discard(p)
            else:
                # print(titleIndex.getTitleById(p))
                f.write(titleIndex.getTitleById(p)+'\n')
        f.close()
    return pages
    
def buildHeaders (categories,stopCategories,prefix):
    directory = "C:/WORK/science/python-data/"
    accessor =  WikiConfiguration(directory)
    pages = getArticles(categories,stopCategories,accessor)
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

def buildFragments (prefix):
    directory = "C:/WORK/science/python-data/"
    accessor =  WikiConfiguration(directory)
    fb = СollocationBuilder(accessor,prefix)
    fb.build()
    fb.printFragments(True)

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
    buildHeaders(['Математика','Информатика','Физика'],["Символы"],'miph_')
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

#pli = POSListIndex(accessor,'math_')
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
