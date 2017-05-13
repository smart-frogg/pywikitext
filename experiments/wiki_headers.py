# -*- coding: utf-8 -*-
import pymysql
from pytextutils.token_splitter import TokenSplitter, ALL_CYR_LETTERS
from pywikiaccessor.wiki_tokenizer import WikiTokenizer
from pywikiaccessor.wiki_accessor import WikiAccessor
from pywikiaccessor.wiki_iterator import WikiIterator
from pywikiaccessor.document_type import DocumentTypeIndex
from pywikiaccessor.redirects_index import RedirectsIndex
import re

class HeadersBuilder (WikiIterator):
    __TRESHOLD = 0.0005
    def __init__(self, accessor, docIds = None):
        super(HeadersBuilder, self).__init__(accessor, 1000, docIds)

    def processSave(self,articlesCount):
        pass
   
    def preProcess(self):
        self.dbConnection = pymysql.connect(host='localhost', port=3306, user='root', passwd='',charset='utf8', db='wikiparse')
        self.dbCursor = self.dbConnection.cursor()
        self.redirects = self.accessor.getIndex(RedirectsIndex) 
        self.cleaner = WikiTokenizer()
        self.doctypeIndex = DocumentTypeIndex(accessor)
        self.headerTemplates = [
                re.compile('\n[ \t]*======([^=]*)======[ \t\r]*\n'),
                re.compile('\n[ \t]*=====([^=]*)=====[ \t\r]*\n'),
                re.compile('\n[ \t]*====([^=]*)====[ \t\r]*\n'),
                re.compile('\n[ \t]*===([^=]*)===[ \t\r]*\n'),
                re.compile('\n[ \t]*==([^=]*)==[ \t\r]*\n'),
                re.compile('\n[ \t]*=([^=]*)=[ \t\r]*\n'),
            ]
 
        self.clear()
        self.headers = {}
        self.wordSplitter = TokenSplitter()  
        self.addHeaderQuery = "INSERT INTO headers(text) VALUES (%s)"
        self.getHeaderIdQuery = "SELECT id FROM headers WHERE text LIKE %s"
        self.insertHeaderToDocQuery = "INSERT INTO header_to_doc(doc_id,header_id,pos_start,pos_end,type) VALUES "
        self.isDocAlreadySaveQuery = "SELECT count(id) as cnt FROM `header_to_doc` WHERE doc_id = %s group by doc_id"

        self.queryElement = "(%s, %s, %s, %s, %s)"
        
        self.dbCursor.execute("SELECT * FROM headers ORDER BY id")
        for element in self.dbCursor.fetchall():
            self.headers[element[1]] = element[0] 
    
    def postProcess(self):
        pass
           
    def clear(self):
        pass

    def isDocAlreadySave(self,docId):
        self.dbCursor.execute(self.isDocAlreadySaveQuery,(docId))
        count = self.dbCursor.fetchone()
        if not count:
            return False
        return count[0] > 0
    
    def getHeaderId(self,header):
        header = header.replace("ё","е")
        header = header.replace("\\","").strip()
        header_id = self.headers.get(header,None)
        if not header_id:
            self.dbCursor.execute(self.addHeaderQuery,(header))
            self.dbConnection.commit()
            self.dbCursor.execute(self.getHeaderIdQuery,(header))
            header_id = self.dbCursor.fetchone()
            if not header_id:
                print(header)
            else:
                self.headers[header] = header_id[0]
        return header_id    
    
    def getAllHeadersForDoc(self, docId):         
        text = self.wikiIndex.getTextArticleById(docId).lower()
        headers = []
        htype = 6
        for template in self.headerTemplates:
            for match in template.finditer(text):
                header = self.cleaner.clean(match.group(1))
                if any(ch in ALL_CYR_LETTERS for ch in header):
                    header_id = self.getHeaderId(header)
                    if header_id: 
                        headers.append({'header':header_id,'type':htype,'position_start':match.end(),'position_match':match.start()})
            htype -= 1
        headers.sort(key=lambda header: header['position_match'])
        return headers
        
    def processDocument(self, docId):
        if self.redirects.isRedirect(docId):
            return
        if self.doctypeIndex.isDocType(docId,'wiki_stuff'):
            return
        if self.isDocAlreadySave(docId):
            return
        text = self.wikiIndex.getTextArticleById(docId)
        headers = self.getAllHeadersForDoc(docId)    
        query = []
        params = []            
        for header_id in range(0,len(headers)-1):
            query.append(self.queryElement)
            params.append(docId)
            params.append(headers[header_id]["header"])
            params.append(headers[header_id]["position_start"])
            if header_id != len(headers)-1:
                params.append(headers[header_id+1]["position_match"])
            else:
                params.append(len(text))
            params.append(headers[header_id]["type"])
        if len(query)>0 :
            self.dbCursor.execute(self.insertHeaderToDocQuery+",".join(query),params)
            self.dbConnection.commit()
        #else:
            # print (docId)
class HeadersIndex:
    def __init__(self,accessor):
        self.dbConnection = pymysql.connect(host='localhost', port=3306, user='root', passwd='',charset='utf8', db='wikiparse')
        self.dbCursor = self.dbConnection.cursor()         
        self.getAllStatQuery = '''
            SELECT headers.id as id, headers.text as text, count(`header_to_doc`.id) as cnt 
            FROM `header_to_doc`, headers 
            WHERE `header_to_doc`.header_id = headers.id 
            GROUP BY headers.id 
            ORDER BY cnt desc
            '''
        self.countHeadersForDocQuery = '''
            SELECT `header_to_doc`.doc_id, count(`header_to_doc`.id) as cnt 
            FROM `header_to_doc` 
            GROUP BY `header_to_doc`.doc_id 
            ORDER BY cnt desc
            LIMIT 200
            '''
    def getCountHeadersForDoc(self, docIds):
        #.format(','.join(str(x) for x in docIds)
        self.dbCursor.execute(self.countHeadersForDocQuery)
        res = []
        for element in self.dbCursor.fetchall():
            res.append ({'id': element[0],'cnt': element[1]})
        return res                
    def getAllStat(self, docIds):
        self.dbCursor.execute(self.getAllStatQuery)
        res = []
        for element in self.dbCursor.fetchall():
            res.append ({'id': element[0],'text': element[1],'cnt': element[2]})
        return res    
  
      
#regex1 = re.compile('\n[ \t]*==([^=]*)==[ \t\r]*\n')
#text = " kdkd\n == kdkd==\n"
#match = regex1.search(text)
#print(match.end())
directory = "C:\\WORK\\science\\onpositive_data\\python\\"
accessor = WikiAccessor(directory)
docTypesIndex = DocumentTypeIndex(accessor)
docIds = docTypesIndex.getDocsOfType("sciense")
#titleIndex = accessor.titleIndex
#doc_id = titleIndex.getIdByTitle("Пушкин, Александр Сергеевич")
hb = HeadersBuilder(accessor,list(docIds))
hb.build()
#hb.preProcess()
#hb.processDocument(doc_id)
hi = HeadersIndex(accessor)
#hi.getCountHeadersForDoc(docIds)
stat = hi.getAllStat(docIds)
for s in stat:
    print (s['text']+": "+str(s['cnt']))
   
  
 