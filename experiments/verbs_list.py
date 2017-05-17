# -*- coding: utf-8 -*-
'''
Модуль для построения списка глаголов

Требует:
+ индекс очищенных от вики-разметки текстов статей
+ индекс редиректов

Схема базы

DROP TABLE IF EXISTS `headers`;
CREATE TABLE IF NOT EXISTS `headers` (
`id` int(11) NOT NULL,
  `text` varchar(1000) CHARACTER SET utf8 NOT NULL
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `header_to_doc`;
CREATE TABLE IF NOT EXISTS `header_to_doc` (
`id` int(11) NOT NULL,
  `doc_id` int(11) NOT NULL,
  `header_id` int(11) NOT NULL,
  `pos_start` mediumint(9) NOT NULL,
  `pos_end` mediumint(9) NOT NULL,
  `type` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

ALTER TABLE `headers`
 ADD PRIMARY KEY (`id`);

ALTER TABLE `header_to_doc`
 ADD PRIMARY KEY (`id`), ADD KEY `doc_id` (`doc_id`), ADD KEY `header_id` (`header_id`), ADD KEY `pos_start` (`pos_start`);

--
-- AUTO_INCREMENT для таблицы `headers`
--
ALTER TABLE `headers`
MODIFY `id` int(11) NOT NULL AUTO_INCREMENT,AUTO_INCREMENT=2;
--
-- AUTO_INCREMENT для таблицы `header_to_doc`
--
ALTER TABLE `header_to_doc`
MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
'''
import pymysql
from pytextutils.token_splitter import TokenSplitter, TYPE_TOKEN, POSTagger
from pywikiaccessor.wiki_accessor import WikiAccessor
from pywikiaccessor.wiki_iterator import WikiIterator
from pywikiaccessor.wiki_plain_text_index import WikiPlainTextIndex
from pywikiaccessor.redirects_index import RedirectsIndex
import numpy as np
import pytextutils.clustering as k_means

# Класс для построения списка глаголов
class VerbListBuilder (WikiIterator):
    # Порог точности определения части речи
    __TRESHOLD = 0.0005
    
    # Инициализация. Параметры:
    # accessor - класс, который содержит конфигурацию для доступа к индексам дампа Википедии (см. модуль wiki_accessor)
    # docIds = None - список обрабатываемых документов, если надо обработать не все
    # prefix='' - префикс файлов индекса (или таблиц индекса)
    def __init__(self, accessor, docIds = None, prefix=''):
        super(VerbListBuilder, self).__init__(accessor, 1000, docIds,prefix)

    # Функция сохранения данных, вызывается каждые N записей
    def processSave(self,articlesCount):
        pass
    
    # Функция подготовки к построению индекса
    def preProcess(self):
        # коннект к базе, параметры надо вынести в конфиг и получать через accessor
        self.dbConnection = pymysql.connect(host='localhost', port=3306, user='root', passwd='',charset='utf8', db='wikiparse')
        # курсор коннекта для запросов
        self.dbCursor = self.dbConnection.cursor()
        # класс для получения
        self.posTagger = POSTagger()
        # индекс редиректов
        self.redirects = self.accessor.getIndex(RedirectsIndex)
        # индекс текстов статей, очищенных от вики-разметки 
        self.plainTextIndex = self.accessor.getIndex(WikiPlainTextIndex)
        self.clear()
        # список начальных форм глаголов
        self.stems = {}
        # разделялка на слова
        self.wordSplitter = TokenSplitter()
        # запросы  
        self.addStemQuery = "INSERT INTO verbs(stem) VALUES (%s)"
        self.getStemIdQuery = "SELECT id FROM verbs WHERE stem LIKE %s"
        self.insertVerbToDocQuery = "INSERT INTO verb_to_doc(doc_id,verb_id,is_ambig,position,score) VALUES "
        self.queryElement = "(%s, %s, %s, %s, %s)"
        
        # выбираем те записи, которые уже есть
        self.dbCursor.execute("SELECT * FROM verbs ORDER BY id")
        for stem in self.dbCursor.fetchall():
            self.stems[stem[1]] = stem[0] 
    
    # выполняется после завершения построения
    def postProcess(self):
        pass
           
    # очистка индекса
    def clear(self):
        pass

    # определяет или генерирует идентификатор словарной формы глагола
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
             
    # обработка документа     
    def processDocument(self, docId):
        # если редирект, то пропускаем
        if self.redirects.isRedirect(docId):
            return
        # берем очищенный текст
        cleanText = self.plainTextIndex.getTextById(docId)
        if cleanText == None:
            return
        verbs = []
        # делим текст на токены
        self.wordSplitter.split(cleanText)
        tokens = self.wordSplitter.getTokenArray()
        # помечаем токены частями речи
        self.posTagger.posTagging(tokens)
        # выбираем те токены, которые представляют глаголы  
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
        # составляем запрос, который добавит все наши глаголы в базу            
        query = []
        params = []            
        for verb in verbs:
            query.append(self.queryElement)
            params.append(docId)
            params.append(verb["stem"])
            params.append(verb["is_ambig"])
            params.append(verb["pos"])
            params.append(verb["score"])
        
        # выполняем запрос    
        if len(query)>0 :
            self.dbCursor.execute(self.insertVerbToDocQuery+",".join(query),params)
            self.dbConnection.commit()
        #else:
            # print (docId)

# индекс для доступа к спискам глаголов            
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
accessor = WikiAccessor(directory)
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