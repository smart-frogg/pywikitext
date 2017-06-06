# -*- coding: utf-8 -*-
from pytextutils.token_splitter import Token, TokenSplitter, POSTagger, TYPE_SIGN, TYPE_TOKEN, TYPE_WORD,LITTLE_CYR_LETTERS, BIG_CYR_LETTERS
import re
import codecs
import pickle
import json
from collections import Counter
from pywikiaccessor.one_opened import OneOpened

class TextCleaner(metaclass= OneOpened):
    def __init__(self,directory,clearWrap = True):
        self.directory = directory
        self.clearWrap = clearWrap
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
        if self.clearWrap:
            workText = self.__clearWraps(workText)
        workText = self.__clearAbbr(workText)
        workText = self.__concatStrings(workText)
        return workText

TEXT_STAT_KEYS = ["DOTS","COMMAS","NOUNS","VERBS","ADJS","FUNC","UNIQUE_NOUNS","UNIQUE_VERBS","UNIQUE_ADJS","UNIQUE_FUNC"]            
class TextStat:
    def __init__(self, directory=None,file=None, text=None, clearWrap=True):
        if file:
            cleaner = TextCleaner(directory,clearWrap)
            self.directory = directory
            self.file = file
            with codecs.open(directory+self.file, 'r', "utf-8") as myfile:
                self.text=myfile.readlines()
            
            self.text = cleaner.clean(self.text)
        elif text:
            self.text = text
        else:
            print ('There is no text or file to parse')
            self.text = ''        
        self.tokenSplitter = TokenSplitter()
        self.posTagger = POSTagger()        
    
    def getStem(self,token):
        return token.POS[0]['normalForm'].replace('ё','е')
    
    def addToken(self,token):
        if token.tokenType == TYPE_SIGN:
            if token.token in ";,":
                self.sumCommas +=1    
            if token.token in ".?!":
                self.sumDots +=1  
        else:
            pos = token.getBestPOS()
            if pos in ['VERB', 'INFN', 'PRTF', 'PRTS','GRND']:
                self.sumVerb += 1
                self.setVerb[self.getStem(token)] += 1
            if pos in ['NOUN','NPRO']:
                self.sumNoun += 1
                self.setNoun[self.getStem(token)] += 1
            if pos in ['ADJF','ADJS','COMP','ADVB','PRED']:
                self.sumAdj += 1
                self.setAdj[self.getStem(token)] += 1
            if pos in ['PREP','CONJ','PRCL','INTJ']:
                self.sumFunc += 1
                self.setFunc[self.getStem(token)] += 1
                
    def removeToken(self,token):
        if token.tokenType == TYPE_SIGN:
            if token.token in ";,":
                self.sumCommas -=1    
            if token.token in ".?!":
                self.sumDots -=1  
        else:
            pos = token.getBestPOS()
            if pos in ['VERB', 'INFN', 'PRTF', 'PRTS','GRND']:
                self.sumVerb -= 1
                self.setVerb -= ({self.getStem(token):1})
            if pos in ['NOUN','NPRO']:
                self.sumNoun -= 1
                self.setNoun -= ({self.getStem(token):1})
            if pos in ['ADJF','ADJS','PRED','COMP','ADVB']:
                self.sumAdj -= 1
                self.setAdj -= ({self.getStem(token):1})
            if pos in ['PREP','CONJ','PRCL','INTJ']:
                self.sumFunc -= 1
                self.setFunc -= ({self.getStem(token):1})  
    
    def prepareText(self,text):
        self.tokenSplitter.split(self.text)
        tokens = self.tokenSplitter.getTokenArray()  
        self.posTagger.posTagging(tokens) 
        parsedTokens = self.clearTokens(tokens)
        return parsedTokens
    
    def clearTokens(self, tokens):
        parsedTokens = []
        signs = ";,.!?"
        for token in tokens:
            if token.tokenType == TYPE_SIGN:
                if token.token in signs:
                    parsedTokens.append(token)
                    
            if (token.tokenType in [TYPE_TOKEN,TYPE_WORD] and token.allCyr() and token.getBestPOS()):
                parsedTokens.append(token)
        return parsedTokens
    
    def getSlice(self,parsedTokens,size):
        res = {}
        res["DOTS"] = [] 
        res["COMMAS"] = [] 
        res["NOUNS"] = [] 
        res["VERBS"] = []
        res["ADJS"] = []
        res["FUNC"] = []
        res["UNIQUE_NOUNS"] = [] 
        res["UNIQUE_VERBS"] = [] 
        res["UNIQUE_ADJS"] = []           
        res["UNIQUE_FUNC"] = []
        self.setNoun = Counter();
        self.setAdj = Counter();
        self.setVerb = Counter();
        self.setFunc = Counter();
        self.sumNoun = 0;
        self.sumVerb = 0;
        self.sumAdj = 0;
        self.sumFunc = 0;
        self.sumDots = 0;
        self.sumCommas = 0;
        tokenAdded = False
        for tokenId in range(0, len(parsedTokens)-1):
            token = parsedTokens[tokenId]
            self.addToken(token)
            tokenAdded = False
            if tokenId >= size:
                prevToken = parsedTokens[tokenId-size]
                self.removeToken(prevToken)
            if tokenId >= size-1:
                res["DOTS"].append(self.sumDots) 
                res["COMMAS"].append(self.sumCommas) 
                res["NOUNS"].append(self.sumNoun) 
                res["VERBS"].append(self.sumVerb)
                res["ADJS"].append(self.sumAdj)
                res["FUNC"].append(self.sumFunc)
                res["UNIQUE_NOUNS"].append(len(self.setNoun)) 
                res["UNIQUE_VERBS"].append(len(self.setVerb)) 
                res["UNIQUE_ADJS"].append(len(self.setAdj)) 
                res["UNIQUE_FUNC"].append(len(self.setFunc))
                tokenAdded = True
        if not tokenAdded:        
            res["DOTS"].append(self.sumDots) 
            res["COMMAS"].append(self.sumCommas) 
            res["NOUNS"].append(self.sumNoun) 
            res["VERBS"].append(self.sumVerb)
            res["ADJS"].append(self.sumAdj)
            res["FUNC"].append(self.sumFunc)
            res["UNIQUE_NOUNS"].append(len(self.setNoun)) 
            res["UNIQUE_VERBS"].append(len(self.setVerb)) 
            res["UNIQUE_ADJS"].append(len(self.setAdj)) 
            res["UNIQUE_FUNC"].append(len(self.setFunc))
        return res

    def buildPOSStat(self):            
        parsedTokens = self.prepareText(self.text)
        surfaceSlice = self.getSlice(parsedTokens,len(parsedTokens))
        return surfaceSlice
    
    def buildPOSSurface(self, minWindowSize = 10, maxWindowSize = 1000, step=5,saveToFile = True):
        parsedTokens = self.prepareText(self.text)
        
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
               
        for windowSize in range(minWindowSize, maxWindowSize,step): 
            surfaceSlice = self.getSlice(parsedTokens,windowSize)
            for key in surfaceSlice: 
                self.data[key][windowSize] = surfaceSlice[key]
        if saveToFile:        
            with open(self.directory+self.file +'-surface.pcl', 'wb') as f:
                pickle.dump(self.data, f, pickle.HIGHEST_PROTOCOL)
        else:
            return pickle.dumps(self.data, pickle.HIGHEST_PROTOCOL)

