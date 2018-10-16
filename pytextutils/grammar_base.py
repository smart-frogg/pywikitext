# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from pytextutils.token_splitter import TokenSplitter, Token, TYPE_COMPLEX_TOKEN,\
    TYPE_SIGN, POSTagger, TYPE_WORD

def genComplexToken(tokens, start, end, embedNewToken = True,lexicalMode=False):
    tokenTextArray = []
    for i in range(start, end):
        tokenTextArray.append(tokens[i].token)
    if len(tokenTextArray) == 0:
        return None
    if lexicalMode:
        splitter = ''
    else:    
        splitter = ' '
    tokenText = splitter.join(tokenTextArray)        
    token = Token(
            tokenText,
            tokens[start].startPos,
            tokens[end-1].endPos,
            tokens[start].isFlag('spaceLeft'),
            tokens[end-1].isFlag('spaceRight'),
            tokens[start].isFlag('newlineLeft'),
            tokens[end-1].isFlag('newlineRight'),
            TYPE_COMPLEX_TOKEN,
            tokens[start].tokenNum)
    token.setInternalTokens(tokens[start:end])
    if embedNewToken:
        tokens[start] = token
        for i in reversed(range(start+1, end)):
            del tokens[i]
    return token
        
class FormalGrammar(metaclass=ABCMeta):
    def __init__(self, grammar,lexicalMode = False):
        self.grammar = grammar
        self.lexicalMode = lexicalMode
        self.operations = {
            'exact': self.matchExact,
            'exactnocase': self.matchExactNoCase,
            'normalform': self.matchNormalForm,
            'maxlen': self.matchMaxLen,
            'newline': self.matchNewLine,
            'onlydigits': self.matchOnlyDigits,
            'onlybig': self.matchOnlyBig,
            'frombigletter': self.matchFromBigLetter,
            'cyrword': self.matchCyrWord,
            'pos':self.matchPOS,
            'endoftext':self.matchEndOfText,
            'checkflags':self.matchCheckFlags,
            
            'not': self.matchNot,
            'optional': self.matchOptional,
            'oneof': self.matchOneOf,
            'group': self.matchGroup,
            'repeat': self.matchRepeat,
            'alluntil': self.matchAllUntil,
            }
    def combineTokens(self,tokens,embedNewTokens = True):
        self.embedNewTokens = embedNewTokens
        self.newTokens = []
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
            if self.tokenUnify >= len(self.tokens):
                return False
            self.tokenUnify = oldTokenUnify 
            operation = gToken 
            unificationComplete &= self.operations[operation.lower()](grammarToken[operation])
            if not unificationComplete:
                break
        return unificationComplete
    
    def matchNormalForm (self,param):   
        result = self.tokens[self.tokenUnify].getBestNormalForm() == param
        if result:
            self.tokenUnify += 1 
        return result 
    def matchExactNoCase(self,param):
        result = self.tokens[self.tokenUnify].token.lower() == param.lower()
        if result:
            self.tokenUnify += 1 
        return result 
        
    def matchExact (self,param):
        result = self.tokens[self.tokenUnify].token == param
        if result:
            self.tokenUnify += 1 
        return result 

    def matchNewLine(self,param):
        result = ((param.lower() == 'left' and self.tokens[self.tokenUnify].isFlag('newlineLeft')) or 
                  (param.lower() == 'right' and self.tokens[self.tokenUnify].isFlag('newlineRight')) or
                  (param.lower() == 'left only' and self.tokens[self.tokenUnify].isFlag('newlineLeft') 
                                                and not self.tokens[self.tokenUnify].isFlag('newlineRight')) or 
                  (param.lower() == 'right only' and self.tokens[self.tokenUnify].isFlag('newlineRight')
                                                 and not self.tokens[self.tokenUnify].isFlag('newlineLeft')) or
                  (param.lower() == 'both' and self.tokens[self.tokenUnify].isFlag('newlineRight') 
                                           and self.tokens[self.tokenUnify].isFlag('newlineLeft')) or
                  (param.lower() == 'none' and not self.tokens[self.tokenUnify].isFlag('newlineRight') 
                                           and not self.tokens[self.tokenUnify].isFlag('newlineLeft')))
        if result:
            self.tokenUnify += 1 
        return result
     
    def matchPOS(self,param):
        result = self.tokens[self.tokenUnify].getBestPOS() == param
        if result:
            self.tokenUnify += 1 
        return result
    
    def matchCheckFlags(self,param):
        result = True
        for f in param: 
            result &= self.tokens[self.tokenUnify].isFlag(f) == param[f]
            if not result:
                break
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
     
    def matchCyrWord(self,param):
        result = (param == self.tokens[self.tokenUnify].allCyr()) 
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
    
    def matchEndOfText(self,param):
        result = self.tokenUnify == len(self.tokens)-1
        if result:
            self.tokenUnify += 1 
        return result 
    
    def matchNot(self,param):
        result = self.__unify(param) 
        return not result
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
        result = self.__unify(param['element'])
        minCount = param.get('minCount',None)
        if not result:
            self.tokenUnify = startTokenUnify
            return False
        count = 1
        while result:        
            if self.tokenUnify >= len(self.tokens):
                #self.tokenUnify = startTokenUnify
                #return True
                break
            oldTokenUnify = self.tokenUnify
            result = self.__unify(param['element'])
            if result:
                count += 1
        if not result:   
            self.tokenUnify = oldTokenUnify
        if minCount and minCount > count:
            self.tokenUnify = startTokenUnify
            return False   
        return True
             
    def matchAllUntil(self,param):
        isInclude = param.get('include',False)
        startTokenUnify = self.tokenUnify
        oldTokenUnify = self.tokenUnify
        if param.get('minCount',None):
            for i in range(param.get('minCount')):
                if self.tokenUnify >= len(self.tokens):
                    self.tokenUnify = startTokenUnify
                    return False
                result = self.__unify(param['exp'])
                if result: 
                    self.tokenUnify = startTokenUnify
                    return False
                if self.tokenUnify == oldTokenUnify:
                    self.tokenUnify += 1
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
            
    def genToken(self,start,end):    
        token = genComplexToken(self.tokens, start, end, self.embedNewTokens,self.lexicalMode)
        self.processToken(token)
        if self.embedNewTokens:
            self.tokenUnify = start
        else:
            self.tokenUnify = end
        self.newTokens.append(token)
    
    @abstractmethod
    def processToken(self,token):
        pass

