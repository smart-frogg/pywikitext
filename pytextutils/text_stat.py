# -*- coding: utf-8 -*-
from pytextutils.token_splitter import Token, TokenSplitter, POSTagger, TYPE_SIGN,TYPE_TOKEN
from collections import Counter
import pickle
import codecs

class TextStat:
    def __init__(self,file):
        self.file = file
        with codecs.open(self.file, 'r', "utf-8") as myfile:
            self.text=myfile.readlines()
        
        self.clearText()
        self.tokenSplitter = TokenSplitter()
        self.posTagger = POSTagger()
        
    def __clearWraps(self):
        ind = 0
        while ind < len(self.text):
            curStr = self.text[ind].strip()
            if len(curStr)>=2 :
                while curStr[-1]=='-' and not curStr[-2]==' ' and ind < len(self.text) :
                    curStr = curStr[:-1] + self.text[ind+1].strip()
                    del self.text[ind+1]  
            self.text[ind] = curStr
            ind+=1
    def __concatStrings(self):
        text = ' '.join(self.text)
        self.text = text
        
    def clearText(self):
        self.__clearWraps()
        self.__concatStrings()
    
    def getStem(self,token):
        return token.POS[0]['normalForm'].replace('ё','е')
    
    def buildPOSSurface(self, minWindowSize = 10, maxWindowSize = 300):
        self.tokenSplitter.split(self.text)
        tokens = self.tokenSplitter.getTokenArray()  
        self.posTagger.posTagging(tokens) 
        self.data = {
            "DOTS": {},
            "COMMAS": {},
            "NOUNS": {},
            "VERBS": {},
            "ADJS": {},
            "FUNC": {},
            "UNIQUE_NOUNS": {},
            "UNIQUE_VERBS": {},
            "UNIQUE_ADJS": {},
            "UNIQUE_FUNC": {},
        }
        
        setNoun = Counter();
        setAdj = Counter();
        setVerb = Counter();
        setFunc = Counter();
        sumNoun = 0;
        sumVerb = 0;
        sumAdj = 0;
        sumFunc = 0;
        sumDots = 0;
        sumCommas = 0;
        
        parsedTokens = []
        signs = ";,.!?"
        for token in tokens:
            if token.tokenType == TYPE_SIGN:
                if token.token in signs:
                    parsedTokens.append(token)
                    
            if (token.tokenType == TYPE_TOKEN and token.allCyr() and token.getBestPOS()):
                parsedTokens.append(token)

        lastId = len(parsedTokens)-1
        
        for windowSize in range(minWindowSize, maxWindowSize):  
            self.data["DOTS"][windowSize] = [] 
            self.data["COMMAS"][windowSize] = [] 
            self.data["NOUNS"][windowSize] = [] 
            self.data["VERBS"][windowSize] = []
            self.data["ADJS"][windowSize] = []
            self.data["UNIQUE_NOUNS"][windowSize] = [] 
            self.data["UNIQUE_VERBS"][windowSize] = [] 
            self.data["UNIQUE_ADJS"][windowSize] = []           
            for tokenId in range(0, lastId):
                token = parsedTokens[tokenId]
                if token.tokenType == TYPE_SIGN:
                    if token.token in ";,":
                        sumCommas +=1    
                    if token.token in ".?!":
                        sumDots +=1  
                else:
                    pos = token.getBestPOS()
                    if pos in ['VERB', 'INFN', 'PRTF', 'PRTS','GRND']:
                        sumVerb += 1
                        setVerb[self.getStem(token)] += 1
                    if pos in ['NOUN','NPRO']:
                        sumNoun += 1
                        setNoun[self.getStem(token)] += 1
                    if pos in ['ADJF','ADJS','COMP','ADVB','PRED']:
                        sumAdj += 1
                        setAdj[self.getStem(token)] += 1
                    if pos in ['PREP','CONJ','PRCL','INTJ']:
                        sumFunc += 1
                        setFunc[self.getStem(token)] += 1
                if tokenId >= windowSize:
                    prevToken = parsedTokens[tokenId-windowSize]
                    if prevToken.tokenType == TYPE_SIGN:
                        if prevToken.token in ";,":
                            sumCommas -=1    
                        if prevToken.token in ".?!":
                            sumDots -=1  
                    else:
                        pos = prevToken.getBestPOS()
                        if pos in ['VERB', 'INFN', 'PRTF', 'PRTS','GRND']:
                            sumVerb -= 1
                            setVerb -= ({self.getStem(prevToken):1})
                        if pos in ['NOUN','NPRO']:
                            sumNoun -= 1
                            setNoun -= ({self.getStem(prevToken):1})
                        if pos in ['ADJF','ADJS','COMP','ADVB','PRED']:
                            sumAdj -= 1
                            setAdj -= ({self.getStem(prevToken):1})
                        if pos in ['PREP','CONJ','PRCL','INTJ']:
                            sumFunc -= 1
                            setFunc -= ({self.getStem(prevToken):1})                    
                if tokenId >= windowSize-1:
                    self.data["DOTS"][windowSize].append(sumDots) 
                    self.data["COMMAS"][windowSize].append(sumCommas) 
                    self.data["NOUNS"][windowSize].append(sumNoun) 
                    self.data["VERBS"][windowSize].append(sumVerb)
                    self.data["ADJS"][windowSize].append(sumAdj)
                    self.data["UNIQUE_NOUNS"][windowSize].append(len(setNoun)) 
                    self.data["UNIQUE_VERBS"][windowSize].append(len(setVerb)) 
                    self.data["UNIQUE_ADJS"][windowSize].append(len(setAdj)) 
        with open(self.file +'-surface.pcl', 'wb') as f:
            pickle.dump(self.data, f, pickle.HIGHEST_PROTOCOL)

textStat = TextStat("C:/WORK/science/onpositive_data/python/texts/sule2.txt")
textStat.buildPOSSurface()
textStat = TextStat("C:/WORK/science/onpositive_data/python/texts/sule3.txt")
textStat.buildPOSSurface()