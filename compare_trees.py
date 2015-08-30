# -*- coding: utf-8 -*-

import os;
#from getTree import *;
import getTree as gt;
import stopURL as su;
import url_process as up;
import drawGraph;
import random;

#from stopURL import *;

PATH = './Data/HARData'
stop_url_path = './Data/noise'
dump_dir = './TREE/'
FILTER_lonelyRoot = False
TOP_K_time_consuming = 10

class Forest:
    def __init__(self, PATH, stop_url_path, dump_dir):
        self.files = os.listdir(PATH)
        self.PATH = PATH
        self.dump_dir = dump_dir
        up.if_dir_exists(dump_dir)
        self.painter = drawGraph.TreePainter(dump_dir)
        self.stop = su.Stop_url(stop_url_path)
        self.forest = []
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
        critical_path = t1.treeRelation
        critical_content = t1.treeContent
        ind = 0
        for index in range(0,len(t1.treeRelation)):
            has_similar, dismatch_list, similar_url_position = t2.has_similar( t1.treeContent[index])
            if not has_similar:
#            if not t2.has_node( t1.treeContent[index]):
                critical_path[index] = -1
            else:
                ind = ind+ 1
        print "critical node num:",ind
        input("critical node")
        return ( critical_path, critical_content)
        
    def get_replaced_tree(self, t1, t2):
        '''
        在t1基础上，获得两树交集，然后
        '''
        critical_path, content_vec = self.intersection_in2Trees(t1,t2)
        for index in range(0,len(critical_path)):
            
            if critical_path[index]== -1 and content_vec !="": #if not in intersection
                t1_parent_ind = t1.get_parent_index(index)
                parent_url = t1.treeContent[ t1_parent_ind]
                has_similar, dismatch_list, similar_url_position = t2.has_similar( parent_url)
                
                if has_similar: # if its parent node has similar
                    front_t1, back_t1, position_t1 = t1.get_surround_text( index)
                    children_index = t2.get_children_indexList( similar_url_position)
                    for ci in children_index:
                        front_t2, back_t2, position_t2 = t2.get_surround_text( ci)
                        if front_t1==front_t2 and back_t1==back_t2:
#                        if front_t1==front_t2: # and back_t1==back_t2:
                            print "similar:"
                            print t1.filename," & ",t2.filename
                            print "t1:",front_t1," + ",t1.treeContent[index]," + ",back_t1,"\nposition:",position_t1
                            print "t2:",front_t2," + ",t2.treeContent[ci]," + ",back_t2,"\nposition:",position_t2
                            input("similar:")
                            critical_path[index] = t1_parent_ind
                if critical_path[index] == -1:
                    content_vec[index] = ""
        filename = t1.dumpPath.split('/')[-1].split('.')[0]+'&'+t2.filename.split('/')[-1].split('.')[0]+'.txt'
        
        tree_info_mat = {}
        tree_info_mat['treeRelation'] = critical_path
        tree_info_mat['treeContent'] = content_vec
        tree_info_mat['indexList'] = t1.indexList
        tree_info_mat['original_treeContent'] = t1.original_treeContent
        tree_info_mat['wait_interval'] = t1.wait_interval
        tree_info_mat['mimeType'] = t1.mimeType
        tree_info_mat['filename'] = t1.filename
        tree_info_mat['treeTimestamp'] = t1.treeTimestamp 
        tree_info_mat['dumpPath'] = self.dump_dir + filename
        
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
                print "forest has a tree only"
            return None
        else:
            critical_tree = self.forest[init_ind]
            for i in range(1,len(self.forest)):
                critical_tree = self.get_replaced_tree(critical_tree, self.forest[i])
            
            f_dump = open(critical_tree.dumpPath,'w')
            for j in range(0,len(critical_tree.treeRelation)):
                f_dump.write( str(j+1)+":"+str(critical_tree.treeRelation[j])+ ","+ critical_tree.treeContent[j]+","+str(critical_tree.wait_interval[j])+ "\n" )
            f_dump.close()
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
        if ind != len(self.forest):
            self.painter.draw_tree( self.forest[ind], TOP_K_time_consuming, FILTER_lonelyRoot)
        else:
            self.draw_all()
        return True
        
    def draw_all(self):
        for t in self.forest:
            self.painter.draw_tree(t, TOP_K_time_consuming, FILTER_lonelyRoot)
        return
        
                            
        
if __name__ == "__main__":
    forest = Forest(PATH, stop_url_path, dump_dir)
    stop = su.Stop_url(stop_url_path)
