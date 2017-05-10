# -*- coding: utf-8 -*-
import pymorphy2
from functools import lru_cache

class CachedPymorphyMorph:
    def __init__(self):
        self.morph = pymorphy2.MorphAnalyzer()
        #self.cache = {}
    @lru_cache(maxsize=1024)    
    def parse(self,text):
        #if not self.cache.get(text, None):
        #    self.cache[text] = self.morph.parse(text)
        return self.morph.parse(text) #self.cache.get(text)
