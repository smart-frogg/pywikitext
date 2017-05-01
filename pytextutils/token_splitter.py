# -*- coding: utf-8 -*-
import CachedPymorphyMorph
TYPE_TOKEN = 1
TYPE_SIGN = 2
TYPE_WORD = 3
class Token:
    __digits = '1234567890'
    __cyr = "ёйцукенгшщзхъфывапролджэячсмитьбюЁЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ"
    def __init__(self, token, spaceLeft, spaceRight, tokenType, tokenNum):
        self.token = token
        self.spaceLeft = spaceLeft
        self.spaceRight = spaceRight 
        self.tokenType = tokenType
        self.tokenNum = tokenNum
    def __str__(self):
        return str(self.tokenType) + ' ' + self.token    
    def setAddInfo(self,info):
        self.addInfo = info
    def setPOS(self,pos):
        self.POS = pos
    def getBestPOS(self):
        if self.POS:
            return self.POS[0]['POS']
        return None
    def hasDigits(self):
        return any(i in Token.__digits for i in self.token)
    def onlyDigits(self):
        return all(i in Token.__digits for i in self.token)
    def allCyr(self):
        return all(i in Token.__cyr for i in self.token)         

class POSTagger: 
    __TRESHOLD = 0.0005   
    __notAVerbs = set(["при","начало","три","день","части","времени","минут","мини","мину","плей","плети","трем","трём","cочи","Сочи"])
    __bigLetters = "ЁЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ"
    def __init__(self):
        self.morph = CachedPymorphyMorph.CachedPymorphyMorph()
    def posTagging(self,tokens):
        for i in range(0,len(tokens)):
            parse_result = self.morph.parse(tokens[i].token)
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
                    if i > 0 and tokens[i-1].getBestPOS() == 'PREP':
                        continue
                    if i > 0 and tokens[i].token[0] in POSTagger.__bigLetters and not tokens[i-1].token == '.':
                        continue
                    
                element = {'POS' : res.tag.POS,
                           'normalForm' : res.normal_form,
                           'score' : res.score}
                stems.add(res.normal_form)
                posInfo.append(element)
            tokens[i].setAddInfo(parse_result)
            tokens[i].setPOS(posInfo)
        
    
class TokenSplitter:
    def __init__(self):
        self.spaces = ' \r\n\t'
        self.signs = '\'\\~!@#$%^&*()_+`"№;:?-={}[]<>/|—«».,„'
    
    def addToken(self):    
        self.wordArray.append(self.curWord)
        self.tokenArray.append(
            Token(
                self.curWord,
                self.hasSpaceLeft,
                self.hasSpaceRight,
                self.tokenType,
                self.tokenNum))   
        self.curWord = ''
        self.tokenNum += 1 
        
    def split(self,text):
        self.wordArray = []
        self.tokenArray = []
        self.curWord = '' 
        self.hasSpaceLeft = False
        self.hasSpaceRight = False
        self.tokenType = TYPE_TOKEN
        self.tokenNum = 0
        for letter in text:
            if (self.tokenType == TYPE_SIGN): # Add sign
                if (self.spaces.find(letter) != -1):
                    self.hasSpaceRight = True
                else:
                    self.hasSpaceRight = False
                if (len(self.curWord)>0):
                    self.addToken()
                self.hasSpaceLeft = False
                self.tokenType = TYPE_TOKEN  
            
            if (letter in self.spaces): # Add when not sign and find space
                self.hasSpaceRight = True
                if (len(self.curWord)>0):
                    self.addToken()
                self.hasSpaceLeft = True
            elif (letter in self.signs): # Create word with sign
                self.hasSpaceRight = False
                if (len(self.curWord)>0):
                    self.addToken()
                self.curWord += letter
                self.tokenType = TYPE_SIGN
            else:                               #Add letter to word
                self.curWord += letter
                self.tokenType = TYPE_TOKEN

        if (len(self.curWord)>0):
            self.addToken()
        
        return self.wordArray
    
    def getWordArray(self):
        return self.wordArray
    
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