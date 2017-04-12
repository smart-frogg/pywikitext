# -*- coding: utf-8 -*-
import pymysql
import TokenSplitter
import TextToken
import math
import CachedPymorphyMorph
from pywikiaccessor.wiki_accessor import WikiAccessorFactory
from pywikiaccessor.wiki_iterator import WikiIterator

class VerbListBuilder (WikiIterator):
    def __init__(self, accessor):
        super(VerbListBuilder, self).__init__(accessor, 100000)

    def processSave(self,articlesCount):
        pass

   
    def preProcess(self):
        self.dbConnection = pymysql.connect(host='localhost', port=3306, user='root', passwd='',charset='utf8', db='wikiparse')
        self.dbCursor = self.dbConnection.cursor()
        self.morph = CachedPymorphyMorph.CachedPymorphyMorph(self.accessor.directory)
        self.redirects = self.accessor.redirectIndex 
        self.plainTextIndex = self.accessor.plainTextIndex
        self.clear()
        self.stems = {}
        self.wordSplitter = TokenSplitter.TokenSplitter()  
        self.addStemQuery = "INSERT INTO verbs(stem) VALUES (%s)"
        self.getStemIdQuery = "SELECT id FROM verbs WHERE stem LIKE %s"
        self.insertVerbToDocQuery = "INSERT INTO verb_to_doc(doc_id,verb_id,is_ambig,position) VALUES "
        self.queryElement = "(%s, %s, %s, %s)"
        
        self.dbCursor.execute("SELECT * FROM verbs ORDER BY id")
        for stem in self.dbCursor.fetchall():
            self.stems[stem[1]] = stem[0] 
    
    def postProcess(self):
        pass
           
    def clear(self):
        pass

    def getStemId(self,stem):
        stem_id = self.stems.get(stem,None)
        if not stem_id:
            self.dbCursor.execute(self.addStemQuery,(stem))
            self.dbConnection.commit()
            self.dbCursor.execute(self.getStemIdQuery,(stem))
            stem_id = self.dbCursor.fetchone()
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
          
        for token in tokens:
            if (token.tokenType == TextToken.TYPE_TOKEN):
                parse_result = self.morph.parse(token.token)
                if(parse_result == None):
                    continue
                isVerb = False
                isOnlyVerb = True
                normalForm = None
                for res in parse_result:
                    if (res.tag.POS == 'VERB'):
                        isVerb = True
                        normalForm = res.normal_form
                    else:
                        isOnlyVerb = False 
                if(isVerb):
                    verb = {"stem": self.getStemId(normalForm), "is_ambig": isOnlyVerb, "pos": token.tokenNum}
                    verbs.append(verb)
        query = []
        params = []            
        for verb in verbs:
            query.append(self.queryElement)
            params.append(docId)
            params.append(verb["stem"])
            params.append(verb["is_ambig"])
            params.append(verb["pos"])
        self.dbCursor.execute("INSERT INTO verb_to_doc(doc_id,verb_id,is_ambig,position) VALUES "+",".join(query),params)
        self.dbConnection.commit()

directory = "C:\\WORK\\science\\onpositive_data\\python\\"
accessor = WikiAccessorFactory.getAccessor(directory)
titleIndex = accessor.titleIndex
bld = VerbListBuilder(accessor)
bld.preProcess()
doc_id = titleIndex.getIdByTitle("Пушкин, Александр Сергеевич") 
bld.processDocument(doc_id)            