# -*- coding: utf-8 -*-

######################################
# 1.正则待改良 [Q1]
# 2.re 的最大匹配 [Q2]
######################################

import re
import url_process as up
import numpy as np
import copy
from fuzzywuzzy import fuzz
import os

#正则有待改良
#from : http://blog.csdn.net/weasleyqi/article/details/7912647
#onLine_re = r'((http|ftp|https)://)(([a-zA-Z0-9\._-]+\.[a-zA-Z]{2,6})|([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}))(:[0-9]{1,4})*(/[a-zA-Z0-9\&%_\./-~-]*)?'
SIMILAR_THRESHOLD_1 = 0.84
SIMILAR_THRESHOLD = 0.67

def find_similar(url, content_arr):
    if url == "":
        return ( [], [])
    else:
        rate_arr = []
        ind_arr = []
        max_rate = 0
        max_ind = -2
        for ind in range(0,len(content_arr)):
            my_url = content_arr[ ind]
            
            rate = fuzz.ratio(url, my_url)/100.0
            if rate < SIMILAR_THRESHOLD_1: # or rate <=max_rate:
                continue
            else:
#                if fuzz.ratio( os.path.splitext( my_url)[1], os.path.splitext( url)[1])<SIMILAR_THRESHOLD:
#                # if not has the same expend name
#                    continue
                max_rate = rate
                max_ind = ind
                rate_arr.append( rate)
                ind_arr.append( ind)
        return ( rate_arr, ind_arr)

def judge_if_existing( content_arr, flag_arr, value):
    '''
        help to find the first node corresponding to the current request URL.
        Working in Function get_Tree
    '''
    if len(content_arr) != len(flag_arr):
        print len(content_arr) ,'!=', len(flag_arr)
        input('ERROR in FUNCTION get_firstNode_location( content_arr, flag_arr, value)\n')
    rate_arr, ind_arr = find_similar( value, content_arr)
    if len(rate_arr)<= 0:
        return (False, 0)
    while len(rate_arr)>0:
        max_rate = max( rate_arr)
        print max_rate
        po = rate_arr.index( max_rate)
        if flag_arr[ ind_arr[po]]< 0:
            print 'EXIST!!\nEG1:',value,'\nEG2:',content_arr[ ind_arr[po]]
            return (True, ind_arr[po])
        else:
            del rate_arr[ po]
            del ind_arr[ po]
    else:
        return (False, 0)
    
#    if not(value in content_arr): #if no corresponding URL
#        return (False, 0)
#    index = -1
#    #if has corresponding URL
#    while index< len(content_arr):
#        if value in content_arr[index+1:]:
#            index = content_arr.index(value, index+1)
#            if flag_arr[index]< 0:
#                return (True, index)
#            else:
#                continue
#        else: #if has corresponding URL but all got.That's mean this page is the root of a new tree
#            return (False, 0)

    
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
#    onLine_re = r'((http|ftp|https)://)(([a-zA-Z0-9\._-]+\.[a-zA-Z]{2,6})|([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}))(:[0-9]{1,4})*(/[a-zA-Z0-9\&%_\./-~-]*)?'
    
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
    indexList = [] #record the index of 'entries' from whose content can find the url, negative element for root node
    wait_interval = [] #record the request-response interval of corresponding page
    mimeType = [] #record the mimeType of corresponding page
    treeTimestamp = [] #tuple elements here, (date, )
    positionInText = [] #tuple elements here represent the url ( begin, end) position
                #in text. ( -2, -2) for root node
    size = []
    
    for i in range(0,len(data['log']['entries'])):
        currentItem = data['log']['entries'][i]
#        if currentItem['response']['content']['size'] > 102400:
#            print i, 'size:',currentItem['response']['content']['size']
#            input('big size')
        ori_requestURL = currentItem['request']['url']
        requestURL = up.drop_variation( ori_requestURL );
        if stop.is_stopURL(ori_requestURL):
            print "StopURL:",ori_requestURL
            continue
        
        #process this request-response pair
        #process request part
        ifInTree, location = judge_if_existing( treeContent, wait_interval, requestURL)
        if ifInTree: #if the requested content has pushed in the tree
            root = location + 1 # get the root index for urls in response text
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
            size[location] = currentItem['response']['content']['size']
            treeContent[ location] = requestURL
            original_treeContent[ location] = ori_requestURL
        else:
            treeRelation.append(0)
            treeContent.append(requestURL)
            original_treeContent.append(ori_requestURL)
            wait_interval.append( currentItem['timings']['wait'] )
            mimeType.append(currentItem['response']['content']['mimeType'])
            treeTimestamp.append(up.get_fiddle_timestamp(currentItem['startedDateTime']))
            indexList.append(-i)
            positionInText.append((-2,-2))
            size.append(currentItem['response']['content']['size'])
            root = len(treeContent)
            
        #process response part
        if data['log']['entries'][i]['response']['content'].has_key('text'):
            string = data['log']['entries'][i]['response']['content']['text']
            for url, start_pos, end_pos, count in up.get_urlSet_from_text( string):
                treeRelation.append( root )
                treeContent.append( up.drop_variation(url)) #[Q2]
                original_treeContent.append( url)
                wait_interval.append(-1)
                indexList.append(i)
                mimeType.append(u'')
                treeTimestamp.append((u'',-1,u''))
                positionInText.append(( start_pos, end_pos))
                size.append(-2)
