# -*- coding: utf-8 -*-
import pymorphy2
from pprint import pprint
morph = pymorphy2.MorphAnalyzer()
parse_result = morph.parse(u'стали')
pprint (parse_result)