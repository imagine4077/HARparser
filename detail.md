手淘应用层通信核心关系图处理方法
==========
##### 作者：Albert Zhao
##### 隶属：南京大学
##### 邮箱：imagine4077@gmail.com / zhaowei@dislab.nju.edu.cn

0.摘要
----------

针对某特定界面的多次加载捕获的应用层信息为输入，以资源调用关系的树形结构为输出，可获得应用层的核心关系图。核心关系图对于APP系统测试、检测恶意代码注入、APP优化等均有很大帮助。

第一节介绍核心关系图的生成方式，第二节展示对手机淘宝(手淘)的处理结果，并提出相关优化建议。

1.核心关系图生成
----------

核心关系图的生成，其总体步骤可分为：(a)应用层通信的收集，(b)单个页面调用关系的生成，(c)核心关系图的生成

#### 1.1 应用层通信的收集

手淘大量数据通过HTTPS协议传送，抓取HTTPS内容成为了应用层通信信息收集的一大挑战。这里我们应用FIDDLER[1]作为抓取工具，采用松散耦合的方式将此工具应用于核心关系图抽取。

##### 1.1.1 HTTPS抽取

FIDDLER提供了"DO_NOT_TRUST_FiddlerRoot"CA证书，并且将此证书用于所有https域名。

使用步骤如下：

1. 将PC和手机接入同一局域网，PC端运行FIDDLER。

2. 根据PC端FIDDLER的设定，设置手机代理服务器地址和端口。

3. 访问FIDDLER代理服务器，安装"DO_NOT_TRUST_FiddlerRoot"证书。

由此即可抓取HTTPS协议下的数据了。

##### 1.1.2 噪音数据

实验过程中，手机中与手淘无关的后台程序可能会产生一些应用层通信，这些通信内容可能会影响到核心关系图抽取的准确性。

在处理噪音数据时，我们采取的办法是在未开启手淘的情景下，大量收集手机的通信数据，抽取其中涉及的url地址，设置为stop_url(即噪音数据)。在抽取单次通信数据时若识别为stop_url，则过滤掉此url。

##### 1.1.3 数据收集

此处简述数据收集的过程。stop_url收集与单次手淘通信收集的方法均相同。此处以收集手淘单次通信数据为例，方法如下：

1. 将PC和手机接入同一局域网，PC端运行FIDDLER。

2. 开启手淘，收集所需手淘数据。

3. 导出数据(export sessions)，导出all sessions，保存为HTTPArchive v1.2，即.har文件

#### 1.2 单次页面调用关系的生成

##### 1.2.1 单次页面调用关系生成的流程

单次页面调用关系生成的整体流程如下：

1. 通过 fiddler收集手淘数据,保存为 .har文件。.har文件以 json的形式保存了每个 request-response请
求对的详细信息。
2. 遍历 .har文件中保存的各 request-response请求对。判断其不是 stop_url,并做去参数处理后,处理方式
如下:
> * 对于 request部分的处理:
> 如果请求的 url已经在本树中,且现有结点未被请求访问过,则此结点作为 response 文本中所有 url 的父结点，并设置"已被请求"。否则,设此 url为根结点。
> * 对于 response 部分的处理:
> 通过正则式,抽取所有 response响应文本中的 url,保存为 request部分中 url的子结点,并设置"未被请求标记"。

3. 与 request部分的 url一同获取的还有 request发送时的时间戳、mimetype、以及资源拉取所消耗的时间等信息。

4. 返回 Tree对象

##### 1.2.2 判断 request url是否已经在树中

手淘交互数据中，某些request url未曾出现在任何响应文本中(即此请求不在已有树中)，但其拉取的内容与树中已有的某个 url所指向的内容一致，且两 url字符串内容相似。例如：

> 地址1:
https://gw.alicdn.com/tps/i4/TB1qFgLJXXXXXa.XVXXFgMv5pXX-225-354.png_320x320q90s110.jpg?*
> 
> 其图片内容为：
> 
> <img style="width: 30%;" src="https://gw.alicdn.com/tps/i4/TB1qFgLJXXXXXa.XVXXFgMv5pXX-225-354.png_320x320q90s110.jpg">
> 
> 地址2:
http://gtms04.alicdn.com/tps/i4/TB1qFgLJXXXXXa.XVXXFgMv5pXX-225-354.png?*
> 
> 其图片内容为：
> 
> <img style="width: 30%;" src="http://gtms04.alicdn.com/tps/i4/TB1qFgLJXXXXXa.XVXXFgMv5pXX-225-354.png">

显然示例中的两url指向同一内容。地址2出现在已有树中，而请求地址1时，若采用常规的字符串匹配方法，难以将地址1与地址2正确匹配。

这里我们采取了模糊匹配的方法处理这类url[2]，即衡量两字符串的 Levenshtein距离，若相似度高于阈值，则判断为相似。

