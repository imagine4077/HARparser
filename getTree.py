# -*- coding: utf-8 -*-

######################################
# 1.正则待改良 [Q1]
# 2.re 的最大匹配 [Q2]
######################################

import re
import url_process as up
import numpy as np

#正则有待改良
#from : http://blog.csdn.net/weasleyqi/article/details/7912647
#onLine_re = r'((http|ftp|https)://)(([a-zA-Z0-9\._-]+\.[a-zA-Z]{2,6})|([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}))(:[0-9]{1,4})*(/[a-zA-Z0-9\&%_\./-~-]*)?'

def judge_if_existing( content_arr, flag_arr, value):
    '''
        help to find the first node that required the current URL 
        in Function get_Tree
    '''
    if len(content_arr) != len(flag_arr):
        print len(content_arr) ,'!=', len(flag_arr)
        input('ERROR in FUNCTION get_firstNode_location( content_arr, flag_arr, value)\n')
    if not(value in content_arr): #if no corresponding URL
        return (False, 0)
    index = -1
    #if has corresponding URL
    while index< len(content_arr):
        if value in content_arr[index+1:]:
            index = content_arr.index(value, index+1)
            if flag_arr[index]< 0:
                return (True, index)
            else:
                continue
        else: #if has corresponding URL but all got.That's mean this page is the root of a new tree
            return (False, 0)

    
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
    
    data = up.readJason(PATH)
    
    '''
        currentItem = data['log']['entries'][i]
        
        treeContent -> up.drop_variation( currentItem['request']['url'] )
        original_treeContent -> currentItem['request']['url']
        indexList -> i(or -i if the node is root of a tree)
        wait_interval -> currentItem['timings']['wait'], (ms毫秒)
        mimeType -> currentItem['response']['content']['mimeType']
    '''
    treeRelation = [] #generate a matlab-treeplot()-like vector
    treeContent = [] #record the simplified URL corresponding to "treeRelation"
    original_treeContent = [] #record the original URL corresponding to "treeRelation"
    indexList = [] #record the index of 'entries' from whose content can find the url
    wait_interval = [] #record the request-response interval of corresponding page
    mimeType = [] #record the mimeType of corresponding page
    treeTimestamp = [] #elements here tuples, (date, )
    
    for i in range(0,len(data['log']['entries'])):
        currentItem = data['log']['entries'][i]
        ori_requestURL = currentItem['request']['url']
        requestURL = up.drop_variation( ori_requestURL );
        if stop.is_stopURL(ori_requestURL):
            print "StopURL:",ori_requestURL
            continue
        
        #process this request-response pair
        #process request part
        ifInTree, location = judge_if_existing( treeContent, wait_interval, requestURL)
        if ifInTree: #if the requested content has pushed in the tree
            root = location + 1 # get the root index for the response
            # section below is used to debug
            if wait_interval[location] >= 0:
                print 'PATH 0f file:\t',PATH
                print 'entity index:\t',i
                print 'requested URL:\t',ori_requestURL
                print 'URL of the existing node:\t',treeContent[location]
                print 'node location in array:\t',location
                print 'root of this node:\t',treeRelation[location]
                print 'value of the existing node:\t',wait_interval[location]
                input("EXCEPTION:wait_interval[location] >= 0!!!\n")
            wait_interval[location] = currentItem['timings']['wait']
            mimeType[location] = currentItem['response']['content']['mimeType']
            treeTimestamp[location] = up.get_fiddle_timestamp(currentItem['startedDateTime'])
        else:
            treeRelation.append(0)
            treeContent.append(requestURL)
            original_treeContent.append(ori_requestURL)
            wait_interval.append( currentItem['timings']['wait'] )
            mimeType.append(currentItem['response']['content']['mimeType'])
            treeTimestamp.append(up.get_fiddle_timestamp(currentItem['startedDateTime']))
            indexList.append(-i)
            root = len(treeContent)
            
        #process response part
        if data['log']['entries'][i]['response']['content'].has_key('text'):
            string = data['log']['entries'][i]['response']['content']['text']
            subPatt = re.findall(onLine_re, string)
            for item in subPatt:
                treeRelation.append( root )
                url = item[0] + item[2] + item[6] # don't aky why, I'll tell you "because of love  ╮(￣▽￣)╭"
                url = url.rstrip('\\')
                treeContent.append( up.drop_variation(url) ) #[Q2]
                original_treeContent.append( url )
                wait_interval.append(-1)
                indexList.append(i)
                mimeType.append(u'')
                treeTimestamp.append((u'',-1,u''))
        else:
            print i
            print currentItem['response']['content']['mimeType']
            
    #to get the timestamp
