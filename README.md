HarParser
================
##### 作者：Albert Zhao
##### 邮箱：imagine4077@gmail.com / zhaowei@dislab.nju.edu.cn

1. python 2.7

2. 可用于检测网络应用层traffic的黑盒测试，生成树状资源调用树状图（graphviz）。

3. 可用于检测web页面，可用于检测移动设备web页面或APP。Fiddler代理需手动设置； 若需检测HTTPS相关内容，请手动添加证书，添加方法此处不再赘述。

#### 数据收集

此处仅介绍移动设备（以手机为例）中APP的检测（后文称“目标程序”）：

1. 将手机与laptop接入同一局域网。

2. 打开Fiddler，手机进行代理设置，登录代理服务器安装相关证书。

3. 不开启目标程序，收集STOP_URL，即非目标程序产生的traffic。将其保存为.har文件，存放于./Data/noise 目录下

4. 开启目标程序，收集数据。将其保存为.har文件，存放于./Data/HARData 目录下

#### 运行

运行compare_trees.py , 详细信息将被保存至 ./TREE 目录下
    
    
    
    
#### 引用
[1] Crussell J, Stevens R, Chen H. MAdFraud: Investigating ad fraud in android applications[C]//Proceedings of the 12th annual international conference on Mobile systems, applications, and services. ACM, 2014: 123-134.

[2] Butkiewicz M, Wang D, Wu Z, et al. Klotski: Reprioritizing Web Content to Improve User Experience on Mobile Devices[J].
