# -*- coding: utf-8 -*-
TYPE_TOKEN = 1
TYPE_SIGN = 2
TYPE_WORD = 3
class Token:

    def __init__(self, token, spaceLeft, spaceRight, tokenType, tokenNum):
        self.token = token
        self.spaceLeft = spaceLeft
        self.spaceRight = spaceRight 
        self.tokenType = tokenType
        self.tokenNum = tokenNum
    def __str__(self):
        return str(self.tokenType) + ' ' + self.token    