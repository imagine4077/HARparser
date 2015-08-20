
% [treeVec, nodeContent, timestamp] = textread('../TREE/1.txt','%d%s%s','delimiter', ',');
% [treeVec, nodeContent, timestamp] = textread('../TREE/0718_2221.txt','%d%s%s','delimiter', ',');
% [treeVec, nodeContent, timestamp] = textread('../TREE/0719_1625.txt','%d%s%s','delimiter', ',');
[treeVec, nodeContent, timestamp] = textread('../TREE/0718_2221&0719_1625-CriticalInfo.txt','%d%s%s','delimiter', ',');
origin_treeVec = treeVec';
origin_nodeContent = nodeContent;
% timestamp = str2double(timestamp);
origin_timestamp = timestamp;
%% check the input
if length(treeVec') ~= length(nodeContent)
    fprintf('Bad input:length(treeVec) ~= length(nodeContent)\n');
    pause
end
for i=1:length(treeVec)
    if treeVec(i)>i
        fprintf('Bad input: TreeVector invalide, illigal node(%d)\n',i);
    end
end
if_critical = find(treeVec==-1);
if sum(if_critical)
    treeVec(if_critical) = 0;
end
%% filter the lonely roots
% %
% % È¥µô http://www.telerik.com/UpdateCheck.aspx?isBeta=False 
% treeVec(1)=0;
% treeVec(2)=0;
% treeVec(3)=0;
% %
nonzeroE = find(treeVec ~= 0);
parents = unique(treeVec(nonzeroE));
%roots' index in the tree
treeRoots =  parents( find(treeVec(parents)==0));
med_node = parents(find(treeVec(parents)~=0));
index = 1;

[treeVec, nodeContent, timestamp] = del_lonelyRoot( treeVec, nodeContent, timestamp );
% while index<= length(treeVec)
% %     if sum(treeVec(index:) )
% %     roots
% %     fprintf('Paused, press any key to continue or use Ctrl-C to stop\n');
% %     pause;
%     if treeVec(index)==0 & ~sum( find( roots ==index )) %if this node is a lonely root
%         if index ==1
%             treeVec(1)=[];
%             nodeContent(1) = [];
%             treeVec( find(treeVec~=0) ) = treeVec( find(treeVec~=0) ) -1;
%         end
%         tmp = treeVec(1:index-1);
%         treeVec(index) = [];
%         nodeContent(index) = [];
%         treeVec( find(treeVec~=0) ) = treeVec( find(treeVec~=0) ) -1;
%         treeVec(1:index-1) = tmp;
%         
%         nonzeroE = find(treeVec ~= 0);
%         roots = unique(treeVec(nonzeroE));
%     else
%         index = index+1;
%     end
% end
% treeVec'
%% get nodes' label
[x, y] = treelayout(treeVec);
x = x';
y = y';

figure
treeplot(treeVec);
%% To name nodes
% timestamp = timestamp *100000;
% show_vec = {};
% for i=1:length(timestamp)
%     show_vec{i} = num2str(timestamp(i) - timestamp(1));
% end
tmp_root = find(treeVec==0);
tmp_nonzeroE = find(treeVec ~= 0);
tmp_parents = unique(treeVec(tmp_nonzeroE));
%roots' index in the tree
tmp_treeRoots =  tmp_parents( find(treeVec(tmp_parents)==0));
tmp_med_node = tmp_parents(find(treeVec(tmp_parents)~=0));
tmp_root = [tmp_root, tmp_med_node];
for i= 1:length(tmp_root)
    timestamp{tmp_root(i)} = strcat(timestamp{tmp_root(i)}, ' , ');
    timestamp{tmp_root(i)} = strcat(timestamp{tmp_root(i)}, nodeContent{tmp_root(i)});
end
text(x(:,1), y(:,1), timestamp, 'VerticalAlignment','bottom','HorizontalAlignment','right')

%% test block
treeRoots
med_node
% get_leaf_num(origin_treeVec)
get_leaf_num(treeVec)