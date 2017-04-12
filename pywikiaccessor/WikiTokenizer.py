# -*- coding: utf-8 -*-
import re
from pyparsing import Literal,Word,ZeroOrMore,Forward,nums,SkipTo,oneOf,Group,CharsNotIn,htmlComment,QuotedString,OneOrMore,nestedExpr,delimitedList,Optional

class WikiTemplate:
    def __init__(self,name,fields):
        self.name = name
        self.fields = []
        for m in fields:
            self.fields.append({
                "name":m[0].strip().lower(),
                "value":m[2]
                })
            
    def getTemplateName(self):
        return self.name 
    
    def getPropertiesName(self,text):
        res = []
        for m in self.fields:
            res.append(m["name"])
        return res  
    def __str__(self):
        res = self.name+": ["
        res_list = []
        for m in self.fields:
            res_list.append(m["name"]+": "+str(m["value"]))
        res += ", ".join(res_list)+"]"    
        return  res
    def __repr__(self):
        return "WikiTemplate("+self.__str__()+")"
        
class WikiTokenizer:
    def genTemplate(self,s,l,t):
        lst = list(t)
        return WikiTemplate(lst[0][0],lst[0][2:])
                
    def initGrammar(self):
        L_Equals = Word("=")
        N_comment = htmlComment()
        
        N_name = CharsNotIn("{}|[]")
        
        N_elements = Forward()
        N_ref = nestedExpr( opener="<ref>", closer="</ref>", content=N_elements).setParseAction( lambda s,l,t: {'REF' : t} ) 
        N_apostrofs = QuotedString("'''").setParseAction( lambda s,l,t: {'APOSTROFS' : t} ) 
        N_link = nestedExpr( opener="[[", closer="]]", content= N_name + Optional("|" + delimitedList(CharsNotIn("[]"),delim="|"))).setParseAction( lambda s,l,t: {'LINK' : t} ) 
        N_header = Group(L_Equals + SkipTo("=") + L_Equals).setParseAction( lambda s,l,t: {'HEADER' : t} ) 
        N_template = Forward()
        N_key = CharsNotIn("{}|=")
        #N_value = ZeroOrMore(CharsNotIn("{}|")) + ZeroOrMore(N_template + ZeroOrMore(CharsNotIn("{}|"))).setResultsName('VALUE')
        N_keyValues = "|" + delimitedList(Group(N_key + "=" + N_elements),delim="|")
        N_template << nestedExpr( opener="{{", closer="}}", content = N_name + Optional(N_keyValues)).setParseAction( self.genTemplate ) 
        N_element = N_comment | N_ref | N_apostrofs | N_link | N_header | N_template | N_name  
        N_elements << ZeroOrMore(N_element)
        
        self.N_S = N_elements
    
    def __init__(self):
         
        self.initGrammar()
        self.headers = re.compile('==+ ([^=]*) ==+ \n', re.VERBOSE)
        self.template = re.compile('\{\{([^\{\}]*)\}\}', re.VERBOSE)
        self.template2 = re.compile('\{\|([^\{\}]*)\|\}', re.VERBOSE)
        self.longLinks = re.compile('\[\[([^\[\]\|]*)\|([^\[\]\|]*)\]\]', re.VERBOSE)
        self.shortLinks = re.compile('\[\[([^\[\]\|]*)\]\]', re.VERBOSE)
        self.refLinks = re.compile('<ref>([^<]*)</ref>', re.VERBOSE)
        self.fileLinks = re.compile('\[\[([^\[\]\|]*)\|([^\[\]\|]*)(\|([^\[\]\|]*))+\]\]', re.VERBOSE)
        self.comments = re.compile('(<!--(.+)-->)', re.VERBOSE)
        self.apostrofs = re.compile("'''(.+)'''", re.VERBOSE)
        
        self.lettersDictionary = {
                'о́':'о',
                'а́':'а',
                'е́':'е',
                'и́':'и'
            }
    
    def parse(self,text):
        match = self.N_S.parseString(text);
        return match    
            
    def applyPattern(self,pattern,replacement,text):
        res = text
        length = len(res)
        res = pattern.sub(replacement,res)
        while (len(res)!=length):
            length = len(res) 
            res = pattern.sub(replacement,res)
        return res
        
    def clean(self, text):
        res = text
        res = self.applyPattern(self.template,'',res)
        res = self.applyPattern(self.template2,'',res)
        res = self.applyPattern(self.refLinks,'',res)
        res = self.applyPattern(self.shortLinks,'\g<1>',res)
        res = self.applyPattern(self.fileLinks,'',res)
        res = self.applyPattern(self.longLinks,'\g<2>',res)
        res = self.applyPattern(self.headers,'\g<1> \n',res)
        res = self.applyPattern(self.comments,'',res)
        res = self.applyPattern(self.apostrofs,'\g<1>',res)
        for letter in self.lettersDictionary:
            res = res.replace(letter,self.lettersDictionary[letter])
        return res


        
