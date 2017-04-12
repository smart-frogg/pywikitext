# -*- coding: utf-8 -*-
import pickle

from pywikiaccessor import wiki_iterator, wiki_file_index

class TitleIndex (wiki_file_index.WikiFileIndex):
    def __init__(self, wikiAccessor):
        super(TitleIndex, self).__init__(wikiAccessor)
    
    def getDictionaryFiles(self): 
        return ['IdToTitleIndex','TitleToIdIndex']
                        
    def getTitleById(self, ident):
        return self.dictionaries['IdToTitleIndex'].get(ident, None)
    
    def getIdByTitle(self, title):
        key = title.lower().replace("_"," ")
        return self.dictionaries['TitleToIdIndex'].get(key, None)
    
    def getBuilder(self):
        return TitleIndexBuilder(self.directory)
    def getName(self):
        return "titles"

class TitleIndexBuilder (wiki_iterator.WikiIterator):
    def __init__(self, directory):
        self.CODE = 'utf-8'
        super(TitleIndexBuilder, self).__init__(directory, 1000000)

    def processSave(self,articlesCount):
        return

    def postProcess(self):
        with open(self.directory + 'IdToTitleIndex.pcl', 'wb') as f:
            pickle.dump(self.toTitleDict, f, pickle.HIGHEST_PROTOCOL)
        with open(self.directory + 'TitleToIdIndex.pcl', 'wb') as f:
            pickle.dump(self.toIdDict, f, pickle.HIGHEST_PROTOCOL)

    def preProcess(self):
        self.toTitleDict = {}
        self.toIdDict = {}
               
    def clear(self):
        return 

    def processDocument(self, docId):
        title = self.wikiIndex.getTitleArticleById(docId).lower().replace("_"," ")  
        if "гражданская" in title:
            print(title)
        self.toTitleDict[docId] = title
        self.toIdDict[title] = docId

#directory = "C:\\WORK\\science\\onpositive_data\\python\\"
#titleIndexBuilder = TitleIndexBuilder(directory)
#titleIndexBuilder.build()
#titleIndex = TitleIndex(directory)
#print(titleIndex.getIdByTitle("гражданская война в россии"))
#print(titleIndex.getTitleById(7))
#print(titleIndex.getIdByTitle(titleIndex.getTitleById(7)))