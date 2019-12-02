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
Flow = pd.read_csv("85中心局之间的流量流向（2019年8月快递包裹）.csv",encoding = 'gbk')
Distance = pd.read_csv("85中心局之间的距离.csv",encoding = 'UTF-8')
Hub = pd.read_csv("北京双向邮路中心局.csv",encoding= 'gbk')
end = time.time()
print("输入表格读取完毕，总用时：",(end-start))
#————————————————————————————————————————————————————————————————————————————————————————————-
# 得出初始的输出表格
Start_list = '北京'
End_list = Hub['城市']
# print(End_list,type(End_list))
def link_route(Start_list,End_list):
    route_detail = pd.DataFrame()
    for i in permutations(End_list,2):
        B = Start_list
        M = list(i)[0]
        N = list(i)[1]
        initial_route = [Start_list + '-' + list(i)[0],list(i)[0] + '-' + Start_list,Start_list + '-' + list(i)[1],list(i)[1] + '-' + Start_list]
        chuan_route = Start_list + '-' + list(i)[0] + '-' + list(i)[1] + '-' + Start_list
        initial_truck = np.nan
        chuan_truck = np.nan
        initial_cost = 0
        chuan_cost = 0
        caving_cost = initial_cost - chuan_cost
        route_detail = route_detail.append([[B,M,N,",".join(initial_route),chuan_route,initial_truck,chuan_truck,initial_cost,chuan_cost,caving_cost]])
    route_detail = pd.DataFrame(np.array(route_detail), columns=['中心局B','中心局M','中心局N','初始路线','串行路线','初始车辆使用情况','串行车辆使用情况','初始成本','串行成本','节约成本'])
    return route_detail
