# -*- coding: utf-8 -*-

######################################
# 1.正则待改良 [Q1]
# 2.re 的最大匹配 [Q2]
######################################
import json
import re
import url_process as up
import numpy as np

#file_Name = "1.txt"
#file_Name = "0718_2221.txt"
#PATH = "TaoBaoData/"+ file_Name
#dumpPATH = "TREE/"+ file_Name

#正则有待改良
#from : http://blog.csdn.net/weasleyqi/article/details/7912647
#onLine_re = r'((http|ftp|https)://)(([a-zA-Z0-9\._-]+\.[a-zA-Z]{2,6})|([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}))(:[0-9]{1,4})*(/[a-zA-Z0-9\&%_\./-~-]*)?'


def readJason( path ):
    x = open(path)
#    x = x.read()
#    return json.loads(x[1:])
    tmp = json.load(x)
    x.close()
    return tmp
    
def get_Tree(PATH, dumpPATH, stop):
    '''
    input:
        PATH: .har file path. The .har file record the traffic
        dumpPATH: A .txt file. This file record a matrix whose fomat is 
            "treeplotVec; url; timestamp"
        stop: A Stop_url(stopURL.py) object.
        
    output:
        a Tree object
    '''
    onLine_re = r'((http|ftp|https)://)(([a-zA-Z0-9\._-]+\.[a-zA-Z]{2,6})|([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}))(:[0-9]{1,4})*(/[a-zA-Z0-9\&%_\./-~-]*)?'
    
    data = readJason(PATH)
    treeRelation = []
    treeContent = []
    indexList = [] #record the index of 'entries' from whose content can find the url
    for i in range(0,len(data['log']['entries'])):
        currentItem = data['log']['entries'][i]
        ori_requestURL = currentItem['request']['url']
        requestURL = up.drop_variation( ori_requestURL );
        if stop.is_stopURL(ori_requestURL):
            print "StopURL:",ori_requestURL
            continue
#        timestamp = up.get_fiddle_timestamp(currentItem['startedDateTime'])
        
        #process this request-response pair
        #process request part
        if requestURL in treeContent: #if the requested content has pushed in the tree
            root = treeContent.index(requestURL) + 1
        else:
            treeRelation.append(0)
            treeContent.append(requestURL)
            indexList.append(-i)
            root = len(treeContent)
            
        #process response part
        if data['log']['entries'][i]['response']['content'].has_key('text'):
            string = data['log']['entries'][i]['response']['content']['text']
            subPatt = re.findall(onLine_re, string)
            for item in subPatt:
                treeRelation.append( root )
#                treeContent.append( str(item[0]) + ''.join(item[2:]) )
                treeContent.append( up.drop_variation(item[0] + item[2] + item[6]) ) #[Q2]
                indexList.append(i)
        else:
            print i
            print currentItem['response']['content']['mimeType']
            
    #to get the timestamp
    treeTimestamp = [(u'',0,u'') for i in range(0,len(treeRelation)) ]
    for i in range(0,len(data['log']['entries'])):
        currentItem = data['log']['entries'][i]
        ori_requestURL = currentItem['request']['url']
        requestURL = up.drop_variation( ori_requestURL );
        timestamp = up.get_fiddle_timestamp(currentItem['startedDateTime'])
        if requestURL in treeContent: #if the requested content has pushed in the tree
            treeTimestamp[treeContent.index(requestURL)] = timestamp
            
    f_dump = open(dumpPATH,'w')
#    first_text = up.get_fiddle_timestamp(data['log']['entries'][0]['startedDateTime'])
#    print first_text[1]
#    input('timestamp aaaaaaaaaaaaaaaaaaaaa!')
    for j in range(0,len(treeRelation)):
#        if treeTimestamp[j][1] != 0:
#            tmp = treeTimestamp[j][1]- first_text[1]
#        else:
#            tmp = 0
#        f_dump.write( str(treeRelation[j])+ ","+ treeContent[j]+","+str(tmp)+ "\n" )
        f_dump.write( str(treeRelation[j])+ ","+ treeContent[j]+","+str(treeTimestamp[j][1])+ "\n" )
    f_dump.close()
    return Tree(treeRelation, treeContent, treeTimestamp, PATH, indexList)
    
##
#treeRelation, treeContent, treeTimestamp, indexList = getTree(PATH, dumpPATH)
#ob = getTree(PATH, dumpPATH)
##

