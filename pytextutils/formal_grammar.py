# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from pytextutils.token_splitter import TokenSplitter, Token, TYPE_COMPLEX_TOKEN,\
    TYPE_SIGN


class FormalGrammar(metaclass=ABCMeta):
    def __init__(self, grammar):
        self.grammar = grammar
        self.operations = {
            'exact': self.matchExact,
            'newline': self.matchNewLine,
            'onlydigits': self.matchOnlyDigits,
            'onlybig': self.matchOnlyBig,
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


class HeaderMatcher(FormalGrammar):
    def __init__(self):
        self.newTokens = []
        super(HeaderMatcher, self).__init__(
         [
            { 'oneOf':
                [   
                    {'group': [
                        {'newLine':'Left','onlyDigits':True},
                        {'optional':
                            {'repeat': {'group':
                                    [{'exact':'.'},{'onlyDigits':True}]}
                             }
                        },
                        {'optional':{'exact':'.'}},
                        {'allUntil':{'exp':{'newLine':'Left'},'include':False}}
                    ]},
                    {'group': [
                        {'newLine':'Left','onlyBig':True},
                        {'repeat': {'onlyBig':True, 'newLine':'None'}},
                        {'newLine':'Right','onlyBig':True},
                    ]},
                    {'newLine':'Both','exact':'Введение'},  
                    {'newLine':'Both','exact':'ВВЕДЕНИЕ'},  
                    {'group': [{'newLine':'Left','exact':'Список'},{'newLine':'Right','exact':'литературы'}]},  
                    {'group': [{'newLine':'Left','exact':'СПИСОК'},{'newLine':'Right','exact':'ЛИТЕРАТУРЫ'}]},  
                    {'newLine':'Both','exact':'Заключение'},  
                    {'newLine':'Both','exact':'ЗАКЛЮЧЕНИЕ'},  
                 ]
             }
        ]
        )  
    __popularHeaders = ['введение', 'заключение', 'список литературы', 'список использованных источников']      
    def genToken(self,start,end):
        tokenText = []
        for i in range(start, end):
            tokenText.append(self.tokens[i].token)
                
        token = Token(
                ' '.join(tokenText),
                self.tokens[start].spaceLeft,
                self.tokens[end].spaceRight,
                self.tokens[start].newlineLeft,
                self.tokens[end].newlineRight,
                TYPE_COMPLEX_TOKEN,
                self.tokens[start].tokenNum)
        token.setInternalTokens(self.tokens[start:end])
        popularHeader = tokenText.lower() in HeaderMatcher.__popularHeaders
        numeratedHeader = False
        if popularHeader:
            headerLevel = 1
        else:
            headerLevel = 0
            for t in token.internalTokens:
                if t.onlyDigits:
                    numeratedHeader = True
                    headerLevel += 1
                elif not t.tokenType == TYPE_SIGN:
                    break
            if headerLevel == 0:
                headerLevel = 1   
        token.setAdditionalInfo("header", 
                                {'is_populat_header':popularHeader, 
                                 'header_level': headerLevel,
                                 'numerated_header':numeratedHeader})   
        self.tokens[start] = token
        for i in reversed(range(start+1, end)):
            del self.tokens[i]
        self.tokenUnify = start
        self.newTokens.append(token)

#text = '''
#Между тем, даже беглый взгляд на тексты новостей в СМИ свидетельствует о том, что как раз лексически полные именные группы выступают в них в качестве основного средства повторной номинации. 
#2. Интродуктивная и идентифицирующая референция в новостных текстах
#2.1. Типы референции и референциальных средств
#Для референции к тем или иным референтам говорящий (автор) может использовать два основных типа референциальных средств: лексически полные и редуцированные. Как уже говорилось, к редуцированным средствам относят анафорическое местоимение и анафорический ноль.
#'''  
            
#ts = TokenSplitter()
#ts.split(text)
#tokens = ts.getTokenArray()
           
#print(len(tokens))

#hm = HeaderMatcher()
#hm.combineTokens(tokens)

#print(len(tokens))
           
