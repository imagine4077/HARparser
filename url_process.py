# -*- coding: utf-8 -*-
import urlparse;
import re;
import os;
import json;
import codecs;

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
        return noNone(tmp.hostname) + noNone(tmp.path) + "?*"
        
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
    tmp = urlparse.urlparse(url)
    result_list = [tmp.hostname]
    path_split_list = tmp.path.split('/')
    if '' in path_split_list:
        path_split_list.remove('')
    if None in path_split_list:
        path_split_list.remove(None)
    if len(path_split_list) ==0:
#        print "ERROR:len(path_split_list) ==0\n",url
        return result_list
    file_type = path_split_list[-1].split('.')
    del path_split_list[-1]
    path_split_list.extend(file_type)
    result_list.extend( path_split_list)
    return result_list
    
def url_list_compare(list1, list2):
#    if list1[0] != list2[0]:
#        return
    length = min(len(list1), len(list2))
    dismatch_list = []
    rate = 0
    for i in range(0,length):
        if list1[i] == list2[i]:
            rate += 1
        else:
            dismatch_list.append(i)
    rate = float(rate)/length
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
            print rate,"  ",
            if rate > THRESHOLD:
                print "SIMILAR URL:\n",my_url,"\n",url
                return (True, dismatch_list, url_list.index(my_url))
        return (False, [], -2)
        
def replace_url( url, ind):
    tmp = url_split(url)
    tmp[ ind] = "*"
    print tmp
    print ''.join(tmp)
    return ''.join(tmp)
    
def readJason( path ):
    x = open(path)
    text = x.read()
    if text.startswith(codecs.BOM_UTF8):
        text = text[3:]
    tmp = json.loads(text)
    x.close()
    return tmp