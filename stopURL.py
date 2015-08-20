# -*- coding: utf-8 -*-
import urlparse;
import json;
from url_process import *;

class Stop_url:
    def __init__(self, path):
        self.path = path
        self.data = self.read_json()
        self.stopURLset = set([])
        self.get_stop_urls();
        self.stopHost = set([])
        self.EXCEPT = set([])
    
    def read_json(self):
        x = open(self.path)
        return json.load(x)
        
    def is_excepted(self, url):
        pass
        
    def get_stop_urls(self):
        for i in range(0,len(self.data['log']['entries'])):
            currentItem = self.data['log']['entries'][i]
            ori_requestURL = currentItem['request']['url']
            tmp = urlparse.urlparse(ori_requestURL)
            requestURL = drop_variation( ori_requestURL );
            
            self.stopURLset.add(requestURL)
#            if tmp.hostname:
#                self.stopURLset.add(tmp.hostname)
        return
            
    def is_stopURL(self, url):
        '''judge if this url is a stopURL'''
        tmp = drop_variation(url)
#        tmp = urlparse.urlparse(ori_requestURL)
        if tmp in self.stopURLset:
            return True
        else:
            return False