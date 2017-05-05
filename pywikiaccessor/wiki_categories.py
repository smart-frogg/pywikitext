# -*- coding: utf-8 -*-
import pickle
import re

from pywikiaccessor import wiki_iterator, wiki_file_index

class CategoryIndex (wiki_file_index.WikiFileIndex):
    def __init__(self, wikiAccessor):
        super(CategoryIndex, self).__init__(wikiAccessor)

    def getDictionaryFiles(self): 
        return [
            'cat_TitleToIdIndex',
            'cat_IdToTitleIndex',
            'cat_IdToChildrenIndex',
            'cat_IdToParentIndex',
            'cat_IdToPagesIndex',
            'cat_PagesToCatIndex']
                        
    def getTitleById(self, ident):
        if len(self.dictionaries['cat_IdToTitleIndex']) <= ident:
            return None
        return self.dictionaries['cat_IdToTitleIndex'][ident]
    
    def getIdByTitle(self, title):
        key = title.lower().replace("_"," ")
        return self.dictionaries['cat_TitleToIdIndex'].get(key, None)
    
    def getSubCatAsSet(self,catId):
        res = set()
        subCats = self.dictionaries['cat_IdToChildrenIndex'][catId]
        res.update(subCats)
        for cat in subCats:
            res.update(self.getSubCatAsSet(cat))
        return res    
    def getPageDirectCategories(self,docId):
        return self.dictionaries['cat_PagesToCatIndex'].get(docId,[])    
    def getBuilder(self):
        return CategoryIndexBuilder(self.accessor)
    def getName(self):
        return "categories"

class CategoryIndexBuilder (wiki_iterator.WikiIterator):
    def __init__(self, directory):
        self.CODE = 'utf-8'
        super(CategoryIndexBuilder, self).__init__(directory, 1000000)

    def processSave(self,articlesCount):
        return

    def postProcess(self):
        with open(self.accessor.directory + 'cat_TitleToIdIndex.pcl', 'wb') as f:
            pickle.dump(self.toIdDict, f, pickle.HIGHEST_PROTOCOL)
        with open(self.accessor.directory + 'cat_IdToTitleIndex.pcl', 'wb') as f:
            pickle.dump(self.toTitleDict, f, pickle.HIGHEST_PROTOCOL)
        with open(self.accessor.directory + 'cat_IdToChildrenIndex.pcl', 'wb') as f:
            pickle.dump(self.toChildrenDict, f, pickle.HIGHEST_PROTOCOL)
        with open(self.accessor.directory + 'cat_IdToParentIndex.pcl', 'wb') as f:
            pickle.dump(self.toParentDict, f, pickle.HIGHEST_PROTOCOL)
        with open(self.accessor.directory + 'cat_IdToPagesIndex.pcl', 'wb') as f:
            pickle.dump(self.toPagesDict, f, pickle.HIGHEST_PROTOCOL)
        with open(self.accessor.directory + 'cat_PagesToCatIndex.pcl', 'wb') as f:
            pickle.dump(self.toPageCatDict, f, pickle.HIGHEST_PROTOCOL)
        pass

    def preProcess(self):
        self.toTitleDict = []
        self.toIdDict = {}
        self.toParentDict = []
        self.toChildrenDict = []
        self.toPagesDict = []
        self.toPageCatDict = {}
        self.categoryPattern = re.compile("\[\[[ \t]*категория:([^\]\|]*)\]\]")
            
    def clear(self):
        return 

    def getOrAdd(self,title):
        clearTitle = title.lower().replace("_"," ")
        catId = self.toIdDict.get(clearTitle,None)
        if not catId:
            catId = len(self.toIdDict)
            self.toIdDict[clearTitle] = catId
            self.toTitleDict.append(clearTitle)
            self.toParentDict.append([])
            self.toChildrenDict.append([])
            self.toPagesDict.append([])
        return catId 
          
    def processDocument(self, docId):
        title = self.wikiIndex.getTitleArticleById(docId).lower()
        catId = None
        if title.startswith("категория:"):
            catId = self.getOrAdd(title[10:])
            
        text = self.wikiIndex.getTextArticleById(docId).lower()
        
        for match in self.categoryPattern.finditer(text):
            if not self.toPageCatDict.get(docId,None):
                self.toPageCatDict[docId] = []
            parentCatId = self.getOrAdd(match.group(1))
            if catId:
                self.toParentDict[catId].append(parentCatId)
                self.toChildrenDict[parentCatId].append(catId)
            self.toPagesDict[parentCatId].append(docId)
            self.toPageCatDict[docId].append(parentCatId)
            
from pywikiaccessor import wiki_accessor
directory = "C:\\WORK\\science\\onpositive_data\\python\\"
accessor =  wiki_accessor.WikiAccessorFactory.getAccessor(directory)
titleIndex = accessor.titleIndex
docId = titleIndex.getIdByTitle('Категория:Разделы биологии')
bld = CategoryIndexBuilder(accessor)
bld.preProcess()
bld.processDocument(docId)
print(bld.toPagesDict)
print(bld.toTitleDict)
#bld.build()