#    treeTimestamp = [(u'',0,u'') for i in range(0,len(treeRelation)) ]
#    for i in range(0,len(data['log']['entries'])):
#        currentItem = data['log']['entries'][i]
#        ori_requestURL = currentItem['request']['url']
#        requestURL = up.drop_variation( ori_requestURL );
#        timestamp = up.get_fiddle_timestamp(currentItem['startedDateTime'])
#        if requestURL in treeContent: #if the requested content has pushed in the tree
#            treeTimestamp[treeContent.index(requestURL)] = timestamp
            
#    f_dump = open(dumpPATH,'w')
#    for j in range(0,len(treeRelation)):
#        f_dump.write( str(j+1)+" : "+str(treeRelation[j])+ ", "+ str(wait_interval[j])+ ", "+ treeContent[j]+", " \
#        +str(mimeType[j])+ ", "+str(treeTimestamp[j])+ "\n" )
#    f_dump.close()
    
    tree_info_mat = {}
    tree_info_mat['treeRelation'] = treeRelation
    tree_info_mat['treeContent'] = treeContent
    tree_info_mat['indexList'] = indexList
    tree_info_mat['original_treeContent'] = original_treeContent
    tree_info_mat['wait_interval'] = wait_interval
    tree_info_mat['mimeType'] = mimeType
    tree_info_mat['filename'] = PATH
    tree_info_mat['treeTimestamp'] = treeTimestamp 
    tree_info_mat['dumpPath'] = dumpPATH

    return Tree(tree_info_mat)


class Tree:
#    def __init__(self, treeRelation, treeContent, treeTimestamp, filename, indexList, original_treeContent):
    def __init__(self, tree_info_matrix):
        '''
        "treeRelation" is a vector that presents the tree's shape,
        and is the main line that we use to manage a tree. Other attributes
        corresponding to the order that "treeRelation" decide.
        '''
        self.treeRelation = tree_info_matrix['treeRelation']
        self.treeContent = tree_info_matrix['treeContent']
        self.treeTimestamp = tree_info_matrix['treeTimestamp']
        self.filename = tree_info_matrix['filename']
        self.indexList = tree_info_matrix['indexList'] #record the index of 'entries' from whose content can find the url
        self.original_treeContent = tree_info_matrix['original_treeContent']
        self.mimeType = tree_info_matrix['mimeType']
        self.wait_interval = tree_info_matrix['wait_interval']
        self.dumpPath = tree_info_matrix['dumpPath']
        self.SURROUND = 10 # for context comparing
        self.SIMILAR_THRESHOLD = 0.75 # accuracy rate for URL similarity judgement
        self.dump_tree_content()
        
    def has_node( self, url):
        '''Judge if the tree has a node correspond to the url'''
        return ((url in self.treeContent) or (url in self.original_treeContent))
            
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
        data = up.readJason(self.filename)
        item_position = self.indexList[index]
        if item_position< 0:
            # the url is a request
            return ("", "", 0)
        currentItem = data['log']['entries'][item_position]
        if currentItem['response']['content'].has_key('text'):
            text = currentItem['response']['content']['text']
            position = text.find(self.original_treeContent[index])
            url_len = len(self.original_treeContent[index])
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
        if url in self.treeContent:
            ind = self.treeContent.index(url)
        else:
            ind = self.original_treeContent.index(url)
        return ind
        
    def dump_tree_content(self):
        f_dump = open(self.dumpPath,'w')
        for j in range(0,len(self.treeRelation)):
            f_dump.write( str(j+1)+" : "+str(self.treeRelation[j])+ ", "+ str(self.wait_interval[j])+ ", "+ self.treeContent[j]+", " \
            +str(self.mimeType[j])+ ", "+str(self.treeTimestamp[j])+ "\n" )
        f_dump.close()
        return