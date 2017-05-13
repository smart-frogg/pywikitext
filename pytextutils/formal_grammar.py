# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from pytextutils.token_splitter import TokenSplitter, Token, TYPE_COMPLEX_TOKEN,\
    TYPE_SIGN

def genComplexToken(tokens, start, end):
    tokenTextArray = []
    for i in range(start, end):
        tokenTextArray.append(tokens[i].token)
        
    tokenText = ' '.join(tokenTextArray)        
    token = Token(
            tokenText,
            tokens[start].startPos,
            tokens[end-1].endPos,
            tokens[start].spaceLeft,
            tokens[end-1].spaceRight,
            tokens[start].newlineLeft,
            tokens[end-1].newlineRight,
            TYPE_COMPLEX_TOKEN,
            tokens[start].tokenNum)
    token.setInternalTokens(tokens[start:end])
    tokens[start] = token
    for i in reversed(range(start+1, end)):
        del tokens[i]
    return token
        
class FormalGrammar(metaclass=ABCMeta):
    def __init__(self, grammar):
        self.grammar = grammar
        self.operations = {
            'exact': self.matchExact,
            'maxlen': self.matchMaxLen,
            'newline': self.matchNewLine,
            'onlydigits': self.matchOnlyDigits,
            'onlybig': self.matchOnlyBig,
            'startfrombig': self.matchStartFromBig,
            'frombigletter': self.matchFromBigLetter,
            
            'optional': self.matchOptional,
            'oneof': self.matchOneOf,
            'group': self.matchGroup,
            'repeat': self.matchRepeat,
            'alluntil': self.matchAllUntil,
            }
    def combineTokens(self,tokens):
        grammarRange = range(0,len(self.grammar))
        self.tokens = tokens
        tokenNum = 0
        while tokenNum < len(tokens):
            self.tokenUnify = tokenNum
            unificationComplete = True
            for grammarNum in grammarRange:
                if not self.__unify(self.grammar[grammarNum]):
                    unificationComplete = False
                    break
            if unificationComplete:
                self.genToken(tokenNum, self.tokenUnify)
                tokenNum = self.tokenUnify + 1
            else:
                tokenNum += 1        
                
    def __unify(self,grammarToken):
        unificationComplete = True
        oldTokenUnify = self.tokenUnify
        for gToken in grammarToken.keys():
            self.tokenUnify = oldTokenUnify 
            operation = gToken 
            unificationComplete &= self.operations[operation.lower()](grammarToken[operation])
            if not unificationComplete:
                break
            if self.tokenUnify >= len(self.tokens):
                return False
        return unificationComplete
        
    def matchExact(self,param):
        result = self.tokens[self.tokenUnify].token == param
        if result:
            self.tokenUnify += 1 
        return result 

    def matchNewLine(self,param):
        result = ((param.lower() == 'left' and self.tokens[self.tokenUnify].newlineLeft) or 
                  (param.lower() == 'right' and self.tokens[self.tokenUnify].newlineRight) or
                  (param.lower() == 'left only' and self.tokens[self.tokenUnify].newlineLeft 
                                                and not self.tokens[self.tokenUnify].newlineRight) or 
                  (param.lower() == 'right only' and self.tokens[self.tokenUnify].newlineRight
                                                 and not self.tokens[self.tokenUnify].newlineLeft) or
                  (param.lower() == 'both' and self.tokens[self.tokenUnify].newlineRight 
                                           and self.tokens[self.tokenUnify].newlineLeft) or
                  (param.lower() == 'none' and not self.tokens[self.tokenUnify].newlineRight 
                                           and not self.tokens[self.tokenUnify].newlineLeft))
        if result:
            self.tokenUnify += 1 
        return result 
    
    def matchOnlyDigits(self,param):
        result = (param == self.tokens[self.tokenUnify].onlyDigits()) 
        if result:
            self.tokenUnify += 1 
        return result

    def matchOnlyBig(self,param):
        result = (param == self.tokens[self.tokenUnify].onlyBigLetters()) 
        if result:
            self.tokenUnify += 1 
        return result
     
    def matchStartFromBig(self,param):
        result = (param == self.tokens[self.tokenUnify].fromBigLetter()) 
        if result:
            self.tokenUnify += 1 
        return result

    def matchMaxLen(self,param):
        result = (param >= len(self.tokens[self.tokenUnify].token)) 
        if result:
            self.tokenUnify += 1 
        return result
    
    def matchFromBigLetter(self,param):
        result = (param == self.tokens[self.tokenUnify].fromBigLetter()) 
        if result:
            self.tokenUnify += 1 
        return result 

    def matchOptional(self,param):
        oldTokenUnify = self.tokenUnify
        result = self.__unify(param) 
        if result:
            return True
        self.tokenUnify = oldTokenUnify  
        return True 
    
    def matchOneOf(self,param):
        oldTokenUnify = self.tokenUnify
        for p in param:
            result = self.__unify(p) 
            if result:
                return True
            self.tokenUnify = oldTokenUnify
        self.tokenUnify = oldTokenUnify      
        return False
    
    def matchGroup(self,param):
        for p in param:
            result = self.__unify(p)
            if not result:
                return False
        return True
    
    def matchRepeat(self,param):
        startTokenUnify = self.tokenUnify
        oldTokenUnify = self.tokenUnify
        result = self.__unify(param)
        if not result:
            self.tokenUnify = oldTokenUnify
            return False
        while result:        
            if self.tokenUnify >= len(self.tokens):
                self.tokenUnify = startTokenUnify
                return False
            oldTokenUnify = self.tokenUnify
            result = self.__unify(param)
        self.tokenUnify = oldTokenUnify  
        return True
             
    def matchAllUntil(self,param):
        isInclude = param.get('include',False)
        startTokenUnify = self.tokenUnify
        oldTokenUnify = self.tokenUnify
        result = self.__unify(param['exp'])
        while not result:        
            if self.tokenUnify == oldTokenUnify:
                self.tokenUnify += 1
            if self.tokenUnify >= len(self.tokens):
                self.tokenUnify = startTokenUnify
                return False
            oldTokenUnify = self.tokenUnify
            result = self.__unify(param['exp'])
            
        if not isInclude:    
            self.tokenUnify = oldTokenUnify  
        return True     
            
    @abstractmethod
    def genToken(self,start,end):    
        pass