def normalizeMaxMin(data):
    if len(data) == 0:
        return []
    if not type(data) is list:
        dataList = list(data.values())
    else:    
        dataList = data
    max_value = max(dataList)
    min_value = min(dataList)
    if max_value == min_value:
        return data
    if not type(data) is list:
        normData = {}
        for key in data:
            normData[key] = (data[key]-min_value)/(max_value-min_value)
    else:
        normData = []
        for d in data:
            normData.append((d-min_value)/(max_value-min_value))
    return normData

def normalize(data):
    if len(data) == 0:
        return []
    if not type(data) is list:
        dataList = list(data.values())
    else:    
        dataList = data
    max_value = max(dataList)
    if max_value == 0:
        return data
    normData = {}
    if not type(data) is list:
        normData = {}
        for key in data:
            normData[key] = (data[key])/(max_value)
    else:
        normData = []
        for d in data:
            normData.append((d)/(max_value))
    return normData
def normalizeSum(data, keys=None):
    if len(data) == 0:
        return []
    if not type(data) is list:
        if keys:
            dataList = []
            for key in keys:
                dataList.append(data[key])
        else:
            dataList = list(data.values())
    else:    
        if keys:
            dataList = []
            for key in keys:
                dataList.append(data[key])
        else:
            dataList = data
    sum_value = sum(dataList)
    if sum_value == 0:
        return data
    normData = {}
    if not type(data) is list:
        normData = {}
        for key in data:
            normData[key] = (data[key])/(sum_value)
    else:
        normData = []
        for d in data:
            normData.append((d)/(sum_value))
    return normData  
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
#from pytextutils.grammar_base import HeaderMatcher 
#ts = TokenSplitter()
#ts.split(textStat.text)
#tokens = ts.getTokenArray()
#hm = HeaderMatcher()
#hm.combineTokens(tokens)

#for token in tokens:
#    if token.tokenType == TYPE_COMPLEX_TOKEN:
#        print(token.token)

#for file in ["texts/ladno.txt","texts/sule1.txt","texts/sule2.txt","texts/sule3.txt"]:
#    textStat = TextStat(directory,file=file)
#    textStat.buildPOSSurface()
