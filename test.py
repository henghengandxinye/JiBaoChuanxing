
import time
import os
import pandas as pd
import numpy as np
from itertools import permutations
import Parameters as pa

os.chdir("C:\\Users\恒恒心页\Desktop\JiBaoChuanxing\Table") # 更改工作目录
# print(os.getcwd()) # 打印当前工作目录
start = time.time()

#————————————————————————————————————————————————————————————————————————————————————————————-
print("开始读取输入表格")
#读取输入表格
Flow = pd.read_csv("85中心局之间的集包件及大件的流量流向.csv",encoding = 'gbk')
Distance = pd.read_csv("85中心局之间的距离.csv",encoding = 'UTF-8')
hub_list = pd.read_csv("hub_list.csv",encoding= 'UTF-8')
end = time.time()
print("输入表格读取完毕，总用时：",(end-start))
#————————————————————————————————————————————————————————————————————————————————————————————-
# 得出初始的输出表格
hub_list = list(hub_list['城市名称'])
print(hub_list,len(hub_list))
def link_route(hub_list):
    cost_detail = pd.DataFrame()
    for i in range(0,len(hub_list)):
        for j in range(0,len(hub_list)):
            start = hub_list[i]
            end = hub_list[j]
            own = 0
            truck = np.nan
            cost = 0
            cost_detail = cost_detail.append([[start,end,own,truck,cost]])
    cost_detail = pd.DataFrame(np.array(cost_detail), columns=['收寄城市','寄达城市','是否自有邮路','车辆使用情况','车辆成本'])
    cost = Flow.loc[(Flow['START_HUB'] == '北京') & (Flow['END_HUB'] == '上海')].index.to_list()
    print(cost,type(cost))
    return cost_detail
Cost_detail = link_route(hub_list)
print(Cost_detail)