class ExampleMatcher(FormalGrammar):
    def __init__(self):
        super(ExampleMatcher, self).__init__(
         [
            { 'oneOf':
                [   
                    {'group': [
                        {'newLine':'Left','exact:':"Пример"},
                        {'optional': {'onlyDigits':True} },
                        {'optional':
                            {'repeat': {'group':
                                    [{'exact':'.'},{'onlyDigits':True}]}
                             }
                        },
                        {'optional':
                            { 'oneOf': [
                                {'exact':'.'},
                                {'exact':':'}
                            ]},
                        },
                        {'allUntil':{'exp':{'newLine':'Left'},'include':False}}
                    ]},
                 ]
             }
        ]
        )
    def genToken(self,start,end):      
        token = genComplexToken(self.tokens, start, end)
        
        numeratedExample = False
        level = 0
        for t in token.internalTokens:
            if t.onlyDigits:
                numeratedExample = True
                level += 1
            elif not t.tokenType == TYPE_SIGN:
                break
        token.setAdditionalInfo("example", 
                                {'level': level,
                                 'numerated_example':numeratedExample})   
        self.tokenUnify = start
        self.newTokens.append(token)

class HeaderMatcher(FormalGrammar):
    def __init__(self):
        self.newTokens = []
        super(HeaderMatcher, self).__init__(
         [
            { 'oneOf':
                [   
                    {'group': [
                        {'newLine':'Left only','onlyDigits':True,'maxLen':1},
                        {'optional':
                            {'repeat': {'group':
                                    [{'exact':'.', 'newLine':'None'},{'onlyDigits':True, 'newLine':'None'}]}
                             }
                        },
                        {'optional':{'exact':'.', 'newLine':'None'}},
                        {'startFromBig':True},
                        {'allUntil':{'exp':{'newLine':'Left'},'include':False}}
                    ]},
                    {'group': [
                        { 'oneOf':
                            [
                                {'newLine':'Left','onlyBig':True},
                                {'group': [
                                    {'newLine':'Left only','onlyDigits':True,'maxLen':1},
                                    {'optional':
                                        {'repeat': {'group':
                                                [{'exact':'.', 'newLine':'None'},{'onlyDigits':True, 'newLine':'None'}]}
                                         }
                                    },
                                    {'optional':{'exact':'.', 'newLine':'None'}},       
                                ]},
                            ]
                        }, 
                        {'optional':{'repeat': {'onlyBig':True, 'newLine':'None'}}},
                        {'newLine':'Right','onlyBig':True},
                    ]},
                    {'newLine':'Both','exact':'Введение'},  
                    {'newLine':'Both','exact':'ВВЕДЕНИЕ'},  
                    {'group': [{'newLine':'Left','exact':'Список'},{'newLine':'Right','exact':'литературы'}]},  
                    {'group': [{'newLine':'Left','exact':'СПИСОК'},{'newLine':'Right','exact':'ЛИТЕРАТУРЫ'}]},  
                    {'newLine':'Both','exact':'Заключение'},  
                    {'newLine':'Both','exact':'ЗАКЛЮЧЕНИЕ'},  
                    {'group': [
                        { 'oneOf':
                            [
                                {'newLine':'Left','exact':"Приложение"},
                                {'newLine':'Left','exact':"ПРИЛОЖЕНИЕ"},
                            ]
                        }, 
                        {'optional':{'repeat': {'maxLen':1, 'newLine':'Right only'}}},
                    ]},
                 ]
             }
        ]
        )  
    __popularHeaders = ['введение', 'заключение', 'список литературы', 'список использованных источников']      
    def genToken(self,start,end):
        token = genComplexToken(self.tokens, start, end)
        
        popularHeader = token.token.lower() in HeaderMatcher.__popularHeaders
        numeratedHeader = False
        if popularHeader:
            headerLevel = 1
        else:
            headerLevel = 0
            for t in token.internalTokens:
                if t.onlyDigits():
                    numeratedHeader = True
                    headerLevel += 1
                elif not t.tokenType == TYPE_SIGN:
                    break
            if headerLevel == 0:
                headerLevel = 1   
        token.setAdditionalInfo("header", 
                                {'is_popular_header':popularHeader, 
                                 'header_level': headerLevel,
                                 'numerated_header':numeratedHeader})   
        self.tokenUnify = start
        self.newTokens.append(token)

#text = '''
#снегонакопления.
#ПРИЛОЖЕНИЕ 5
#Классификация снега
#'''  
            
#ts = TokenSplitter()
#ts.split(text)
#tokens = ts.getTokenArray()
           
#print(len(tokens))

#hm = HeaderMatcher()
#hm.combineTokens(tokens)

#print(len(tokens))
           
