# -*- coding: utf-8 -*-
import urlparse;
import url_process as up;
import os;

class Stop_url:
    def __init__(self, path):
        self.path = path
        self.file_list = os.listdir(path)
        self.stopURLset = set([])
        self.get_stop_urls();
        self.stopHost = set([])
        self.EXCEPT = set([])
    
    def read_json(self, path):
        return up.readJason(path)
        
    def is_excepted(self, url):
        pass
        
    def get_stop_urls(self):
        for f in self.file_list:
            data = self.read_json(self.path +'/'+ f)
            for i in range(0,len( data['log']['entries'])):
                currentItem = data['log']['entries'][i]
                ori_requestURL = currentItem['request']['url']
                tmp = urlparse.urlparse(ori_requestURL)
                requestURL = up.drop_variation( ori_requestURL );
                
                self.stopURLset.add(requestURL)
                self.stopURLset.add(ori_requestURL)
#            if tmp.hostname:
#                self.stopURLset.add(tmp.hostname)
        return
            
    def is_stopURL(self, url):
        '''judge if this url is a stopURL'''
        tmp = up.drop_variation(url)
#        tmp = urlparse.urlparse(ori_requestURL)
        if (tmp in self.stopURLset) or (url in self.stopURLset):
            return True
        else:
            return False