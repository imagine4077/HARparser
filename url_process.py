# -*- coding: utf-8 -*-
import urlparse;
import re;
import os;
import json;
import codecs;
from fuzzywuzzy import fuzz;
from colorama import Fore

def if_dir_exists( dir_path):
    if not os.path.exists( dir_path):
        os.mkdir( dir_path)
    return

def drop_variation(url):
    # drop variation in url which post by GET method
    tmp = urlparse.urlparse(url);
    
    def noNone(obj):
        if obj:
            return obj
        else:
            return ""
    
    if len(tmp.query) == 0:
        return url
    else:
        return tmp.scheme +'://'+ noNone(tmp.hostname) + noNone(tmp.path) + "?*"
        
def get_fiddle_timestamp( time_str ):
    ''' fiddle .har time ['startedDateTime'] format:\n
        example:    2015-07-18T22:20:41.9559490+08:00
        that's mean the GotRequestHeaders
        
        convert to a timestamp which stand for the time interval from time_str to
        00:00 of this day
    '''
    ss = re.split('[T+]', time_str)
    h, m, s = ss[1].split(':')
    h = float(h)
    m = float(m)
    s = float(s)
    interval = h*3600 + m *60 + s
    return (ss[0], interval, ss[2])
    
def url_split( url):
    tmp = urlparse.urlsplit( url)
    result_list = [ tmp.scheme+"://", tmp.netloc]
#    tmp = urlparse.urlparse(url)
    path_split_list = tmp.path.split('/')
    while True:
        if '' in path_split_list:
            path_split_list.remove('')
        else:
            break
    while True:
        if None in path_split_list:
            path_split_list.remove(None)
        else:
            break
    if len(path_split_list) ==0:
#        print "ERROR:len(path_split_list) ==0\n",url
        return result_list
#    file_type = path_split_list[-1].split('.')
#    del path_split_list[-1]
#    path_split_list.extend(file_type)
    result_list.extend( path_split_list)
    return result_list
    
def url_list_compare(list1, list2):
    if len(list1) != len(list2):
        return (0, [])
#    length = min(len(list1), len(list2))
    length = len(list1)
    dismatch_list = []
    rate = 0
    for i in range(0,length):
        if list1[i] == list2[i]:
            rate += 1
        else:
            dismatch_list.append(i)
    print float(rate), "length:", length
    rate = float(rate)/length
    print rate
    return (rate, dismatch_list)
    
def has_similar_url(url, url_list, THRESHOLD):
    if url in url_list:
        root = url_list.index(url) + 1
        return (True, root, url_list.index(url))
    else:
        url_split_list = url_split( url)
        for my_url in url_list:
            my_url_list = url_split(my_url)
            rate, dismatch_list = url_list_compare(url_split_list, my_url_list)
            rate = fuzzywuzzy.fuzz.ratio(url, my_url)
            print rate,"  ",
            if rate > THRESHOLD:
                print "SIMILAR URL:\n",my_url,"\n",url
                return (True, dismatch_list, url_list.index(my_url))
        return (False, [], -2)
        
def replace_url( url, ind):
    print 'up.replace_url,ori:',url
    if ind==0:
        return url
    tmp = url_split(url)
    last_name = os.path.splitext(url)[1]
    tmp[ ind] = "*"
    result_str = tmp[0][:-1]
    for ind in range(1,len(tmp)):
        result_str = result_str + '/' +tmp[ind]
    if os.path.splitext(result_str)[1]!= last_name:
        result_str = result_str + last_name
    print 'up.replace_url,modi:',result_str
    return result_str
    
def readJason( path ):
    x = open(path)
    text = x.read()
    if text.startswith(codecs.BOM_UTF8):
        text = text[3:]
    tmp = json.loads(text)
    x.close()
    return tmp
    
def get_urlSet_from_text( data):
    '''
    input: response content
    output: urls extracted from the content
    '''
    onLine_re = r'(?P<protocol>http:|ftp:|https:)?(?P<hostname>(?P<domain>//[a-zA-Z0-9\._-]+\.[a-zA-Z]{2,6})|(?P<IPaddress>//[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}))(?P<port>:[0-9]{1,4})*(?P<path>/[a-zA-Z0-9\&%_\./-~-]*)?'
    pos = 0
    count = 0
    mat=re.search(onLine_re, data)
    while mat != None:
        URL = ""
        if mat.groupdict()['hostname'] ==None:
            input('ERROR:no hostname\n')
    #        continue
        URL = URL +mat.groupdict()['hostname']
        if mat.groupdict()['port'] != None:
            URL = URL + mat.groupdict()['port']
        if mat.groupdict()['path'] != None:
            URL = URL + mat.groupdict()['path']
        if mat.groupdict()['protocol'] == None:
            URL = "http:" + URL
            count = count +1
        else:
            URL = mat.groupdict()['protocol'] + URL
#            print URL
        yield ( URL, pos+ mat.start(), pos+ mat.end(), count)
        pos = pos + mat.end()
        mat = re.search(onLine_re, data[pos:])
        