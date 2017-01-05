# -*- coding: utf-8 -*-
import codecs
import re


class ParsedWikiXML:
    def __init__(self, idTitle, idShift, indexedText):
        self.idTitle = codecs.open(idTitle, 'r', 'utf-8')
        self.idShift = codecs.open(idShift, 'r', 'utf-8')
        self.indexedText = codecs.open(indexedText, 'rb')

        self.dictOfInfoAboutArticle = {}

        allIdTitle = self.idTitle.readlines()
        allIdShift = self.idShift.readlines()

        for i in range(len(allIdShift)):
            ident = int(re.sub('^\s+|^\n+|\s+$|\n+$', '', allIdShift[i].split('|')[0]))
            shift = re.sub('^\s+|^\n+|\s+$|\n+$', '', allIdShift[i].split('|')[1])
            title = re.sub('^\s+|^\n+|\s+$|\n+$', '', allIdTitle[i].split('|')[0])
            self.dictOfInfoAboutArticle[ident] = (title, shift)


    def getTitleArticleById(self, ident):
        if not self.dictOfInfoAboutArticle.get(ident, None):
            return "Нет статьи с таким идентификатором."
        else:
            return self.dictOfInfoAboutArticle.get(ident)[0]

    def getTextArticleById(self, ident):
        if not self.dictOfInfoAboutArticle.get(ident, None):
            return "Нет статьи с таким идентификатором."
        else:
            textOfArticle = []
            position = int(self.dictOfInfoAboutArticle.get(ident)[1])
            self.indexedText.seek(position, 0)
            while True:
                char = self.indexedText.read(1)
                if not char:
                    break
                elif char == b'\x00':
                    break
                textOfArticle.append(char)
            return b''.join(textOfArticle).decode('utf-8')
dir = "C:\\WORK\\science\\onpositive_data\\python\\"
pwXML = ParsedWikiXML(dir+'title_and_id.bin', dir+'id_and_shift.bin', dir+'indexed_wiki.bin')
print(pwXML.getTitleArticleById(7))
print(pwXML.getTextArticleById(7))