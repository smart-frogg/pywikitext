# -*- coding: utf-8 -*-
'''
 Модуль индекса типов документов
 
 Индекс требует:
 + базовый индекс доступа к сырым статьям
 + индекс редиректов
 + индекс категорий
 + конфигурационный файл DocumentTypeConfig.json

 Примеры использования:

Инициализация, чтобы примеры работали: 
directory = "C:\\WORK\\science\\onpositive_data\\python\\"
accessor =  wiki_accessor.WikiAccessor(directory)
 
Построение:
bld = DocumentTypeIndexBuilder(accessor)
bld.build()

Проверка, что строится для одной статьи:
titleIndex = accessor.getIndex(TitleIndex)
docId = titleIndex.getIdByTitle('devil may cry 3: dante’s awakening')
bld = DocumentTypeIndexBuilder(accessor)
bld.preProcess()
bld.processDocument(docId)
print(bld.dataToTypes)

Получение информации о типах документов для страниц: 
index = DocumentTypeIndex(accessor)
print(index.getDocTypeById(docId))
print(index.getDocTypeById(titleIndex.getIdByTitle("Арцебарский, Анатолий Павлович")))
print(index.getDocTypeById(titleIndex.getIdByTitle("Санкт-Петербург")))
print(index.getDocTypeById(titleIndex.getIdByTitle('Великая теорема Ферма')))

Получение всех статей одного типа:
pages =index.getDocsOfType('event')

Вывод документов, у которых не определился тип:
dWt = index.getDocsWithoutType()
print(len(dWt))
for docId in dWt:
    print(titleIndex.getTitleById(docId))

Вывод количества документов для каждого типа:
DocumentTypeConfig(directory)
for docType in DocumentTypeConfig.doctypeList:
    r = index.getDocsOfType(docType)
    print(docType+": "+str(len(r)))
'''
import pickle
import json
import re
#from antlr4 import *
#from antlrwiki.gen.wiki_markupLexer import wiki_markupLexer
#from antlrwiki.gen.wiki_markupParser import wiki_markupParser
from abc import ABCMeta, abstractmethod
from pywikiaccessor.wiki_categories import CategoryIndex
from pywikiaccessor.page_types_indexes import RedirectsIndex
from pywikiaccessor.wiki_core import TitleIndex

REDIRECT = "redirect"

# Класс для доступа к конфигу
class DocumentTypeConfig:
    doctypes = None
    propsToDoctypes = {}
    templatesToDoctypes= {}
    prefixesToDoctypes = {}
    categoriesToDoctypes = {}
    doctypeList = []
    ids = {}
    reverseIds = []
    def __new__(cls,directory):
        if not DocumentTypeConfig.doctypes:
            with open(directory + 'config/DocumentTypeConfig.json', encoding="utf8") as data_file:    
                doctypes = json.load(data_file,encoding="utf-8")
                doctypeId = 0
                DocumentTypeConfig.reverseIds.append(REDIRECT)
                DocumentTypeConfig.ids[REDIRECT] = doctypeId 
                for doctype in doctypes:
                    doctype['name'] = doctype['name'].lower()
                    doctype['id'] = doctypeId
                    DocumentTypeConfig.reverseIds.append(doctype['name'])
                    DocumentTypeConfig.ids[doctype['name']] = doctypeId 
                    doctypeId += 1
                    DocumentTypeConfig.doctypeList.append(doctype['name'])
                    if (doctype.get('templates',None)):
                        for template in doctype['templates']:
                            template = template.lower()
                            DocumentTypeConfig.templatesToDoctypes[template] = doctype['id']    
                    if (doctype.get('properties',None)): 
                        for prop in doctype['properties']:
                            prop = prop.lower()
                            DocumentTypeConfig.propsToDoctypes[prop] = doctype['id']
                    if (doctype.get('prefixes',None)): 
                        for prefix in doctype['prefixes']:
                            prefix = prefix.lower()
                            DocumentTypeConfig.prefixesToDoctypes[prefix] = doctype['id']
                    if (doctype.get('categories',None)): 
                        for category in doctype['categories']:
                            category = category.lower()
                            DocumentTypeConfig.categoriesToDoctypes[category] = doctype['id']
        return doctypes 
    @staticmethod
    def getDocTypeByTemplate(template):
        return DocumentTypeConfig.templatesToDoctypes.get(template)
    @staticmethod
    def getDocTypeByProperty(prop):
        return DocumentTypeConfig.propertiesToDoctypes.get(prop)
    @staticmethod
    def getDocTypeByPrefix(prefix):
        return DocumentTypeConfig.propertiesToDoctypes.get(prefix)

# Интерфейс определителя типа документа
class WikiDocTypeParser(metaclass=ABCMeta):
    @abstractmethod
    def getDocType(self,text):
        pass

