import time
import os
import pandas as pd
import numpy as np
import Procedure_2 as pr
import warnings

os.chdir("C:\\Users\恒恒心页\Desktop\JiBaoChuanxing\Table") # 更改工作目录
# print(os.getcwd()) # 打印当前工作目录
start = time.time()

#————————————————————————————————————————————————————————————————————————————————————————————-
print("开始读取输入表格")

#读取输入表格
# flow_big = pd.read_csv("flow_big.csv",encoding = 'UTF-8')
# flow_jibao = pd.read_csv("flow_jibao.csv",encoding = 'UTF-8')
route = pd.read_csv("route.csv",encoding = 'UTF-8')
hub_list = pd.read_csv("hub_list.csv",encoding = 'UTF-8')
distance = pd.read_csv("85中心局之间的距离.csv",encoding = 'UTF-8')
#print(Route)
end = time.time()
print("输入表格读取完毕，总用时：",(end-start))

# #————————————————————————————————————————————————————————————————————————————————————————————-
# print("计算大件运量及处理量")
# yunliang_big,chuliliang_big = pr.yunliang(flow_big,route,hub_list)
# yunliang_big = pd.DataFrame(np.array(yunliang_big), columns=['收寄城市', '寄达城市', '大件运量'])
# chuliliang_big = pd.DataFrame(np.array(chuliliang_big), columns=['中心局', '大件处理量'])
# yunliang_big.to_csv('yunliang_big.csv',index = 0,encoding = 'utf_8_sig')
# chuliliang_big.to_csv('chuliliang_big.csv',index = 0,encoding = 'utf_8_sig')
# print("大件运量及处理量计算完毕，总用时：",(end-start))
#
# #————————————————————————————————————————————————————————————————————————————————————————————-
# print("计算集包件运量及处理量")
# yunliang_jibao,chuliliang_jibao = pr.yunliang(flow_jibao,route,hub_list)
# yunliang_jibao = pd.DataFrame(np.array(yunliang_jibao), columns=['收寄城市', '寄达城市', '集包件运量'])
# chuliliang_jibao = pd.DataFrame(np.array(chuliliang_jibao), columns=['中心局', '集包件处理量'])
# yunliang_jibao.to_csv('yunliang_jibao.csv',index = 0,encoding = 'utf_8_sig')
# chuliliang_jibao.to_csv('chuliliang_jibao.csv',index = 0,encoding = 'utf_8_sig')
# print("集包件运量及处理量计算完毕，总用时：",(end-start))
#
# #————————————————————————————————————————————————————————————————————————————————————————————-
# print("合并集包件大件运量转换为重量")
# yunliang_big = pd.read_csv("yunliang_big.csv",encoding = 'UTF-8')
# yunliang_jibao = pd.read_csv("yunliang_jibao.csv",encoding = 'UTF-8')
# weight = pr.weight(yunliang_big,yunliang_jibao)
# weight.to_csv('weight.csv',index = 0,encoding = 'utf_8_sig')
# #————————————————————————————————————————————————————————————————————————————————————————————-
# print("打印初始的成本输入表,开始计算初始往返路线及成本")
# weight = pd.read_csv("weight.csv",encoding = 'UTF-8')
# cost_detail = pr.link_route(hub_list)
# cost_detail = pr.transport_cost_1(cost_detail,weight,distance)
# cost_detail.to_csv("cost_detail(尾量空载).csv",index = 0,encoding = 'utf_8_sig')
# print("结果已输出，总用时：",(end-start))
# #————————————————————————————————————————————————————————————————————————————————————————————-
# print("打印初始的成本输入表,开始计算初始往返路线及成本")
# weight = pd.read_csv("weight.csv",encoding = 'UTF-8')
# cost_detail = pr.link_route(hub_list)
# cost_detail = pr.transport_cost_2(cost_detail,weight,distance)
# cost_detail.to_csv("cost_detail(尾量委办,大车优先委办,更新).csv",index = 0,encoding = 'utf_8_sig')
# print("结果已输出，总用时：",(end-start))
#
#
# #————————————————————————————————————————————————————————————————————————————————————————————-
# print("打印初始的成本输入表,开始计算初始往返路线及成本")
# cost_detail_1 = pd.read_csv("cost_detail(尾量空载).csv",encoding = 'UTF-8')
# cost_detail_2 = pd.read_csv("cost_detail(尾量委办).csv",encoding = 'UTF-8')
# cost_detail_final = pr.compare_transport_cost(cost_detail_1,cost_detail_2)
# cost_detail_final.to_csv("cost_detail_final.csv",index = 0,encoding = 'utf_8_sig')
# print("结果已输出，总用时：",(end-start))
#
# #————————————————————————————————————————————————————————————————————————————————————————————-
# print("计算处理成本")
# chuliliang_big = pd.read_csv("chuliliang_big.csv",encoding = 'UTF-8')
# chuliliang_jibao = pd.read_csv("chuliliang_jibao.csv",encoding = 'UTF-8')
# cost_handle = pr.handle_cost(chuliliang_big,chuliliang_jibao)
# cost_handle.to_csv('cost_handle.csv',index = 0,encoding = 'utf_8_sig')
#————————————————————————————————————————————————————————————————————————————————————————————-
print("以成本最低方式计算车型")
weight = pd.read_csv("weight.csv",encoding = 'UTF-8')
trans_cost = pr.transport_cost_3(hub_list, weight, distance)
cost_detail = pr.output(hub_list,trans_cost)
cost_detail.to_csv("cost_detail（小边标记）.csv",encoding = 'utf_8_sig',index = 0)
end = time.time()
print("结果已输出，总用时：",(end-start))