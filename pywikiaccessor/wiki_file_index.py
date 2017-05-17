# -*- coding: utf-8 -*-
from abc import abstractmethod
import os
import pickle
from pywikiaccessor.one_opened import OneOpened

class WikiFileIndex(metaclass= OneOpened):
    def __init__(self, wikiAccessor, prefix=''):
        self.accessor = wikiAccessor
        self.prefix = prefix
        self.directory = wikiAccessor.directory
        self.dictionaries = {}
        self.loadOrBuild()
        
    def loadOrBuild(self):
        consistent = True
        for file in self.getDictionaryFiles():
            consistent = consistent and os.path.exists(self.getFullFileName(file)+".pcl")
        for file in self.getOtherFiles():
            consistent = consistent and os.path.exists(self.getFullFileName(file))
        if not consistent:   
            builder = self.getBuilder()
            builder.build()    
        for file in self.getDictionaryFiles():
            with open(self.getFullFileName(file)+".pcl", 'rb') as f:
                self.dictionaries[file] = pickle.load(f)
                f.close()
        self.loadOtherFiles()        
                       
    def getDictionaryFiles(self):    
        return []
    
    def getOtherFiles(self):    
        return []
    
    def loadOtherFiles(self):    
        pass

    def clear(self):
        for file in self.getDictionaryFiles():
            os.remove(self.directory + file + ".pcl")
        for file in self.getOtherFiles():
            os.remove(self.directory + file)
    def getFullFileName(self,fileName):
        return self.accessor.directory + self.prefix + fileName 
    
    @abstractmethod
    def getBuilder(self):
        pass
    
    @abstractmethod
    def getName(self):
        pass     