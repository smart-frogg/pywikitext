# -*- coding: utf-8 -*-
import re

import WikiIndex


class WikiTokenizer:
    def __init__(self):
        self.headers = re.compile('==+ ([^=]*) ==+ \n', re.VERBOSE)
        self.template = re.compile('\{\{([^\{\}]*)\}\}', re.VERBOSE)
        self.template2 = re.compile('\{\|([^\{\}]*)\|\}', re.VERBOSE)
        self.longLinks = re.compile('\[\[([^\[\]]*)\|([^\[\]]*)\]\]', re.VERBOSE)
        self.shortLinks = re.compile('\[\[([^\[\]]*)\]\]', re.VERBOSE)
        self.refLinks = re.compile('<ref>([^<]*)</ref>', re.VERBOSE)
        self.fileLinks = re.compile('\[\[([^\[\]]*)\|([^\[\]]*)(\|([^\[\]]*))+\]\]', re.VERBOSE)
        self.comments = re.compile('<!--(.+)-->', re.VERBOSE)
    def clean(self, text):
        res = text
        res = self.refLinks.sub('',res)
        res = self.longLinks.sub('\g<2>',res)
        res = self.fileLinks.sub('',res)
        res = self.shortLinks.sub('\g<1>',res)
        res = self.headers.sub('\g<1> \n',res)
        res = self.template.sub('',res)
        res = self.template2.sub('',res)
        res = self.comments.sub('',res)
        return res
        
tokenizer = WikiTokenizer()
#print(tokenizer.clean('Хоккейная команда Балтика Вильнюс выступает в МХЛ-Б (см. Первенство МХЛ в сезоне 2012/2013<ref>[http://sportas.delfi.lt/wbc2010/aistruoliai-audringai-svente-rinktines-pergale-pries-argentina.d?id=36357497 Литва на ЧМ-2010]</ref>).'))
#print(tokenizer.clean('==== Центристы ==== \n* [[Партия труда (Литва)|Партия труда]] — либеральная,'))
#print(tokenizer.clean('== Географические данные ==\n{{нет источников в разделе|дата=2013-05-02}}\n[[Файл:Litauen RUS.png|frame|Карта Литвы]]  Правовая система\n \n[[Файл:Gedimino 30 a.JPG|thumb|Министерство юстиции Литвы]]\n[[Файл:Lietuvos Auksciausiasis Teismas.JPG|thumb|right|Верховный суд Литвы]]\n[[Файл:Lithuanian Constitutional Court.jpg|thumb|Конституционный суд Литвы]]'))
#print(tokenizer.clean('[[Полезные ископаемые]] — [[торф]], [[минерал|минеральные материалы]], [[природный газ]], [[нефть]], строительные материалы.'))
                      
#print(tokenizer.clean("== История == \n {{нет источников в разделе|дата=2013-05-02}} \n{{main|История Литвы}}\nНазвание «Литва»"))
directory = "C:\\WORK\\science\\onpositive_data\\python\\"
wikiIndex = WikiIndex.WikiIndex(directory)
print(tokenizer.clean(wikiIndex.getTextArticleById(7)))
