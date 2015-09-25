# -*- coding: utf-8 -*-

import os;
#from getTree import *;
import getTree as gt;
import stopURL as su;
import url_process as up;
import drawGraph;
import random;
import copy;
from fuzzywuzzy import fuzz;

#from stopURL import *;

#PATH = './Data/HARData(cached)'
PATH = './Data/HARData'
stop_url_path = './Data/noise'

# test using weilaoshi.net
#PATH = './Data/WLS/Hars'
#stop_url_path = './Data/WLS/noise'

dump_dir = './TREE/'
FILTER_lonelyRoot = False
TOP_K_time_consuming = 10
CONTEXT_SIMILARITY_THRESHOLD = 0.9

class Forest:
    def __init__(self, PATH, stop_url_path, dump_dir):
        self.files = os.listdir(PATH)
        self.PATH = PATH
        self.dump_dir = dump_dir
        up.if_dir_exists(dump_dir)
        self.painter = drawGraph.TreePainter(dump_dir)
        self.stop = su.Stop_url(stop_url_path)
        self.forest = []
        self.timestampList = []
        self.get_forest()
        self.intersec_tree = None
        self.intersec_tree = self.intersection()
        while True:
            if not self.draw_a_tree():
                break
        
    def get_forest(self):
        for f in self.files:
            path = self.PATH +'/'+ f
            dumpPATH = self.dump_dir + f + "._treeContent"
            print path
            self.forest.append(gt.get_Tree(path, dumpPATH, self.stop))
            
    def intersection_in2Trees(self, t1, t2):
        '''
        get the intersection of t1 and t2
        element in critical_path is -1 if it's not in intersection
        len(critical_path) == len(t1.treeRelation)
        '''
        critical_path = copy.deepcopy( t1.treeRelation)
        critical_content = copy.deepcopy( t1.treeContent)
        tmp_timestamp_list = copy.deepcopy( t2.treeTimestamp)
        for index in range(0,len(t1.treeRelation)):
            if not t2.has_node( t1.treeContent[index]):
                critical_path[index] = -1
                
#            has_similar, dismatch_list, similar_url_position = t2.has_similar( t1.treeContent[index])
#            if not has_similar:
#                critical_path[index] = -1
#                tmp_timestamp_list[index] = ()
#            else:
#                tmp_timestamp_list[index] = copy.deepcopy( t2.treeTimestamp[similar_url_position])
#                tmp_url = critical_content[index]
#                for item in dismatch_list:
#                    tmp_url = up.replace_url(tmp_url, item)
#                if len(dismatch_list)!=0:
#                    print t1.filename," vs ", t2.filename
#                    print '(before)',critical_content[index]
#                    print '(after)',tmp_url
##                    input("main.L62,replace")
#                critical_content[index] = tmp_url
##        self.timestampList.append(tmp_timestamp_list)
##        input("critical node")
        return ( critical_path, critical_content)
        
    def get_replaced_tree(self, t1, t2):
        '''
        在t1基础上，获得两树交集，然后
        '''
        critical_path, content_vec = self.intersection_in2Trees(t1,t2)
        ori_contenc_vec = copy.deepcopy( t1.original_treeContent)
        for index in range(0,len(critical_path)):
            if critical_path[index]== -1 and content_vec[index] !="": #if not in intersection
                if index in t1.roots_list:
                    # if the node is a root
                    content_vec[index] = t2.find_similar_and_replace( content_vec[index], t2.roots_list)
                else:
                    # if the node is not a root
                    t1_parent_ind = t1.get_parent_index(index)
                    parent_url = t1.treeContent[ t1_parent_ind]
                    if parent_url !="":
                        has_similar, dismatch_list, similar_url_indexList = t2.has_similar( parent_url)
                    else:
                        has_similar = False
                        content_vec[index] = ''
                        
                    if has_similar: # if its parent node has similar
                        front_t1, back_t1, position_t1 = t1.get_surround_text( index)
                        desc_node_indexSet = set([])
                        for t2_pare_ind in similar_url_indexList:
                            desc_node_indexSet = desc_node_indexSet.union(set(t2.get_descendant_indexList(t2_pare_ind)))
                        content_vec[index] = t2.find_similar_and_replace( content_vec[index], list(desc_node_indexSet), {'front':front_t1,'back':back_t1})
                    else:
                        content_vec[index] = ''
                        
                if ''!= content_vec[index]:
                    critical_path[index] = t1.treeRelation[index]
                else:
                    ori_contenc_vec[index] = ""
        filename = t1.dumpPath.split('/')[-1].split('.')[0]+'&'+t2.filename.split('/')[-1].split('.')[0]+'.txt'
        
        tree_info_mat = {}
        tree_info_mat['treeRelation'] = copy.deepcopy( critical_path)
        tree_info_mat['treeContent'] = copy.deepcopy( content_vec)
        tree_info_mat['indexList'] = copy.deepcopy( t1.indexList)
        tree_info_mat['original_treeContent'] = copy.deepcopy( ori_contenc_vec) #t1.original_treeContent
        tree_info_mat['wait_interval'] = copy.deepcopy( t1.wait_interval)
        tree_info_mat['mimeType'] = copy.deepcopy( t1.mimeType)
        tree_info_mat['filename'] = copy.deepcopy( t1.filename)
        tree_info_mat['treeTimestamp'] = copy.deepcopy( t1.treeTimestamp)
        tree_info_mat['dumpPath'] = self.dump_dir + filename
        tree_info_mat['positionInText'] = copy.deepcopy( t1.positionInText)
        tree_info_mat['size'] = copy.deepcopy( t1.size)
        
        critical_tree = gt.Tree( tree_info_mat)
        return critical_tree
        
    def intersection(self, rand_select = False):
        if rand_select:
            init_ind = int(len(self.forest)*random.random())
        else:
            init_ind = 0
        if len(self.forest) <=1:
            if len(self.forest) == 0:
                print "forest has No tree yet"
            if len(self.forest) == 1:
                print "forest has one tree only"
            return None
        else:
            critical_tree = copy.deepcopy( self.forest[init_ind])
            for i in range(1,len(self.forest)):
                critical_tree = self.get_replaced_tree(critical_tree, self.forest[i])

        self.intersec_tree = critical_tree
        return critical_tree
    
    def draw_a_tree(self):
        print "Tree list:"
        for i in range(0,len(self.forest)):
            print i,": ",self.forest[i].filename
        print i+1,": all trees"
        if self.intersec_tree != None:
            print i+2,"critical path"
        print i+3,": exit"
        ind = input("input the tree index:")
        if ind == (2+len(self.forest)): # quit draw_a_tree
            return False
        if ind == (1+len(self.forest)) and self.intersec_tree!=None: #draw critical path
            self.painter.draw_tree( self.intersec_tree, TOP_K_time_consuming, FILTER_lonelyRoot)
            return True
        if ind<0 or ind> (1+len(self.forest)):
            print "invalid input"
            return True
        if ind < len(self.forest) and ind>=0:
            self.painter.draw_tree( self.forest[ind], TOP_K_time_consuming, FILTER_lonelyRoot)
        else:
            self.draw_all()
        return True
        
    def draw_all(self):
        for t in self.forest:
            self.painter.draw_tree(t, TOP_K_time_consuming, FILTER_lonelyRoot)
        return
        
    def compare_context(self):
        pass
        
                            
        
if __name__ == "__main__":
    forest = Forest(PATH, stop_url_path, dump_dir)
    stop = su.Stop_url(stop_url_path)
