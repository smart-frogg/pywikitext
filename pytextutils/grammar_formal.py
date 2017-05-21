# -*- coding: utf-8 -*-
from pytextutils.formal_grammar import FormalGrammar
from pytextutils.token_splitter import TYPE_SIGN

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
        
    def processToken(self,token):      
        numeratedExample = False
        level = 0
        for t in token.internalTokens:
            if t.onlyDigits:
                numeratedExample = True
                level += 1
            elif not t.tokenType == TYPE_SIGN:
                break
        token.setFlag("example")    
        token.setAdditionalInfo("example", 
                                {'level': level,
                                 'numerated_example':numeratedExample})   

class HeaderMatcher(FormalGrammar):
    def __init__(self):
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
    def processToken(self,token):        
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
        token.setFlag("header")
        token.setAdditionalInfo("header", 
                                {'is_popular_header':popularHeader, 
                                 'header_level': headerLevel,
                                 'numerated_header':numeratedHeader})   