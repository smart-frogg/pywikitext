from pywikiutils.science_patterns import AbstractFragmentIterator
from pytextutils.text_fragmentation import TextFragmentator
from pywikiaccessor.wiki_core import WikiConfiguration
import pickle
class CorpusSentenceAnalisys(AbstractFragmentIterator): 
    def __init__(self, accessor, indexPrefix):
        super(CorpusSentenceAnalisys, self).__init__(accessor, indexPrefix)
        self.fragmentator = TextFragmentator(self.accessor,'miph_')
        
    def preProcess(self):
        self.fragments = {}
  
    def postProcess(self):
        with open(self.accessor.directory+self.prefix + 'corpus_fragments.pcl', 'wb') as f:
            pickle.dump(self.fragments, f, pickle.HIGHEST_PROTOCOL)        

    def processFragmentStart(self, fType): 
        self.fragments[fType] = []
    def processFragmentEnd(self, fType):    
        pass
    
    def processDocument(self, fType, headerId, docId):
        text = self.headerIndex.getDocSection(docId, headerId)
        fragments = self.fragmentator.genFragments(text,0.1)
        shortFragments = []    
        for f in fragments:
            if ('ft_estimations' in f.additionalInfo) :
                shortFragments.append({"text":f.token,"estimation":f.additionalInfo['ft_estimations']})
        self.fragments[fType].append({'headerId':headerId,'docId':docId,'fragments':shortFragments})
        for f in shortFragments:
            totalData = f["estimation"][2][1]
            print ("\t\t{} {}\n\t\t{}:".format(totalData[3][0],f["text"],totalData))
      
    def printFragments(self,fType):
        print(fType)
        for fragment in self.fragments[fType]:
            print ("\t{}:".format(fragment['headerId']))
            for f in fragment['fragments']:
                print ("\t\t{}\n\t\t{}:".format(f["text"],f["estimation"]))
    def analizeFragments(self,fType):
        print(fType)
        for fragment in self.fragments[fType]:
            print ("\t{}:".format(fragment['headerId']))
            for f in fragment['fragments']:
                for e in f["estimation"]['total']:
                    print(e)
                    
if __name__ =="__main__":
    directory = "C:/WORK/science/python-data/"
    accessor =  WikiConfiguration(directory)
    builder = CorpusSentenceAnalisys(accessor,"miph_")
    builder.build();
    builder.printFragments("definition")
