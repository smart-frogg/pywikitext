# -*- coding: utf-8 -*-
import pickle
import re

from pywikiaccessor.wiki_core import WikiIterator, WikiFileIndex, WikiBaseIndex,WikiTitleBaseIndex,WikiConfiguration,TitleIndex
from pywikiaccessor.wiki_sql_loader import WikiSqlLoader

class CategoryIndex (WikiFileIndex):
    def __init__(self, wikiAccessor):
        super(CategoryIndex, self).__init__(wikiAccessor)

    def getDictionaryFiles(self): 
        return [
            'cat_TitleToIdIndex',
            'cat_IdToTitleIndex',
            'cat_IdToChildrenIndex',
            'cat_IdToParentIndex',
            'cat_IdToPagesIndex',
            'cat_PagesToCatIndex',
            'cat_CategoryPages']
                        
    def getTitleById(self, ident):
        if len(self.dictionaries['cat_IdToTitleIndex']) <= ident:
            return None
        return self.dictionaries['cat_IdToTitleIndex'][ident]
    
    def getIdByTitle(self, title):
        key = title.lower().replace("_"," ")
        return self.dictionaries['cat_TitleToIdIndex'].get(key, None)

    def getSubCatAsSet(self,catId,stopCatsSet=set()):
        res = set()
        return self._getSubCatAsSet(catId,res,stopCatsSet)
    def _getSubCatAsSet(self,catId,res,stopCatsSet=set()):   
        subCats = self.dictionaries['cat_IdToChildrenIndex'][catId]
        #res.update(subCats)
        for cat in subCats:
            if cat in res or cat == catId or cat in stopCatsSet:
                continue
            res.add(cat)
            print(str(self.getTitleById(cat)))
            res.update(self._getSubCatAsSet(cat,res))
        return res

    def getAllParentsAsSet(self,catId):
        res = set()
        parCats = self.dictionaries['cat_IdToParentIndex'][catId]
        #res.update(subCats)
        for cat in parCats:
            if cat in res or cat == catId:
                continue
            res.update(self.getAllParentsAsSet(cat))
        return res
    
    def getAllPagesAsSet(self,catId, stopCatsSet=set()):
        res = set()
        res.update(self.getDirectPages(catId))
        subCats = self.getSubCatAsSet(catId, stopCatsSet)
        for cat in subCats:
            if cat in stopCatsSet:
                continue
            res.update(self.getDirectPages(cat))
        return res      
    def getPageDirectCategories(self,docId):
        return self.dictionaries['cat_PagesToCatIndex'].get(docId,[])    
    def getDirectPages(self,catId):
        return self.dictionaries['cat_IdToPagesIndex'][catId]    
    def getBuilder(self):
        return CategoryIndexBuilder(self.accessor)
    def getName(self):
        return "categories"
    
class CategoryIndexBuilder:
    def __init__(self, accessor):
        self.fromPagesBuilder = CategoryFromPagesBuilder(accessor)
        self.fromCatlinksBuilder = CategoryFromCatlinksBuilder(accessor)
    def build(self):
        self.fromPagesBuilder.preProcess()
        self.fromPagesBuilder.build()
        self.fromCatlinksBuilder.build(self.fromPagesBuilder,True)
        
class CategoryFromCatlinksBuilder:
    def __init__(self, accessor):
        self.accessor = accessor
    def build(self, dictionaries = None, compact = False):
        wl = WikiSqlLoader()
        if dictionaries:
            self.toTitleDict = dictionaries.toTitleDict
            self.toIdDict = dictionaries.toIdDict
            self.toParentDict = dictionaries.toParentDict
            self.toChildrenDict = dictionaries.toChildrenDict
            self.toPagesDict = dictionaries.toPagesDict
            self.toPageCatDict = dictionaries.toPageCatDict
            self.catPagesRenumerer = dictionaries.catPagesRenumerer
            self.catCount = len(self.toTitleDict)
        else:
            self.toTitleDict = []
            self.toIdDict = {}
            self.toParentDict = []
            self.toChildrenDict = []
            self.toPagesDict = []
            self.toPageCatDict = {}
            self.catPagesRenumerer = {}
            self.catCount = 0
        self.count = 0
        wl.parse(self.accessor.directory+"categorylinks.sql",self)
        if (compact):
            saveCompactDictionaries(self)
        else:
            saveDictionaries(self)
    def getOrAdd(self,title):
        clearTitle = title.lower().replace("_"," ").replace("ё","е")
        catId = self.toIdDict.get(clearTitle,"None")
       
        if catId is "None":
            catId = self.catCount
            self.catCount+=1
            self.toIdDict[clearTitle] = catId
            self.toTitleDict.append(clearTitle)
            self.toParentDict.append([])
            self.toChildrenDict.append([])
            self.toPagesDict.append([])
        return catId     
    def consume(self,data):    
        docId = data[0]
        parentCatId = self.getOrAdd(data[1])
        if len(data)==7 and data[6] is 'subcat':
            catId = self.catPagesRenumerer.get(docId,"None")
            if catId is "None":
                self.toParentDict[catId].append(parentCatId)
                self.toChildrenDict[parentCatId].append(catId)
        elif len(data)==7 and data[6] is 'file':
            pass
        else:
            self.toPagesDict[parentCatId].append(docId)
            if not self.toPageCatDict.get(docId,None):
                self.toPageCatDict[docId] = []
            self.toPageCatDict[docId].append(parentCatId)
        self.count+=1
        if self.count%10000 == 0:
            print("Processed "+str(self.count)+" categories")        
    def getFullFileName(self,fileName):
        return self.accessor.directory + fileName     
        