#            for item in subPatt:
#                treeRelation.append( root )
#                url = item[0] + item[2] + item[6] # don't aky why, I'll tell you "because of love  ╮(￣▽￣)╭"
#                url = url.rstrip('\\')
#                treeContent.append( up.drop_variation(url) ) #[Q2]
#                original_treeContent.append( url )
#                wait_interval.append(-1)
#                indexList.append(i)
#                mimeType.append(u'')
#                treeTimestamp.append((u'',-1,u''))
        else:
            print i
            print currentItem['response']['content']['mimeType']
    
    tree_info_mat = {}
    tree_info_mat['treeRelation'] = copy.deepcopy( treeRelation)
    tree_info_mat['treeContent'] = copy.deepcopy( treeContent)
    tree_info_mat['indexList'] = copy.deepcopy( indexList)
    tree_info_mat['original_treeContent'] = copy.deepcopy( original_treeContent)
    tree_info_mat['wait_interval'] = copy.deepcopy( wait_interval)
    tree_info_mat['mimeType'] = copy.deepcopy( mimeType)
    tree_info_mat['filename'] = PATH
    tree_info_mat['treeTimestamp'] = copy.deepcopy( treeTimestamp )
    tree_info_mat['dumpPath'] = dumpPATH
    tree_info_mat['positionInText'] = copy.deepcopy( positionInText)
    tree_info_mat['size'] = copy.deepcopy( size)

    return Tree(tree_info_mat)


class Tree:
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
        self.positionInText = tree_info_matrix['positionInText']
        self.size = tree_info_matrix['size']
        self.roots_list = []
        self.SURROUND = 14 # for context comparing
        self.SIMILAR_THRESHOLD = 0.80 # accuracy rate for URL similarity judgement
        self.dump_tree_content()
        self.get_all_root_index()
        
    def has_node( self, url):
        '''Judge if the tree has a node correspond to the url'''
        return ((url in self.treeContent) or (url in self.original_treeContent))
            
    def has_similar(self, url):
        '''
        '''
        if url == "":
            return (False,[], [])
        if self.has_node( url):
            return (True,[], self.search_url_index(url))
        else:
            max_rate = 0
            url_split_list, host_po = up.url_split( url)
            max_list =[]
            max_url = ""
            rate = 0
            for my_url in self.treeContent:
                if fuzz.ratio( os.path.splitext( my_url)[1], os.path.splitext( url)[1])<SIMILAR_THRESHOLD:
                # if not has the same expend name
                    continue
                if (fuzz.ratio(url, my_url)/100.0)< self.SIMILAR_THRESHOLD:
                    continue
                my_url_list, my_host_po = up.url_split(my_url)
                rate, dismatch_list = up.url_list_compare(url_split_list, my_url_list)
                rate = max( fuzz.ratio(url, my_url)/100.0, rate)
                if max_rate < rate:
                    max_rate = rate
                    max_list = dismatch_list
                    max_url = my_url
            if max_rate > self.SIMILAR_THRESHOLD and max_url != "":
                print "SIMILAR URL(Tree.has_similar):\n",max_url,"\n",url
                return (True, dismatch_list, self.search_url_index(max_url))
            return (False, max_list, [])
            
    def find_similar_and_replace(self, url, indSet, context={'front':' ', 'back':' '}):
        if url == "":
            return ""
        else:
            max_rate = 0
            max_ind = -2
            url_split_list, url_host_po = up.url_split( url)
            for ind in indSet:
                my_url = self.treeContent[ ind]
                if fuzz.ratio( os.path.splitext( my_url)[1], os.path.splitext( url)[1])<SIMILAR_THRESHOLD:
                    # if not has the same expend name
                    continue
                DIYrate, dis_list = up.similar_ratio( url, my_url)
                rate = max( fuzz.ratio(url, my_url)/100.0 +0.001, DIYrate+0.001)
                if rate < self.SIMILAR_THRESHOLD or rate <=max_rate:
                    continue
                front, back, start = self.get_surround_text( ind)
                context_similar_ratio = (fuzz.ratio(front, context['front'])/100.0+0.001) \
                * (fuzz.ratio(back, context['back'])/100.0+0.001)
                rate = rate* context_similar_ratio
                if rate < self.SIMILAR_THRESHOLD or rate <=max_rate:
                    continue
                else:
                    max_rate = rate
                    max_ind = ind
                    
            # max_ind is the one that most similar to the given url
            # replace
            if max_rate == 0 or max_rate< self.SIMILAR_THRESHOLD or max_ind<0:
                print "No similar"
                return ""
            url_split_list, host_po = up.url_split( url)
            simi_url_list, simi_url_host_po = up.url_split( self.treeContent[ max_ind])
            DIYrate, dismatch_list = up.url_list_compare(url_split_list, simi_url_list)
            tmp_url = url
            for item in dismatch_list:
                tmp_url = up.replace_url(tmp_url, item)
            print "SIMILAR URL(Tree.find_similar_and_replace):\n",self.treeContent[ max_ind],"\n",url
            print "replace:",tmp_url
