# -*- coding: utf-8 -*-
import pymysql
from pytextutils.token_splitter import TokenSplitter, ALL_CYR_LETTERS
from pywikiaccessor.wiki_tokenizer import WikiTokenizer
from pywikiaccessor.wiki_accessor import WikiAccessorFactory
from pywikiaccessor.wiki_iterator import WikiIterator
from pywikiaccessor.document_type import DocumentTypeIndex
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
        self.redirects = self.accessor.redirectIndex 
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
        self.queryElement = "(%s, %s, %s, %s, %s)"
        
        self.dbCursor.execute("SELECT * FROM headers ORDER BY id")
        for element in self.dbCursor.fetchall():
            self.headers[element[1]] = element[0] 
    
    def postProcess(self):
        pass
           
    def clear(self):
        pass

    def getHeaderId(self,header):
        header = header.replace("ё","е")
        header = header.replace("\\","")
        header_id = self.headers.get(header,None)
        if not header_id:
            self.dbCursor.execute(self.addHeaderQuery,(header))
            self.dbConnection.commit()
            self.dbCursor.execute(self.getHeaderIdQuery,(header))
            header_id = self.dbCursor.fetchone()
            if not header_id:
                print(header)
            self.headers[header] = header_id[0]
        return header_id    
             
    def processDocument(self, docId):
        if self.redirects.isRedirect(docId):
            return
        if self.doctypeIndex.isDocType(docId,'wiki_stuff'):
            return
        text = self.wikiIndex.getTextArticleById(docId).lower()
        headers = []
        htype = 6
        for template in self.headerTemplates:
            for match in template.finditer(text):
                header = self.cleaner.clean(match.group(1))
                if any(ch in ALL_CYR_LETTERS for ch in header):
                    header_id = self.getHeaderId(header)
                    headers.append({'header':header_id,'type':htype,'position_start':match.end(),'position_match':match.start()})
            htype -= 1
        headers.sort(key=lambda header: header['position_match'])    
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
    def __init__(self):
        self.dbConnection = pymysql.connect(host='localhost', port=3306, user='root', passwd='',charset='utf8', db='wikiparse')
        self.dbCursor = self.dbConnection.cursor()         

#regex1 = re.compile('\n[ \t]*==([^=]*)==[ \t\r]*\n')
#text = " kdkd\n == kdkd==\n"
#match = regex1.search(text)
#print(match.end())
directory = "C:\\WORK\\science\\onpositive_data\\python\\"
accessor = WikiAccessorFactory.getAccessor(directory)
#titleIndex = accessor.titleIndex
#doc_id = titleIndex.getIdByTitle("Пушкин, Александр Сергеевич")
hb = HeadersBuilder(accessor)
hb.build()
#hb.preProcess()
#hb.processDocument(doc_id)   
  
 