from pywikiutils.science_patterns import AbstractFragmentIterator
from pytextutils.text_fragmentation import TextFragmentator
from pywikiaccessor.wiki_core import WikiFileIndex,WikiConfiguration
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
        #for f in shortFragments:
        #    totalData = f["estimation"][2][1]
        #    print ("\t\t{} {}\n\t\t{}:".format(totalData[3][0],f["text"],totalData))
      
    def printFragments(self,fType):
        print(fType)
        for fragment in self.fragments[fType]:
            print ("\t{}:".format(fragment['headerId']))
            for f in fragment['fragments']:
                print ("\t\t{}\n\t\t{}:".format(f["text"],f["estimation"]))
             
class CorpusSentenceIndex(WikiFileIndex):
    def __init__(self, wikiAccessor,prefix):
        super(CorpusSentenceIndex, self).__init__(wikiAccessor,prefix)
    def getDictionaryFiles(self): 
        return ['corpus_fragments']
    def getBuilder(self):
        return CorpusSentenceAnalisys(self.accessor,self.prefix)
    def getName(self):
        return "corpus_sentence"
    def analizeFragments(self,fType):
        #print(fType)
        counts = {'definition':0, 'theorem':0, 'application': 0, 'algorithm':0}
        total = 0
        for fragment in self.dictionaries['corpus_fragments'][fType]:
            for f in fragment['fragments']:
                counts[f["estimation"][2][1][3][0]] += 1
                total+=1
        for k in counts.keys():
            counts[k] = counts[k]*100/total
        #    print("\t{}:\t{}".format(k, counts[k]/total))
        print(" & {} & {} & {} & {} & {}".format('Sentence count','definition', 'theorem', 'application', 'algorithm'))
        print("{} & \centering {} & \centering {:0.2f}\% & \centering {:0.2f}\% & \centering {:0.2f}\% & \centering {:0.2f}\%".format(fType, total, counts['definition'], counts['theorem'], counts['application'], counts['algorithm']))


def testCorpusAnalysis ():
    directory = "C:/WORK/science/python-data/"
    accessor =  WikiConfiguration(directory)
    
    import json
    
    with open(directory+"test_corpus/corpus.json",encoding='utf-8') as data_file: 
        testData = json.load(data_file)
    
    fragmentator = TextFragmentator(accessor,'miph_')
    good = 0    
    for item in testData:
        estimates = fragmentator.genFragments(item['text'],0.1)
        if item["type"] == estimates[0].additionalInfo['functionalType']:
            good+=1
        print("{}\t{}\t{}\t{}".format(item["type"] == estimates[0].additionalInfo['functionalType'],
                                      item["type"],
                                      estimates[0].additionalInfo['functionalType'],
                                      item["text"]))
    print(good)
    print(good/len(testData))                                    
if __name__ =="__main__":
    # testCorpusAnalysis ()
    
    directory = "C:/WORK/science/python-data/"
    accessor =  WikiConfiguration(directory)

    builder = CorpusSentenceAnalisys(accessor,"miph_")
    builder.build();
    builder.printFragments("definition")
    
    index = CorpusSentenceIndex(accessor,"miph_")
    index.analizeFragments("definition")
    index.analizeFragments("theorem")
    index.analizeFragments("application")
    index.analizeFragments("algorithm")
    
