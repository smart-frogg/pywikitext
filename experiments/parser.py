import codecs
import xml.sax


class WikiContentHandler(xml.sax.ContentHandler):
    
    def __init__(self, idTitle, idShift, indexedText):
        xml.sax.ContentHandler.__init__(self)

        self.CODE = 'utf-8'

        self.idTitle = open(idTitle, 'wb')
        self.idShift = open(idShift, 'wb')
        self.indexedText = open(indexedText, 'wb')

        self.shift = 0

        self.inTitle = False
        self.inText = False
        self.inId = False
        self.inRevision = False

    def startElement(self, name, attr):
        if name == 'title':
            self.inTitle = True
        if name == 'revision':
            self.inRevision = True
        if (name == 'id') & (self.inRevision != True):
            self.inId = True
        if name == 'text':
            self.inText = True

    def endElement(self, name):
        if name == 'title':
            self.inTitle = False
        if name == 'revision':
            self.inRevision = False
        if (name == 'id') & (self.inRevision != True):
            self.inId = False
        if name == 'text':
            self.inText = False
            self.shift += 2
            self.indexedText.write(bytes('\0', self.CODE))

    def characters(self, content):
        if self.inTitle:
            self.idTitle.write(bytes(content, self.CODE))
            self.idTitle.write(bytes('|', self.CODE))
        if self.inId:
            self.idTitle.write(bytes(content, self.CODE))
            self.idTitle.write(bytes('\r\n', self.CODE))

            self.idShift.write(bytes(content, self.CODE))
            self.idShift.write(bytes('|', self.CODE))
            self.idShift.write(bytes(str(self.shift), self.CODE))
            self.idShift.write(bytes('\r\n', self.CODE))
        if self.inText:
            self.indexedText.write(bytes(content, self.CODE))
            self.shift += len(bytes(content, self.CODE))

    def endDocument(self):
        self.indexedText.close()
        self.idShift.close()
        self.idTitle.close()


def main(wiki, idTitle, idShift, indexedText):
    inputXml = codecs.open(wiki, 'r', 'utf-8')
    xml.sax.parse(inputXml, WikiContentHandler(idTitle, idShift, indexedText))

dir = "C:\\WORK\\science\\onpositive_data\\python\\"
#main('30000.xml', 'title_and_id.dat', 'id_and_shift.dat', 'indexed_wiki.dat')
main(dir+'ruwiki.xml', dir+'title_and_id.bin', dir+'id_and_shift.bin', dir+'indexed_wiki.bin')