Route_detail = link_route(Start_list,End_list)
# print(Route_detail)
# Route_detail.to_csv("Route_detail.csv",encoding = 'utf_8_sig')
#————————————————————————————————————————————————————————————————————————————————————————————-
# 计算初始车辆使用情况
# Route = '北京-上海'
def initial_truck(Route,Flow,Distance):
    initial_truck_list =  []
    for i in range(0,pa.GL_MAX + 1):
        for j in range(0,pa.GL_MAX + 1):
            for k in range(0,pa.GL_MAX + 1):
                if i + j + k <= pa.GL_MAX:
                    initial_truck_list.append([i,j,k,i * pa.GL_CAP[2] + j * pa.GL_CAP[1] + k * pa.GL_CAP[0]])
    hub_list = Route.split('-')
    flow = Flow.iloc[Flow.loc[(Flow['START_HUB'] == hub_list[0]) & (Flow['END_HUB'] == hub_list[1])].index.tolist()[0],2]
    # distance = Distance.iloc[Distance.loc[(Distance['收寄城市'] == hub_list[0]) & (Distance['寄达城市'] == hub_list[1])].index.tolist()[0], 2]
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
# print(initial_truck(Route,Flow,Distance))
# print(Route_detail)
# print(Route_detail.iloc[0,0].split(",")[0],type(Route_detail.iloc[0,0]))
#————————————————————————————————————————————————————————————————————————————————————————————-
# 计算初始车辆成本情况
def initial_cost(Route_detail,Flow,Distance):
    for i in range(0,Route_detail.shape[0]):
    # for i in range(0,1):
        print("循环共{0}层，计算已开始，目前循环到{1}层!".format(Route_detail.shape[0],i))
        # 计算每条线路的最终车辆情况（包含满载车辆情况和空载车辆情况）
        route_list = Route_detail.loc[i,"初始路线"].split(",")
        # print(route_list,len(route_list))
        full_truck_list = []
        empty_truck_list = [[0,0,0,0] for i in range(0,len(route_list))]
        final_truck_list = []
        driver_num_list = []
        truck_cost = 0
        for j in range(0,len(route_list)):
            full_truck_list.append(initial_truck(route_list[j],Flow,Distance))
            if j % 2 == 1:
                if full_truck_list[j][3] >= full_truck_list[j-1][3]:
                    final_truck_list.append(full_truck_list[j])
                    hub_list = route_list[j-1].split('-')
                    flow = Flow.iloc[Flow.loc[(Flow['START_HUB'] == hub_list[0]) & (Flow['END_HUB'] == hub_list[1])].index.tolist()[0], 2]
                    for m in range(0,full_truck_list[j][0]+1):
                        for n in range(0,full_truck_list[j][1]+1):
                            for p in range(0,full_truck_list[j][2]+1):
                                if m * pa.GL_CAP[2] + n * pa.GL_CAP[1] + p* pa.GL_CAP[0] >= flow:
                                    full_truck_list[j-1] = [m,n,p,m * pa.GL_CAP[2] + n * pa.GL_CAP[1] + p* pa.GL_CAP[0]]
                                    empty_truck_list[j-1] = [full_truck_list[j][i] - full_truck_list[j-1][i] for i in range(len(full_truck_list[j]))]
                                    empty_truck_list[j-1][3] = empty_truck_list[j-1][0] * pa.GL_CAP[2] + empty_truck_list[j-1][1] * pa.GL_CAP[1] + empty_truck_list[j-1][2] * pa.GL_CAP[0]
                                    break
                            else:
                                continue
                            break
                        else:
                            continue
                        break
                else:
                    final_truck_list.append(full_truck_list[j-1])
                    hub_list = route_list[j].split('-')
                    flow = Flow.iloc[Flow.loc[(Flow['START_HUB'] == hub_list[0]) & (Flow['END_HUB'] == hub_list[1])].index.tolist()[0], 2]
                    for m in range(0,full_truck_list[j-1][0]+1):
                        for n in range(0,full_truck_list[j-1][1]+1):
                            for p in range(0,full_truck_list[j-1][2]+1):
                                if m * pa.GL_CAP[2] + n * pa.GL_CAP[1] + p* pa.GL_CAP[0] >= flow:
                                    full_truck_list[j] = [m,n,p,m * pa.GL_CAP[2] + n * pa.GL_CAP[1] + p* pa.GL_CAP[0]]
                                    empty_truck_list[j] = [full_truck_list[j-1][i] - full_truck_list[j][i] for i in range(len(full_truck_list[j-1]))]
                                    empty_truck_list[j][3] = empty_truck_list[j][0] * pa.GL_CAP[2] + empty_truck_list[j][1] * pa.GL_CAP[1] + empty_truck_list[j][2] * pa.GL_CAP[0]
                                    break
                            else:
                                continue
                            break
                        else:
                            continue
                        break
        # 计算成本
        for w in range(0, len(route_list)):
            local_route = route_list[w].split('-')
            distance = Distance.iloc[Distance.loc[(Distance['收寄城市'] == local_route[0]) & (Distance['寄达城市'] == local_route[1])].index.tolist()[0], 2]
            driver_num_list.append(2 if distance >= 400 else 1)
            truck_cost += distance * ((full_truck_list[w][0] + empty_truck_list[w][0])  * (pa.GL_DEP[2] + pa.GL_LQ[2] + pa.GL_OTHER[2])
                        + (full_truck_list[w][1] + empty_truck_list[w][1]) * (pa.GL_DEP[1] + pa.GL_LQ[1] + pa.GL_OTHER[1])
                        + (full_truck_list[w][2] + empty_truck_list[w][2]) * (pa.GL_DEP[0] + pa.GL_LQ[0] + pa.GL_OTHER[0]))\
                        + distance * (full_truck_list[w][0] * pa.GL_OIL[2] + full_truck_list[w][1] * pa.GL_OIL[1] + full_truck_list[w][2] * pa.GL_OIL[0])\
                        + distance * (empty_truck_list[w][0] * pa.GL_EMP_OIL[2] + empty_truck_list[w][1] * pa.GL_EMP_OIL[1] + empty_truck_list[w][2] * pa.GL_EMP_OIL[0])\
                        + (distance / pa.GL_V[2] * driver_num_list[w] * pa.GL_LABOR[2] * (full_truck_list[w][0] + empty_truck_list[w][0])) \
                        + (distance / pa.GL_V[1] * driver_num_list[w] * pa.GL_LABOR[1] * (full_truck_list[w][1] + empty_truck_list[w][1])) \
                        + (distance / pa.GL_V[0] * driver_num_list[w] * pa.GL_LABOR[0] * (full_truck_list[w][2] + empty_truck_list[w][2]))
        Route_detail.loc[i, "初始车辆使用情况"] = "{0}-{1}的往返邮路使用{2}辆40t车,{3}辆20t车,{4}辆12t车;\n{5}-{6}的往返邮路使用{7}辆40t车,{8}辆20t车,{9}辆12t车".format(Route_detail.iloc[0,0],Route_detail.iloc[0,1],final_truck_list[0][0],final_truck_list[0][1],final_truck_list[0][2],Route_detail.iloc[0,0],Route_detail.iloc[0,2],final_truck_list[1][0],final_truck_list[1][1],final_truck_list[1][2])
        Route_detail.loc[i, "初始成本"] = truck_cost
    # return full_truck_list,empty_truck_list,final_truck_list,driver_num_list,truck_cost,Route_detail
    return Route_detail