#tokenizer = WikiTokenizer()
#print (tokenizer.parse("<!--Комментарий --> Привет"))
#print (tokenizer.parse("<!--Комментарий --> Привет [[Полезные ископаемые]] — [[торф]], [[минерал|минеральные материалы]], [[природный газ]], [[нефть]], строительные материалы."))
#print (tokenizer.parse("{{Государство |\r\nРусское название=Литовская Республика }}"))
#print(tokenizer.parse('==== Центристы и самолеты ==== \n* [[Партия труда (Литва)|Партия труда]] — либеральная,'))
#data = tokenizer.parse("{{Государство |\r\nРусское название=Литовская Республика |\r\nОригинальное название=Lietuvos Respublika|Часовой пояс= [[Восточноевропейское время|EET]] ([[UTC+02:00|UTC+2]], [[Летнее время|летом]] [[Восточноевропейское летнее время|UTC+3]])}}")
#print(data)


#print(tokenizer.clean('Хоккейная команда Балтика Вильнюс выступает в МХЛ-Б (см. Первенство МХЛ в сезоне 2012/2013<ref>[http://sportas.delfi.lt/wbc2010/aistruoliai-audringai-svente-rinktines-pergale-pries-argentina.d?id=36357497 Литва на ЧМ-2010]</ref>).'))
#print(tokenizer.clean('==== Центристы ==== \n* [[Партия труда (Литва)|Партия труда]] — либеральная,'))
#print(tokenizer.clean('== Географические данные ==\n{{нет источников в разделе|дата=2013-05-02}}\n[[Файл:Litauen RUS.png|frame|Карта Литвы]]  Правовая система\n \n[[Файл:Gedimino 30 a.JPG|thumb|Министерство юстиции Литвы]]\n[[Файл:Lietuvos Auksciausiasis Teismas.JPG|thumb|right|Верховный суд Литвы]]\n[[Файл:Lithuanian Constitutional Court.jpg|thumb|Конституционный суд Литвы]]'))
#print(tokenizer.clean('[[Полезные ископаемые]] — [[торф]], [[минерал|минеральные материалы]], [[природный газ]], [[нефть]], строительные материалы.'))
#print(tokenizer.clean(' [[Файл:Gedimino 30 a.JPG|thumb|Министерство юстиции Литвы]] '))            
#print(tokenizer.clean('[[Файл:Lietuvos Auksciausiasis Teismas.JPG|thumb|right|[[Верховный суд Литвы]]]]     '))      
#print(tokenizer.clean("== История == \n {{нет источников в разделе|дата=2013-05-02}} \n{{main|История Литвы}}\nНазвание «Литва»"))
#print(tokenizer.clean("{{Государство |\r\nРусское название=Литовская Республика |\r\nОригинальное название=Lietuvos Respublika|Часовой пояс= [[Восточноевропейское время|EET]] ([[UTC+02:00|UTC+2]], [[Летнее время|летом]] [[Восточноевропейское летнее время|UTC+3]])}}"))
#print(tokenizer.clean("<!--Комментарий --> Привет"))
#print(tokenizer.clean("Социоло́гия "))
#print(
#    tokenizer.clean(
#        u"{{Государство\r\n |Русское название=Литовская Республика\r\n |Оригинальное название=Lietuvos Respublika\r\n |Родительный падеж=Литвы\r\n |Герб=Coat of Arms of Lithuania.svg\r\n\r\n |Название гимна=Tautiška giesmė\r\n |Аудио=Tautiška_giesme_instumental.ogg\r\n |Дата независимости= 16 февраля 1918 года<br />11 марта 1990 года (от СССР)\r\n |lat_dir =N |lat_deg = 55|lat_min =20 |lat_sec = 0\r\n  |lon_dir =E |lon_deg =24 |lon_min =6 |lon_sec = 0\r\n  |region                 = LT\r\n  |CoordScale             =1800000\r\n |На карте=EU-Lithuania.svg\r\n  |подпись к карте = Расположение '''Литвы''' (зелёный):<br />— в Европе (светло-зелёный и тёмно-серый)<br />— в Европейском союзе (светло-зелёный)\r\n |Язык= Литовский язык\r\n |Столица=Вильнюс\r\n |Форма правления= Парламентская республика\r\n |Крупнейшие города=Вильнюс, Каунас, Клайпеда, Шяуляй, Паневежис, Алитус\r\n |Курорты=Паланга, Друскининкай, Неринга, Бирштонас, Тракай\r\n |Должности руководителей=Президент<br />Премьер-министр\r\n |Руководители=Даля Грибаускайте<br />Альгирдас Буткявичюс\r\n |Место по территории=123\r\n |Территория=65 301\r\n |Процент воды=-\r\n |Этнохороним             = литовцы, литовец, литовка\r\n  |Место по населению     = 137\r\n  |Население              =  2 944 459\r\n  |Год оценки             = 2014\r\n  |Население по переписи  = 3 054 000<ref name=\"прессрелиз\">[http://www.stat.gov.lt/uploads/docs/gyv_sk_surasymas.pdf Предварительные итоги переписи в официальном пресс-релизе Департамента статистики.]</ref>\r\n  |Год переписи           = 2011\r\n  |Плотность населения    = 49\r\n  |Место по плотности     = \r\n |ВВП (ППС)               = 61,342 млрд.<ref name=\"IMF\">[http://www.imf.org/external/pubs/ft/weo/2011/02/weodata/weorept.aspx?sy=2011&ey=2011&scsm=1&ssd=1&sort=country&ds=.&br=1&c=946&s=NGDPD%2CNGDPDPC%2CPPPGDP%2CPPPPC&grp=0&a=&pr.x=41&pr.y=11 Report for Selected Countries and Subjects]</ref>\r\n |Год расчёта ВВП (ППС)   = 2011\r\n |Место по ВВП (ППС)      = 86\r\n |ВВП (ППС) на душу населения = 22,566<ref name=\"IMF\" />\r\n |ВВП (номинал)=43,171 млрд.<ref name=\"IMF\" />\r\n |Год расчёта ВВП (номинал) =2011\r\n |Место по ВВП (номинал) =82\r\n |ВВП (номинал) на душу населения=13 190<ref name=\"IMF\"/>\r\n |ИРЧП =  0,834<ref name=\"HDI\"></ref>\r\n |Год расчёта ИРЧП        = 2013\r\n |Место по ИРЧП           = 35\r\n |Уровень ИРЧП            = <span style=\"color:#090;\">очень высокий</span>\r\n |Валюта=Литовский лит (LTL) (Код 440)\r\n |Телефонный код=370\r\n |Домен=.lt, .eu\r\n |ISO = LTU\r\n |МОК = LTU \r\n |Часовой пояс= EET (UTC+2, летом UTC+3)\r\n}}"
#        )
#      )
#print(tokenizer.clean("'''Литва́''' (), официальное название — '''Лито́вская Респу́блика'''"))

#directory = "C:\\WORK\\science\\onpositive_data\\python\\"
#wikiIndex = WikiIndex.WikiIndex(directory)
#print(wikiIndex.getTextArticleById(7))
#print("------------------------------------------------------------")
#print(tokenizer.clean(wikiIndex.getTextArticleById(7)))


