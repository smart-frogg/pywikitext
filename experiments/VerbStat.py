# -*- coding: utf-8 -*-
import pickle
import os.path

import TokenSplitter
import TextToken
import math
import CachedPymorphyMorph
from pywiki import WikiIterator,WikiPlainTextIndex,RedirectsIndex


class VerbStat (WikiIterator.WikiIterator):
    def __init__(self, directory):
        super(VerbStat, self).__init__(directory, 100000)

    def processSave(self,articlesCount):
        postfix = str(self.prevArticlesCount) + '.pkl'   
        with open(self.directory + 'countVerbs_' + postfix , 'wb') as f:
            pickle.dump(self.countVerbsDict, f, pickle.HIGHEST_PROTOCOL)
        with open(self.directory + 'countWords_' + postfix, 'wb') as f:
            pickle.dump(self.countWordsDict, f, pickle.HIGHEST_PROTOCOL)
        with open(self.directory + 'countMultivalVerbs_' + postfix, 'wb') as f:
            pickle.dump(self.countMultivalVerbsDict, f, pickle.HIGHEST_PROTOCOL)
        with open(self.directory + 'countMultivalWords_' + postfix, 'wb') as f:
            pickle.dump(self.countMultivalWordsDict, f, pickle.HIGHEST_PROTOCOL)

    def load(self):
        postfix = 0;
        filename = self.directory + 'countVerbs_' + str(postfix) + '.pkl'
        self.countVerbsDict = {}
        self.countWordsDict = {}
        self.countMultivalVerbsDict = {}    
        self.countMultivalWordsDict = {}
        
          
        while os.path.isfile(filename):
            with open(filename, 'rb') as f:
                tmpDict = pickle.load(f)
            self.countVerbsDict = {**self.countVerbsDict, **tmpDict}

            with open(self.directory + 'countWords_' + str(postfix) + '.pkl', 'rb') as f:
                tmpDict = pickle.load(f)
            self.countWordsDict = {**self.countWordsDict, **tmpDict}
            
            with open(self.directory + 'countMultivalVerbs_' + str(postfix) + '.pkl', 'rb') as f:
                tmpDict = pickle.load(f)
            self.countMultivalVerbsDict = {**self.countMultivalVerbsDict, **tmpDict}  
            
            with open(self.directory + 'countMultivalWords_' + str(postfix) + '.pkl', 'rb') as f:
                tmpDict = pickle.load(f)
            self.countMultivalWordsDict = {**self.countMultivalWordsDict, **tmpDict}
               
            postfix += self.fileCount
            filename = self.directory + 'countVerbs_' + str(postfix) + '.pkl'
    
    def avgDict(self,dictionary):
        avg = 0
        for key in dictionary:
            avg += dictionary[key]
        avg /= len(dictionary)
        derivation = 0;     
        for key in dictionary:
            derivation += (avg-dictionary[key]) * (avg-dictionary[key])
        derivation /= len(dictionary)
        return [avg, math.sqrt(derivation)] 
                
    def avgCountVerbs(self):
        return self.avgDict(self.countVerbsDict)
    def avgCountWords(self):
        return self.avgDict(self.countWordsDict)
    def avgCountMultivalVerbs(self):
        return self.avgDict(self.countMultivalVerbsDict)
    def avgCountMultivalWords(self):
        return self.avgDict(self.countMultivalWordsDict)
    
    def preProcess(self):
        self.morph = CachedPymorphyMorph.CachedPymorphyMorph(self.directory)
        self.redirects = RedirectsIndex.RedirectsIndex(self.directory)
        self.plainTextIndex = WikiPlainTextIndex.WikiPlainTextIndex(self.directory)
        self.clear()
        self.wordSplitter = TokenSplitter.TokenSplitter()  
    
    def postProcess(self):
        return
           
    def clear(self):
        self.countVerbsDict = {}
        self.countWordsDict = {}
        self.countMultivalVerbsDict = {}    
        self.countMultivalWordsDict = {} 

    def processDocument(self, docId):
        if self.redirects.isRedirect(docId):
            return
        cleanText = self.plainTextIndex.getTextById(docId)
        if cleanText == None:
            return
        countVerbs = 0
        countWords = 0
        countMultivalVerbs = 0    
        countMultivalWords = 0  

        
        self.wordSplitter.split(cleanText)
        tokens = self.wordSplitter.getTokenArray()
          
        for token in tokens:
            if (token.tokenType == TextToken.TYPE_TOKEN):
                countWords += 1
                parse_result = self.morph.parse(token.token)
                if(parse_result == None):
                    continue
                count = len(parse_result)
                isVerb = False
                for res in parse_result:
                    if (res.tag.POS == 'VERB'):
                        isVerb = True
                if(count > 1):
                    countMultivalWords += 1
                if(isVerb):
                    countVerbs += 1
                    if(count > 1):
                        countMultivalVerbs += 1 
        self.countVerbsDict[docId] = countVerbs
        self.countWordsDict[docId] = countWords
        self.countMultivalVerbsDict[docId] = countMultivalVerbs    
        self.countMultivalWordsDict[docId] = countMultivalWords     
            
directory = "C:\\WORK\\science\\onpositive_data\\python\\"
#wi = WikiIndex.WikiIndex(directory)
#print(wi.getTextArticleById(4))
vs = VerbStat(directory)
#vs.build()
vs.load()
val = vs.avgCountVerbs()
print("count verbs: "+str(val[0])+", "+str(val[1]))
val = vs.avgCountWords()
print("count words: "+str(val[0])+", "+str(val[1]))
val = vs.avgCountMultivalVerbs()
print("count multival verbs: "+str(val[0])+", "+str(val[1]))
val = vs.avgCountMultivalWords()
print("count multival words: "+str(val[0])+", "+str(val[1]))
