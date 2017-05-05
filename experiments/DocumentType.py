# -*- coding: utf-8 -*-
import pickle
import json
import re
from antlr4 import *
#from antlrwiki.gen.wiki_markupLexer import wiki_markupLexer
#from antlrwiki.gen.wiki_markupParser import wiki_markupParser
from abc import ABCMeta, abstractmethod
from pywikiaccessor.wiki_categories import CategoryIndex

REDIRECT = "REDIRECT"
class DocumentTypeConfig:
    doctypes = None
    propsToDoctypes = {}
    templatesToDoctypes= {}
    prefixesToDoctypes = {}
    categoriesToDoctypes = {}
    doctypeList = []
    def __new__(cls,directory):
        if not DocumentTypeConfig.doctypes:
            with open(directory + 'DocumentTypeConfig.json', encoding="utf8") as data_file:    
                doctypes = json.load(data_file,encoding="utf-8")
                for doctype in doctypes:
                    doctype['name'] = doctype['name'].lower()
                    DocumentTypeConfig.doctypeList.append(doctype['name'])
                    if (doctype.get('templates',None)):
                        for template in doctype['templates']:
                            template = template.lower()
                            DocumentTypeConfig.templatesToDoctypes[template] = doctype['name']    
                    if (doctype.get('properties',None)): 
                        for prop in doctype['properties']:
                            prop = prop.lower()
                            DocumentTypeConfig.propsToDoctypes[prop] = doctype['name']
                    if (doctype.get('prefixes',None)): 
                        for prefix in doctype['prefixes']:
                            prefix = prefix.lower()
                            DocumentTypeConfig.prefixesToDoctypes[prefix] = doctype['name']
                    if (doctype.get('categories',None)): 
                        for category in doctype['categories']:
                            category = category.lower()
                            DocumentTypeConfig.categoriesToDoctypes[category] = doctype['name']
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

class WikiDocTypeParser(metaclass=ABCMeta):
    @abstractmethod
    def getDocType(self,text):
        pass
                   
class StupidTemplateParser (WikiDocTypeParser):
    def __init__(self, accessor):
        self.templatePatterns = {}
        self.propertyPatterns = {}
        self.categoryLists = {}
        self.doctypes = DocumentTypeConfig(accessor.directory)
        self.categoryIndex = accessor.categoryIndex
        for prop in  DocumentTypeConfig.propsToDoctypes.keys():
            self.propertyPatterns[prop] = re.compile('\|[ \t\r\n]*'+prop+'[ \t\r\n]*=')
        for template in  DocumentTypeConfig.templatesToDoctypes.keys():    
            self.templatePatterns[template] = re.compile('\{\{[ \t]*'+template+'[ \t\}\|\r\n]')
        for category in  DocumentTypeConfig.categoriesToDoctypes.keys():
            if not self.categoryLists.get(DocumentTypeConfig.categoriesToDoctypes[category],None):  
                self.categoryLists[DocumentTypeConfig.categoriesToDoctypes[category]] = set() 
            catId = self.categoryIndex.getIdByTitle(category)    
            self.categoryLists[DocumentTypeConfig.categoriesToDoctypes[category]].update(self.categoryIndex.getSubCatAsSet(catId))
  
    def getDocType(self,docId,text,title):
        result = set()
        preparedText = text.lower()
        preparedTitle = title.lower()

        for template in  DocumentTypeConfig.templatesToDoctypes.keys():
            match = self.templatePatterns[template].search(preparedText)
            if match:
                result.add(DocumentTypeConfig.templatesToDoctypes[template])
                break
        for prop in  DocumentTypeConfig.propsToDoctypes.keys():
            match = self.propertyPatterns[prop].search(preparedText)
            if match:
                result.add(DocumentTypeConfig.propsToDoctypes[prop])
                break
        for docType in self.categoryLists.keys():
            docCats = self.categoryIndex.getPageDirectCategories(docId)
            if any(cat in self.categoryLists[docType] for cat in docCats): 
                result.add(docType)
                break
        for prefix in  DocumentTypeConfig.prefixesToDoctypes.keys():
            if preparedTitle.startswith(prefix+":"):
                result.add(DocumentTypeConfig.prefixesToDoctypes[prefix])
        return result    
        
