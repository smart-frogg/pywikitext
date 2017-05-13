# -*- coding: utf-8 -*-
from pywikiaccessor.one_opened import OneOpened

class WikiAccessor(metaclass=OneOpened):
    def __init__(self, directory):
        self.directory = directory
        self.__indexes = {}
    def getIndex(self, indexClass):
        index = self.__indexes.get(indexClass,None)
        if not index:
            self.__indexes[indexClass] = indexClass(self)
        return self.__indexes.get(indexClass,None)        


#directory = "C:\\WORK\\science\\onpositive_data\\python\\"
#wa = WikiAccessor(directory)
#titleIndex = wa.getIndex(TitleIndex)
#print(titleIndex.getIdByTitle("Барнаул"))    

                  
# directory = "C:\\WORK\\science\\onpositive_data\\python\\"
# pwXML = WikiIndex(directory)
# print(pwXML.getTitleArticleById(7))
# print(pwXML.getTextArticleById(7))