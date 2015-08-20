function [ output_vec, output_content, output_timestamp ] = del_lonelyRoot( treeVec, nodeContent, timestamp )
%DEL_LONELYROOT Summary of this function goes here
%   Detailed explanation goes here

nonzeroE = find(treeVec ~= 0);
roots = unique(treeVec(nonzeroE));
treeRoots =  find(treeVec(roots)==0)
med_node = find(treeVec(roots)~=0)
index = 1;

new_vec = [];
output_content = {};
output_timestamp = {};
pointer = 1; %point to the current null position
hash_table = [];
while index<= length(treeVec)
%     index
    if treeVec(index)~=0 | sum( find( roots ==index )) %not a lonely root
        if sum( find( roots ==index )) %& treeVec(index)==0 %if it's a root
            hash_table(index) = pointer;
            if treeVec(index)==0 %if it's a root
                new_vec = [new_vec, 0];
            else %if it's a med_node
                new_vec = [new_vec, hash_table( treeVec(index) )];
            end
%             pointer = pointer +1;
        else % is a node
            new_vec = [new_vec, hash_table( treeVec(index) )];
%             pointer = pointer +1;
        end
        output_content(pointer) = nodeContent(index);
        output_timestamp(pointer) = timestamp(index);
        pointer = pointer +1;
    end
    index = index + 1;
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
%     treeVec'
end
output_vec = new_vec;


end

