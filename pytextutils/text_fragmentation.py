# -*- coding: utf-8 -*-
from pytextutils.token_splitter import TokenSplitter, POSTagger
from pytextutils.text_stat import TextCleaner,normalize
from pytextutils.formal_grammar import FormalLanguagesMatcher,  SentenceSplitter, PatternMatcher
from pytextutils.grammar_lexic import DefisWordsBuilder, InitialsWordsBuilder
from pytextutils.science_patterns import POSListIndex,CollocationGrammars,calcHist
from pywikiaccessor.wiki_accessor import WikiAccessor
from math import sqrt
from operator import itemgetter

class TextFragmentator:
    def __init__(self,accessor,prefix):
        #self.hists
        #self.tfidf
        #self.patterns
        
        
        self.tokenSplitter = TokenSplitter()
        self.posTagger = POSTagger()
        self.flSelector = FormalLanguagesMatcher()
        self.defisWordsBuilder = DefisWordsBuilder() 
        self.initialsWordsBuilder = InitialsWordsBuilder()
        self.formalLanguagesMatcher = FormalLanguagesMatcher() 
        self.sentenceSplitter = SentenceSplitter()
        
        self.posListIndex = POSListIndex(accessor,prefix)
        self.collocatonsGrammars = CollocationGrammars(accessor,prefix)
        self.fragmentTypes = self.collocatonsGrammars.getFunctionalTypes() 
        self.verbs = self.posListIndex.getVerbsHistsForAllTypes()
        self.patternMatcher = PatternMatcher()
        
        self.sq = lambda x: x*x
        self.sums = {}
        for fType in self.verbs:
            self.sums[fType] = self.module(self.verbs[fType])

    def module(self,data):
        return sqrt(sum(map(self.sq, data.values())))
    
    def findPatterns(self,fType,sentence):
        patterns = self.collocatonsGrammars.getGrammars(fType,200)
        patternsWeight = 0
        for pattern in patterns:
            self.patternMatcher.setParameters(pattern['grammar'], fType)
            self.patternMatcher.combineTokens(sentence.internalTokens,False)
            if len(self.patternMatcher.newTokens) > 0:
                sentence.setFlag(fType,True)
                patternsWeight += pattern['freq']/pattern['total_freq']
        return patternsWeight 

    def estimateLexicalSimilarity(self,fType,sentence):
        hists = calcHist(sentence.internalTokens)
        typeVerbs = self.verbs[fType]
        est = 0
        for v in hists['VERB']:
            est += hists['VERB'][v]*typeVerbs[v]
        module = self.module(hists['VERB'])
        if module == 0: 
            return 0
        est /= self.sums[fType]*module   
        return est
            
    def estimate(self,fType,sentence):
        patternsCount = self.findPatterns(fType, sentence)
        lexicalSimilarity = self.estimateLexicalSimilarity(fType, sentence)
        #print (fType+": "+str(patternsCount))
        return {
                'pattern': patternsCount,
                'lexical': lexicalSimilarity,
            }
        
    def genFragments(self,text):
        tokens = self.tokenSplitter.split(text)
        self.posTagger.posTagging(tokens)
        self.defisWordsBuilder.combineTokens(tokens)
        self.initialsWordsBuilder.combineTokens(tokens)
        self.formalLanguagesMatcher.combineTokens(tokens)
        self.sentenceSplitter.combineTokens(tokens)
        
        estimations = []
        for ind in range(len(tokens)):
            bestEstimation = {
                'pattern':
                    {
                        'fType' : self.fragmentTypes[0],
                        'estimation' : 0,
                        'all' : {}
                     },
                'lexical':
                    {
                        'fType' : self.fragmentTypes[0],
                        'estimation' : 0,
                        'all' : {}
                    },
                'total':
                    {
                        'fType' : self.fragmentTypes[0],
                        'estimation' : 0,
                        'all' : {}
                    }
            }
            for fType in self.fragmentTypes:
                oneEstimation = self.estimate(fType, tokens[ind])
                for parameter in ['pattern','lexical']:
                    bestEstimation[parameter]['all'][fType] = oneEstimation[parameter] 
                    
            for parameter in ['pattern','lexical']:
                bestEstimation[parameter]['all'] = normalize(bestEstimation[parameter]['all'])
            for fType in self.fragmentTypes:
                bestEstimation['total']['all'][fType] = bestEstimation['pattern']['all'][fType] + 0.7*bestEstimation['lexical']['all'][fType]        
            bestEstimation['total']['all'] = normalize(bestEstimation['total']['all'])    
            for parameter in bestEstimation:
                bestEstimation[parameter]['all'] = sorted(bestEstimation[parameter]['all'].items(), key=itemgetter(1),reverse=True)
                bestEstimation[parameter]['estimation'] = bestEstimation[parameter]['all'][0][1]
                if bestEstimation[parameter]['estimation'] == 0:
                    bestEstimation[parameter]['fType'] = None
                else:
                    bestEstimation[parameter]['fType'] = bestEstimation[parameter]['all'][0][0]
            estimations.append(bestEstimation)
            print (tokens[ind].token)
            for parameter in bestEstimation:
                print("\t"+parameter+'\t'+str(bestEstimation[parameter]['fType'])+'\t'+str(bestEstimation[parameter]['estimation']))
        #self.combineTokens(estimations)
        
    def compatible(self,estC,estL=None,estR=None):
        if not (estL or estR):
            return True
        #if estL:
            
        
    def combineTokens(self,estimations):
        fragmentStart = -1
        fragmentEnd = -1
        for indToken in range(len(estimations)):
            if (estimations['pattern']['fType'] == estimations['lexical']['fType'] and
                estimations['lexical']['fType']):
                if fragmentEnd == -1:
                    fragmentEnd = indToken
                else:
                    if indToken > 0 and self.compatible(None,estimations[indToken],None): 
                        pass   
                if fragmentStart == -1: 
                    fragmentStart = 0
                         
        
