# -*- coding: utf-8 -*-
import codecs
import xml.sax  
from pywikiaccessor.one_opened import OneOpened 

class WikiConfiguration(metaclass=OneOpened):
    def __init__(self, directory):
        self.directory = directory
        self.__indexes = {}
    def getIndex(self, indexClass):
        index = self.__indexes.get(indexClass,None)
        if not index:
            self.__indexes[indexClass] = indexClass(self)
        return self.__indexes.get(indexClass,None)    

from abc import abstractmethod
import os
import pickle

class WikiFileIndex(metaclass= OneOpened):
    def __init__(self, wikiAccessor, prefix=''):
        self.accessor = wikiAccessor
        self.prefix = prefix
        self.directory = wikiAccessor.directory
        self.dictionaries = {}
        self.loadOrBuild()
        
    def loadOrBuild(self):
        consistent = True
        for file in self.getDictionaryFiles():
            consistent = consistent and os.path.exists(self.getFullFileName(file)+".pcl")
        for file in self.getOtherFiles():
            consistent = consistent and os.path.exists(self.getFullFileName(file))
        if not consistent:   
            builder = self.getBuilder()
            builder.build()    
        for file in self.getDictionaryFiles():
            with open(self.getFullFileName(file)+".pcl", 'rb') as f:
                self.dictionaries[file] = pickle.load(f)
                f.close()
        self.loadOtherFiles()        
                       
    def getDictionaryFiles(self):    
        return []
    
    def getOtherFiles(self):    
        return []
    
    def loadOtherFiles(self):    
        pass

    def clear(self):
        for file in self.getDictionaryFiles():
            os.remove(self.directory + file + ".pcl")
        for file in self.getOtherFiles():
            os.remove(self.directory + file)
    def getFullFileName(self,fileName):
        return self.accessor.directory + self.prefix + fileName 
    
    @abstractmethod
    def getBuilder(self):
        pass
    
    @abstractmethod
    def getName(self):
        pass   
        
class WikiBaseIndex (WikiFileIndex):
    def __init__(self, configuration):
        super(WikiBaseIndex, self).__init__(configuration)
        self.textDict = self.dictionaries['textIndex']
    
    def getDictionaryFiles(self): 
        return ['textIndex']
    def getOtherFiles(self):    
        return ["text.dat"]
    
    def loadOtherFiles(self):    
        self.textFile = open(self.directory+"text.dat", 'rb')
                                
    def getBuilder(self):
        from os import listdir
        from os.path import isfile, join
        onlyfiles = [f for f in listdir(self.directory) 
                     if isfile(join(self.directory, f)) 
                        and f.endswith("-pages-articles-multistream.xml")]
        return WikiBaseIndexBuilder(self.directory,onlyfiles[0])
    def getName(self):
        return "base"
    def getTextArticleById(self, ident):
        if not self.textDict.get(ident, None):
            return None
        else:
            self.textFile.seek(self.textDict[ident],0)
            lenBytes = self.textFile.read(4)
            length = int.from_bytes(lenBytes, byteorder='big')
            return self.textFile.read(length).decode("utf-8") 
    def getCount(self):
        return len(self.textDict)
    def getIds(self):
        return list(self.textDict.keys()) 
    
class WikiTitleBaseIndex (WikiFileIndex):
    def __init__(self, wikiAccessor):
        super(WikiTitleBaseIndex, self).__init__(wikiAccessor)
        self.titleDict = self.dictionaries['title_RawTitleIndex']
    def getDictionaryFiles(self): 
        return ['title_RawTitleIndex']
    def getOtherFiles(self):    
        return []
    def loadOtherFiles(self):    
        pass
    def getBuilder(self):
        from os import listdir
        from os.path import isfile, join
        onlyfiles = [f for f in listdir(self.directory) if isfile(join(self.directory, f)) and f.startswith("articles") and f.endswith("articles")]
        return WikiBaseIndexBuilder(self.directory,onlyfiles[0])
    def getName(self):
        return "baseTitle"
    def getTitleArticleById(self, ident):
        return self.titleDict.get(ident, None) 
    def getCount(self):
        return len(self.textDict)
    def getIds(self):
        return list(self.textDict.keys())     

