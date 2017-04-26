# -*- coding: utf-8 -*-
import pickle
import json
import re
from antlr4 import *
from antlrwiki.gen.wiki_markupLexer import wiki_markupLexer
from antlrwiki.gen.wiki_markupParser import wiki_markupParser
from abc import ABCMeta, abstractmethod

class DocumentTypeConfig:
    doctypes = None
    propsToDoctypes = {}
    templatesToDoctypes= {}
    def __new__(cls,directory):
        if not DocumentTypeConfig.doctypes:
            with open(directory + 'DocumentTypeConfig.json', encoding="utf8") as data_file:    
                doctypes = json.load(data_file,encoding="utf-8")
                for doctype in doctypes:
                    doctype['name'] = doctype['name'].lower()
                    for template in doctype['templates']:
                        template['name'] = template['name'].lower()
                        DocumentTypeConfig.templatesToDoctypes[template['name']] = doctype['name']    
                    if (doctype.get('properties',None)): 
                        for prop in doctype['properties']:
                            prop['name'] = prop['name'].lower()
                            DocumentTypeConfig.propsToDoctypes[prop['name']] = doctype['name']
        return doctypes 
    @staticmethod
    def getDocTypeByTemplate(template):
        return DocumentTypeConfig.templatesToDoctypes.get(template)
    @staticmethod
    def getDocTypeByProperty(property):
        return DocumentTypeConfig.propertiesToDoctypes.get(property)

class WikiDocTypeParser(metaclass=ABCMeta):
    @abstractmethod
    def getDocType(self,text):
        pass
                   
class StupidTemplateParser (WikiDocTypeParser):
    def __init__(self, directory):
        self.templatePatterns = {}
        self.propertyPatterns = {}
        self.doctypes = DocumentTypeConfig(directory)
        for property in  DocumentTypeConfig.propsToDoctypes.keys():
            self.propertyPatterns[property] = re.compile('\|[ \t\r\n]*'+property+'[ \t\r\n]*=', re.VERBOSE)
        for template in  DocumentTypeConfig.templatesToDoctypes.keys():    
            self.templatePatterns[template] = re.compile('\{\{[ \t]*'+template, re.VERBOSE)
  
    def getDocType(self,text):
        result = None
        for template in  DocumentTypeConfig.templatesToDoctypes.keys():
            match = self.templatePatterns[template].search(text.lower())
            if match:
                result = DocumentTypeConfig.templatesToDoctypes[template]
                break
        if not result:
            for property in  DocumentTypeConfig.propsToDoctypes.keys():
                match = self.propertyPatterns[property].search(text.lower())
                if match:
                    result = DocumentTypeConfig.propsToDoctypes[property]
                    break
        return result    
        
    
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
    
    def getDocType(self,text):
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
                                 
class DocumentTypeIndex:
    def __init__(self, directory):
        self.directory = directory
        self.doctypes = DocumentTypeConfig(directory)
        with open(self.directory + 'DocTypes.pcl', 'rb') as f: 
            self.data = pickle.load(f)
            f.close()

from pywikiaccessor import wiki_iterator,wiki_accessor
class DocumentTypeIndexBuilder (wiki_iterator.WikiIterator):
    
    def __init__(self, accessor):
        self.CODE = 'utf-8'
        self.docTypeParser = StupidTemplateParser(accessor.directory)

        #self.doctypes = DocumentTypeConfig(accessor.directory)
        super(DocumentTypeIndexBuilder, self).__init__(accessor, 10000)
        #with open(self.accessor.directory + 'DocumentTypeConfig.json', encoding="utf8") as data_file:    
        #    self.doctypes = json.load(data_file)


    def processSave(self,articlesCount):
        return

    def postProcess(self):
        with open(self.accessor.directory + 'DocTypes.pcl', 'wb') as f:
            pickle.dump(self.data, f, pickle.HIGHEST_PROTOCOL)

    def preProcess(self):
        self.data = {}
        self.redirects = self.accessor.redirectIndex
             
    def clear(self):
        return 
                                              
    def processDocument(self, docId):
        if self.redirects.isRedirect(docId):
            return
        text = self.accessor.baseIndex.getTextArticleById(docId).lower()
        #print(text)
        self.data[docId] = self.docTypeParser.getDocType(text)
            

directory = "C:\\WORK\\science\\onpositive_data\\python\\"
accessor =  wiki_accessor.WikiAccessorFactory.getAccessor(directory)
bld = DocumentTypeIndexBuilder(accessor)
bld.build()
#titleIndex = accessor.titleIndex
#
#bld.preProcess()
#doc_id = titleIndex.getIdByTitle("Арцебарский, Анатолий Павлович") 
#bld.processDocument(doc_id)                
#print(bld.data)
#doc_id = titleIndex.getIdByTitle("Барнаул")
#bld.processDocument(doc_id)                
#print(bld.data)