#            if len(dismatch_list)>=2:
#                print "Multi-Replacement:\n",url
#                print self.treeContent[ max_ind]
#                input('Multi-Replacement:\n')
            return tmp_url
            
    def get_surround_text(self, index):
        '''
        input: node's index in the "treeRelation" list
        get surround text.Return self.SURROUND chars for front and back respectively.
        And return "start" in addition.
        "start" == 0 means the url is a root.
        "start" == -1 means the url is not found.
        Otherwise, "start" is the url start position in response body text
        '''
        data = up.readJason(self.filename)
        item_position = self.indexList[index]
        if item_position< 0:
            # the url is a root
            return (" ", " ", 0)
        currentItem = data['log']['entries'][item_position]
        if currentItem['response']['content'].has_key('text'):
            text = currentItem['response']['content']['text']
            start = self.positionInText[ index][0]
            end = self.positionInText[ index][1]
            if start+1>= self.SURROUND and (len(text)-end-1)>= self.SURROUND:
                front = text[start-self.SURROUND: start]
                back = text[end: end+ self.SURROUND]
            else:
                min_num = min([start+1, len(text)-end-1])
                front = text[start- min_num: start]
                back = text[end: end+ min_num]
        else:
            front = ""
            back = ""
            start = -1
        
        return (front, back, start)
        
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
        
    def get_all_root_index(self):
        '''
        get all root node in the pattern
        '''
        self.roots_list = []
        for ind in range(0,len(self.treeRelation)):
            if self.treeRelation[ind] ==0:
                self.roots_list.append( ind)
        return self.roots_list
        
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
        
    def get_descendant_indexList( self, node_ind):
        '''
        input: node_index
        output: descendant index of the input node
        iteratively find the children and append to descendant list
        '''
        descendant_list = []
        if not ((node_ind+1) in self.treeRelation):
            return descendant_list
        else:
            tmp_childList = self.get_children_indexList( node_ind)
            descendant_list.extend(tmp_childList)
            for item in tmp_childList:
                descendant_list.extend( self.get_descendant_indexList(item))
            return descendant_list
        
    def search_url_index(self, url):
        '''
        output: node's index in the "treeRelation" list
        '''
        url_tmp = up.drop_variation( url)
        ind_arr = []
        ind = -1
        while ind <= len(self.treeContent):
            if url_tmp in self.treeContent[ind+1:]:
                ind = self.treeContent.index(url_tmp,ind+1)
                ind_arr.append( ind)
            else:
                break
        return ind_arr
        
    def dump_tree_content(self):
        f_dump = open(self.dumpPath,'w')
        for j in range(0,len(self.treeRelation)):
            f_dump.write( str(j+1)+" : "+str(self.treeRelation[j])+ ", "+ str(self.wait_interval[j])+ ", "+ self.treeContent[j]+", " \
            +str(self.mimeType[j])+ ", "+str(self.treeTimestamp[j])+ ", "+ str(self.indexList[j])+", "+str(self.positionInText[j])+ \
            ", "+str(self.size[j])+"\n" )
        f_dump.close()
        return