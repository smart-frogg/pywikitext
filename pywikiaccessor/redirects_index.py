# -*- coding: utf-8 -*-
import pickle
import re

from pywikiaccessor import wiki_iterator, wiki_file_index
from pywikiaccessor.one_opened import OneOpened

class RedirectPageFabric:
    @staticmethod
    def createRedirectPage(toId, anchor):
        return {"toId" : toId, "anchor" : anchor}

class RedirectsIndex (wiki_file_index.WikiFileIndex): 
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
    
class RedirectsIndexBuilder (wiki_iterator.WikiIterator):
    
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

#simpleRedirect = re.compile('\#REDIRECT([^\[])*\[\[([^\]]+)\]\]', re.VERBOSE)    
#complexRedirect = re.compile('\#REDIRECT([^\[])\[\[([^\]\#]+)\#([^\]]+)\]\]', re.VERBOSE)         
#text = "#REDIRECT [[Вергилий]]" #"#REDIRECT [[Вергилий]]"
#res = complexRedirect.match(text)
#print(str(res.groups()))
#res = simpleRedirect.match(text)
#print(str(res.groups()))

#directory = "C:\\WORK\\science\\onpositive_data\\python\\"
#builder = RedirectsIndexBuilder(directory)
#builder.build()
#titleIndex = TitleIndex.TitleIndex(directory)
#index = RedirectsIndex(directory)
#print(titleIndex.getTitleById(0))
#print(builder.wikiIndex.getTextArticleById(0))
#print(str(index.isRedirect(0)))
#for docId in index.getRedirectsIds():
#    print(str(titleIndex.getTitleById(docId))+": "+str(titleIndex.getTitleById(index.getRedirect(docId).toId)))
