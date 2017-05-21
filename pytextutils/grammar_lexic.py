# -*- coding: utf-8 -*-
from pytextutils.formal_grammar import FormalGrammar
from pytextutils.token_splitter import TYPE_TOKEN

class DefisWordsBuilder (FormalGrammar):
    def __init__(self):
        super(DefisWordsBuilder, self).__init__(
         [
            {'oneOf': 
                [
                    {'group': [{'exactnocase':'из'},{'exact':'-'},{'exactnocase':'за'}]},
                    {'group': [{'exactnocase':'из'},{'exact':'-'},{'exactnocase':'под'}]},
                    {'group': [{'exactnocase':'по'},{'exact':'-'},{'exactnocase':'над'}]},
                    {'group': [
                        {'oneOf':
                            [
                                {'exactnocase':'когда'},
                                {'exactnocase':'кто'},
                                {'exactnocase':'где'},
                                {'exactnocase':'зачем'},
                                {'exactnocase':'почему'},
                                {'exactnocase':'отчего'},
                            ]},
                        {'exact':'-'},
                        {'oneOf':
                            [
                                {'exactnocase':'то'},
                                {'exactnocase':'либо'},
                                {'exactnocase':'нибудь'}
                            ]
                        }
                    ]},
                    {'group': [
                        {'oneOf':
                            [
                                {'exactnocase':'северо'},
                                {'exactnocase':'юго'},
                            ]},
                        {'exact':'-'},
                        {'oneOf':
                            [
                                {'exactnocase':'запад'},
                                {'exactnocase':'восток'}
                            ]
                        }
                    ]},
                    {'oneOf':
                        [
                            {'group': [
                                {'exactnocase':'в'},
                                {'exact':'-'},
                                {'oneOf':
                                    [
                                        {'exactnocase':'третьих'},
                                        {'exactnocase':'четвертых'},
                                        {'exactnocase':'пятых'},
                                        {'exactnocase':'шестых'},
                                        {'exactnocase':'седьмых'},
                                        {'exactnocase':'восьмых'},
                                    ]
                                }
                            ]},
                            {'group': [
                                {'exactnocase':'во'},
                                {'exact':'-'},
                                {'oneOf':
                                    [
                                        {'exactnocase':'первых'},
                                        {'exactnocase':'вторых'}
                                    ]
                                }
                            ]},
                        ]
                    }
                ]
            }
          ], lexicalMode = True
        ) 
    def processToken(self,token):
        token.tokenType = TYPE_TOKEN
        token.setFlag("defis_group") 

class InitialsWordsBuilder (FormalGrammar):
    def __init__(self):
        super(InitialsWordsBuilder, self).__init__(
         [
            {'oneOf': 
                [
                    {'group': [
                        {'fromBigLetter':True},
                        {'fromBigLetter':True, 'maxLen':2},
                        {'exact':'.'},
                        {'optional': {
                            'group':[
                                {'fromBigLetter':True, 'maxLen':2},
                                {'exact':'.'}
                            ]
                        }}
                    ]},
                    {'group': [
                        {'fromBigLetter':True, 'maxLen':2},
                        {'exact':'.'},
                        {'optional': {
                            'group':[
                                {'fromBigLetter':True, 'maxLen':2},
                                {'exact':'.'}
                            ]
                        }},
                        {'fromBigLetter':True}
                    ]}
                ]
            }
          ]
        ) 
    def processToken(self,token):
        token.tokenType = TYPE_TOKEN
        token.setFlag("initials")         