# -*- coding: utf-8 -*-
from graphviz import Digraph

def find_nonzero( arr):
    '''
    matlab: find( arr ~= 0 )
    '''
    index_arr = []
    for i in range(0,len(arr)):
        if arr[i] != 0:
            index_arr.append(i)
    return index_arr
    
def find_zero( arr):
    '''
    matlab: find( arr == 0 )
    '''
    index_arr = []
    for i in range(0,len(arr)):
        if arr[i] == 0:
            index_arr.append(i)
    return index_arr

def get_part_arr( arr, ind):
    '''
    matlab: arr( ind )
    '''
    tmp_arr = []
    for item in ind:
        tmp_arr.append(arr[item])
    return tmp_arr
    
def get_part_ind( arr, ind):
    '''
    cause the value in arr is matlab-style
    '''
    tmp_arr = []
    for item in ind:
        tmp_arr.append(arr[item]-1)
    return tmp_arr

def reverse_selection(arr, ind):
    reverse_ind = []
    for i in range(0,len(arr)):
        if not(i in ind):
            reverse_ind.append(i)
    return reverse_ind
    
def get_1st_unmarked(arr, flag_arr, value):
    if len(arr) != len(flag_arr):
        print len( arr) ,'!=', len(flag_arr)
        input('ERROR in FUNCTION get_1st_unmarked( arr, flag_arr, value)\n')
    if not(value in arr): #if no corresponding element
        return (flag_arr, -1)
    index = -1
    #if has corresponding element
    while index< len( arr):
        if value in arr[index+1:]:
            index = arr.index(value, index+1)
            if flag_arr[index] == 0:
                flag_arr[index] = 1
                return (flag_arr, index)
            else:
                continue
        else: #if has corresponding element but all got.That's mean this page is the root of a new tree
            return (flag_arr, -1)
    
   
class TreePainter:
    def __init__(self, dump_dir):#
        self.dump_dir = dump_dir
    
    def draw( self, vec, contentMatrix, fig_coment,K = 0, filter_lonelyRoot = True):
        self.find_lonely(vec)
        dot = Digraph(comment=fig_coment, engine='dot')
        dot.format = 'png'
#        dot.body.extend(['rankdir=LR']) # set vertical layout
        if K >0:
            time_consuming = self.most_timeConsuming(contentMatrix['wait_interval'],K)
        else:
            time_consuming = []
#        dot.body.append('center=ture')
#        dot.node_attr.update(color='lightblue2', style='filled',width='0.04',height='0.04')
        for i in range(0,len(vec)):
            if (filter_lonelyRoot and (i in self.lonely)) or vec[i]<0:
                continue
            if i in time_consuming:
                if contentMatrix['wait_interval'][i] != -1:
                    dot.node(str(i+1),"("+str(i+1)+")\n"+contentMatrix['mimeType'][i].split(';')[0].split('/')[-1]+':'+str(contentMatrix['wait_interval'][i]),color='tomato2', style='filled')
                else:
                    dot.node(str(i+1),"("+str(i+1)+")\n"+"no request", style='filled')
            else:
                if contentMatrix['wait_interval'][i] != -1:
                    dot.node(str(i+1),"("+str(i+1)+")\n"+contentMatrix['mimeType'][i].split(';')[0].split('/')[-1]+':'+str(contentMatrix['wait_interval'][i]),color='lightblue2', style='filled')
                else:
                    dot.node(str(i+1),"("+str(i+1)+")\n"+"no request", style='filled')
            if vec[i] != 0:
                dot.edge(str(vec[i]), str(i+1))#,constraint='false')
        dot.render(fig_coment+'_treeplot.dot', view=True)
        return dot

    def draw_tree(self, tree, K=0, filter_lonelyRoot=True):
        tmp = {}
        tmp['wait_interval'] = tree.wait_interval
        tmp['treeContent'] = tree.treeContent
        tmp['mimeType'] = tree.mimeType
        vec = tree.treeRelation
        self.draw(vec, tmp, tree.dumpPath, K, filter_lonelyRoot)
    
    def find_lonely( self, vec):
        '''
        get an array contains the indexex of lonely roots
        '''
#        nonroot_ind = find_nonzero( vec) #非根节点（因有指向）
#        nonLeaf_ind = set( get_part_ind( vec, nonroot_ind)) #非叶子节点，因被指向
#        root_ind = reverse_selection(vec, nonroot_ind) #根节点，全集-非根=根
        lonely = []
        for i in range(0,len(vec)):
            if vec[i]==0 and not((i+1) in vec):
                lonely.append(i)
        self.lonely = lonely
        return lonely
        
    def most_timeConsuming( self, interval_arr, n):
        '''
        find the top n most time-consuming resources, then return their index
        '''
        tmp = sorted(interval_arr, reverse=True)[:n]
        ind_arr = []
        flag_arr = [0 for i in range(0,len(interval_arr))]
        for item in tmp:
            flag_arr, index = get_1st_unmarked(interval_arr, flag_arr, item)
            if index >=0:
                ind_arr.append( index)
            else:
                input('ERROR:drawTree.most_timeConsuming(), index <0')
        return ind_arr
        