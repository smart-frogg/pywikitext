# -*- coding: utf-8 -*-
import pymysql
dbConnection = pymysql.connect(host='localhost', port=3306, user='root', passwd='',charset='utf8', db='wikiparse')
dbCursor = dbConnection.cursor()         
dbCursor.execute("delete from headers where 1=1")

import numpy as np
def change(arr):
    arr[2]=3
myArr = np.zeros((10),dtype=np.int8)
change(myArr)
print(myArr)
change(myArr[2:7])
print(myArr)