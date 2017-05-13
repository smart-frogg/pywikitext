# -*- coding: utf-8 -*-
from pytextutils.token_splitter import Token, TokenSplitter, POSTagger, TYPE_SIGN, TYPE_TOKEN, TYPE_WORD,LITTLE_CYR_LETTERS, BIG_CYR_LETTERS
import re
import codecs
import pickle
import json
from collections import Counter
from pywikiaccessor.one_opened import OneOpened

class TextCleaner(metaclass= OneOpened):
    def __init__(self,directory):
        self.directory = directory
        self.__loadAbbrs()
    def __clearWraps(self,text):
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
    __startStringRegex = re.compile('^[1234567890.)(\[\]]+', re.VERBOSE)

    def __loadAbbrs(self):
        with open(self.directory + 'abbrsConfig.json', encoding="utf8") as data_file:    
            self.__abbrs = json.load(data_file,encoding="utf-8")
 
    def __clearAbbr(self,text):
        ind = 0
        for curStr in text:
            for abbr in self.__abbrs:
                curStr = curStr.replace(abbr['short'],abbr['full'])
            text[ind] = curStr
            ind+=1                
        return text  
    
    def __concatStrings(self,text):
        concatText = text[0]
        onlyBig = all (not ch in LITTLE_CYR_LETTERS for ch in text[0])
        for ind in range (1,len(text)):
            curOnlyBig = all (not ch in LITTLE_CYR_LETTERS for ch in text[ind])
            if ((len(text[ind]) > 0 and len(concatText) > 0) and
                ((onlyBig and curOnlyBig) or
                ((not TextCleaner.__startStringRegex.match(text[ind]))
                and (not text[ind][0] in BIG_CYR_LETTERS) 
                and (not concatText[-1] == '.')))
                ):  
                concatText += ' ' + text[ind]
            else:
                concatText += '\n' + text[ind]
            onlyBig = curOnlyBig
        return concatText     
    
    def clean(self,text):
        if type(text) == str:
            workText = text.split("\n")
        else:
            workText = text
        workText = self.__clearWraps(workText)
        workText = self.__clearAbbr(workText)
        workText = self.__concatStrings(workText)
        return workText
            
class TextStat:
    def __init__(self,file):
        self.file = file
        with codecs.open(self.file, 'r', "utf-8") as myfile:
            self.text=myfile.readlines()
        
        self.text = TextCleaner.clean(self.text)
        self.tokenSplitter = TokenSplitter()
        self.posTagger = POSTagger()
        
    
    def getStem(self,token):
        return token.POS[0]['normalForm'].replace('ё','е')
    
    def buildPOSSurface(self, minWindowSize = 10, maxWindowSize = 1000, step=5):
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
                    
            if (token.tokenType in [TYPE_TOKEN,TYPE_WORD] and token.allCyr() and token.getBestPOS()):
                parsedTokens.append(token)

        lastId = len(parsedTokens)-1
        
        for windowSize in range(minWindowSize, maxWindowSize,step):  
            self.data["DOTS"][windowSize] = [] 
            self.data["COMMAS"][windowSize] = [] 
            self.data["NOUNS"][windowSize] = [] 
            self.data["VERBS"][windowSize] = []
            self.data["ADJS"][windowSize] = []
            self.data["FUNC"][windowSize] = []
            self.data["UNIQUE_NOUNS"][windowSize] = [] 
            self.data["UNIQUE_VERBS"][windowSize] = [] 
            self.data["UNIQUE_ADJS"][windowSize] = []           
            self.data["UNIQUE_FUNC"][windowSize] = []
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
                    self.data["FUNC"][windowSize].append(sumFunc)
                    self.data["UNIQUE_NOUNS"][windowSize].append(len(setNoun)) 
                    self.data["UNIQUE_VERBS"][windowSize].append(len(setVerb)) 
                    self.data["UNIQUE_ADJS"][windowSize].append(len(setAdj)) 
                    self.data["UNIQUE_FUNC"][windowSize].append(len(setFunc))
        with open(self.file +'-surface.pcl', 'wb') as f:
            pickle.dump(self.data, f, pickle.HIGHEST_PROTOCOL)


#directory = "C:/WORK/science/onpositive_data/python/"
#tc = TextCleaner(directory)
#tc1 = TextCleaner(directory)
#print(tc1)
#text = '''
#рис.1 и т.д.
#и пр.
#'''
#tc = TextCleaner(directory)
#print(tc.clean(text))
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
