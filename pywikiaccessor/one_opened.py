# -*- coding: utf-8 -*-
from abc import ABCMeta
class OneOpened(ABCMeta):
    _instances = {}
    def __call__(self, *args, **kwargs):
        cls = self.__name__
        directory = args[0].directory
        if not OneOpened._instances.get(directory,None):
            OneOpened._instances[directory] = {}
        if not OneOpened._instances[directory].get(cls,None):    
            OneOpened._instances[directory][cls] = super(OneOpened, self).__call__(*args, **kwargs)
        return OneOpened._instances[directory][cls]