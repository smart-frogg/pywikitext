import json

class Corpus: 
    def __init__(self, fileName=None):
        if (fileName is None):
            self.texts = []
        else:
            with open(fileName, encoding="utf8") as data_file:    
                self.texts = json.load(data_file,encoding="utf-8")
    def addText(self, text):
        self.texts.append(text)
        
    def getByMark(self, mark):
        return [ t for t in self.texts if t.mark == mark]
    @staticmethod
    def genItem(text, mark, header, docId, docTitle):
        return {
            "text": text,
            "mark": mark,
            "header": header,
            "docId": docId,
            "docTitle": docTitle             
            }
    

from pywikiaccessor.wiki_core import WikiConfiguration, WikiTitleBaseIndex
from pywikiutils.science_patterns import AbstractFragmentIterator
from pywikiaccessor.wiki_plain_text_index import WikiPlainTextIndex

class CorpusBuilder(AbstractFragmentIterator):
    
    def __init__(self, accessor, indexPrefix):
        super(CorpusBuilder, self).__init__(accessor, indexPrefix)
    
    def preProcess(self):
        self.fragments = []
        self.titleIndex = WikiTitleBaseIndex(self.accessor)
        self.plainTextIndex = WikiPlainTextIndex(self.accessor)
        self.frCount = 0
        self.count = 0

    def postProcess(self):
        with open(self.accessor.directory+self.prefix+'corpus.json', 'w') as outfile:
            json.dump(self.fragments, outfile)
            outfile.close()

    def processFragmentStart(self, fType):
        self.count += self.frCount
        self.frCount = 0    
    def processFragmentEnd(self, fType):    
        print(fType)
        print(self.frCount)
        print(self.count) 
    
    def processDocument(self, fType, headerId, docId):
        text = self.headerIndex.getDocSection(docId, headerId)
        item = Corpus.genItem(text,fType,self.headerIndex.headerText(headerId),docId,self.titleIndex.getTitleArticleById(docId))
        self.fragments.append(item);
        self.frCount +=1
                                                    
def buildCorpus (directory, prefix):
    accessor =  WikiConfiguration(directory)
    builder = CorpusBuilder(accessor,prefix)
    builder.build()
        
if __name__ =="__main__":
    directory = "C:/WORK/science/python-data/"
    buildCorpus (directory,'miph_')
