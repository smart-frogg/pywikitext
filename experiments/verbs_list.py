# -*- coding: utf-8 -*-
import pymysql
from pytextutils.token_splitter import TokenSplitter, Token, TYPE_TOKEN, POSTagger
from pywikiaccessor.wiki_accessor import WikiAccessorFactory
from pywikiaccessor.wiki_iterator import WikiIterator
import numpy as np
import pytextutils.k_means as k_means

class VerbListBuilder (WikiIterator):
    __TRESHOLD = 0.0005
    def __init__(self, accessor, docIds = None):
        super(VerbListBuilder, self).__init__(accessor, 1000, docIds)

    def processSave(self,articlesCount):
        pass
   
    def preProcess(self):
        self.dbConnection = pymysql.connect(host='localhost', port=3306, user='root', passwd='',charset='utf8', db='wikiparse')
        self.dbCursor = self.dbConnection.cursor()
        self.posTagger = POSTagger()
        self.redirects = self.accessor.redirectIndex 
        self.plainTextIndex = self.accessor.plainTextIndex
        self.clear()
        self.stems = {}
        self.wordSplitter = TokenSplitter()  
        self.addStemQuery = "INSERT INTO verbs(stem) VALUES (%s)"
        self.getStemIdQuery = "SELECT id FROM verbs WHERE stem LIKE %s"
        self.insertVerbToDocQuery = "INSERT INTO verb_to_doc(doc_id,verb_id,is_ambig,position,score) VALUES "
        self.queryElement = "(%s, %s, %s, %s, %s)"
        
        self.dbCursor.execute("SELECT * FROM verbs ORDER BY id")
        for stem in self.dbCursor.fetchall():
            self.stems[stem[1]] = stem[0] 
    
    def postProcess(self):
        pass
           
    def clear(self):
        pass

    def getStemId(self,stem):
        stem = stem.replace("ё","е")
        stem_id = self.stems.get(stem,None)
        if not stem_id:
            self.dbCursor.execute(self.addStemQuery,(stem))
            self.dbConnection.commit()
            self.dbCursor.execute(self.getStemIdQuery,(stem))
            stem_id = self.dbCursor.fetchone()
            if not stem_id:
                print(stem)
            self.stems[stem] = stem_id[0]
        return stem_id    
             
    def processDocument(self, docId):
        if self.redirects.isRedirect(docId):
            return
        cleanText = self.plainTextIndex.getTextById(docId)
        if cleanText == None:
            return
        verbs = []
        self.wordSplitter.split(cleanText)
        tokens = self.wordSplitter.getTokenArray()
        self.posTagger.posTagging(tokens)  
        for token in tokens:
            if (token.tokenType == TYPE_TOKEN and not token.hasDigits()):
                #if (not token.allCyr()) or token.token.lower() in self.notAVerbs:
                #    break;
                #parse_result = self.pos.parse(token.token)
                #if(parse_result == None):
                #    continue
                isVerb = False
                isOnlyVerb = True
                normalForm = None
                verbScore = 0
                for res in token.POS:
                    if (res['POS'] == 'VERB'):
                        isVerb = True
                        normalForm = res['normalForm']
                        verbScore = res['score']
                    else:
                        isOnlyVerb = False 
                if(isVerb):
                    verb = {"stem": self.getStemId(normalForm), "is_ambig": isOnlyVerb, "pos": token.tokenNum, "score": verbScore}
                    verbs.append(verb)
        query = []
        params = []            
        for verb in verbs:
            query.append(self.queryElement)
            params.append(docId)
            params.append(verb["stem"])
            params.append(verb["is_ambig"])
            params.append(verb["pos"])
            params.append(verb["score"])
        if len(query)>0 :
            self.dbCursor.execute(self.insertVerbToDocQuery+",".join(query),params)
            self.dbConnection.commit()
        #else:
            # print (docId)
