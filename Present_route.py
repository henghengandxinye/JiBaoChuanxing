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
    return cost_detail
Cost_detail = link_route(hub_list)
print(Cost_detail)
Cost_detail.to_csv("Cost_detail.csv",encoding = 'utf_8_sig')
#————————————————————————————————————————————————————————————————————————————————————————————-
# 计算初始车辆使用情况
# Route = ['北京-上海']
def initial_truck(Route,Flow):
    initial_truck_list =  []
    for i in range(0,pa.GL_MAX + 1):
        for j in range(0,pa.GL_MAX + 1):
            for k in range(0,pa.GL_MAX + 1):
                if i + j + k <= pa.GL_MAX:
                    initial_truck_list.append([i,j,k,i * pa.GL_CAP[2] + j * pa.GL_CAP[1] + k * pa.GL_CAP[0]])
    hub_list = Route.split('-')
    flow = Flow.iloc[Flow.loc[(Flow['START_HUB'] == hub_list[0]) & (Flow['END_HUB'] == hub_list[1])].index.tolist()[0],2]
    final_truck = initial_truck_list[0]
    temp_cap = max([p[3] for p in initial_truck_list])
    temp_truck_num = pa.GL_MAX
    for n in range(len(initial_truck_list)):
        if initial_truck_list[n][3] >= flow:
            if ((initial_truck_list[n][3] <= temp_cap) and (initial_truck_list[n][0] + initial_truck_list[n][1] + initial_truck_list[n][2] <= temp_truck_num)):
                temp_cap = initial_truck_list[n][3]
                temp_truck_num = initial_truck_list[n][0] + initial_truck_list[n][1] + initial_truck_list[n][2]
                final_truck = initial_truck_list[n]
    return final_truck