# Упрощенный способ определения типа документа, парсер просто ищет вхождения соответствующих кострукций для поиска шаблонов и свойств                   
class StupidTemplateParser (WikiDocTypeParser):
    def __init__(self, accessor):
        self.templatePatterns = {}
        self.propertyPatterns = {}
        self.categoryLists = {}
        self.doctypes = DocumentTypeConfig(accessor.directory)
        self.categoryIndex = accessor.getIndex(CategoryIndex)
        for prop in  DocumentTypeConfig.propsToDoctypes.keys():
            self.propertyPatterns[prop] = re.compile('\|[ \t\r\n]*'+prop+'[ \t\r\n]*=')
        for template in  DocumentTypeConfig.templatesToDoctypes.keys():    
            self.templatePatterns[template] = re.compile('\{\{[ \t]*'+template+'[ \t\}\|\r\n]')
        for category in  DocumentTypeConfig.categoriesToDoctypes.keys():
            if not self.categoryLists.get(DocumentTypeConfig.categoriesToDoctypes[category],None):  
                self.categoryLists[DocumentTypeConfig.categoriesToDoctypes[category]] = set() 
            catId = self.categoryIndex.getIdByTitle(category)    
            self.categoryLists[DocumentTypeConfig.categoriesToDoctypes[category]].add(catId)
            self.categoryLists[DocumentTypeConfig.categoriesToDoctypes[category]].update(self.categoryIndex.getSubCatAsSet(catId))
  
    def getDocType(self,docId,text,title):
        result = set()
        preparedText = text.lower()
        preparedTitle = title.lower()

        for template in  DocumentTypeConfig.templatesToDoctypes.keys():
            match = self.templatePatterns[template].search(preparedText)
            if match:
                result.add(DocumentTypeConfig.templatesToDoctypes[template])
                #break
        for prop in  DocumentTypeConfig.propsToDoctypes.keys():
            match = self.propertyPatterns[prop].search(preparedText)
            if match:
                result.add(DocumentTypeConfig.propsToDoctypes[prop])
                #break
        for docType in self.categoryLists.keys():
            docCats = self.categoryIndex.getPageDirectCategories(docId)
            if any(cat in self.categoryLists[docType] for cat in docCats): 
                result.add(docType)
                #break
        for prefix in  DocumentTypeConfig.prefixesToDoctypes.keys():
            if preparedTitle.startswith(prefix+":"):
                result.add(DocumentTypeConfig.prefixesToDoctypes[prefix])
        return result    
        
'''
# Определитель типа на основе парсера ANTLR    
class ANTLRTemplateParser (WikiDocTypeParser):
    def __init__(self,directory):
        self.TERMINAL_ELEMENT = "<class 'antlr4.tree.Tree.TerminalNodeImpl'>"
        self.TEMPLATE_CONTEXT = "<class 'gen.wiki_markupParser.wiki_markupParser.TemplateContext'>"    
        self.TEMPLATE_ELEMENT = "<class 'gen.wiki_markupParser.wiki_markupParser.Template_elementContext'>"
        self.doctypes = DocumentTypeConfig(directory)
    def getTemplateNames(self,tree):
        templates = []
        for c in tree.children:
            if str(type(c)) != self.TERMINAL_ELEMENT:
                for c1 in c.children:
                    if str(type(c1)) == self.TEMPLATE_CONTEXT:
                        for c2 in c1.children:
                            if str(type(c2)) == self.TEMPLATE_ELEMENT:
                                templates.add({ 'text': c2.getText().strip().lower(), 'elements': c1})
                                break
        return templates
        
    def getPropertiesNames(self,tree):
        properties = []
        isFirst = True
        for c in tree.children:
            if str(type(c)) == "<class 'gen.wiki_markupParser.wiki_markupParser.Template_elementContext'>"  and not isFirst:
                properties.add(c.getText())
        return properties    
    
    def getDocType(self,text,title):
        result = None
        lexer = wiki_markupLexer(text)
        stream = CommonTokenStream(lexer)
        parser = wiki_markupParser(stream)
        tree = parser.wiki_article()
        templateNames = self.getTemplateNames(tree)
        for token in templateNames:
            result = DocumentTypeConfig.getDocTypeByTemplate(token['text'])
            if result :
                break
            for prop in self.getPropertiesNames(token['elements']):
                docType = DocumentTypeConfig.getDocTypeByProperty(prop.strip().lower())
                if docType:
                    result = docType
                    break                        
        return result        
'''
                                    
