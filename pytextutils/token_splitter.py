# -*- coding: utf-8 -*-
from pytextutils.cached_pymorphy_morph import CachedPymorphyMorph
TYPE_TOKEN = 1
TYPE_SIGN = 2
TYPE_WORD = 3
TYPE_COMPLEX_TOKEN = 4
BIG_CYR_LETTERS = "ЁЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ"
BIG_LATIN_LETTERS = "QWERTYUIOPASDFGHJKLZXCVBNM"
LITTLE_CYR_LETTERS = "ёйцукенгшщзхъфывапролджэячсмитьбю"
ALL_CYR_LETTERS = "ёйцукенгшщзхъфывапролджэячсмитьбюЁЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ"
DIGITS = '1234567890'
SPACES = ' \r\n\t'
SIGNS = '\'\\~!@#$%^&*()_+`"№;:?-={}[]<>/|—«».,„'

class Token:
    def __init__(self, 
                 token, 
                 startPos, endPos, 
                 spaceLeft, spaceRight, 
                 newlineLeft, newlineRight, 
                 tokenType, tokenNum):
        self.token = token
        self.startPos = startPos
        self.endPos = endPos 
        self.spaceLeft = spaceLeft
        self.spaceRight = spaceRight 
        self.newlineLeft = newlineLeft
        self.newlineRight = newlineRight 
        self.tokenType = tokenType
        self.tokenNum = tokenNum
        self.additionalInfo = {}
        self.POS = None
        self.flags = {}
    def __str__(self):
        return str(self.tokenType) + ' ' + self.token  
    def setFlag(self,flag,value=True):
        self.flags[flag] = value  
    def isFlag(self,flag):
        return self.flags.get(flag,False)  
    def setAdditionalInfo(self,field,info):
        self.additionalInfo[field] = info
    def setPOS(self,pos):
        self.tokenType = TYPE_WORD
        self.POS = pos
    def getBestPOS(self):
        if self.POS:
            return self.POS[0]['POS']
        return None
    def getBestNormalForm(self):
        if self.POS:
            return self.POS[0]['normalForm']
        return None
    def hasDigits(self):
        return any(i in DIGITS for i in self.token)
    def onlyDigits(self):
        return all(i in DIGITS for i in self.token)
    def allCyr(self):
        return all(i in ALL_CYR_LETTERS for i in self.token)         
    def fromBigLetter(self):
        return self.token[0] in BIG_CYR_LETTERS and (
            len(self.token) <= 1 or
            not (self.token[1] in BIG_CYR_LETTERS)
        )
    def onlyBigLetters(self):
        return all(i in BIG_CYR_LETTERS or i in BIG_LATIN_LETTERS for i in self.token)   
    def setInternalTokens(self,tokens):
        self.internalTokens = tokens     

   
class POSTagger: 
    __TRESHOLD = 0.0005   
    __notAVerbs = set(["данные","гипер","прокси","при","начало","три","день","части","времени","минут","мини","мину","плей","плети","трем","трём","cочи","Сочи"])
    __morph = CachedPymorphyMorph()
    
    @staticmethod
    def posTagging(tokens):
        for i in range(0,len(tokens)):
            if tokens[i].tokenType == TYPE_SIGN:
                continue
            parse_result = POSTagger.__morph.parse(tokens[i].token)
            if(parse_result == None):
                continue
            posInfo = []
            stems = set()
            for res in parse_result:
                if res.score < POSTagger.__TRESHOLD:
                    break
                if res.normal_form in stems:
                    continue
                if (res.tag.POS == 'VERB'):
                    if tokens[i].token in POSTagger.__notAVerbs:
                        continue
                    if i > 0 and tokens[i-1].tokenType != TYPE_SIGN and tokens[i-1].getBestPOS() == 'PREP':
                        continue
                    if i > 0 and tokens[i].token[0] in BIG_CYR_LETTERS and not tokens[i-1].token == '.':
                        continue
                    
                element = {'POS' : res.tag.POS,
                           'normalForm' : res.normal_form,
                           'score' : res.score}
                stems.add(res.normal_form)
                posInfo.append(element)
            tokens[i].setAdditionalInfo('parse_result',parse_result)
            tokens[i].setPOS(posInfo)        

class TokenSplitter:
    def __init__(self):
        pass
    
    def addToken(self):    
        self.tokenArray.append(
            Token(
                self.curWord,
                self.startPos,
                self.endPos,
                self.hasSpaceLeft,
                self.hasSpaceRight,
                self.hasNewlineLeft,
                self.hasNewlineRight,
                self.tokenType,
                self.tokenNum))   
        self.curWord = ''
        self.tokenNum += 1 
        
    def split(self,text):
        self.tokenArray = []
        self.curWord = '' 
        self.startPos = 0
        self.endPos = 0
        self.hasSpaceLeft = False
        self.hasSpaceRight = False
        self.hasNewlineLeft = True
        self.hasNewlineRight = False
        self.tokenType = TYPE_TOKEN
        self.tokenNum = 0
        pos = 0
        for letter in text:
            if (self.tokenType == TYPE_SIGN): # Add sign
                if (letter in SPACES):
                    self.hasSpaceRight = True
                else:
                    self.hasSpaceRight = False
                if (letter == '\n'):
                    self.hasNewlineRight = True
                else:
                    self.hasNewlineRight = False
                if (len(self.curWord)>0):
                    self.endPos = pos-1
                    self.addToken()
                self.startPos = pos
                self.hasSpaceLeft = self.hasSpaceRight
                self.hasNewlineLeft = self.hasNewlineRight
                self.hasSpaceRight = False
                self.hasNewlineRight = False    
                self.tokenType = TYPE_TOKEN  
            
            if (letter in SPACES): # Add when not sign and find space
                self.hasSpaceRight = True
                if (letter == '\n'):
                    self.hasNewlineRight = True
                if (len(self.curWord)>0):
                    self.endPos = pos
                    self.addToken()
                self.startPos = pos+1
                self.hasSpaceLeft = self.hasSpaceRight
                self.hasNewlineLeft = self.hasNewlineRight
                self.hasSpaceRight = False
                self.hasNewlineRight = False    
            elif (letter in SIGNS): # Create word with sign
                self.hasSpaceRight = False
                if (len(self.curWord)>0):
                    self.endPos = pos-1
                    self.addToken()
                    self.hasSpaceLeft = False 
                    self.hasNewlineLeft = False 
                self.startPos = pos    
                self.curWord += letter
                self.tokenType = TYPE_SIGN
                self.hasSpaceRight = False
                self.hasNewlineRight = False   
            else:                               #Add letter to word
                self.curWord += letter
                self.tokenType = TYPE_TOKEN
            pos += 1    

        if (len(self.curWord)>0):
            self.endPos = pos
            self.addToken()
        
        return self.tokenArray 
    
    def getTokenArray(self):
        return self.tokenArray 
        
                                  
#directory = "C:\\WORK\\science\\onpositive_data\\python\\"
#tokenizer = WikiTokenizer.WikiTokenizer()
#wikiIndex = WikiIndex.WikiIndex(directory)
#print(wikiIndex.getTextArticleById(7))
#print("------------------------------------------------------------")
#cleanText = tokenizer.clean(wikiIndex.getTextArticleById(7))
#print(cleanText)

#wordSplitter = TokenSplitter()
#words = wordSplitter.split(cleanText)
#for word in words:
#    print(word)     
#tokens = wordSplitter.getTokenArray()    
#for token in tokens:
#    print(token)      