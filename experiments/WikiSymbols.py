# -*- coding: utf-8 -*-
import pickle

from pywikiaccessor import wiki_iterator,wiki_accessor

class AllSymbolsBuilder (wiki_iterator.WikiIterator):
    
    def __init__(self, accessor):
        self.allChars = set()
        super(AllSymbolsBuilder, self).__init__(accessor, 10000)

    def processSave(self,articlesCount):
        return

    def postProcess(self):
        with open(self.accessor.directory + 'allChars.txt', 'w', encoding='utf-8') as f:
            f.write (str(self.allChars))
            f.close ()

    def preProcess(self):
        pass
    
    def clear(self):
        pass 

    def processDocument(self, docId):
        text = self.wikiIndex.getTextArticleById(docId)
        self.allChars.update(text)

#a= set("ddffdsлалалаssdf")
#b = "bnnПриветnvbbnnvv"
#a.update(b)
#print (str(a))
directory = "C:\\WORK\\science\\onpositive_data\\python\\"
#import codecs
#with open(directory + 'allChars.txt', 'w', encoding='utf-8') as f:
#    f.write (str(a))
#    f.write(u'\ufeff')
#    f.close ()
#
accessor =  wiki_accessor.WikiAccessorFactory.getAccessor(directory)        
builder = AllSymbolsBuilder(accessor)
builder.build()

#

#directory = "C:\\WORK\\science\\onpositive_data\\python\\"
#accessor =  wiki_accessor.WikiAccessorFactory.getAccessor(directory)
#titleIndex = accessor.titleIndex
#bld = DocumentTypeIndexBuilder(accessor)
#bld.preProcess()
#doc_id = titleIndex.getIdByTitle("Арцебарский, Анатолий Павлович") 
#bld.processDocument(doc_id)                
#doc_id = titleIndex.getIdByTitle("Барнаул")
#bld.processDocument(doc_id)                
#print(bld.data)