#### 1.3 核心关系图的生成

核心关系图的生成借鉴了[3,4]中的方法。在抽取到若干个针对同一页面的"单页面调用关系图"后，我们可以生成此页面的核心关系图。

##### 1.3.1 核心关系图生成的流程

"单页面调用关系图"和"核心关系图"在本工具中，均以Tree对象的形式保存。核心关系图的生成流程如下：

1. 生成多个"单页面调用关系图"(即多个 Tree对象，一个 Tree对象即一个"单页面调用关系图")，并将它们顺序保存于一个列表(后文以"forest"称呼这个列表)。随机选取一个 Tree对象作为初始核心关系图，标记此 Tree对象为"已使用"

2. 从 forest中选取某一个"未使用"的 Tree对象(后文称为T)，与核心关系图中的结点取交集，标记此 Tree对象为"已使用"。

3. 对于核心关系图中，不在所得交集的结点N，处理方法如下:
> + (a) 选取结点N的父结点 NODE_fc，在T中模糊查找与 NODE_fc相似的结点 NODE_ft。若存在 NODE_ft，则转至步骤(b)；否则判断结点N不在新的核心关系图中。
> + (b) 结点N与 NODE_ft的子孙结点做相似匹配。找出相似度最高的结点 SIM_N。若 SIM_N的相似度大于阈值，则判断结点N存在与新的核心关系图中，转至步骤(c)；否则判断结点N不在新的核心关系图中。
> + (c) 若结点N与结点 SIM_N这两个 url字符串不完全相同，则用符号"*"替换不相同部分

4. 重复步骤(2)(3)，直到所有 forest中的 Tree对象均被遍历一遍，即 forest中无"未使用"的 Tree对象。

##### 1.3.2 相似匹配方法与相似度的计算

对于存在于不同 Tree对象中的结点，判断其url是否相似是个有趣的问题。由于实验数据取自不同设备，某些url可能含有设备特异性信息。

> 例如:
> url1: http://i.mmcdn.cn/simba/img/TB1EAq6JXXXXXcJXpXXSutbFXXX.jpg
> url2: http://i.mmcdn.cn/simba/img/TB1AFwLIFXXXXcoXFXXSutbFXXX.jpg

这类url如果出现在两 Tree对象中相似的父结点下，我们通过如下方法判断 url1和 url2是否相似:

1. 为两 url字符串本身做相似度打分，得到 ratio_url+0.001。

2. 从两 url所在的response响应文本中，获取 url提取处的上下文，为上下文做相似度打分，得到 ratio_context+0.001

3. 将两种相似度相乘，即得到 url1与 url2的相似度ratio = ratio_url × ratio_context

此处的打分方式同样采用衡量两字符串的 Levenshtein距离。

2.处理结果与优化建议
------------

#### 2.1 处理结果

下图展示了三次收集手淘首页生成的核心关系图。数据收集信息如下：

> + 数据收集时间: 2015年8月30日，2015年8月31日
> + 手机设备: 红米手机2A，魅族MX4
> + 手淘状态: 无缓存无登录状态

核心关系图展示如下:

> <img style="width: 100%;" src="/home/albert/Documents/CODE&PROJECT/01.ING/TaoBao/TREE/0&0831_1213www&150830_1920NC.txt_treeplot.dot.svg">

展示的核心关系图过滤掉了response响应文本中出现但未请求的资源，即只显示了已请求的资源，随着用户交互的进行(如用户在手淘首页持续下拉)，核心关系图中的已请求结点数会有所增加。

如图所示，核心关系图中存在大量孤立结点，部分 json文本用于用户信息的传递。部分图片资源应用了webp压缩。

#### 2.2 优化建议

针对所得核心关系图，我们提出以下优化建议：

1. 根据重要程度(如根据图片所在屏幕位置、内容位置)，设置资源优先级，优先级高的先发送[3]。
2. 将优先级较低的资源分组，捆绑打包。如优先级较低的10张图片，可通过将每3张打包发送，利用大资源的速度优势[5]，提高访问速度。
3. 交互信息捆绑，减少协议开销和能效开销，加速传输。

引用
------------

[1] Telerik, FIDDLER. http://www.telerik.com/fiddler

[2] python, fuzzywuzzy. https://github.com/seatgeek/fuzzywuzzy

[3] Butkiewicz M, Wang D, Wu Z, et al. Klotski: Reprioritizing Web Content to Improve User Experience on Mobile Devices[J].

[4] Crussell J, Stevens R, Chen H. MAdFraud: Investigating ad fraud in android applications[C]//Proceedings of the 12th annual international conference on Mobile systems, applications, and services. ACM, 2014: 123-134.

[5] Huang J, Qian F, Guo Y, et al. An in-depth study of LTE: Effect of network protocol and application behavior on performance[C]//ACM SIGCOMM Computer Communication Review. ACM, 2013, 43(4): 363-374.




