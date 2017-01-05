# -*- coding: utf-8 -*-
import pickle


class WikiIndex:
    def __init__(self, directory):
        self.directory = directory
        with open(self.directory + 'titleIndex' + '.pkl', 'rb') as f:
            self.titleDict = pickle.load (f)
            f.close()
        with open(self.directory + 'plainTextIndex' + '.pkl', 'rb') as f:
            self.textDict = pickle.load(f)
            f.close()
        self.textFile = open(directory+"plainText.dat", 'rb')
        self.titleFile = open(directory+"title.dat", 'rb')    

    def getTitleArticleById(self, ident):
        if not self.titleDict.get(ident, None):
            return "Нет статьи с таким идентификатором."
        else:
            self.titleFile.seek(self.titleDict[ident],0)
            lenBytes = self.titleFile.read(4)
            length = int.from_bytes(lenBytes, byteorder='big')
            return self.titleFile.read(length).decode("utf-8")
            

    def getTextArticleById(self, ident):
        if not self.textDict.get(ident, None):
            return "Нет статьи с таким идентификатором."
        else:
            self.textFile.seek(self.textDict[ident],0)
            lenBytes = self.textFile.read(4)
            length = int.from_bytes(lenBytes, byteorder='big')
            return self.textFile.read(length).decode("utf-8") 

# directory = "C:\\WORK\\science\\onpositive_data\\python\\"
# pwXML = WikiIndex(directory)
# print(pwXML.getTitleArticleById(7))
# print(pwXML.getTextArticleById(7))