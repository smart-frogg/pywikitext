from pytextutils.text_fragmentation import TextFragmentator
from pywikiutils.science_patterns import AbstractFragmentIterator
from pywikiutils.wiki_headers import DocumentByHeadersIterator,HeadersFileIndex
from pywikiaccessor.wiki_core import WikiConfiguration,WikiFileIndex,TitleIndex

import pickle

class FragmentDocumentListBuilder(AbstractFragmentIterator):
    
    def __init__(self, accessor, indexPrefix):
        super(FragmentDocumentListBuilder, self).__init__(accessor, indexPrefix)
        self.fromConfig = False
        
    def preProcess(self):
        self.documentList = set()

    def postProcess(self):
        with open(self.accessor.directory+self.prefix + 'docList.pcl', 'wb') as f:
            pickle.dump(self.documentList, f, pickle.HIGHEST_PROTOCOL)        
    def processFragmentStart(self, fType):    
        pass
    def processFragmentEnd(self, fType):    
        pass
    
    def processDocument(self, fType, headerId, docId):
        self.documentList.add(docId)

class FragmentDocumentList (WikiFileIndex):
    def __init__(self, wikiAccessor,prefix):
        super(FragmentDocumentList, self).__init__(wikiAccessor,prefix)
    
    def getDictionaryFiles(self): 
        return ['docList']
    def getDocList(self):
        return list(self.dictionaries.get('docList'))
    def getBuilder(self):
        return FragmentDocumentListBuilder(self.accessor,self.prefix)
    def getName(self):
        return "fr_doc_list"    
        
class OtherFragmentDocumentListBuilder(DocumentByHeadersIterator):
    def preProcess(self):
        self.docHeadersType = {}
        self.fragmentator = TextFragmentator(self.accessor,'miph_')
    def processDocumentStart(self, docId):
        self.docHeadersType[docId] = {}
    def processDocumentEnd(self, docId):
        pass
    def clear(self):
        pass  
    def processSave(self,articlesCount):
        pass  
    def postProcess(self):
        with open(self.accessor.directory+self.prefix + 'sectionType.pcl', 'wb') as f:
            pickle.dump(self.docHeadersType, f, pickle.HIGHEST_PROTOCOL)     
    def processFragment(self, docId, headerId):
        text = self.headerIndex.getDocSection(docId, headerId['header'])
        self.docHeadersType[docId][headerId['header']] = self.fragmentator.estimateFullText(text,0.1)
        
class OtherFragmentDocumentList (WikiFileIndex):
    def __init__(self, wikiAccessor,prefix):
        super(OtherFragmentDocumentList, self).__init__(wikiAccessor,prefix)
    
    def getDictionaryFiles(self): 
        return ['sectionType']
    def getSections(self):
        return self.dictionaries.get('sectionType')
    def getBuilder(self):
        return FragmentDocumentListBuilder(self.accessor,self.prefix)
    def getName(self):
        return "fr_section_types" 
    
if __name__ =="__main__":
    directory = "C:/WORK/science/python-data/"
    accessor =  WikiConfiguration(directory)
    dl = FragmentDocumentList(accessor,'miph_')
    docs = dl.getDocList()
    #ofdlb = OtherFragmentDocumentListBuilder(accessor,docs[1:10],'miph_')
    #ofdlb.build()
    ofdl = OtherFragmentDocumentList(accessor,'miph_')
    sections = ofdl.getSections()
    titles = TitleIndex(accessor)
    hi = HeadersFileIndex(accessor,'miph_')
    for d in sections:
        print (titles.getTitleById(d))
        for h in sections[d]:
            estimates = sections[d][h];
            if estimates is None:
                continue 
            print ("\t"+hi.headerText(h)+" ")
            
            for v in estimates["total"]:
                print ("\t\t"+v[0]+"\t"+str(v[1]))
        
    #fdlb = FragmentDocumentListBuilder(accessor,'miph_')
    #fdlb.build()