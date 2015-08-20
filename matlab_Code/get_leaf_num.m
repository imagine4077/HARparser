function [ leaf_num ] = get_leaf_num( treeVec )
%GET_LEAF_NUM Summary of this function goes here
%   Detailed explanation goes here
nonzeroE = find(treeVec ~= 0);
roots = unique(treeVec(nonzeroE));

leaf_num = [];
for i=1:length(roots)
    tmp = length( find(treeVec == roots(i) & treeVec(roots(i))==0) );
    if tmp <=0
        fprintf('tmp:%g <= 0\n',tmp);
    end
    leaf_num = [leaf_num,tmp];
end

end