directory = "C:/WORK/science/onpositive_data/python/"
accessor =  WikiAccessor(directory)
text = '''
Элементарный перцептрон состоит из элементов трёх типов: S-элементов, A-элементов и одного R-элемента. S-элементы — это слой сенсоров или рецепторов. В физическом воплощении они соответствуют, например, светочувствительным клеткам сетчатки глаза или фоторезисторам матрицы камеры. Каждый рецептор может находиться в одном из двух состояний — покоя или возбуждения, и только в последнем случае он передаёт единичный сигнал в следующий слой, ассоциативным элементам.

A-элементы называются ассоциативными, потому что каждому такому элементу, как правило, соответствует целый набор (ассоциация) S-элементов. A-элемент активизируется, как только количество сигналов от S-элементов на его входе превысило некоторую величину θ[nb 5]. Таким образом, если набор соответствующих S-элементов располагается на сенсорном поле в форме буквы «Д», A-элемент активизируется, если достаточное количество рецепторов сообщило о появлении «белого пятна света» в их окрестности, то есть A-элемент будет как бы ассоциирован с наличием/отсутствием буквы «Д» в некоторой области.

Сигналы от возбудившихся A-элементов, в свою очередь, передаются в сумматор R, причём сигнал от i-го ассоциативного элемента передаётся с коэффициентом w i {\displaystyle w_{i}} w_{{i}}[9]. Этот коэффициент называется весом A—R связи.

Так же как и A-элементы, R-элемент подсчитывает сумму значений входных сигналов, помноженных на веса (линейную форму). R-элемент, а вместе с ним и элементарный перцептрон, выдаёт «1», если линейная форма превышает порог θ, иначе на выходе будет «−1». Математически, функцию, реализуемую R-элементом, можно записать так:

    f ( x ) = sign ⁡ ( ∑ i = 1 n w i x i − θ ) {\displaystyle f(x)=\operatorname {sign} (\sum _{i=1}^{n}w_{i}x_{i}-\theta )} f(x)=\operatorname {sign} (\sum _{i=1}^{n}w_{i}x_{i}-\theta ).

Обучение элементарного перцептрона состоит в изменении весовых коэффициентов w i {\displaystyle w_{i}} w_{i} связей A—R. Веса связей S—A (которые могут принимать значения {−1; 0; +1}) и значения порогов A-элементов выбираются случайным образом в самом начале и затем не изменяются. (Описание алгоритма смотреть ниже.)

После обучения перцептрон готов работать в режиме распознавания[10] или обобщения[11]. В этом режиме перцептрону предъявляются ранее неизвестные ему объекты, и перцептрон должен установить, к какому классу они принадлежат. Работа перцептрона состоит в следующем: при предъявлении объекта возбудившиеся A-элементы передают сигнал R-элементу, равный сумме соответствующих коэффициентов w i {\displaystyle w_{i}} w_{i}. Если эта сумма положительна, то принимается решение, что данный объект принадлежит к первому классу, а если она отрицательна — то ко второму[12].

Классический метод обучения перцептрона — это метод коррекции ошибки[8]. Он представляет собой такой вид обучения с учителем, при котором вес связи не изменяется до тех пор, пока текущая реакция перцептрона остается правильной. При появлении неправильной реакции вес изменяется на единицу, а знак (+/-) определяется противоположным от знака ошибки.

Допустим, мы хотим обучить перцептрон разделять два класса объектов так, чтобы при предъявлении объектов первого класса выход перцептрона был положителен (+1), а при предъявлении объектов второго класса — отрицательным (−1). Для этого выполним следующий алгоритм:[5]

    Случайным образом выбираем пороги для A-элементов и устанавливаем связи S—A (далее они изменяться не будут).
    Начальные коэффициенты w i {\displaystyle w_{i}} w_{i} полагаем равными нулю.
    Предъявляем обучающую выборку: объекты (например, круги либо квадраты) с указанием класса, к которым они принадлежат.
        Показываем перцептрону объект первого класса. При этом некоторые A-элементы возбудятся. Коэффициенты w i {\displaystyle w_{i}} w_{i}, соответствующие этим возбуждённым элементам, увеличиваем на 1.
        Предъявляем объект второго класса и коэффициенты w i {\displaystyle w_{i}} w_{i} тех A-элементов, которые возбудятся при этом показе, уменьшаем на 1.
    Обе части шага 3 выполним для всей обучающей выборки. В результате обучения сформируются значения весов связей w i {\displaystyle w_{i}} w_{i}.

Теорема сходимости перцептрона[8], описанная и доказанная Ф. Розенблаттом (с участием Блока, Джозефа, Кестена и других исследователей, работавших вместе с ним), показывает, что элементарный перцептрон, обучаемый по такому алгоритму, независимо от начального состояния весовых коэффициентов и последовательности появления стимулов всегда приведёт к достижению решения за конечный промежуток времени.
'''
tf = TextFragmentator(accessor,'miph_')
tf.genFragments(text)