start = time.time()
print("开始计算初始往返路线及成本")
# Full_truck_list,Empty_truck_list,Final_truck_list,Driver_num_list,Truck_cost,Route_detail = initial_cost(Route_detail,Flow,Distance)
Route_detail = initial_cost(Route_detail,Flow,Distance)
# print(Full_truck_list,Empty_truck_list,Final_truck_list,Driver_num_list,Truck_cost,Route_detail,sep = '\n')
print(Route_detail)
# Route_detail.to_csv("Route_detail.csv",encoding = 'utf_8_sig',index = 0)
end = time.time()
print("结果已输出，总用时：",(end-start))

#————————————————————————————————————————————————————————————————————————————————————————————-
# 计算串行车辆初始使用情况
Route = '北京-天津-上海-北京'
def chuan_truck(Route,Flow,Distance):
    hub_list = Route.split("-")
    chuan_truck_list = []
    initial_truck_list = []
    chuan_num_list = []
    for i in range(0, pa.GL_MAX + 1):
        for j in range(0, pa.GL_MAX + 1):
            for k in range(0, pa.GL_MAX + 1):
                if i + j + k <= pa.GL_MAX:
                    initial_truck_list.append([i, j, k, i * pa.GL_CAP[2] + j * pa.GL_CAP[1] + k * pa.GL_CAP[0]])
    for m in range(0,len(hub_list)-1):
        if m == 0:
            flow = Flow.iloc[Flow.loc[(Flow['START_HUB'] == hub_list[m]) & (Flow['END_HUB'] == hub_list[m+1])].index.tolist()[0], 2]\
                    + Flow.iloc[Flow.loc[(Flow['START_HUB'] == hub_list[m]) & (Flow['END_HUB'] == hub_list[m+2])].index.tolist()[0], 2]
        elif m == 1:
            flow = Flow.iloc[Flow.loc[(Flow['START_HUB'] == hub_list[m-1]) & (Flow['END_HUB'] == hub_list[m+1])].index.tolist()[0], 2]\
                    + Flow.iloc[Flow.loc[(Flow['START_HUB'] == hub_list[m]) & (Flow['END_HUB'] == hub_list[m+2])].index.tolist()[0], 2]
        elif m == 2:
            flow = Flow.iloc[Flow.loc[(Flow['START_HUB'] == hub_list[m-1]) & (Flow['END_HUB'] == hub_list[m+1])].index.tolist()[0], 2]\
                    + Flow.iloc[Flow.loc[(Flow['START_HUB'] == hub_list[m]) & (Flow['END_HUB'] == hub_list[m+1])].index.tolist()[0], 2]
        # distance = Distance.iloc[Distance.loc[(Distance['收寄城市'] == hub_list[0]) & (Distance['寄达城市'] == hub_list[1])].index.tolist()[0], 2]
        final_truck = initial_truck_list[0]
        temp_cap = max([p[3] for p in initial_truck_list])
        temp_truck_num = pa.GL_MAX
        for n in range(len(initial_truck_list)):
            if initial_truck_list[n][3] >= flow:
                if ((initial_truck_list[n][3] <= temp_cap) and (initial_truck_list[n][0] + initial_truck_list[n][1] + initial_truck_list[n][2] <= temp_truck_num)):
                    temp_cap = initial_truck_list[n][3]
                    temp_truck_num = initial_truck_list[n][0] + initial_truck_list[n][1] + initial_truck_list[n][2]
                    final_truck = initial_truck_list[n]
        num = flow
        chuan_truck_list.append(final_truck)
        chuan_num_list.append(num)
    return chuan_truck_list,chuan_num_list
Chuan_truck_list,Chuan_num_list = chuan_truck(Route,Flow,Distance)
print(Chuan_truck_list,Chuan_num_list)
#————————————————————————————————————————————————————————————————————————————————————————————-
# 计算串行车辆最终使用情况
# def final_chuan_truck(Route,Flow,Distance):
