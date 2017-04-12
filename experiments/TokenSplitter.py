# -*- coding: utf-8 -*-
import TextToken 

class TokenSplitter:
    def __init__(self):
        self.spaces = ' \r\n\t'
        self.signs = '\'".,/!@#$%^&*()[]{}|:;-—»«'
    
    def addToken(self):    
        self.wordArray.append(self.curWord)
        self.tokenArray.append(
            TextToken.Token(
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
        self.tokenType = TextToken.TYPE_TOKEN
        self.tokenNum = 0
        for letter in text:
            if (self.tokenType == TextToken.TYPE_SIGN): # Add sign
                if (self.spaces.find(letter) != -1):
                    self.hasSpaceRight = True
                else:
                    self.hasSpaceRight = False
                if (len(self.curWord)>0):
                    self.addToken()
                self.hasSpaceLeft = False
                self.tokenType = TextToken.TYPE_TOKEN  
            
            if (self.spaces.find(letter) != -1): # Add when not sign and find space
                self.hasSpaceRight = True
                if (len(self.curWord)>0):
                    self.addToken()
                self.hasSpaceLeft = True
            elif (self.signs.find(letter) != -1): # Create word with sign
                self.hasSpaceRight = False
                if (len(self.curWord)>0):
                    self.addToken()
                self.curWord += letter
                self.tokenType = TextToken.TYPE_SIGN
            else:                               #Add letter to word
                self.curWord += letter
                self.tokenType = TextToken.TYPE_TOKEN

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