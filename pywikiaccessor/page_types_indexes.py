# -*- coding: utf-8 -*-
import pickle
import re

from pywikiaccessor.wiki_core import WikiIterator, WikiFileIndex, TitleIndex, WikiBaseIndex

class TemplateBasedIndexBuilder (WikiIterator):
    def __init__(self, className, accessor, cnt):
        self.CODE = 'utf-8'
        self.titleIndex = TitleIndex(accessor)
        super(TemplateBasedIndexBuilder, self).__init__(accessor, cnt)
    def getBodyTemplates(self):
        return []
    def getTitleTemplates(self):
        return []
    def getFileName(self):
        pass
    def createRecord(self,docId,res):
        pass
    def processSave(self,articlesCount):
        return

    def postProcess(self):
        with open(self.getFullFileName(self.getFileName()), 'wb') as f:
            pickle.dump(self.data, f, pickle.HIGHEST_PROTOCOL)               
    def clear(self):
        return 
    def processDocument(self, docId):
        text = self.wikiIndex.getTextArticleById(docId).lower()
        for template in self.getBodyTemplates():
            res = template.match(text)
            if res != None:
                if (self.createRecord(docId, res)):
                    return
        title = self.titleIndex.getTitleById(docId).lower()        
        for template in self.getTitleTemplates():
            res = template.match(title)
            if res != None:
                if (self.createRecord(docId, res)):
                    return

class RedirectPageFabric:
    @staticmethod
    def createRedirectPage(toId, anchor):
        return {"toId" : toId, "anchor" : anchor}

class RedirectsIndex (WikiFileIndex): 
    def __init__(self, wikiAccessor):
        super(RedirectsIndex, self).__init__(wikiAccessor)
        self.data = self.dictionaries["redirects"]
    def getDictionaryFiles(self): 
        return ['redirects']
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

class RedirectsIndexBuilder (TemplateBasedIndexBuilder):
    def __init__(self, accessor):
        super(RedirectsIndexBuilder, self).__init__(RedirectsIndexBuilder, accessor, 10000)
    def getBodyTemplates(self):
        return [re.compile('\#(redirect|перенаправление)([^\[])*\[\[([^\]]+)\]\]'),re.compile('\#(redirect|перенаправление)([^\[])\[\[([^\]\#]+)\#([^\]]+)\]\]')]
    def getFileName(self):
        return 'redirects.pcl'
    def createRecord(self,docId,res):
        if res != None:
            if (res.lastindex == 4):
                self.data[docId] = RedirectPageFabric.createRedirectPage(self.titleIndex.findArticleId(res.group(3)),res.group(4))
            else:
                self.data[docId] = RedirectPageFabric.createRedirectPage(self.titleIndex.findArticleId(res.group(3)),"")
            return True
    
    def processSave(self,articlesCount):
        return
    def preProcess(self):
        self.data = {}
    def clear(self):
        return 
                                         
class AmbigPagesIndex (WikiFileIndex): 
    def __init__(self, wikiAccessor):
        super(AmbigPagesIndex, self).__init__(wikiAccessor)
        self.data = self.dictionaries["ambigpages"]
    def getDictionaryFiles(self): 
        return ['ambigpages']
    def getAmbigPagesIds(self):
        return self.data;
    def getAmbigPagesCount(self):
        return len(self.data);
    def isAmbigPage(self, docId):
        return docId in self.data
    def getBuilder(self):
        return AmbigPagesIndexBuilder(self.accessor)
    def getName(self):
        return "ambigpages"

class AmbigPagesIndexBuilder (TemplateBasedIndexBuilder):
    
    def __init__(self, accessor):
        super(AmbigPagesIndexBuilder, self).__init__(AmbigPagesIndexBuilder, accessor, 10000)
    def getBodyTemplates(self):
        return [re.compile('{{неоднозначность')]
    def getTitleTemplates(self):
        return [re.compile('(значения)')]
    def getFileName(self):
        return 'ambigpages.pcl'
    def createRecord(self,docId,res):
        self.data.append(docId)
        return True
    def preProcess(self):
        self.data = []
    def clear(self):
        return 

class TemplatesPagesIndex (WikiFileIndex): 
    def __init__(self, wikiAccessor):
        super(TemplatesPagesIndex, self).__init__(wikiAccessor)
        self.data = self.dictionaries["templatepages"]
    def getDictionaryFiles(self): 
        return ['templatepages']
    def getTemplatesPagesIds(self):
        return self.data;
    def getTemplatesPagesCount(self):
        return len(self.data);
    def isTemplatesPage(self, docId):
        return docId in self.data
    def getBuilder(self):
        return TemplatesIndexBuilder(self.accessor)
    def getName(self):
        return "templatepages"
    
class TemplatesIndexBuilder (TemplateBasedIndexBuilder):
    
    def __init__(self, accessor):
        super(TemplatesIndexBuilder, self).__init__(TemplatesIndexBuilder, accessor, 10000)
    def getBodyTemplates(self):
        return []
    def getTitleTemplates(self):
        return [re.compile('шаблон:'),re.compile('template:')]
    def getFileName(self):
        return 'templatepages.pcl'
    def createRecord(self,docId,res):
        self.data.append(docId)
        return True
    def preProcess(self):
        self.data = []
    def clear(self):
        return 
    
def onlyArticlesPages(accessor):
    redirects = accessor.getIndex(RedirectsIndex).getRedirectsIds()
    print(len(redirects))
    ambigPages = accessor.getIndex(AmbigPagesIndex).getAmbigPagesIds()
    print(len(ambigPages))
    templatePages = accessor.getIndex(TemplatesPagesIndex).getTemplatesPagesIds()
    print(len(templatePages))
    allIds = accessor.getIndex(WikiBaseIndex).getIds()
    print(len(allIds))
    notAnArticleSet = set(redirects)
    notAnArticleSet |= set(ambigPages)
    notAnArticleSet |= set(templatePages)
    return [x for x in allIds if (x not in notAnArticleSet)]
    

if __name__ == '__main__':
    from pywikiaccessor.wiki_core import WikiConfiguration    
    directory = "C:/WORK/science/python-data/"
    accessor =  WikiConfiguration(directory)
    len(onlyArticlesPages(accessor))
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
