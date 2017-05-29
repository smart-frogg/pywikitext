# -*- coding: utf-8 -*-
from pytextutils.grammar_base import FormalGrammar
from pytextutils.token_splitter import TYPE_SIGN

class ExampleMatcher(FormalGrammar):
    def __init__(self):
        super(ExampleMatcher, self).__init__(
         [
            { 'oneOf':
                [   
                    {'group': [
                        {'newLine':'Left','exact':"Пример"},
                        {'optional': {'onlyDigits':True} },
                        {'optional':
                            {'repeat': { 'element': {'group':
                                    [{'exact':'.'},{'onlyDigits':True}]}}
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
                            {'repeat': { 'element': {'group':
                                    [{'exact':'.', 'newLine':'None'},{'onlyDigits':True, 'newLine':'None'}]}
                             }}
                        },
                        {'optional':{'exact':'.', 'newLine':'None'}},
                        {'fromBigLetter':True},
                        {'allUntil':{'exp':{'newLine':'Left'},'include':False}}
                    ]},
                    {'group': [
                        { 'oneOf':
                            [
                                {'newLine':'Left','onlyBig':True},
                                {'group': [
                                    {'newLine':'Left only','onlyDigits':True,'maxLen':1},
                                    {'optional':
                                        {'repeat': { 'element': {'group':
                                                [{'exact':'.', 'newLine':'None'},{'onlyDigits':True, 'newLine':'None'}]}
                                         }}
                                    },
                                    {'optional':{'exact':'.', 'newLine':'None'}},       
                                ]},
                            ]
                        }, 
                        {'optional':{'repeat': { 'element': {'onlyBig':True, 'newLine':'None'}}}},
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
                        {'optional':{'repeat': { 'element': {'maxLen':1, 'newLine':'Right only'}}}},
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

class InSentenceListMatcher (FormalGrammar):
    def __init__(self):
        super(InSentenceListMatcher, self).__init__( 
            # item; item; item
            [{'group':[
                    {'repeat': { 'element':
                        {'oneOf':
                            [   
                                {'POS':'NOUN'},
                                {'POS':'NPRO'},
                                {'POS':'ADJF'},
                                {'POS':'ADJS'},
                                {'POS':'PRED'}
                            ]
                         }
                    }},
                    {'repeat': { 'element': 
                        {'group':
                            [
                                {'exact':';'},
                                {'repeat': { 'element':
                                    {'oneOf':
                                        [   
                                            {'POS':'NOUN'},
                                            {'POS':'NPRO'},
                                            {'POS':'ADJF'},
                                            {'POS':'ADJS'},
                                            {'POS':'PRED'}
                                        ]
                                     }
                                }}
                                
                            ]
                        },'minCount':2
                    }}
                 ]}]
            )
    def processToken(self,token):   
        token.setFlag("inSentenceList")
        token.setAdditionalInfo('listType',"inSentenceList")
        
class UnorderedListMatcher (FormalGrammar):
    def __init__(self):
        self.items = [
                [# ∙ Item text
                    {'exact':"∙"}
                ],
                [# - Item text
                    {'exact':"-"}
                ]
            ]                 
        grammars = [] 
        for item in self.items:
            item[0]['newLine'] = 'Left'
            for elem in item[1:]:
                elem['newLine'] = 'None'
            item.append({'allUntil':{'exp':{'oneOf':[{'newLine':'Right'},{'endOfText':True}]},'include':True}})
            grammars.append({"repeat":{ 'element': {'group': item},'minCount':2}})
        super(UnorderedListMatcher, self).__init__([{ 'oneOf': grammars}])
       
    def processToken(self,token):   
        token.setFlag("unorderedList")
        token.setAdditionalInfo('listType',"unorderedList")

class OrderedListMatcher (FormalGrammar):
    def __init__(self):
        self.items = [
                [# [1] Item text
                    {'exact':"["},
                    {'onlyDigits':True},
                    {'exact':"]"}
                ],
                [# (1) Item text
                    {'exact':"("},
                    {'onlyDigits':True},
                    {'exact':")"}
                ],
                [# 1) Item text
                    {'onlyDigits':True},
                    {'exact':")"}
                ],
                [# 1. Item text
                    {'onlyDigits':True},
                    {'exact':"."}
                ],
                [# 1: Item text
                    {'onlyDigits':True},
                    {'exact':":"}
                ]
            ]                 
        grammars = [] 
        for item in self.items:
            item[0]['newLine'] = 'Left'
            for elem in item[1:]:
                elem['newLine'] = 'None'
            item.append({'allUntil':{'exp':{'oneOf':[{'newLine':'Right'},{'endOfText':True}]},'include':True}})
            grammars.append({"repeat":{ 'element': {'group': item},'minCount':2}})
        super(OrderedListMatcher, self).__init__([{ 'oneOf': grammars}])
       
    def processToken(self,token):   
        token.setFlag("orderedList")
        token.setAdditionalInfo('listType',"orderedList")
                
class ListMatcher:
    def __init__(self):
        self.inSentenceMatcher = InSentenceListMatcher() 
        self.unorderedMatcher = UnorderedListMatcher() 
        self.orderedMatcher = OrderedListMatcher() 
    def getListFlags(self):
        return ["orderedList","unorderedList","inSentenceList"]    
    def combineTokens(self,tokens,embedNewTokens = True):
        self.newTokens = []
        self.inSentenceMatcher.combineTokens(tokens, embedNewTokens)
        self.newTokens.extend(self.inSentenceMatcher.newTokens) 
        self.unorderedMatcher.combineTokens(tokens, embedNewTokens) 
        self.newTokens.extend(self.unorderedMatcher.newTokens) 
        self.orderedMatcher.combineTokens(tokens, embedNewTokens) 
        self.newTokens.extend(self.orderedMatcher.newTokens) 

def headersTest():
    from pytextutils.token_splitter import TokenSplitter         
    text = '''Введение
Одной из важнейших задач в сфере обработки естественного языка (Natural Language Processing, NLP) является извлечение фактографической информации (information extraction, event extraction), то есть извлечение структурированной информации о ситуации заданного типа из текстов на естественном языке (в первую очередь мы ориентируемся на тексты СМИ). Структура (фрейм) извлеченной информации зависит от поставленной задачи, но в самом типичном случае извлекается упоминание о событии и атрибуты события: где произошло событие, его участники и тому подобное (Подробнее об этом смотрите [1])
Для получения более полной картины необходимо также извлечь модальные и темпоральные характеристики события. Настоящая статья посвящена анализу модального аспекта.
В отличие от существующих подходов к этому вопросу, особое внимание уделяется тому, как следует анализировать события, находящиеся в сфере действия разнородных маркеров модальности.
Учитывается максимально широкий круг модальных модификаторов: не только модальные глаголы и вводные конструкции со значением достоверности (которые обычно в первую очередь рассматриваются всеми авторами в теме модальность), но и показатели цитирования, фактивные и импликативные глаголы и тому подобное
1. Основные понятия
Поскольку в терминологии по теме «модальность» существует множество разночтений, необходимо начать с определения основных терминов, которыми мы будем пользоваться.
1.1. Понятие пропозиции
Прежде, чем вплотную подойти к обсуждению модальности, нам необходимо упомянуть крайне важное для этой темы понятие пропозиции (в данном случае это лингвистический термин, не идентичный пропозиции в логике).

    '''  
                
    ts = TokenSplitter()
    ts.split(text)
    tokens = ts.getTokenArray()
               
    print(len(tokens))
    
    hm = HeaderMatcher()
    hm.combineTokens(tokens)
    
    print(len(tokens))
    

def listsTest():
    from pytextutils.token_splitter import TokenSplitter         
    text = '''
1. Введение
    Перечислим основные виды замены, характерные для повторных номинаций в новостных текстах:

(1) замена ИГ на ИГ, которой соответствует вышестоящий концепт:губернатор — глава, область — регион, дума — парламент;
(2) замена имени экземпляра (имени собственного или названиядескрипции) на ИГ, которой соответствует родительский концепт экземпляра: МЧС — министерство, Приморский край — край;
(3) замена ИГ с семантикой базового концепта на ИГ с семантикойаспекта: компания — ритейлер;
Наиболее распространены в
качестве номинаций лица функциональные имена (названия лиц
по должности, роду занятий, титулы, ранги, звания), реляционные
имена (например, термины родства) и актуальные имена (носители
ситуативного признака, например кандидат в ситуации выборов).
Перечислим основные виды замены, характерные для повторных номинаций в новостных текстах:

     Список литературы
[1] Кронгауз М. А. Семантика. М : РГГУ, 2001. –– 299 c. ↑1
[2] Giv`on T. Coherence in text, coherence in mind // Pragmatics and cognition,1993. Vol. 1(2) ↑1
[3] Валгина Н. С. Теория текста: Учебное пособие. М. : Логос, 2003. ↑1
[4] Фёдорова О. С. Текстовая анафора: сочетание статистического икогнитивного подходов (на материале цахурского языка) // ТрудыМеждународного семинара Диалог-2000 по компьютерной лингвистике и ееприложениям. –– Протвино, 2000. Т. 1 ↑1, 1.1
   '''  
                
    ts = TokenSplitter()
    ts.split(text)
    tokens = ts.getTokenArray()
               
    print(len(tokens))
    
    lm = ListMatcher()
    lm.combineTokens(tokens)
    
    print(len(tokens))       

if __name__=='__main__':
    from pytextutils.token_splitter import TokenSplitter,POSTagger         
    text = '''
    (1) замена ИГ на ИГ, которой соответствует вышестоящий концепт: губернатор — глава, область — регион, дума — парламент;
(2) замена имени экземпляра (имени собственного или названиядескрипции) на ИГ, которой соответствует родительский концепт экземпляра: МЧС — министерство, Приморский край — край;
(3) замена ИГ с семантикой базового концепта на ИГ с семантикой аспекта: компания — ритейлер;
(4) замена-трансформация: администрация края — краевая администрация, губернатор Приморья — приморский губернатор;
(5) «метонимическая» замена: адвокат X-а (реляционное имя) — адвокат (род занятий); вариант такой замены — подмена референта, например: Московская область — Подмосковье;
(6) синонимическая и квазисинонимическая замена: адвокат (род занятий) — правозащитник, мэр — градоначальник, городской голова;
(7) ассоциативная замена: премьер-министр — политик, министр — чиновник, федеральное агентство — ведомство.
'''  
                
    ts = TokenSplitter()
    ts.split(text)
    tokens = ts.getTokenArray()
               
    print(len(tokens))
    
    POSTagger().posTagging(tokens)
    hm = HeaderMatcher()
    hm.combineTokens(tokens)
    lm = ListMatcher()
    lm.combineTokens(tokens)
    
    print(len(tokens)) 