# -*- coding: utf-8 -*-
import pymysql
from pytextutils.token_splitter import TokenSplitter, Token, TYPE_TOKEN, POSTagger
import math
import CachedPymorphyMorph
from pywikiaccessor.wiki_accessor import WikiAccessorFactory
from pywikiaccessor.wiki_iterator import WikiIterator

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
    pass
    

directory = "C:\\WORK\\science\\onpositive_data\\python\\"
accessor = WikiAccessorFactory.getAccessor(directory)

from DocumentType import DocumentTypeIndex
docTypesIndex = DocumentTypeIndex(accessor)
docIds = docTypesIndex.getDocsOfType("event")
bld = VerbListBuilder(accessor,list(docIds))
bld.build()
'''
titleIndex = accessor.titleIndex
bld = VerbListBuilder(accessor)
bld.preProcess()
doc_id = titleIndex.getIdByTitle("Пушкин, Александр Сергеевич") 
bld.processDocument(doc_id)       
'''     