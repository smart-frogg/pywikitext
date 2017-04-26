# -*- coding: utf-8 -*-
from pyparsing import Literal,Word,ZeroOrMore,Forward,ParseException,nums,makeHTMLTags,StringEnd,SkipTo,oneOf,Group,CharsNotIn,htmlComment,QuotedString,OneOrMore,nestedExpr,delimitedList,Optional

class WikiComment:
    def __init__(self,text):
        self.text = text
    def __str__(self):
        return self.text    
    def __repr__(self):
        return "WikiComment("+self.__str__()+")"
class WikiHeader:
    def __init__(self,text):
        self.text = text
    def __str__(self):
        return self.text    
    def __repr__(self):
        return "WikiHeader("+self.__str__()+")"    
class WikiLink:
    def __init__(self,name,fields):
        self.name = name
        self.fields = []
        for m in fields:
            if(m != '|'):
                self.fields.append(m)    
    def __str__(self):
        res = self.name+": ["
        res_list = []
        for m in self.fields:
            res_list.append(m)
        res += ", ".join(res_list)+"]"    
        return  res
    def __repr__(self):
        return "WikiLink("+self.__str__()+")"
    
class WikiTemplate:
    def __init__(self,name,fields):
        self.name = name
        self.fields = []
        for m in fields:
            if len(m) >= 3:
                if len(m) == 3:
                    value = m[2]
                else:
                    value = m[2:]     
                    
                self.fields.append({
                    "name":m[0].strip().lower(),
                    "value":value
                    })
            else:
                if len(m) == 2:
                    self.fields.append({
                        "name":m[0]
                        })
                else:
                    self.fields.append({
                        "value":m[0]
                        })
        
    def getTemplateName(self):
        return self.name 
    
    def getPropertiesNames(self):
        res = []
        for m in self.fields:
            if m.get("name",None) :
                res.append(m["name"])
        return res  
    def __str__(self):
        res = self.name+": ["
        res_list = []
        for m in self.fields:
            res_list.append(m.get("name","None")+": "+str(m.get("value","None")))
        res += ", ".join(res_list)+"]"    
        return  res
    def __repr__(self):
        return "WikiTemplate("+self.__str__()+")"
class WikiParser:
    def genTemplate(self,s,l,t):
        lst = list(t)
        return WikiTemplate(lst[0][0],lst[0][2:])
    def genLink(self,s,l,t):
        lst = list(t)
        return WikiLink(lst[0][0],lst[0][1:])
    def genComment(self,s,l,t):
        lst = list(t)
        return WikiComment(lst[0])
    def genHeader(self,s,l,t):
        lst = list(t)
        return WikiHeader(lst[0])
    def genRef(self,s,l,t):
        return None            
    def initGrammar(self):
        N_comment = htmlComment().setParseAction( self.genComment )
        
        N_name = CharsNotIn("{}|[]")
        N_link = nestedExpr( opener="[[", closer="]]", content= N_name + Optional("|" + delimitedList(CharsNotIn("[]"),delim="|"))).setParseAction( self.genLink ).setDebug(True )
        L_Equals = Word("=")
        N_header = Group(L_Equals + SkipTo("=") + L_Equals).setParseAction( self.genHeader )
        
        N_element = Forward()
        
        N_template = Forward().setDebug(True )
        N_key = CharsNotIn("{}|=")
        N_internalText = CharsNotIn("{}|=<[") + SkipTo(Literal("{{")|Literal("[[")|Literal("<!--")|Literal("<ref")|Literal("|")|Literal("}}"))#CharsNotIn("{}|[]<")
        N_insideElements = OneOrMore(N_element | N_internalText).setDebug(True )
        N_keyValue = Group(Optional(N_key) + Optional(Literal("=") + N_insideElements)).setDebug(True )
        N_keyValues = "|" + delimitedList(N_keyValue,delim="|")
        N_keyValues.setDebug(True )
        #N_label_content = N_template | ("{{"+OneOrMore("!")+"}}") | CharsNotIn("{}|") 
        #N_label = nestedExpr( opener="{", closer="}", content = N_label_content)
        N_template << nestedExpr( opener="{{", closer="}}", content = N_name + Optional(N_keyValues)).setParseAction( self.genTemplate )
        
        #ref_start, ref_end = makeHTMLTags("ref")
        #N_named_ref = ref_start + SkipTo(ref_end) + ref_end
        #N_named_ref.setParseAction( lambda s,l,t: {'REF' : t} ) 

        N_element = N_comment | N_link | N_header | N_template 
        N_element.setDebug(True )
        
        self.N_S = N_element
    
    def __init__(self):
        self.initGrammar() 
    
    def parse(self,text):
        match = self.N_S.scanString(text);
        return match     
    
     