class PatternMatcher(FormalGrammar):
    def __init__(self, grammar=[]):
        super(PatternMatcher, self).__init__(grammar)
    def setParameters (self, grammar, fragmentType):
        self.grammar = grammar
        self.fragmentType = fragmentType
    def processToken(self,token):      
        token.setFlag(self.fragmentType)   
            


class SentenceSplitter(FormalGrammar):
    def __init__(self):
        super(SentenceSplitter, self).__init__(
         [
            {'oneOf': [
                {'checkFlags':{'header':True}},
                {'allUntil':
                    {'exp':
                        {'oneOf':
                            [
                                {'exact':'.'},
                                {'exact':'?'},
                                {'exact':'!'},
                                {'endoftext':True},
                            ]
                        },
                      'include':True
                     }
                
                }
            ]}
            
         ]
        )  
    def processToken(self,token):
        if token:
            token.setFlag("sentence") 

class FormalLanguagesMatcher(FormalGrammar):
    def __init__(self):
        super(FormalLanguagesMatcher, self).__init__(
         [
            {'group':
                [
                    {'not':
                        {'oneOf': [
                            {'exact': '.'},
                            {'cyrWord': True},
                        ]}
                    },
                    {'allUntil':
                        {
                            'exp': {
                                'oneOf':[
                                    {'cyrWord': True},
                                    {'group':[
                                        {'exact': '.'},
                                        {'cyrWord': True},
                                    ]},
                                    {'exact': '.', 'endOfText': True}                             
                                ]
                            },
                            'include':False,
                            'minCount':3
                         }
                     }
                 ]
             }
         ]
        )  
    def processToken(self,token):
        token.setFlag("formal") 
        
class NameGroupsMatcher(FormalGrammar):
    def __init__(self):
        super(NameGroupsMatcher, self).__init__(
         [
            {'repeat': 
                {'oneOf':
                    [   
                        {'POS':'NOUN'},
                        {'POS':'NPRO'},
                        {'POS':'ADJF'},
                        {'POS':'ADJS'},
                        {'POS':'PRED'}
                    ]
                 }
             }
         ]
        )  
         
    def processToken(self,token):
        token.setFlag("name_group") 


        

#text = '''
# После обучения перцептрон готов работать в режиме распознавания [ 10 ] или обобщения [ 11 ] . В этом режиме перцептрону предъявляются ранее неизвестные ему объекты , и перцептрон должен установить , к какому классу они принадлежат .
#    '''
#ts = TokenSplitter()
#tokens = ts.split(text)
#fs = FormalLanguagesMatcher()
#fs.combineTokens(tokens)
#ss = SentenceSplitter()
#ss.combineTokens(tokens)
#print(len(tokens))

#text = 'Каждый рецептор может находиться в одном из двух состояний — покоя или возбуждения , и только в последнем случае он передаёт единичный сигнал в следующий слой , ассоциативным элементам . A - элементы называются ассоциативными , потому что каждому такому элементу , как правило , соответствует целый набор ( ассоциация ) S - элементов . A - элемент активизируется , как только количество сигналов от S - элементов на его входе превысило некоторую величину θ [ nb 5 ] .'        
#text = 'величину θ [ nb 5 ] .'        
#text = 'Иногда (а точнее, довольно часто) tokens = ts.getTokenArray() возникают ситуации, когда нужно сделать строку, подставив в неё некоторые данные, полученные в процессе выполнения программы (пользовательский ввод, данные из файлов и так далее). Подстановку данных можно сделать с помощью ts.split(text) форматирования строк. '
#ts = TokenSplitter()
#ts.split(text)
#tokens = ts.getTokenArray()
#fs = FormalLanguagesMatcher()
#fs.combineTokens(tokens)
#ss = SentenceSplitter()
#ss.combineTokens(tokens)
#print(len(tokens))
#POSTagger().posTagging(tokens)

#ns = NameGroupsSelector()
#ns.combineTokens(tokens)
#print(len(tokens))           
#fs = FormalLanguagesSelector()
#fs.combineTokens(tokens)
#print(len(tokens))

#ss = SentenceSplitter()
#ss.combineTokens(tokens)
#print(len(tokens))

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
           
