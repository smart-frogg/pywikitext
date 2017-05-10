# -*- coding: utf-8 -*-
from pytextutils.token_splitter import Token, TokenSplitter, POSTagger, TYPE_SIGN, TYPE_TOKEN, TYPE_COMPLEX_TOKEN, BIG_CYR_LETTERS
from collections import Counter
import pickle
import codecs

class TextCleaner:
    @staticmethod
    def __clearWraps(text):
        ind = 0
        while ind < len(text):
            curStr = text[ind].strip()
            if len(curStr)>=2 :
                while curStr[-1]=='-' and not curStr[-2]==' ' and ind < len(text) :
                    curStr = curStr[:-1] + text[ind+1].strip()
                    del text[ind+1]  
            text[ind] = curStr
            ind+=1
        return text 
    @staticmethod
    def __concatStrings(text):
        concatText = text[0]
        for ind in range (1,len(text)):
            if (len(text[ind]) > 0 and len(concatText) > 0
                and (not text[ind][0] in BIG_CYR_LETTERS) 
                and (not concatText[-1] == '.')
                ):  
                concatText += ' ' + text[ind]
            else:
                concatText += '\n' + text[ind]  
        return concatText     
        
    @staticmethod    
    def clean(text):
        if type(text) == str:
            workText = text.split("\n")
        else:
            workText = text
        workText = TextCleaner.__clearWraps(workText)
        workText = TextCleaner.__concatStrings(workText)
        return workText
            
class TextStat:
    def __init__(self,file):
        self.file = file
        with codecs.open(self.file, 'r', "utf-8") as myfile:
            self.text=myfile.readlines()
        
        TextCleaner.clearText(self.text)
        self.tokenSplitter = TokenSplitter()
        self.posTagger = POSTagger()
        
    
    def getStem(self,token):
        return token.POS[0]['normalForm'].replace('ё','е')
    
    def buildPOSSurface(self, minWindowSize = 50, maxWindowSize = 1000):
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

#directory = "C:/WORK/science/onpositive_data/python/texts/"
#file = "sule1.txt"
#textStat = TextStat(directory+file)
#print(textStat.text)
#from pytextutils.formal_grammar import HeaderMatcher 
#ts = TokenSplitter()
#ts.split(textStat.text)
#tokens = ts.getTokenArray()
#hm = HeaderMatcher()
#hm.combineTokens(tokens)

#for token in tokens:
#    if token.tokenType == TYPE_COMPLEX_TOKEN:
#        print(token.token)

#for file in ["ladno.txt","sule1.txt","sule2.txt","sule3.txt"]:
#textStat = TextStat(directory+file)
#textStat.buildPOSSurface()
