# -*- coding: utf-8 -*-

class WikiAccessorFactory:
    _instances = {}
    @staticmethod
    def getAccessor(directory):
        if not WikiAccessorFactory._instances.get(directory,None):
            WikiAccessorFactory._instances[directory] = WikiAccessor(directory)
        return WikiAccessorFactory._instances[directory]    
    
from pywikiaccessor.redirects_index import RedirectsIndex
from pywikiaccessor.wiki_base_index import WikiBaseIndex
from pywikiaccessor.title_index import TitleIndex 
from pywikiaccessor.wiki_categories import CategoryIndex 
from pywikiaccessor.wiki_plain_text_index import WikiPlainTextIndex

class WikiAccessor():
    def __init__(self, directory):
        self.directory = directory
        self.baseIndex = WikiBaseIndex(self)
        self.titleIndex = TitleIndex(self)
        self.categoryIndex = CategoryIndex(self)
        self.redirectIndex = RedirectsIndex(self)
        self.plainTextIndex = WikiPlainTextIndex(self)
        self.customIndexes = {}
    def addCustomIndex(self,index):
        if index.wikiAccessor != self:
            return False
        if not self.customIndexes.get(index.getName()):
            self.customIndexes[index.getName()] = index
            return True
        return False
    instances = {}

 
    

                  
# directory = "C:\\WORK\\science\\onpositive_data\\python\\"
# pwXML = WikiIndex(directory)
# print(pwXML.getTitleArticleById(7))
# print(pwXML.getTextArticleById(7))