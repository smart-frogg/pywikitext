# -*- coding: utf-8 -*-
from pytextutils.token_splitter import TYPE_SIGN, TYPE_COMPLEX_TOKEN

WORD_POS = ['VERB', 'INFN', 'PRTF', 'PRTS','GRND','ADVB','PRED','PREP','CONJ','PRCL','INTJ']

TYPE_FUNCTIONAL_TOKEN = -1

FT_NAME_GROUP = "@NAME_GROUP@"
FT_FORMAL_GROUP = "@FORMAL_GROUP@"
FT_SIGN = "@SIGN@"
FT_FUNCTIONAL_WORD = "@WORD@"
FT_FUNCTIONAL_TOKEN = "@TOKEN@"


class Fragment:
    @staticmethod
    def isCommon(token,goodWords):
        if token.tokenType == TYPE_COMPLEX_TOKEN:
            if token.isFlag('formal'):
                return True
            return False
        elif token.tokenType in [TYPE_SIGN,TYPE_FUNCTIONAL_TOKEN]:
            return False
        elif (token.getBestNormalForm() in goodWords or    
              token.getBestPOS() in WORD_POS):
            return False
        else:
            return True    
        
    def __init__(self,tokens,goodWords = []):
        self.tokens = []
        self.tokenTypes = []
        for t in tokens:
            if t.tokenType == TYPE_COMPLEX_TOKEN:
                if t.isFlag('formal'):
                    self.tokens.append(FT_FORMAL_GROUP)
                    self.tokenTypes.append(FT_FORMAL_GROUP)
            elif t.tokenType is TYPE_SIGN:
                self.tokens.append(t.token)
                self.tokenTypes.append(FT_SIGN)
            elif t.tokenType is TYPE_FUNCTIONAL_TOKEN:
                self.tokens.append(t.token)
                self.tokenTypes.append(FT_FUNCTIONAL_TOKEN)
            elif (t.getBestNormalForm() in goodWords or    
                  t.getBestPOS() in WORD_POS):
                self.tokens.append(t.POS[0]['normalForm'])
                self.tokenTypes.append(FT_FUNCTIONAL_WORD)
            else:
                self.tokens.append(FT_NAME_GROUP)   
                self.tokenTypes.append(FT_NAME_GROUP) 
    def __str__(self):
        return '|'.join(self.tokens)
             
    def __hash__(self):
        return hash('|'.join(self.tokens))

    def __eq__(self, other):
        return self.tokens == other.tokens
    
    def isGood(self):
        badTokensCount = 0
        for t in self.tokens:
            if t in [FT_NAME_GROUP,FT_FORMAL_GROUP]:
                badTokensCount += 1
        return badTokensCount < 0.7*len(self.tokens)
    def genGrammar(self):
        listOfTokens = []
        for indT in range(len(self.tokens)):
            if self.tokenTypes[indT] is FT_SIGN:
                listOfTokens.append({'exact':self.tokens[indT]})
            elif self.tokenTypes[indT] is FT_FUNCTIONAL_WORD:   
                listOfTokens.append({'normalForm':self.tokens[indT]})
        grammar = [{'group':listOfTokens}]
        return grammar             

from collections import Counter
def calcHist(tokens):
    counters = {"VERB":Counter(), "NOUN":Counter()}
    for t in tokens:
        bestPOS = t.getBestPOS()
        if bestPOS == "VERB" or bestPOS == "NOUN":
            counters[bestPOS][t.getBestNormalForm()] += 1
    return counters 