# Final_truck = initial_truck(Route,Flow,Distance)
#————————————————————————————————————————————————————————————————————————————————————————————-
# 计算车辆成本情况
def initial_cost(Cost_detail,Flow,Distance):
    for i in range(0,Cost_detail.shape[0]):
    # for i in range(0,1):
        print("循环共{0}层，计算已开始，目前循环到{1}层!".format(Cost_detail.shape[0],i+1))
        # 计算每条线路的最终车辆情况（包含满载车辆情况和空载车辆情况）
        # 计算是否为自有邮路
        flow_1 = Flow.iloc[Flow.loc[(Flow['START_HUB'] == Cost_detail.loc[i,"收寄城市"]) & (Flow['END_HUB'] == Cost_detail.loc[i,"寄达城市"])].index.tolist()[0], 2]
        flow_2 = Flow.iloc[Flow.loc[(Flow['START_HUB'] == Cost_detail.loc[i,"寄达城市"]) & (Flow['END_HUB'] == Cost_detail.loc[i,"收寄城市"])].index.tolist()[0], 2]
        own = 1 if (flow_1 >= (pa.GL_CAP[2] * 0.8) and (flow_2 >= pa.GL_CAP[2] * 0.8)) else 0
        route_list = [Cost_detail.loc[i,"收寄城市"] + "-" + Cost_detail.loc[i,"寄达城市"],Cost_detail.loc[i,"寄达城市"] + "-" + Cost_detail.loc[i,"收寄城市"]]
        # print(route_list,len(route_list))
        full_truck_list = []
        empty_truck_list = [0,0,0,0]
        for j in range(0,len(route_list)):
            full_truck_list.append(initial_truck(route_list[j],Flow))
            if j == 1:
                if full_truck_list[j][3] >= full_truck_list[j-1][3]:
                    hub_list = route_list[j-1].split('-')
                    flow = Flow.iloc[Flow.loc[(Flow['START_HUB'] == hub_list[0]) & (Flow['END_HUB'] == hub_list[1])].index.tolist()[0], 2]
                    for m in range(0,full_truck_list[j][0]+1):
                        for n in range(0,full_truck_list[j][1]+1):
                            for p in range(0,full_truck_list[j][2]+1):
                                if m * pa.GL_CAP[2] + n * pa.GL_CAP[1] + p* pa.GL_CAP[0] >= flow:
                                    full_truck_list[j-1] = [m,n,p,m * pa.GL_CAP[2] + n * pa.GL_CAP[1] + p* pa.GL_CAP[0]]
                                    empty_truck_list = [full_truck_list[j][i] - full_truck_list[j-1][i] for i in range(len(full_truck_list[j]))]
                                    empty_truck_list[3] = empty_truck_list[0] * pa.GL_CAP[2] + empty_truck_list[1] * pa.GL_CAP[1] + empty_truck_list[2] * pa.GL_CAP[0]
                                    break
                            else:
                                continue
                            break
                        else:
                            continue
                        break
                    final_truck_list = [full_truck_list[j-1],empty_truck_list]
                else:
                    final_truck_list = [full_truck_list[j-1],[0,0,0,0]]
        # 计算成本
        local_route = route_list[0].split('-')
        distance = Distance.iloc[Distance.loc[(Distance['收寄城市'] == local_route[0]) & (Distance['寄达城市'] == local_route[1])].index.tolist()[0], 2]
        driver_num = 2 if distance >= 400 else 1
        truck_cost = distance * ((final_truck_list[0][0] + final_truck_list[1][0])  * (pa.GL_DEP[2] + pa.GL_LQ[2] + pa.GL_OTHER[2])
                    + (final_truck_list[0][1] + final_truck_list[1][1]) * (pa.GL_DEP[1] + pa.GL_LQ[1] + pa.GL_OTHER[1])
                    + (final_truck_list[0][2] + final_truck_list[1][2]) * (pa.GL_DEP[0] + pa.GL_LQ[0] + pa.GL_OTHER[0]))\
                    + distance * (final_truck_list[0][0] * pa.GL_OIL[2] + final_truck_list[0][1] * pa.GL_OIL[1] + final_truck_list[0][2] * pa.GL_OIL[0])\
                    + distance * (final_truck_list[1][0] * pa.GL_EMP_OIL[2] + final_truck_list[1][1] * pa.GL_EMP_OIL[1] + final_truck_list[1][2] * pa.GL_EMP_OIL[0])\
                    + (distance / pa.GL_V[2] * driver_num * pa.GL_LABOR[2] * (final_truck_list[0][0] + final_truck_list[1][0])) \
                    + (distance / pa.GL_V[1] * driver_num * pa.GL_LABOR[1] * (final_truck_list[0][1] + final_truck_list[1][1])) \
                    + (distance / pa.GL_V[0] * driver_num * pa.GL_LABOR[0] * (final_truck_list[0][2] + final_truck_list[1][2]))
        Cost_detail.loc[i, "是否自有邮路"] = own
        Cost_detail.loc[i, "车辆使用情况"] = "{0}-{1}的邮路使用{2}辆40t满载车,{3}辆20t满载车,{4}辆12t满载车以及{5}辆40t空载车,{6}辆20t空载车,{7}辆12t空载车".format(Cost_detail.iloc[0,0],Cost_detail.iloc[0,1],final_truck_list[0][0],final_truck_list[0][1],final_truck_list[0][2],final_truck_list[1][0],final_truck_list[1][1],final_truck_list[1][2])
        Cost_detail.loc[i, "车辆成本"] = truck_cost * (1 if own == 1 else 1.5)
    # return full_truck_list,empty_truck_list,final_truck_list,driver_num_list,truck_cost,Route_detail
    return Cost_detail

start = time.time()
print("开始计算初始往返路线及成本")
# Full_truck_list,Empty_truck_list,Final_truck_list,Driver_num_list,Truck_cost,Route_detail = initial_cost(Route_detail,Flow,Distance)
Cost_detail = initial_cost(Cost_detail,Flow,Distance)
# print(Full_truck_list,Empty_truck_list,Final_truck_list,Driver_num_list,Truck_cost,Route_detail,sep = '\n')
print(Cost_detail)
Cost_detail.to_csv("Cost_detail_1.csv",encoding = 'utf_8_sig',index = 0)
end = time.time()
print("结果已输出，总用时：",(end-start))

#————————————————————————————————————————————————————————————————————————————————————————————-