'''    
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
                                    
from pywikiaccessor import wiki_iterator,wiki_accessor, wiki_file_index
class DocumentTypeIndex(wiki_file_index.WikiFileIndex):
    def __init__(self, wikiAccessor):
        super(DocumentTypeIndex, self).__init__(wikiAccessor)
    
    def getDictionaryFiles(self): 
        return ['IdToDocTypes','DocTypesToId']
                        
    def getDocTypeById(self, ident):
        return self.dictionaries['IdToDocTypes'].get(ident, None)
    
    def getDocsOfType(self,docType):
        return self.dictionaries['DocTypesToId'][docType]

    def getDocsWithoutType(self):
        res = []
        for docId in self.dictionaries['IdToDocTypes'].keys():
            if len(self.dictionaries['IdToDocTypes'][docId]) == 0:
                res.append(docId)
        return res

    def getBuilder(self):
        return DocumentTypeIndexBuilder(self.accessor)
   
    def getName(self):
        return "Document types"


class DocumentTypeIndexBuilder (wiki_iterator.WikiIterator):
    
    def __init__(self, accessor):
        self.CODE = 'utf-8'
        self.docTypeParser = StupidTemplateParser(accessor)

        #self.doctypes = DocumentTypeConfig(accessor.directory)
        super(DocumentTypeIndexBuilder, self).__init__(accessor, 10000)
        #with open(self.accessor.directory + 'DocumentTypeConfig.json', encoding="utf8") as data_file:    
        #    self.doctypes = json.load(data_file)


    def processSave(self,articlesCount):
        return

    def postProcess(self):
        with open(self.accessor.directory + 'IdToDocTypes.pcl', 'wb') as f:
            pickle.dump(self.dataToTypes, f, pickle.HIGHEST_PROTOCOL)
        with open(self.accessor.directory + 'DocTypesToId.pcl', 'wb') as f:
            pickle.dump(self.dataToIds, f, pickle.HIGHEST_PROTOCOL)

    def preProcess(self):
        self.dataToTypes = {}
        self.dataToIds = {}
        self.redirects = self.accessor.redirectIndex
        self.titleIndex = self.accessor.titleIndex
        self.dataToIds[REDIRECT] = set()
             
    def clear(self):
        return 
                                              
    def processDocument(self, docId):
        if self.redirects.isRedirect(docId):
            self.dataToTypes[docId] = REDIRECT
            self.dataToIds[REDIRECT].add(docId)
            return
        title = self.accessor.titleIndex.getTitleById(docId)
        text = self.accessor.baseIndex.getTextArticleById(docId)
        #print(text)
        self.dataToTypes[docId] = self.docTypeParser.getDocType(docId,text,title)
        for docType in self.dataToTypes[docId]:
            if not self.dataToIds.get(docType,None):
                self.dataToIds[docType] = set()
            self.dataToIds[docType].add(docId)
            

directory = "C:\\WORK\\science\\onpositive_data\\python\\"
accessor =  wiki_accessor.WikiAccessorFactory.getAccessor(directory)
titleIndex = accessor.titleIndex
#docId = titleIndex.getIdByTitle('Великая теорема Ферма')

bld = DocumentTypeIndexBuilder(accessor)
#bld.preProcess()
#bld.processDocument(docId)
#print(bld.dataToTypes)
bld.build() 
  
#print(titleIndex.getTitleById(5243160))
#bld = MoscowSearcher(accessor)
#bld.build()
#print(bld.count)     

index = DocumentTypeIndex(accessor)
#print(index.getDocTypeById(titleIndex.getIdByTitle("Арцебарский, Анатолий Павлович")))
#print(index.getDocTypeById(titleIndex.getIdByTitle("Пушкин, Александр Сергеевич")))
#print(index.getDocTypeById(titleIndex.getIdByTitle("Хрущёв, Никита Сергеевич")))
#print(index.getDocTypeById(titleIndex.getIdByTitle("Бегичев, Матвей Семёнович")))
#print(index.getDocTypeById(titleIndex.getIdByTitle("Санкт-Петербург")))
#print(index.getDocTypeById(titleIndex.getIdByTitle("Екатеринбург")))
#print(index.getDocTypeById(titleIndex.getIdByTitle('Великая теорема Ферма')))

#print(index.getDocTypeById(titleIndex.getIdByTitle("категория:москва")))
#print(index.getDocTypeById(10989))
#print(titleIndex.getTitleById(10989))
#print(accessor.redirectIndex.getRedirect(titleIndex.getIdByTitle("Москва (город)")))

dWt = index.getDocsWithoutType()
print(len(dWt))
DocumentTypeConfig(directory)
for docType in DocumentTypeConfig.doctypeList:
    r = index.getDocsOfType(docType)
    print(docType+": "+str(len(r)))
#for docId in dWt:
#    print(titleIndex.getTitleById(docId))

#bld = DocumentTypeIndexBuilder(accessor)
#bld.build()
#titleIndex = accessor.titleIndex
#

#bld.preProcess()
#doc_id = titleIndex.getIdByTitle("категория:москва") 
#bld.processDocument(doc_id)                
#print(bld.data)

#doc_id = titleIndex.getIdByTitle("категория:министры культуры и туризма азербайджана") 
#bld.processDocument(doc_id)                
#print(bld.data)
#doc_id = titleIndex.getIdByTitle("Барнаул")
#bld.processDocument(doc_id)                
#print(bld.data)