class Tree:
    def __init__(self, treeRelation, treeContent, treeTimestamp, filename, indexList):
        '''
        "treeRelation" is a vector that presents the tree's shape,
        and is the main line that we use to manage a tree. Other attributes
        corresponding to the order that "treeRelation" decide.
        '''
        self.treeRelation = treeRelation
        self.treeContent = treeContent
        self.treeTimestamp = treeTimestamp
        self.urlSet = set(treeContent)
        self.filename = filename
        self.indexList = indexList #record the index of 'entries' from whose content can find the url
        self.SURROUND = 10
        self.SIMILAR_THRESHOLD = 0.75
        
    def has_node( self, url):
        '''Judge if the tree has a node correspond to the url'''
        if url in self.urlSet:
            return True
        else:
            return False
            
    def has_similar(self, url):
        '''
        '''
        if self.has_node( url):
            return (True,[], self.search_url_index(url))
        else:
            max_rate = 0
            url_split_list = up.url_split( url)
            max_list =[]
            for my_url in self.treeContent:
                my_url_list = up.url_split(my_url)
                rate, dismatch_list = up.url_list_compare(url_split_list, my_url_list)
#                print rate,"  ",
                if max_rate < rate:
                    max_rate = rate
                    max_list = dismatch_list
                if rate > self.SIMILAR_THRESHOLD:
                    print "SIMILAR URL:\n",my_url,"\n",url
                    return (True, dismatch_list, self.search_url_index(my_url))
            return (False, max_list, -1)
            
    def get_surround_text(self, index):
        '''
        input: node's index in the "treeRelation" list
        get surround text.Return self.SURROUND chars for front and back respectively.
        And return "position" in addition.
        "position" == 0 means the url is a root.
        "position" == -1 means the url is not found.
        Otherwise, "position" is the position in response body text
        '''
        data = readJason(self.filename)
        item_position = self.indexList[index]
        if item_position< 0:
            # the url is a request
            return ("", "", 0)
        currentItem = data['log']['entries'][item_position]
        if currentItem['response']['content'].has_key('text'):
            text = currentItem['response']['content']['text']
            position = text.find(self.treeContent[index])
            url_len = len(self.treeContent[index])
            if position+1>= self.SURROUND and (len(text)-position-1)>= self.SURROUND:
                front = text[position-self.SURROUND: position]
                back = text[position+ url_len: position+ url_len+ self.SURROUND]
            else:
                min_num = min([position+1, len(text)-position-1])
                front = text[position- min_num: position]
                back = text[position+ url_len: position+ url_len+ min_num]
        else:
            front = ""
            back = ""
            position = -1
        
        return (front, back, position)
        
    def get_root_index(self, node_ind):
        '''
        input: node's index in the "treeRelation" list
        output: the root(coresponding to the input node) index in the "treeRelation" list.
        
        output -2 if input is illigal
        '''
        root_ind = -2
        if node_ind <0 or node_ind >len(self.treeRelation):
            print "Tree.get_root_index ERROR: bad input, illigal node_ind, node_ind beyond list domain"
            return root_ind
        root_ind = node_ind
        while(self.treeRelation[root_ind]!= 0):
            root_ind = self.treeRelation[root_ind] -1
        return root_ind
        
    def get_parent_index(self, node_ind):
        '''
        input: node's index in the "treeRelation" list
        output: the parent node (coresponding to the input node) index in the "treeRelation" list.
        
        output -2 if input is illigal
        '''
        if node_ind <0 or node_ind >len(self.treeRelation):
            print "Tree.get_parent_index ERROR: bad input, illigal node_ind, node_ind beyond list domain"
            return -2
        else:
            if self.treeRelation[node_ind] !=0:
                return self.treeRelation[node_ind] -1
            else:
                return node_ind
                
    def get_children_indexList(self, node_ind):
        '''
        input: node's index in the "treeRelation" list
        output: children index list
        '''
        if node_ind <0 or node_ind >len(self.treeRelation):
            print "Tree.get_children_indexList ERROR: bad input, illigal node_ind, node_ind beyond list domain"
            return []
        tmp = np.where( np.array(self.treeRelation)== node_ind+1)
        return list(tmp[0])
        
    def search_url_index(self, url):
        '''
        output: node's index in the "treeRelation" list
        '''
        return self.treeContent.index(url)