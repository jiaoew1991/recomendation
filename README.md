# 推荐模块安装部署文档

## 依赖

1. 系统环境: 建议Linux 2.6以上，Ubuntu、CentOS均可
1. java虚拟机: Java SE 1.7以上
1. 框架PredictionIO: [安装PredictionIO][pio-install],该框架依赖hadoop、spark、elasticsearch、hbase等，具体集群部署方式再研究

## 运行

1. 在装有PredictionIO的机器上运行```$ pio app new {{app_name}}```即创建推荐应用，会生成一个access_key用于导入数据使用。
1. 检查PredictionIO运行状态```$ pio status```，启动PredictionIO事件服务器```$ pio eventserver {{args}}```其中参数可以更改绑定的ip和端口
1. 在项目根目录下运行```$ python client/import_eventserver.py {{args}}```开始从MongoDB中导入数据，其中args一定要填对,尤其是其中的access_key
1. 编译项目```$ pio build```
1. 导入数据成功后训练模型```$ pio train```
1. 部署启动一用```$ pio deploy {{args}}```，参数可以更改绑定的ip、端口、日志位置等以及一些运行spark的参数

## 使用

1. 安装predictionio```$ sudo pip install predictionio```
1. python函数在client/recommender.py及client/data_source.py中，有一个测试用例在client/recommender_test.py中

## 调试

1. 主要是看服务器日志，recommender.py仅为http调用和MongoDB准备数据的简单封装

## 其他

1. 更多详情访问PredictionIO官网: [prediction.io][pio-home]
1. 建议服务每天定时重启重新训练模型，否则不会有新的用户数据被使用
1. 现在算法主要使用的是用户之间的关系数据即A like B, C dislike D的数据来推荐，用户本身的属性几乎没有使用需要更新算法。

[pio-install]: http://docs.prediction.io/install/
[pio-home]: http://prediction.io
