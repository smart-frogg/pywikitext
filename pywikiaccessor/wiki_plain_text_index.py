# -*- coding: utf-8 -*-
import pickle
from pywikiaccessor import wiki_accessor, WikiTokenizer, wiki_iterator, wiki_file_index

class WikiPlainTextIndex(wiki_file_index.WikiFileIndex): 
    def __init__(self, wikiAccessor):
        super(WikiPlainTextIndex, self).__init__(wikiAccessor)
        self.textDict = self.dictionaries['plainTextIndex']
        
    def getDictionaryFiles(self):    
        return ['plainTextIndex']
    
    def getOtherFiles(self):    
        return ["plainText.dat"]
    
    def loadOtherFiles(self):    
        self.textFile = open(self.directory+"plainText.dat", 'rb')
    
    def getTextById(self, ident):
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
    def getBuilder(self):
        return WikiPlainTextBuilder(self.directory)
    def getName(self):
        return "plainTexts"

class WikiPlainTextBuilder (wiki_iterator.WikiIterator):
    
    def __init__(self, directory):
        self.CODE = 'utf-8'
        super(WikiPlainTextBuilder, self).__init__(directory, 10000)

    def processSave(self,articlesCount):
        return

    def postProcess(self):
        self.textFile.close()
        with open(self.directory + 'plainTextIndex.pcl', 'wb') as f:
            pickle.dump(self.textDict, f, pickle.HIGHEST_PROTOCOL)


    def preProcess(self):
        self.textFile = open(self.directory+"plainText.dat", 'wb')
        self.tokenizer = WikiTokenizer.WikiTokenizer()
        self.textShift = 0
        self.textDict = {}
               
    def clear(self):
        return 

    def processDocument(self, docId):
        self.textDict[docId] = self.textShift
        cleanText = self.tokenizer.clean(self.wikiIndex.getTextArticleById(docId))  
        byteArray = cleanText.encode(self.CODE)
        length = len(byteArray)
        self.textFile.write(length.to_bytes(4, byteorder='big'))
        self.textFile.write(byteArray)
        self.textShift += length+4    
        
#directory = "C:\\WORK\\science\\onpositive_data\\python\\"
#plainTextBuilder = WikiPlainTextBuilder(directory)
#plainTextBuilder.build()