from pywikiaccessor.wiki_core import WikiIterator,WikiFileIndex
# Индекс типов документов
class DocumentTypeIndex(WikiFileIndex):
    def __init__(self, wikiAccessor):
        super(DocumentTypeIndex, self).__init__(wikiAccessor)
        self.doctypes = DocumentTypeConfig(wikiAccessor.directory)
    
    def getDictionaryFiles(self): 
        return ['doctype_IdToDocTypes','doctype_DocTypesToId','doctype_DocWithoutTypes']
                        
    def getDocTypeById(self, ident):
        return self.dictionaries['doctype_IdToDocTypes'].get(ident, None)
    
    def isDocType(self, ident, docType):
        dtList = self.getDocTypeById(ident)
        if not dtList:
            return False
        idToFind = DocumentTypeConfig.ids[docType.lower()]
        if isinstance(dtList, set):
            return idToFind in dtList
        else:
            return idToFind == dtList

    def haveDocType(self, ident, docTypeList):
        
        dtList = self.getDocTypeById(ident)
        if not dtList:
            return False
        docTypeIds = set()
        for docTypeName in docTypeList:
            id = DocumentTypeConfig.ids[docTypeName.lower()]
            if id: 
                docTypeIds.add(id)
        if isinstance(dtList, set):
            for item in dtList:
                if item in docTypeIds:
                    return True
            return False
        else:
            return dtList in docTypeIds


    def getDocsOfType(self,docType):
        return self.dictionaries['doctype_DocTypesToId'][docType]

    def getDocsWithoutType(self):
        return list(self.dictionaries['doctype_DocWithoutTypes'])
        #res = []
        #for docId in self.dictionaries['doctype_IdToDocTypes'].keys():
        #    if len(self.dictionaries['doctype_IdToDocTypes'][docId]) == 0:
        #        res.append(docId)
        #return res

    def getBuilder(self):
        return DocumentTypeIndexBuilder(self.accessor)
   
    def getName(self):
        return "Document types"

# Билдер индекса типов документов
class DocumentTypeIndexBuilder (WikiIterator):
    
    def __init__(self, accessor):
        self.CODE = 'utf-8'
        self.docTypeParser = StupidTemplateParser(accessor)
        super(DocumentTypeIndexBuilder, self).__init__(accessor, 10000)

    def processSave(self,articlesCount):
        return

    def postProcess(self):
        with open(self.getFullFileName('doctype_DocWithoutTypes.pcl'), 'wb') as f:
            pickle.dump(frozenset(self.docWithoutTypes), f, pickle.HIGHEST_PROTOCOL)               
        with open(self.getFullFileName('doctype_IdToDocTypes.pcl'), 'wb') as f:
            pickle.dump(self.dataToTypes, f, pickle.HIGHEST_PROTOCOL)
        
        compactDataToIds = {}
        for docType, docSet in self.dataToIds.items():
            compactDataToIds[docType] = frozenset(docSet)
        with open(self.getFullFileName('doctype_DocTypesToId.pcl'), 'wb') as f:
            pickle.dump(compactDataToIds, f, pickle.HIGHEST_PROTOCOL)

    def preProcess(self):
        self.dataToTypes = {}
        self.dataToIds = {}
        self.docWithoutTypes = set()
        self.redirects = self.accessor.getIndex(RedirectsIndex)
        self.titleIndex = self.accessor.getIndex(TitleIndex)
        self.dataToIds[REDIRECT] = set()
             
    def clear(self):
        # os.remove(self.accessor.directory + 'IdToDocTypes.pcl')
        # os.remove(self.accessor.directory + 'DocTypesToId.pcl')
        pass
                                              
    def processDocument(self, docId):
        if self.redirects.isRedirect(docId):
            self.dataToTypes[docId] = REDIRECT
            self.dataToIds[REDIRECT].add(docId)
            return
        title = self.titleIndex.getTitleById(docId)
        text = self.wikiIndex.getTextArticleById(docId)
        #print(text)
        types = self.docTypeParser.getDocType(docId,text,title)
        if (len(types) == 0):
            self.docWithoutTypes.add(docId)
        else:
            if (len(types) == 1):
                self.dataToTypes[docId] = list(types)[0]
            else:
                self.dataToTypes[docId] = frozenset(types)
            for docType in types:
                if not self.dataToIds.get(docType,None):
                    self.dataToIds[docType] = set()
                self.dataToIds[docType].add(docId)

if __name__ == '__main__':
    from pywikiaccessor.wiki_core import WikiConfiguration            
    directory = "C:/WORK/science/python-data/"
    accessor =  WikiConfiguration(directory)
    # index = DocumentTypeIndex(accessor)
#Построение:
    bld = DocumentTypeIndexBuilder(accessor)
   
    #titleIndex = accessor.getIndex(TitleIndex)
    #docId = titleIndex.getIdByTitle('Президентские выборы в Киргизии (2017)')
    #bld = DocumentTypeIndexBuilder(accessor)
    #bld.preProcess()
    #bld.processDocument(docId)
    #print(bld.dataToTypes)
    bld.build()

#titleIndex = accessor.getIndex(TitleIndex)
#index = DocumentTypeIndex(accessor)
#r = index.getDocsOfType('software')
#print(len(r))
#import codecs
#with codecs.open( directory+'titles_soft.txt', 'w', 'utf-8' ) as f:
#    for docId in r:
#        f.write(titleIndex.getTitleById(docId)+'\n')
#    f.close()
