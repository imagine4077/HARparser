# -*- coding: utf-8 -*-

######################################
# 1.正则待改良 [Q1]
# 2.re 的最大匹配 [Q2]
######################################
import json
import re
from url_process import *

#file_Name = "1.txt"
file_Name = "0718_2221.txt"
PATH = "TaoBaoData/"+ file_Name
dumpPATH = "TREE/"+ file_Name

#正则有待改良
#from : http://blog.csdn.net/weasleyqi/article/details/7912647
onLine_re = r'((http|ftp|https)://)(([a-zA-Z0-9\._-]+\.[a-zA-Z]{2,6})|([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}))(:[0-9]{1,4})*(/[a-zA-Z0-9\&%_\./-~-]*)?'


def readJason( path ):
    x = open(path)
#    x = x.read()
#    return json.loads(x[1:])
    tmp = json.load(x)
    x.close()
    return tmp
    
if __name__ == '__main__':
    data = readJason(PATH)
    treeIndex = []
    treeContent = []
    for i in range(0,len(data['log']['entries'])):
        currentItem = data['log']['entries'][i]
        ori_requestURL = currentItem['request']['url']
        requestURL = drop_variation( ori_requestURL );
        
        #process this request-response pair
        #process request part
        if requestURL in treeContent: #if the requested content has pushed in the tree
            root = treeContent.index(requestURL) + 1
        else:
            treeRelation.append(0)
            treeContent.append(requestURL)
            root = len(treeContent)
            
        #process response part
        if data['log']['entries'][i]['response']['content'].has_key('text'):
            string = data['log']['entries'][i]['response']['content']['text']
            subPatt = re.findall(onLine_re, string)
            for item in subPatt:
                treeIndex.append( root )
#                treeContent.append( str(item[0]) + ''.join(item[2:]) )
                treeContent.append( item[0] + item[2] + item[6] ) #[Q2]
        else:
            print i
            print currentItem['response']['content']['mimeType']
            
    #to get the timestamp
    treeTimestamp = [(u'',0,u'') for i in range(0,len(treeIndex)) ]
    for i in range(0,len(data['log']['entries'])):
        currentItem = data['log']['entries'][i]
        ori_requestURL = currentItem['request']['url']
        requestURL = drop_variation( ori_requestURL );
        timestamp = get_fiddle_timestamp(currentItem['startedDateTime'])
        if requestURL in treeContent: #if the requested content has pushed in the tree
            treeTimestamp[treeContent.index(requestURL)] = timestamp
    f_dump = open(dumpPATH,'w')
    for j in range(0,len(treeIndex)):
        f_dump.write( str(treeIndex[j])+ ","+ treeContent[j]+","+str(treeTimestamp[j][1])+ "\n" )
    f_dump.close()

class Tree:
    def __init__(self):
        pass