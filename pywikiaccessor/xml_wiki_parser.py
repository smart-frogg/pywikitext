# -*- coding: utf-8 -*-
import codecs
import pickle
import xml.sax

'''
SAX-парсер xml-дампа Википедии
Используется при построении базового индекса
Пример использования:
directory = "C:\\WORK\\science\\onpositive_data\\python\\"
main('articles.xml', directory)
'''

class XMLWikiParser(xml.sax.ContentHandler):
    
    def __init__(self, directory):
        xml.sax.ContentHandler.__init__(self)

        self.CODE = 'utf-8'

        self.textFile = open(directory+"text.dat", 'wb')
        self.directory = directory;
        
        self.inTitle = False
        self.inText = False
        self.inId = False
        self.inRevision = False
        self.titleDict = {}
        self.textDict = {}
        self.textShift = 0
        self.curId = -1;
        self.textShiftToSave = 0;
        self.articlesCount = 0;

    def startElement(self, name, attr):
        if name == 'title':
            self.inTitle = True
            self.curTitle = ''
        if name == 'revision':
            self.inRevision = True
        if (name == 'id') & (self.inRevision != True):
            self.inId = True
        if name == 'text':
            self.inText = True
            self.text = ''
            self.length = 0
            self.textShiftToSave = self.textShift;

    def endElement(self, name):
        if name == 'title':
            self.inTitle = False
        if name == 'revision':
            self.inRevision = False
        if (name == 'id') & (self.inRevision != True):
            self.inId = False
        if name == 'text':
            self.inText = False
            byteArray = self.text.encode(self.CODE)
            length = len(byteArray)
            self.textFile.write(length.to_bytes(4, byteorder='big'))
            self.textFile.write(byteArray)
            self.textShift += length+4
        if name == 'page':
            self.textDict[self.curId] = self.textShiftToSave
            self.titleDict[self.curId] = self.curTitle
            self.articlesCount += 1
            if (self.articlesCount % 10000 == 0) :
                print('Complete '+str(self.articlesCount)+' articles')
                
    def characters(self, content):
        if self.inTitle:
            self.curTitle += content
        if self.inId:
            self.curId = int(content)
        if self.inText:
            self.text += content
    def endDocument(self):
        self.textFile.close()
        with open(self.directory + 'title_RawTitleIndex.pcl', 'wb') as f:
            pickle.dump(self.titleDict, f, pickle.HIGHEST_PROTOCOL)
        with open(self.directory + 'textIndex.pcl', 'wb') as f:
            pickle.dump(self.textDict, f, pickle.HIGHEST_PROTOCOL)       

def main(wikiDumpFile, directory):
    inputXml = codecs.open(directory+wikiDumpFile, 'r', 'utf-8')
    xml.sax.parse(inputXml, XMLWikiParser(directory))
    print('Finish!')