class VerbsListIndex:
    def __init__(self):
        self.dbConnection = pymysql.connect(host='localhost', port=3306, user='root', passwd='',charset='utf8', db='wikiparse')
        self.dbCursor = self.dbConnection.cursor()
        self.getAllStatQuery = "SELECT verbs.id as id, verbs.stem as stem, count(`verb_to_doc`.id) as cnt FROM `verb_to_doc`,verbs WHERE `verb_to_doc`.verb_id = verbs.id group by verbs.id order by cnt desc"
        self.getVerbIdsQuery = "select id from (SELECT verbs.id as id, verbs.stem as stem, count(`verb_to_doc`.id) as cnt FROM `verb_to_doc`,verbs WHERE `verb_to_doc`.verb_id = verbs.id group by verbs.id) as table1 where cnt > 1 "
        self.getHistQueryLeft = "SELECT verb_id, doc_id, count(id) as cnt FROM `verb_to_doc` WHERE verb_id in ("
        self.getHistQueryRight = ") group by verb_id,doc_id order by verb_id asc, doc_id asc"
        self.getVerbsQuery = "SELECT verbs.id, verbs.stem FROM verbs"
        self.getDimentionQuery = "SELECT count(DISTINCT doc_id) as cnt FROM `verb_to_doc`"
        self.verbs = None
    def getAllStat(self):
        self.dbCursor.execute(self.getAllStatQuery)
        res = []
        for element in self.dbCursor.fetchall():
            res.append ({'id': element['id'],'stem': element['stem'],'cnt': element['cnt']})
        return res    
    def getHists(self):        
        self.dbCursor.execute(self.getVerbIdsQuery)
        ids = []
        self.verbRenum = {}
        self.docRenum = {}
        for element in self.dbCursor.fetchall():
            ids.append(str(element[0]))
            self.verbRenum[element[0]] = len(self.verbRenum)
        self.dbCursor.execute(self.getDimentionQuery)
        dim = self.dbCursor.fetchone()  
        hist = np.zeros((len(ids),dim[0]))
          
        self.dbCursor.execute(self.getHistQueryLeft+",".join(ids)+self.getHistQueryRight)
        
        for element in self.dbCursor.fetchall():
            if not self.docRenum.get(element[1],None):
                self.docRenum[element[1]] = len(self.docRenum)
            x = self.verbRenum[element[0]]
            y = self.docRenum[element[1]]
            hist[x,y] = element[2]
        return hist
    def getVerbs(self):
        if not self.verbs:        
            self.dbCursor.execute(self.getVerbsQuery)
            self.verbs = {}
            for element in self.dbCursor.fetchall():
                self.verbs[element[0]] = element[1]
        return self.verbs
    def similarity(self,a,b):
        similarity = (a * b).sum()
        
        return similarity / (np.linalg.norm(a)*np.linalg.norm(b))      
         
    def clusterizeVerbs(self, clusterCount, iterations):
        data = self.getHists() 
        return k_means.clusterize(data,clusterCount, iterations,self.similarity)            

directory = "C:\\WORK\\science\\onpositive_data\\python\\"
accessor = WikiAccessorFactory.getAccessor(directory)
verbsListIndex = VerbsListIndex()
centers, verbsClusters = verbsListIndex.clusterizeVerbs(5, 2000)
verbs = verbsListIndex.getVerbs()
for verbId in verbs.keys():
    goodVerbId = verbsListIndex.verbRenum.get(verbId,None)
    if goodVerbId:
        print(str(verbs[verbId])+" \t "+str(verbsClusters[goodVerbId]))
#for cid, center in enumerate(centers):
#    print (cid)
#    for coordId,coord in center.items():
#        print(str(coordId)+" : "+str(coord))

#from DocumentType import DocumentTypeIndex
#docTypesIndex = DocumentTypeIndex(accessor)
#docIds = docTypesIndex.getDocsOfType("event")
#bld = VerbListBuilder(accessor,list(docIds))
#bld.build()
'''
titleIndex = accessor.titleIndex
bld = VerbListBuilder(accessor)
bld.preProcess()
doc_id = titleIndex.getIdByTitle("Пушкин, Александр Сергеевич") 
bld.processDocument(doc_id)       
'''     