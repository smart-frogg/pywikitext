# -*- coding: utf-8 -*-
import codecs

class WikiSqlLoader:
    def parse(self,file, consumer):
        with codecs.open(file,'r',encoding='utf-8', errors='ignore') as f:
            for line in f:
                if line.startswith("INSERT INTO"):
                    line = line[line.find('('):]
                    subPars = []
                    pos=0
                    while True:
                        indexOf = line.find("),(",pos)
                        if indexOf == -1:
                            subPars.append(line[pos:])
                            break
                        subPars.append(line[pos:indexOf])
                        pos = indexOf+3                        
                    for s in subPars:
                        self.consume(s, consumer)

    def consume(self, s, consumer) :
        sm = []
        if s[0] == '(':
            s = s[1:];
        quote = None
        pc = None
        res = ''
        for c in s:
            if c == '\'':
                if quote == '\'':
                    if pc != '\\':
                        quote = None
                elif quote == None:
                        quote = c
            if c == '\"':
                if quote == '\"':
                    if pc != '\\':
                        quote = None
                elif quote == None:
                        quote = c
            if c == ',' and quote == None:
                sm.append(res)
                res=''
                continue
            res += c
            if pc != '\\':
                pc = c
            else:
                pc = 0
        sm.append(res)
        rs = []
        
        for sq in sm:
            if sq.endswith(");"):
                sq = sq[:len(sq) - 2]
            if len(sq)>0 and sq[0].isdigit():
                rs.append(int(sq))
                continue
            if sq[0] == '\'' or sq[0] == '"':
                rs.append(sq[1: len(sq) - 1])
                continue
            rs.append(sq)
        consumer.consume(rs)
