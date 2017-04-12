# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod

class WikiStore(metaclass=ABCMeta):
    @abstractmethod
    def save(self):
        pass
    @abstractmethod
    def load(self):
        pass
    