def saveDictionaries(dictionaries):
    with open(dictionaries.getFullFileName('cat_TitleToIdIndex.pcl'), 'wb') as f:
        pickle.dump(dictionaries.toIdDict, f, pickle.HIGHEST_PROTOCOL)
    with open(dictionaries.getFullFileName('cat_IdToTitleIndex.pcl'), 'wb') as f:
        pickle.dump(dictionaries.toTitleDict, f, pickle.HIGHEST_PROTOCOL)
    with open(dictionaries.getFullFileName('cat_IdToChildrenIndex.pcl'), 'wb') as f:
        pickle.dump(dictionaries.toChildrenDict, f, pickle.HIGHEST_PROTOCOL)
    with open(dictionaries.getFullFileName('cat_IdToParentIndex.pcl'), 'wb') as f:
        pickle.dump(dictionaries.toParentDict, f, pickle.HIGHEST_PROTOCOL)
    with open(dictionaries.getFullFileName('cat_IdToPagesIndex.pcl'), 'wb') as f:
        pickle.dump(dictionaries.toPagesDict, f, pickle.HIGHEST_PROTOCOL)
    with open(dictionaries.getFullFileName('cat_PagesToCatIndex.pcl'), 'wb') as f:
        pickle.dump(dictionaries.toPageCatDict, f, pickle.HIGHEST_PROTOCOL)

def makeCompact(listOfListDictionaty):
    for i in range(0, len(listOfListDictionaty)):
        listOfListDictionaty[i] = tuple(listOfListDictionaty[i]) 
    return tuple(listOfListDictionaty)      
            
def saveCompactDictionaries(dictionaries):
    dictionaries.toParentDict = makeCompact(dictionaries.toParentDict)
    dictionaries.toChildrenDict = makeCompact(dictionaries.toChildrenDict)
    dictionaries.toPagesDict = makeCompact(dictionaries.toPagesDict)
    saveDictionaries(dictionaries);        
                
class CategoryFromPagesBuilder (WikiIterator):
    def __init__(self, accessor):
        self.CODE = 'utf-8'
        super(CategoryFromPagesBuilder, self).__init__(accessor, 100000)

    def processSave(self,articlesCount):
        return

    def postProcess(self):
        saveDictionaries(self)
        with open(self.getFullFileName('cat_CategoryPages.pcl'), 'wb') as f:
            pickle.dump(self.catPagesRenumerer, f, pickle.HIGHEST_PROTOCOL)

    def preProcess(self):
        self.toTitleDict = []
        self.toIdDict = {}
        self.toParentDict = []
        self.toChildrenDict = []
        self.toPagesDict = []
        self.toPageCatDict = {}
        self.catPagesRenumerer = {}
        self.catCount = 0
        self.categoryPattern = re.compile("\[\[[ \t]*категория:([^\]\|]*)(\|.*)?\]\]")
        self.titleIndex = self.accessor.getIndex(WikiTitleBaseIndex)
            
    def clear(self):
        return 

    def getOrAdd(self,title):
        clearTitle = title.lower().replace("_"," ")
        catId = self.toIdDict.get(clearTitle,"None")
        if catId is "None":
            catId = self.catCount
            self.catCount+=1
            self.toIdDict[clearTitle] = catId
            self.toTitleDict.append(clearTitle)
            self.toParentDict.append([])
            self.toChildrenDict.append([])
            self.toPagesDict.append([])
        return catId 
          
    def processDocument(self, docId):
        title = self.titleIndex.getTitleArticleById(docId).lower()
        catId = None
        if title.startswith("категория:"):
            catId = self.getOrAdd(title[10:])
            self.catPagesRenumerer[docId] = catId
            
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
            
#directory = "C:/WORK/science/python-data/"
#accessor = WikiConfiguration(directory)
#titleIndex = accessor.getIndex(TitleIndex)
#docId = titleIndex.getIdByTitle("Категория:Фильмы по первоисточникам для сценария")
#bld = CategoryIndexBuilder(accessor)
#bld = CategoryFromPagesBuilder(accessor)
#bld.preProcess()
#bld.processDocument(docId)
#print(bld.toPagesDict)
#print(bld.toTitleDict)
#bld.build()

#ci = CategoryIndex(accessor)
#print(ci.dictionaries['cat_IdToTitleIndex'][ci.dictionaries['cat_TitleToIdIndex']["изображения:введенское кладбище"]])

#titles = set()
#for c in range(len(ci.dictionaries['cat_IdToTitleIndex'])):
#    if ci.dictionaries['cat_IdToTitleIndex'][c] in titles:
#        print (c)
#        print (ci.dictionaries['cat_IdToTitleIndex'][c])
#    titles.add(ci.dictionaries['cat_IdToTitleIndex'][c])
    

#cid = ci.getIdByTitle("Фильмы")
#subcats = ci.getSubCatAsSet(cid)
#for sc in subcats:
#    print(ci.getTitleById(sc)) 

#print('------------')

#cid = ci.getIdByTitle("актёры озвучивания по алфавиту")
#print(cid)
#subcats = ci.getAllParentsAsSet(cid)
#for sc in subcats:
#    print(ci.getTitleById(sc)) 
#print('------------')
#cid = ci.getIdByTitle("родившиеся в теколотлане")
#print(cid)
#pids = ci.getAllParentsAsSet(cid)
#for sc in pids:
#    print(ci.getTitleById(sc))

 
