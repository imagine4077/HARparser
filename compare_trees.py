# -*- coding: utf-8 -*-

import os;
#from getTree import *;
import getTree as gt;
import stopURL as su;
import url_process as up;

#from stopURL import *;

PATH = './TaoBaoData/txtData'
stop_url_path = './TaoBaoData/noise0719_2016.txt'
dump_dir = 'TREE/'

class Forest:
    def __init__(self, PATH, stop_url_path):
        self.files = os.listdir(PATH)
        self.PATH = PATH
        self.stop = su.Stop_url(stop_url_path)
        self.forest = []
        self.get_forest()
        
    def get_forest(self):
        for f in self.files:
            path = self.PATH +'/'+ f
            dumpPATH = "TREE/"+ f
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
#                critical_content[index] = ""
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
            
            if critical_path[index]== -1: #if not in intersection
                t1_parent_ind = t1.get_parent_index(index)
                parent_url = t1.treeContent[ t1_parent_ind]
                has_similar, dismatch_list, similar_url_position = t2.has_similar( parent_url)
                
                if has_similar:
                    front_t1, back_t1, position_t1 = t1.get_surround_text( index)
                    children_index = t2.get_children_indexList( similar_url_position)
#                    children_index = t2.get_children_indexList( t2.search_url_index(parent_url))
                    for ci in children_index:
                        front_t2, back_t2, position_t2 = t2.get_surround_text( ci)
                        if front_t1==front_t2 and back_t1==back_t2:
#                        if front_t1==front_t2: # and back_t1==back_t2:
                            print "similar:"
                            print "t1:",front_t1," + ",t1.treeContent[index]," + ",back_t1,"\nposition:",position_t1
                            print "t2:",front_t2," + ",t2.treeContent[ci]," + ",back_t2,"\nposition:",position_t2
                            input("similar:")
                            critical_path[index] = t1_parent_ind
                            content_vec[index] = parent_url
                        else:
                            content_vec[index] = ""
#            else: #"single token in the URL changes",klotski p444
##                t1_parent_ind = t1.get_parent_index(index)
#                current_url = t1.treeContent[ index]
#                has_similar, dismatch_list, similar_url_position = t2.has_similar( current_url)
#                if has_similar:
#                    for i in range(0,len(dismatch_list)):
#                        content_vec[index] = up.replace_url( content_vec[index], dismatch_list[i])
        dumpPath = dump_dir + t1.filename[21:30]+'&'+t2.filename[21:30]+'-CriticalInfo.txt'
        f_dump = open(dumpPath,'w')
        first_text = t1.treeTimestamp[0]
        for j in range(0,len(critical_path)):
            if t1.treeTimestamp[j][1] != 0:
                tmp = t1.treeTimestamp[j][1]- first_text[1]
            else:
                tmp = ''
            f_dump.write( str(critical_path[j])+ ","+ content_vec[j]+","+str(tmp)+ "\n" )
#            f_dump.write( str(critical_path[j])+ ","+ content_vec[j]+","+str(t1.treeTimestamp[j][1])+ "\n" )
        f_dump.close()
        return (critical_path, content_vec)
                            
        

def get_forest(PATH, stop_url_path):
    files = os.listdir(PATH)
    stop = su.Stop_url(stop_url_path)
    forest = []
    for f in files:
        path = PATH +'/'+ f
        dumpPATH = "TREE/"+ f
        print path
        forest.append(gt.get_Tree(path, dumpPATH, stop))
    
    return forest
        
def get_intersection():
    pass
        
#forest = get_forest(PATH, stop_url_path)
forest = Forest(PATH, stop_url_path)
stop = su.Stop_url(stop_url_path)
#for url in forest[0].