class WikiBaseIndexBuilder:     
    def __init__(self, directory,wikiDumpFile):
        self.directory = directory
        self.wikiDumpFile = wikiDumpFile       
    def build(self):
        inputXml = codecs.open(self.directory+self.wikiDumpFile, 'r', 'utf-8')
        from pywikiaccessor import xml_wiki_parser
        xml.sax.parse(inputXml, xml_wiki_parser.XMLWikiParser(self.directory)) 

 
           
class TitleIndex (WikiFileIndex):
    def __init__(self, wikiAccessor):
        self.CATEGORY_PATTERN = "категория:"
        super(TitleIndex, self).__init__(wikiAccessor)
        
    
    def getDictionaryFiles(self): 
        return ['title_IdToTitleIndex','title_TitleToIdIndex']
                        
    def getTitleById(self, ident):
        return self.dictionaries['title_IdToTitleIndex'].get(ident, None)
    
    def getIdByTitle(self, title):
        key = title.replace("_"," ")
        return self.dictionaries['title_TitleToIdIndex'].get(key, None)
    
    def findArticleId(self,title):
        res = self.getIdByTitle(title)
        if res == None:
            return self.getIdByTitle(self.CATEGORY_PATTERN+title)
        return res
    def isCategoryTitle(self,title):
        if self.getIdByTitle( self.CATEGORY_PATTERN+title):
            return True
        return False 
    def isCategory(self,docId):
        title = self.getTitleById(docId)
        if title.startswith(self.CATEGORY_PATTERN):
            return True
        return False 
      
    def getBuilder(self):
        return TitleIndexBuilder(self.accessor)
    def getName(self):
        return "titles"

from abc import ABCMeta, abstractmethod

class WikiIterator(metaclass=ABCMeta):
    def __init__(self, accessor, fileCount, docList = None, prefix = ''):
        self.accessor = accessor
        self.fileCount = fileCount
        self.docList = docList
        self.prefix = prefix
        self.wikiIndex = self.accessor.getIndex(WikiBaseIndex)

    def build (self, start=0):
        self.clear()
        self.preProcess()
        articlesCount = 0
        self.prevArticlesCount = 0;
        if self.docList:
            indexes = self.docList
        else:  
            indexes = self.wikiIndex.getIds()
        indexes = indexes[start:len(indexes)]
        print("Need to process "+str(len(indexes)) + " docs.")
        for i in indexes:
            articlesCount += 1
            self.processDocument(i)
            if (articlesCount % self.fileCount == 0):
                print("Processed "+str(articlesCount))
                self.save(articlesCount)
                self.clear() 
        print("Processed "+str(articlesCount))
        self.save(articlesCount)
        self.postProcess()
    
    def getFullFileName(self,fileName):
        return self.accessor.directory + self.prefix + fileName            
    def save(self,articlesCount): 
        self.processSave(articlesCount)
        self.prevArticlesCount = articlesCount 
        
    @abstractmethod
    def processSave(self,articlesCount):    
        pass
    @abstractmethod
    def preProcess(self):
        pass
    @abstractmethod
    def postProcess(self):
        pass
    @abstractmethod
    def clear(self):
        pass            
    @abstractmethod
    def processDocument(self, docId):
        pass            
             
class TitleIndexBuilder (WikiIterator):
    def __init__(self, directory):
        self.CODE = 'utf-8'
        super(TitleIndexBuilder, self).__init__(directory, 1000000)

    def processSave(self,articlesCount):
        return

    def postProcess(self):
        with open(self.getFullFileName('title_IdToTitleIndex.pcl'), 'wb') as f:
            pickle.dump(self.toTitleDict, f, pickle.HIGHEST_PROTOCOL)
        with open(self.getFullFileName('title_TitleToIdIndex.pcl'), 'wb') as f:
            pickle.dump(self.toIdDict, f, pickle.HIGHEST_PROTOCOL)

    def preProcess(self):
        self.toTitleDict = {}
        self.toIdDict = {}
        self.wikiTitleIndex = self.accessor.getIndex(WikiTitleBaseIndex)
            
    def clear(self):
        return 

    def processDocument(self, docId):
        title = self.wikiTitleIndex.getTitleArticleById(docId).replace("_"," ")  
        self.toTitleDict[docId] = title
        self.toIdDict[title] = docId
    
