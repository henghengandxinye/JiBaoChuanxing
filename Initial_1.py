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
Route = pd.read_csv("北京双向邮路中心局.csv",encoding= 'gbk')
end = time.time()
print("输入表格读取完毕，总用时：",(end-start))
#————————————————————————————————————————————————————————————————————————————————————————————-

# Start_list = route['起点'][0]
Start_list = '北京'
# End_list = route['中心局名单'][0:85]['经转次数'== 0]
# End_list = np.array(Route).tolist()
End_list = Route['城市']
print(End_list,type(End_list))
# print(Start_list,End_list,Flow)
def truck(Q1,Q2,Q3,Q4,D1,D2,D3,pa):
    # 计算初始车辆数
    # 计算流量
    flow_1 = Q1 + Q2
    flow_2 = Q2 + Q3
    flow_3 = Q3 + Q4
    f_40 = lambda x : (x // pa.GL_CAP[2]) if (x % pa.GL_CAP[2]) <= pa.GL_CAP[1] else (x // pa.GL_CAP[2]) + 1
    f_20 = lambda x : 1 if pa.GL_CAP[0] <= (x % pa.GL_CAP[2]) <= pa.GL_CAP[1] else 0
    f_12 = lambda x : 1 if x % (pa.GL_CAP[2]) <= pa.GL_CAP[0] else 0
    truck_num_1_40 = f_40(flow_1)
    truck_num_1_20 = f_20(flow_1)
    truck_num_1_12 = f_12(flow_1)
    truck_num_2_40 = f_40(flow_2)
    truck_num_2_20 = f_20(flow_2)
    truck_num_2_12 = f_12(flow_2)
    truck_num_3_40 = f_40(flow_3)
    truck_num_3_20 = f_20(flow_3)
    truck_num_3_12 = f_12(flow_3)
    # 计算初始车辆数之和
    truck_num_1 = truck_num_1_12 + truck_num_1_20 + truck_num_1_40
    truck_num_2 = truck_num_2_12 + truck_num_2_20 + truck_num_2_40
    truck_num_3 = truck_num_3_12 + truck_num_3_12 + truck_num_3_40
    truck_num_statistics_1 = [truck_num_1_40, truck_num_1_20, truck_num_1_12]
    truck_num_statistics_2 = [truck_num_2_40, truck_num_2_20, truck_num_2_12]
    truck_num_statistics_3 = [truck_num_3_40, truck_num_3_20, truck_num_3_12]
    # 三段路车辆数相同
    if ((truck_num_1 == truck_num_2) and (truck_num_1 == truck_num_3)):
        # 计算车辆数相等
        truck_num_1_40 = max(truck_num_statistics_1, truck_num_statistics_2, truck_num_statistics_3)[0]
        truck_num_2_40 = truck_num_1_40
        truck_num_3_40 = truck_num_1_40
        truck_num_1_20 = max(truck_num_statistics_1, truck_num_statistics_2, truck_num_statistics_3)[1]
        truck_num_2_20 = truck_num_1_20
        truck_num_3_20 = truck_num_1_20
        truck_num_1_12 = max(truck_num_statistics_1, truck_num_statistics_2, truck_num_statistics_3)[2]
        truck_num_2_12 = truck_num_1_12
        truck_num_3_12 = truck_num_1_12
        truck_num_40 = truck_num_1_40
        truck_num_20 = truck_num_1_20
        truck_num_12 = truck_num_1_12
        # 计算邮路数据
        route_num = 1
        route = []
        l_40 = [truck_num_40 * (D1 + D2 + D3),0]
        l_20 = [truck_num_20 * (D1 + D2 + D3),0]
        l_12 = [truck_num_12 * (D1 + D2 + D3),0]
        driver_num_40 = [2 if ((D1 + D2 + D3)) < 400 else 1 for x in range(0, truck_num_40)]
        driver_num_20 = [2 if ((D1 + D2 + D3)) < 400 else 1 for x in range(0, truck_num_20)]
        driver_num_12 = [2 if ((D1 + D2 + D3)) < 400 else 1 for x in range(0, truck_num_12)]
        driver_time_40 = [(D1 + D2 + D3) / pa.GL_V[2] for x in range(0, truck_num_40)]
        driver_time_20 = [(D1 + D2 + D3) / pa.GL_V[1] for x in range(0, truck_num_20)]
        driver_time_12 = [(D1 + D2 + D3) / pa.GL_V[0] for x in range(0, truck_num_12)]
        own = 1
    # 三段路有两段车辆数相同且均小于第三段路
    elif ((truck_num_1 == truck_num_2) and (truck_num_1 < truck_num_3)):
        # 计算车辆数不等（举例为1，1，2）
        # 车辆外包
        truck_num_1_40 = truck_num_1
        truck_num_2_40 = truck_num_2
        truck_num_3_40 = truck_num_3_40
        truck_num_1_20 = 0
        truck_num_2_20 = 0
        truck_num_3_20 = truck_num_3_20
        truck_num_1_12 = 0
        truck_num_2_12 = 0
        truck_num_3_12 = truck_num_3_12
    elif ((truck_num_1 == truck_num_3) and (truck_num_1 < truck_num_2)):
        # 计算车辆数不等（举例为1，2，1）
        # 车辆外包
        truck_num_1_40 = truck_num_1
        truck_num_3_40 = truck_num_3
        truck_num_2_40 = truck_num_2_40
        truck_num_1_20 = 0
        truck_num_3_20 = 0
        truck_num_2_20 = truck_num_2_20
        truck_num_1_12 = 0
        truck_num_3_12 = 0
        truck_num_2_12 = truck_num_2_12
    elif ((truck_num_2 == truck_num_3) and (truck_num_2 < truck_num_1)):
        # 计算车辆数不等（举例为2，1，1）
        # 车辆外包
        truck_num_2_40 = truck_num_2
        truck_num_3_40 = truck_num_3
        truck_num_1_40 = truck_num_1_40
        truck_num_2_20 = 0
        truck_num_3_20 = 0
        truck_num_1_20 = truck_num_1_20
        truck_num_2_12 = 0
        truck_num_3_12 = 0
        truck_num_1_12 = truck_num_1_12
    # 三段路有两段车辆数相同且均大于第三段路
    elif ((truck_num_1 == truck_num_2) and (truck_num_1 > truck_num_3)):
        # 计算车辆数不等（举例为2，2，1）
        # 车辆外包
        truck_num_3_40_1 = truck_num_3
        truck_num_2_40_1 = max(truck_num_statistics_1, truck_num_statistics_2)[0]
        truck_num_1_40_1 = truck_num_2_40_1
        truck_num_3_20_1 = 0
        truck_num_2_20_1 = max(truck_num_statistics_1, truck_num_statistics_2)[1]
        truck_num_1_20_1 = truck_num_2_20_1
        truck_num_3_12_1 = 0
        truck_num_2_12_1 = max(truck_num_statistics_1, truck_num_statistics_2)[2]
        truck_num_1_12_1 = truck_num_2_12_1
        # 车辆空跑
        truck_num_1_40_2 = max(truck_num_statistics_1, truck_num_statistics_2, truck_num_statistics_3)[0]
        truck_num_2_40_2 = truck_num_1_40_2
        truck_num_3_40_2 = truck_num_1_40_2
        truck_num_1_20_2 = max(truck_num_statistics_1, truck_num_statistics_2, truck_num_statistics_3)[1]
        truck_num_2_40_2 = truck_num_1_20_2
        truck_num_3_40_2 = truck_num_1_20_2
        truck_num_1_12_2 = max(truck_num_statistics_1, truck_num_statistics_2, truck_num_statistics_3)[2]
        truck_num_2_40_2 = truck_num_1_12_2
        truck_num_3_40_2 = truck_num_1_12_2
    elif ((truck_num_2 == truck_num_3) and (truck_num_2 > truck_num_1)):
        # 计算车辆数不等（举例为1，2，2）
        # 车辆外包
        truck_num_1_40_1 = truck_num_1
        truck_num_2_40_1 = max(truck_num_statistics_2, truck_num_statistics_3)[0]
        truck_num_3_40_1 = truck_num_2_40_1
        truck_num_1_20_1 = 0
        truck_num_2_20_1 = max(truck_num_statistics_2, truck_num_statistics_3)[1]
        truck_num_3_20_1 = truck_num_2_20_1
        truck_num_1_12_1 = 0
        truck_num_2_12_1 = max(truck_num_statistics_2, truck_num_statistics_3)[2]
        truck_num_3_12_1 = truck_num_2_12_1
        # 车辆空跑
        truck_num_1_40_2 = max(truck_num_statistics_1, truck_num_statistics_2, truck_num_statistics_3)[0]
        truck_num_2_40_2 = truck_num_1_40_2
        truck_num_3_40_2 = truck_num_1_40_2
        truck_num_1_20_2 = max(truck_num_statistics_1, truck_num_statistics_2, truck_num_statistics_3)[1]
        truck_num_2_40_2 = truck_num_1_20_2
        truck_num_3_40_2 = truck_num_1_20_2
        truck_num_1_12_2 = max(truck_num_statistics_1, truck_num_statistics_2, truck_num_statistics_3)[2]
        truck_num_2_40_2 = truck_num_1_12_2
        truck_num_3_40_2 = truck_num_1_12_2
    elif ((truck_num_1 == truck_num_3) and (truck_num_1 > truck_num_2)):
        # 计算车辆数不等（举例为2，1，2）
        # 车辆外包
        truck_num_2_40_1 = truck_num_1
        truck_num_1_40_1 = max(truck_num_statistics_1, truck_num_statistics_3)[0]
        truck_num_3_40_1 = truck_num_1_40_1
        truck_num_2_20_1 = 0
        truck_num_1_20_1 = max(truck_num_statistics_1, truck_num_statistics_3)[1]
        truck_num_3_20_1 = truck_num_1_20_1
        truck_num_2_12_1 = 0
        truck_num_1_12_1 = max(truck_num_statistics_1, truck_num_statistics_3)[2]
        truck_num_3_12_1 = truck_num_1_12_1
    # 三段路车辆数均不同
    elif ((truck_num_1 < truck_num_2) and (truck_num_2 < truck_num_3)):
        # 计算车辆数不等（举例为1，2，3）
        # 车辆外包
        truck_num_1_40_1 = truck_num_1
        truck_num_2_40_1 = truck_num_2
        truck_num_3_40_1 = truck_num_3_40
        truck_num_1_20_1 = 0
        truck_num_2_20_1 = 0
        truck_num_3_20_1 = truck_num_3_20
        truck_num_1_12_1 = 0
        truck_num_2_12_1 = 0
        truck_num_3_12_1 = truck_num_3_12
        # 车辆空跑
        truck_num_1_40_2 = max(truck_num_statistics_1, truck_num_statistics_2, truck_num_statistics_3)[0]
        truck_num_2_40_2 = truck_num_1_40_2
        truck_num_3_40_2 = truck_num_1_40_2
        truck_num_1_20_2 = max(truck_num_statistics_1, truck_num_statistics_2, truck_num_statistics_3)[1]
        truck_num_2_40_2 = truck_num_1_20_2
        truck_num_3_40_2 = truck_num_1_20_2
        truck_num_1_12_2 = max(truck_num_statistics_1, truck_num_statistics_2, truck_num_statistics_3)[2]
        truck_num_2_40_2 = truck_num_1_12_2
        truck_num_3_40_2 = truck_num_1_12_2
    elif ((truck_num_2 < truck_num_1) and (truck_num_1 < truck_num_3)):
        # 计算车辆数不等（举例为2，1，3）
        # 车辆外包
        truck_num_2_40_1 = truck_num_2
        truck_num_1_40_1 = truck_num_1
        truck_num_3_40_1 = truck_num_3_40
        truck_num_2_20_1 = 0
        truck_num_1_20_1 = 0
        truck_num_3_20_1 = truck_num_3_20
        truck_num_2_12_1 = 0
        truck_num_1_12_1 = 0
        truck_num_3_12_1 = truck_num_3_12
        # 车辆空跑
        truck_num_1_40_2 = max(truck_num_statistics_1, truck_num_statistics_2, truck_num_statistics_3)[0]
        truck_num_2_40_2 = truck_num_1_40_2
        truck_num_3_40_2 = truck_num_1_40_2
        truck_num_1_20_2 = max(truck_num_statistics_1, truck_num_statistics_2, truck_num_statistics_3)[1]
        truck_num_2_40_2 = truck_num_1_20_2
        truck_num_3_40_2 = truck_num_1_20_2
        truck_num_1_12_2 = max(truck_num_statistics_1, truck_num_statistics_2, truck_num_statistics_3)[2]
        truck_num_2_40_2 = truck_num_1_12_2
        truck_num_3_40_2 = truck_num_1_12_2
    elif ((truck_num_1 < truck_num_3) and (truck_num_3 < truck_num_2)):
        # 计算车辆数不等（举例为1，3，2）
        # 车辆外包
        truck_num_1_40_1 = truck_num_1
        truck_num_3_40_1 = truck_num_3
        truck_num_2_40_1 = truck_num_2_40
        truck_num_1_40_1 = 0
        truck_num_3_20_1 = 0
        truck_num_2_20_1 = truck_num_2_20
        truck_num_1_12_1 = 0
        truck_num_3_12_1 = 0
        truck_num_2_12_1 = truck_num_2_12
        # 车辆空跑
        truck_num_1_40_2 = max(truck_num_statistics_1, truck_num_statistics_2, truck_num_statistics_3)[0]
        truck_num_2_40_2 = truck_num_1_40_2
        truck_num_3_40_2 = truck_num_1_40_2
        truck_num_1_20_2 = max(truck_num_statistics_1, truck_num_statistics_2, truck_num_statistics_3)[1]
        truck_num_2_40_2 = truck_num_1_20_2
        truck_num_3_40_2 = truck_num_1_20_2
        truck_num_1_12_2 = max(truck_num_statistics_1, truck_num_statistics_2, truck_num_statistics_3)[2]
        truck_num_2_40_2 = truck_num_1_12_2
        truck_num_3_40_2 = truck_num_1_12_2
    elif ((truck_num_3 < truck_num_1) and (truck_num_1 < truck_num_2)):
        # 计算车辆数不等（举例为2，3，1）
        # 车辆外包
        truck_num_3_40_1 = truck_num_3
        truck_num_1_40_1 = truck_num_1
        truck_num_2_40_1 = truck_num_2_40
        truck_num_3_40_1 = 0
        truck_num_1_20_1 = 0
        truck_num_2_20_1 = truck_num_2_20
        truck_num_3_12_1 = 0
        truck_num_1_12_1 = 0
        truck_num_2_12_1 = truck_num_2_12
        # 车辆空跑
        truck_num_1_40_2 = max(truck_num_statistics_1, truck_num_statistics_2, truck_num_statistics_3)[0]
        truck_num_2_40_2 = truck_num_1_40_2
        truck_num_3_40_2 = truck_num_1_40_2
        truck_num_1_20_2 = max(truck_num_statistics_1, truck_num_statistics_2, truck_num_statistics_3)[1]
        truck_num_2_40_2 = truck_num_1_20_2
        truck_num_3_40_2 = truck_num_1_20_2
        truck_num_1_12_2 = max(truck_num_statistics_1, truck_num_statistics_2, truck_num_statistics_3)[2]
        truck_num_2_40_2 = truck_num_1_12_2
        truck_num_3_40_2 = truck_num_1_12_2
    elif ((truck_num_2 < truck_num_3) and (truck_num_3 < truck_num_1)):
        # 计算车辆数不等（举例为3，1，2）
        # 车辆外包
        truck_num_2_40_1 = truck_num_2
        truck_num_3_40_1 = truck_num_3
        truck_num_1_40_1 = truck_num_1_40
        truck_num_2_40_1 = 0
        truck_num_3_20_1 = 0
        truck_num_1_20_1 = truck_num_1_20
        truck_num_2_12_1 = 0
        truck_num_3_12_1 = 0
        truck_num_1_12_1 = truck_num_1_12
        # 车辆空跑
        truck_num_1_40_2 = max(truck_num_statistics_1, truck_num_statistics_2, truck_num_statistics_3)[0]
        truck_num_2_40_2 = truck_num_1_40_2
        truck_num_3_40_2 = truck_num_1_40_2
        truck_num_1_20_2 = max(truck_num_statistics_1, truck_num_statistics_2, truck_num_statistics_3)[1]
        truck_num_2_40_2 = truck_num_1_20_2
        truck_num_3_40_2 = truck_num_1_20_2
        truck_num_1_12_2 = max(truck_num_statistics_1, truck_num_statistics_2, truck_num_statistics_3)[2]
        truck_num_2_40_2 = truck_num_1_12_2
        truck_num_3_40_2 = truck_num_1_12_2
    elif ((truck_num_3 < truck_num_2) and (truck_num_2 < truck_num_1)):
        # 计算车辆数不等（举例为3，2，1）
        # 车辆外包
        truck_num_1_40_1 = truck_num_1
        truck_num_2_40_1 = truck_num_2
        truck_num_3_40_1 = truck_num_3_40
        truck_num_1_40_1 = 0
        truck_num_2_20_1 = 0
        truck_num_3_20_1 = truck_num_3_20
        truck_num_1_12_1 = 0
        truck_num_2_12_1 = 0
        truck_num_3_12_1 = truck_num_3_12
        # 车辆空跑
        truck_num_1_40_2 = max(truck_num_statistics_1, truck_num_statistics_2, truck_num_statistics_3)[0]
        truck_num_2_40_2 = truck_num_1_40_2
        truck_num_3_40_2 = truck_num_1_40_2
        truck_num_1_20_2 = max(truck_num_statistics_1, truck_num_statistics_2, truck_num_statistics_3)[1]
        truck_num_2_40_2 = truck_num_1_20_2
        truck_num_3_40_2 = truck_num_1_20_2
        truck_num_1_12_2 = max(truck_num_statistics_1, truck_num_statistics_2, truck_num_statistics_3)[2]
        truck_num_2_40_2 = truck_num_1_12_2
        truck_num_3_40_2 = truck_num_1_12_2
def link_route(Start_list,End_list):
    Route_detail = pd.DataFrame()
    for i in permutations(End_list,2):
        route = [Start_list,list(i)[0],list(i)[1],Start_list]
        Cost_saving = 0
        Route_detail = Route_detail.append([[route,Cost_saving]])
    Route_detail.columns.name = ['路线', '节约的成本']
    print(Route_detail)
    return Route_detail
Route_detail = link_route(Start_list,End_list)
# Route_detail.to_csv("Route_detail.csv",encoding = 'utf_8_sig')