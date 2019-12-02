import pandas as pd
import numpy as np
import Parameters as pa
import math

#运量及处理量计算函数
def yunliang(flow,route,hub_list):
    '''
    :param flow: 流量表
    :param route: 路由表
    :param prohub_list: 城市信息清单
    :return: 运量表+处理量表
    '''
    hub_num = 85
    hubs = hub_list['城市名称']   #提取85个中心局
    hubs = list(hubs)     #列表化
    yunliang_matrix =  [[0 for col in range(hub_num)] for row in range(hub_num)]  #初始化运量矩阵
    yunliang = pd.DataFrame()    #初始化运量表
    chuliliang_list = [0] * hub_num        #初始化处理量列表
    chuliliang = pd.DataFrame()    #初始化处理量表

    route_row = route.shape[0]    #统计路由行数
    for i in range(0,route_row):
        print(i)
        # flow_temp = flow[flow.收寄城市 == route.iloc[i, 0]]   #flow表中筛选收寄城市
        # flow_temp = flow_temp[flow_temp.寄达城市 == route.iloc[i, 1]]   #flow表中筛选寄达城市
        # flow_value = flow_temp.iloc[0,2]   #筛选后提取flow表中的流量值

        flow_value = float(flow.loc[(flow['收寄城市'] == route.iloc[i,0]) & (flow['寄达城市'] == route.iloc[i,1])]['运量（重量）'])

        cflist = route.iloc[i,3].split('-')   #将路由按‘-’拆分为数组
        cflist_length = len(cflist)   #统计该数组长度
        for j in range(0,cflist_length-1):
            yunliang_matrix[hubs.index(cflist[j])][hubs.index(cflist[j+1])] += flow_value   #从0-倒数第二个元素，逐一添加城市对的运量
            chuliliang_list[hubs.index(cflist[j])] += flow_value #从0-倒数第二个元素，逐一添加城市的处理量

        chuliliang_list[hubs.index(cflist[cflist_length-1])] += flow_value  #循环结束，补充添加最后一个元素城市的处理量

    for i in range(0,hub_num):
        temp_tongcheng = flow[flow.收寄城市 == hubs[i]]     #筛选同城处理量
        temp_tongcheng = temp_tongcheng[temp_tongcheng.寄达城市 == hubs[i]]   #筛选同城处理量
        if(temp_tongcheng.shape[0]!=0):
            chuliliang_list[i] += temp_tongcheng.iloc[0,2]    #添加同城处理量

        chuliliang = chuliliang.append([[hubs[i],chuliliang_list[i]]])
        for j in range(0,hub_num):
            yunliang = yunliang.append([[hubs[i],hubs[j],yunliang_matrix[i][j]]])
    return yunliang, chuliliang

#集包件与大件运量的总重量计算
def weight(yunliang_big,yunliang_jibao):
    '''
    
    :param yunliang_big: 大件运量
    :param yunliang_jibao: 集包件运量
    :return: 总运量（重量）表
    '''
    weight = pd.merge(yunliang_big,yunliang_jibao,how = 'outer', on = ['收寄城市','寄达城市'])
    weight.replace(np.nan,0,inplace = True)
    weight['运量（重量）'] = weight.apply(lambda x: (pa.GL_PERW[0]*x.大件运量 + pa.GL_PERW[1]*x.集包件运量),axis = 1 )
    weight.drop(columns = ['大件运量','集包件运量'],inplace = True)

    return weight

#计算各种车型组合清单
def truck_list(MAX):
    '''
    
    :param MAX: 最大车辆数
    :return: 各种车型组合清单
    '''
    initial_truck_list = []
    for i in range(0, MAX + 1):
        for j in range(0, MAX + 1):
            for k in range(0, MAX + 1):
                if i + j + k <= MAX:
                    initial_truck_list.append([i, j, k, i * pa.GL_CAP[2] + j * pa.GL_CAP[1] + k * pa.GL_CAP[0]])
    return initial_truck_list

def initial_truck(initial_truck_list, flow):
    '''
    
    :param initial_truck_list: 各种车型组合清单
    :param flow: 运量
    :return: 初始车辆使用情况
    '''
    final_truck = initial_truck_list[0]   #初始化车辆使用为[0,0,0]
    temp_cap = max([p[3] for p in initial_truck_list])   #初始化当前装载量为最大值
    temp_truck_num = pa.GL_MAX   #初始化当前车辆数为最大值

    for n in range(len(initial_truck_list)):   #循环所有车辆组合
        if ((initial_truck_list[n][3] >= flow) and (initial_truck_list[n][3] <= temp_cap) and (initial_truck_list[n][0] + initial_truck_list[n][1] + initial_truck_list[n][2] <= temp_truck_num)):    #若该车辆组合装载量大于等于运量,且该组合装载量小于等于当前装载量，且该组合车辆数小于等于当前车辆数
            temp_cap = initial_truck_list[n][3]
            #更新当前装载量为该组合装载量
            temp_truck_num = initial_truck_list[n][0] + initial_truck_list[n][1] + initial_truck_list[n][2]           #更新当前车辆数为该组合车辆数
            final_truck = [initial_truck_list[n][0],initial_truck_list[n][1],initial_truck_list[n][2]]
            #更新车辆使用为该组合

    return final_truck

# 得出初始的输出表格
def link_route(hub_list):
    '''
    
    :param hub_list: 中心局清单
    :return: 车辆成本空表，包含列'收寄城市', '寄达城市', '车辆使用情况', '车辆成本'（只添加前两列）
    '''
    hub_list = list(hub_list['城市名称'])

    cost_detail = pd.DataFrame()
    for i in range(0, len(hub_list)):
        for j in range(0, len(hub_list)):
            start = hub_list[i]
            end = hub_list[j]
            truck = np.nan
            cost = np.nan
            cost_detail = cost_detail.append([[start, end, truck, cost]])
    cost_detail = pd.DataFrame(np.array(cost_detail), columns=['收寄城市', '寄达城市', '车辆使用情况', '车辆成本'])
    return cost_detail

#尾量空载情况运输成本计算公式
def transport_1(final_truck_list,temp_distance,driver_num):
    '''
    
    :param final_truck_list: 车辆使用情况（满载，空载两个list）
    :param temp_distance: 路线之间的距离
    :param driver_num: 司机数
    :return: 单条线路运输成本
    '''
    # 计算成本
    truck_cost = temp_distance * ((final_truck_list[0][0] + final_truck_list[1][0]) * (pa.GL_DEP[2] + pa.GL_LQ[2] + pa.GL_OTHER[2]) + (final_truck_list[0][1] + final_truck_list[1][1]) * (pa.GL_DEP[1] + pa.GL_LQ[1] + pa.GL_OTHER[1])+ (final_truck_list[0][2] + final_truck_list[1][2]) * (pa.GL_DEP[0] + pa.GL_LQ[0] + pa.GL_OTHER[0])) + \
                 temp_distance * (final_truck_list[0][0] * pa.GL_OIL[2] + final_truck_list[0][1] * pa.GL_OIL[1] + final_truck_list[0][2] * pa.GL_OIL[0]) + \
                 temp_distance * (final_truck_list[1][0] * pa.GL_EMP_OIL[2] + final_truck_list[1][1] * pa.GL_EMP_OIL[1] +final_truck_list[1][2] * pa.GL_EMP_OIL[0]) + \
                 (round(temp_distance / pa.GL_V[2], 6) * driver_num * pa.GL_LABOR[2] * (final_truck_list[0][0] + final_truck_list[1][0])) + (round(temp_distance / pa.GL_V[1], 6) * driver_num * pa.GL_LABOR[1] * (final_truck_list[0][1] + final_truck_list[1][1])) + (round(temp_distance / pa.GL_V[0], 6) * driver_num * pa.GL_LABOR[0] * (final_truck_list[0][2] + final_truck_list[1][2]))
                #折旧+路桥+其他费用+
                #满载车油耗费用+
                #空载车油耗费用+
                #司机费用

    return truck_cost

# 计算尾量空载情况车辆成本
def transport_cost_1(cost_detail, weight, distance):
    '''
    
    :param cost_detail: 初始化车辆成本表
    :param weight: 运量（重量）表
    :param distance: 距离表
    :return: 最终成本表（尾量空载）
    '''
    initial_truck_list = truck_list(pa.GL_MAX)   #计算车辆组合清单

    for i in range(0, cost_detail.shape[0]):    #循环初始化表中的每一行

        print("共{0}层，目前循环到{1}层!".format(cost_detail.shape[0], i + 1))

        route_list = [[cost_detail.loc[i, "收寄城市"] ,  cost_detail.loc[i, "寄达城市"]],
                      [cost_detail.loc[i, "寄达城市"] ,  cost_detail.loc[i, "收寄城市"]]]

        # 线路清单 [[起，终],[终，起]]
        flow = [0,0]
        full_truck_list = []
        empty_truck_list = [0, 0, 0, 0]

        for j in range(0, len(route_list)):

            flow[j] = weight.iloc[weight.loc[(weight['收寄城市'] == route_list[j][0]) & (weight['寄达城市'] == route_list[j][1])].index.tolist()[0], 2]
            # 查询该行起-终和终-起的运量（重量）并赋给flow
            full_truck_list.append(initial_truck(initial_truck_list,flow[j]))
            # 计算起-终和终-起的初始车辆使用情况
            if j == 1: #如果起-终和终-起的初始车辆使用情况均计算完毕
                if full_truck_list[j][3] >= full_truck_list[j - 1][3]:
                #如果起-终使用的车型组合载重更小，则进入下列循环进行车辆更新
                    for m in range(0, full_truck_list[j][0] + 1):
                        for n in range(0, full_truck_list[j][1] + 1):
                            for p in range(0, full_truck_list[j][2] + 1):
                                if (m * pa.GL_CAP[2] + n * pa.GL_CAP[1] + p * pa.GL_CAP[0]) >= flow[j-1]:
                                    full_truck_list[j - 1] = [m, n, p, m * pa.GL_CAP[2] + n * pa.GL_CAP[1] + p * pa.GL_CAP[0]]
                                    empty_truck_list = [full_truck_list[j][i] - full_truck_list[j - 1][i] for i in range(len(full_truck_list[j]))]
                                    empty_truck_list[3] = empty_truck_list[0] * pa.GL_CAP[2] + empty_truck_list[1] * pa.GL_CAP[1] + empty_truck_list[2] * pa.GL_CAP[0]
                                    break
                            else:
                                continue
                            break
                        else:
                            continue
                        break
                    final_truck_list = [full_truck_list[j - 1], empty_truck_list]
                else:
                # 如果起-终使用的车型组合载重更大，则该条线路无需更新车辆使用情况
                    final_truck_list = [full_truck_list[j - 1], [0, 0, 0, 0]]
                #计算成本
        temp_distance = distance.iloc[distance.loc[(distance['收寄城市'] == route_list[0][0]) & (distance['寄达城市'] == route_list[0][1])].index.tolist()[0], 2]  # 查询距离
        driver_num = 2 if temp_distance >= pa.GL_DSP else 1  #司机数量
        truck_cost = transport_1(final_truck_list, temp_distance, driver_num)
        cost_detail.loc[i, "车辆使用情况"] = "{0}-{1}的邮路使用{2}辆40t满载车,{3}辆20t满载车,{4}辆12t满载车以及{5}辆40t空载车,{6}辆20t空载车,{7}辆12t空载车".format(cost_detail.iloc[i, 0], cost_detail.iloc[i, 1], final_truck_list[0][0], final_truck_list[0][1],final_truck_list[0][2], final_truck_list[1][0], final_truck_list[1][1], final_truck_list[1][2])
        cost_detail.loc[i, "车辆成本"] = truck_cost

    return cost_detail

# 计算单条线路运输成本（尾量委办）
def transport_2(final_truck_list,temp_distance,driver_num):
    truck_cost_1= temp_distance * ((final_truck_list[0][0]) * (pa.GL_DEP[2] + pa.GL_LQ[2] + pa.GL_OTHER[2])+ (final_truck_list[0][1]) * (pa.GL_DEP[1] + pa.GL_LQ[1] + pa.GL_OTHER[1]) + (final_truck_list[0][2]) * (pa.GL_DEP[0] + pa.GL_LQ[0] + pa.GL_OTHER[0])) + \
                  temp_distance * (final_truck_list[0][0] * pa.GL_OIL[2] + final_truck_list[0][1] * pa.GL_OIL[1] + final_truck_list[0][2] *pa.GL_OIL[0]) + \
                  (temp_distance / pa.GL_V[2] * driver_num * pa.GL_LABOR[2] * final_truck_list[0][0]) + \
                  (temp_distance / pa.GL_V[1] * driver_num * pa.GL_LABOR[1] * final_truck_list[0][1]) + \
                  (temp_distance / pa.GL_V[0] * driver_num * pa.GL_LABOR[0] * final_truck_list[0][2])

    #自办邮路运输成本 = 折旧+路桥+其他费用+
                 #油耗费用+
                 #司机费用
    truck_cost_2 = temp_distance * ((final_truck_list[1][0]) * (pa.GL_DEP[2] + pa.GL_LQ[2] + pa.GL_OTHER[2]) * pa.GL_K[0]+ (final_truck_list[1][1]) * (pa.GL_DEP[1] + pa.GL_LQ[1] + pa.GL_OTHER[1]) * pa.GL_K[1]+ (final_truck_list[1][2]) * (pa.GL_DEP[0] + pa.GL_LQ[0] + pa.GL_OTHER[0]) * pa.GL_K[2]) + \
                   temp_distance * (final_truck_list[1][0] * pa.GL_OIL[2] * pa.GL_K[0] + final_truck_list[1][1] * pa.GL_OIL[1] * pa.GL_K[1] + final_truck_list[1][2] * pa.GL_OIL[0]) * pa.GL_K[2] + \
                   (temp_distance / pa.GL_V[2] * driver_num * pa.GL_LABOR[2] * final_truck_list[1][0] * pa.GL_K[0]) + \
                   (temp_distance / pa.GL_V[1] * driver_num * pa.GL_LABOR[1] * final_truck_list[1][1] * pa.GL_K[1]) + \
                   (temp_distance / pa.GL_V[0] * driver_num * pa.GL_LABOR[0] * final_truck_list[1][2] * pa.GL_K[2])
    #委办邮路运输成本 = 折旧+路桥+其他费用+
                 #油耗费用+
                 #司机费用（各类车型分别乘对应系数）
    truck_cost = truck_cost_1 + truck_cost_2
    return  truck_cost

# 计算车辆成本情况（尾量委办）
def transport_cost_2(cost_detail, weight, distance):
    '''

    :param cost_detail: 初始化车辆成本表
    :param weight: 运量（重量）表
    :param distance: 距离表
    :return: 最终成本表（尾量空载）
    '''
    initial_truck_list = truck_list(pa.GL_MAX)  # 计算车辆组合清单
    for i in range(0, cost_detail.shape[0]):  # 循环初始化表中的每一行

        print("共{0}层，目前循环到{1}层!".format(cost_detail.shape[0], i + 1))

        route_list = [[cost_detail.loc[i, "收寄城市"], cost_detail.loc[i, "寄达城市"]],
                      [cost_detail.loc[i, "寄达城市"], cost_detail.loc[i, "收寄城市"]]]
        # 线路清单 [[起，终],[终，起]]
        flow = [0,0]
        ziban_truck_list = []
        weiban_truck_list = [0, 0, 0, 0]
        for j in range(0, len(route_list)):
            flow[j] = weight.iloc[weight.loc[(weight['收寄城市'] == route_list[j][0]) & (weight['寄达城市'] == route_list[j][1])].index.tolist()[0], 2]
            # 查询该行起-终和终-起的运量（重量）并赋给flow
            ziban_truck_list.append(initial_truck(initial_truck_list, flow[j]))
            # 计算起-终和终-起的初始车辆使用情况
            if j == 1:
                if ziban_truck_list[j][3] <= ziban_truck_list[j - 1][3]:
                    for p in range(0, ziban_truck_list[j-1][2] + 1):
                        for n in range(0, ziban_truck_list[j-1][1] + 1):
                            for m in range(0, ziban_truck_list[j-1][0] + 1):
                                if m * pa.GL_CAP[2] + n * pa.GL_CAP[1] + p * pa.GL_CAP[0] >= flow[j]:
                                    ziban_truck_list[j] = [m, n, p,m * pa.GL_CAP[2] + n * pa.GL_CAP[1] + p * pa.GL_CAP[0]]
                                    weiban_truck_list = [ziban_truck_list[j-1][i] - ziban_truck_list[j][i] for i in range(len(ziban_truck_list[j-1]))]
                                    weiban_truck_list[3] = weiban_truck_list[0] * pa.GL_CAP[2] + weiban_truck_list[1] * pa.GL_CAP[1] + weiban_truck_list[2] * pa.GL_CAP[0]
                                    break
                            else:
                                continue
                            break
                        else:
                            continue
                        break
                    final_truck_list = [ziban_truck_list[j], weiban_truck_list]
                else:

                    for p in range(0, ziban_truck_list[j][2] + 1):
                        for n in range(0, ziban_truck_list[j][1] + 1):
                            for m in range(0, ziban_truck_list[j][0] + 1):
                                if m * pa.GL_CAP[2] + n * pa.GL_CAP[1] + p * pa.GL_CAP[0] >= flow[j-1]:
                                    ziban_truck_list[j-1] = [m, n, p,m * pa.GL_CAP[2] + n * pa.GL_CAP[1] + p * pa.GL_CAP[0]]
                                    break
                            else:
                                continue
                            break
                        else:
                            continue
                        break
                    final_truck_list = [ziban_truck_list[j-1], [0, 0,  0,0]]

            # 计算成本

        temp_distance = distance.iloc[distance.loc[(distance['收寄城市'] == route_list[0][0]) & (distance['寄达城市'] == route_list[0][1])].index.tolist()[0], 2]    #查询距离
        driver_num = 2 if temp_distance >= 400 else 1    #司机数量
        truck_cost = transport_2(final_truck_list, temp_distance, driver_num)   #计算单条线路运输成本
        cost_detail.loc[i, "车辆使用情况"] = "{0}-{1}的邮路使用{2}辆40t自办车,{3}辆20t自办车,{4}辆12t自办车以及{5}辆40t委办车,{6}辆20t委办车,{7}辆12t委办车".format(cost_detail.iloc[i, 0], cost_detail.iloc[i, 1], final_truck_list[0][0], final_truck_list[0][1],final_truck_list[0][2], final_truck_list[1][0], final_truck_list[1][1], final_truck_list[1][2])
        cost_detail.loc[i, "车辆成本"] = truck_cost
    return cost_detail

# 比较空载和委办车辆运输成本
def compare_transport_cost(cost_detail_1,cost_detail_2):
    cost_detail_final = pd.merge(cost_detail_1,cost_detail_2,how = 'outer',on = ['收寄城市','寄达城市'])  #全连接
    cost_detail_final['车辆使用情况'] = np.nan  #添列
    cost_detail_final['车辆成本'] = np.nan  #添列
    for i in range(0,cost_detail_final.shape[0]):
        print('共{0}层，目前到第{1}层'.format(cost_detail_final.shape[0],i+1))
        temp_cost_detail_1 = cost_detail_final[cost_detail_final.收寄城市 == cost_detail_final.loc[i,'寄达城市'] ]
        temp_cost_detail = temp_cost_detail_1[temp_cost_detail_1.寄达城市 == cost_detail_final.loc[i,'收寄城市']]

        temp_cost_detail.reset_index(inplace = True)

        temp_cost_x = temp_cost_detail.loc[0, '车辆成本_x']
        temp_cost_y = temp_cost_detail.loc[0, '车辆成本_y']


        if (int(cost_detail_final.loc[i,'车辆成本_x']) + int(temp_cost_x )) >= (int(cost_detail_final.loc[i,'车辆成本_y']) + int( temp_cost_y )):

            cost_detail_final.loc[i, '车辆使用情况'] = cost_detail_final.loc[i, '车辆使用情况_y']
            cost_detail_final.loc[i, '车辆成本'] = cost_detail_final.loc[i, '车辆成本_y']
        else:

            cost_detail_final.loc[i, '车辆使用情况'] = cost_detail_final.loc[i, '车辆使用情况_x']
            cost_detail_final.loc[i, '车辆成本'] = cost_detail_final.loc[i, '车辆成本_x']
    cost_detail_final.drop(columns = ['车辆使用情况_x','车辆成本_x','车辆使用情况_y','车辆成本_y'],inplace = True)

    return cost_detail_final

#处理成本计算
def handle_cost(chuliliang_big,chuliliang_jibao):
    cost_handle = pd.merge(chuliliang_big,chuliliang_jibao,how = 'outer', on = ['中心局'])
    cost_handle.replace(np.nan,0,inplace = True)
    cost_handle['处理成本'] = cost_handle.apply(lambda x: (pa.GL_HANDLEC[0]*x.大件处理量 + pa.GL_HANDLEC[1]*x.集包件处理量),axis = 1 )


    cost_handle.drop(columns = ['大件处理量','集包件处理量'],inplace = True)

    return cost_handle

#以成本最低原则确定车型
# 计算单条线路运输成本（尾量委办）
def transport_3(final_truck_list,distance_1,distance_2,driver_num_1,driver_num_2):
    #自办邮路运输成本 = 折旧+路桥+其他费用+
                 #油耗费用+
                 #司机费用
    temp_distance = distance_1 + distance_2
    driver_num = max(driver_num_1,driver_num_2)
    truck_cost_1= temp_distance * ((final_truck_list[2][0]) * (pa.GL_DEP[2] + pa.GL_LQ[2] + pa.GL_OTHER[2])+ (final_truck_list[2][1]) * (pa.GL_DEP[1] + pa.GL_LQ[1] + pa.GL_OTHER[1]) + (final_truck_list[2][2]) * (pa.GL_DEP[0] + pa.GL_LQ[0] + pa.GL_OTHER[0])) + \
                  temp_distance * (final_truck_list[2][0] * pa.GL_OIL[2] + final_truck_list[2][1] * pa.GL_OIL[1] + final_truck_list[2][2] *pa.GL_OIL[0]) + \
                  ((temp_distance / pa.GL_V[2]) * driver_num * pa.GL_LABOR[2] * final_truck_list[2][0]) + \
                  ((temp_distance / pa.GL_V[1]) * driver_num * pa.GL_LABOR[1] * final_truck_list[2][1]) + \
                  ((temp_distance / pa.GL_V[0]) * driver_num * pa.GL_LABOR[0] * final_truck_list[2][2])
    #去边运量委办邮路运输成本 = 折旧+路桥+其他费用+
                 #油耗费用+
                 #司机费用（各类车型分别乘对应系数）
    truck_cost_2 = distance_1 * ((final_truck_list[0][0]) * (pa.GL_DEP[2] + pa.GL_LQ[2] + pa.GL_OTHER[2]) * pa.GL_K[0]+ (final_truck_list[0][1]) * (pa.GL_DEP[1] + pa.GL_LQ[1] + pa.GL_OTHER[1]) * pa.GL_K[1]+ (final_truck_list[0][2]) * (pa.GL_DEP[0] + pa.GL_LQ[0] + pa.GL_OTHER[0]) * pa.GL_K[2]) + \
                   distance_1 * (final_truck_list[0][0] * pa.GL_OIL[2] * pa.GL_K[0] + final_truck_list[0][1] * pa.GL_OIL[1] * pa.GL_K[1] + final_truck_list[0][2] * pa.GL_OIL[0]) * pa.GL_K[2] + \
                   ((distance_1 / pa.GL_V[2]) * driver_num_1 * pa.GL_LABOR[2] * final_truck_list[0][0] * pa.GL_K[0]) + \
                   ((distance_1 / pa.GL_V[1]) * driver_num_1 * pa.GL_LABOR[1] * final_truck_list[0][1] * pa.GL_K[1]) + \
                   ((distance_1 / pa.GL_V[0]) * driver_num_1 * pa.GL_LABOR[0] * final_truck_list[0][2] * pa.GL_K[2])
    #回边运量委办邮路运输成本 = 折旧+路桥+其他费用+
                 #油耗费用+
                 #司机费用（各类车型分别乘对应系数）
    truck_cost_3 = distance_2 * ((final_truck_list[1][0]) * (pa.GL_DEP[2] + pa.GL_LQ[2] + pa.GL_OTHER[2]) * pa.GL_K[0]+ (final_truck_list[1][1]) * (pa.GL_DEP[1] + pa.GL_LQ[1] + pa.GL_OTHER[1]) * pa.GL_K[1]+ (final_truck_list[1][2]) * (pa.GL_DEP[0] + pa.GL_LQ[0] + pa.GL_OTHER[0]) * pa.GL_K[2]) + \
                   distance_2 * (final_truck_list[1][0] * pa.GL_OIL[2] * pa.GL_K[0] + final_truck_list[1][1] * pa.GL_OIL[1] * pa.GL_K[1] + final_truck_list[1][2] * pa.GL_OIL[0]) * pa.GL_K[2] + \
                   ((distance_2 / pa.GL_V[2]) * driver_num_2 * pa.GL_LABOR[2] * final_truck_list[1][0] * pa.GL_K[0]) + \
                   ((distance_2 / pa.GL_V[1]) * driver_num_2 * pa.GL_LABOR[1] * final_truck_list[1][1] * pa.GL_K[1]) + \
                   ((distance_2 / pa.GL_V[0]) * driver_num_2 * pa.GL_LABOR[0] * final_truck_list[1][2] * pa.GL_K[2])
    truck_cost = truck_cost_1 + truck_cost_2 + truck_cost_3
    return  truck_cost

def transport_cost_3(hub_list, weight, distance):
    '''
    :param hub_list: 城市信息表
    :param weight: 运量（重量）表
    :param distance: 距离表
    :return: 最终成本表（尾量空载）
    '''
    m_2 = 1
    m_3 = 1
    while (m_2 * pa.GL_CAP[2] < (m_2 + 1) * pa.GL_CAP[1]):
        m_2 += 1
    while (m_3 * pa.GL_CAP[2] < (m_3 + 1) * pa.GL_CAP[0]):
        m_3 += 1
    print(m_2, m_3)

    hubs = list(hub_list['城市名称'])
    hubs_pair = []
    trans_cost = pd.DataFrame()
    #城市对列表
    for y_2 in range(0,len(hubs)-1):
        for j in range(y_2+1,len(hubs)):
            hubs_pair.append([hubs[y_2],hubs[j]])
    # for y_2 in range(0,1):
    #     for j in range(y_2+1,len(hubs)):
    #         hubs_pair.append([hubs[y_2],hubs[j]])
    pair_dui = 0
    for pair in hubs_pair:#循环每一对城市对
        pair_dui+=1
        print("第{0}个城市对为{1},正在运行！".format(pair_dui, pair))
        weight_1 = float(weight.loc[(weight['收寄城市'] == pair[0]) & (weight['寄达城市']== pair[1])]['运量（重量）'])
        weight_2 = float(weight.loc[(weight['收寄城市'] == pair[1]) & (weight['寄达城市'] == pair[0])]['运量（重量）'])
        #查询往返运量（重量）
        weight_min = min(weight_1,weight_2)
        weight_max = max(weight_1, weight_2)
        k_1 = math.ceil(weight_1 / pa.GL_CAP[2]) + 1  #计算去边所需最大车辆数

        k_2 = math.ceil(weight_2 / pa.GL_CAP[2]) + 1  # 计算回边所需最大车辆数

        # 查询往返距离
        distance_1 = float(distance.loc[(distance['收寄城市'] == pair[0]) & (distance['寄达城市']== pair[1])]['距离'])
        distance_2 = float(distance.loc[(distance['收寄城市'] == pair[1]) & (distance['寄达城市']== pair[0])]['距离'])

        # 查询司机人数
        driver_num_1 = 2 if distance_1 >= pa.GL_DSP else 1
        driver_num_2 = 2 if distance_2 >= pa.GL_DSP else 1
        # 双向无直达邮路或运量为0
        if(weight_max == 0):
            trans_cost = trans_cost.append([[pair[0], pair[1], np.nan, np.nan]])
            trans_cost = trans_cost.append([[pair[1], pair[0], np.nan, np.nan]])
        # 如果某一边无直达邮路或无运量，直接委办
        elif(weight_min == 0):
            initial_truck_list = truck_list(pa.GL_MAX)
            if weight_1 != 0:
                final_truck_list = [initial_truck(initial_truck_list, weight_1),[0,0,0],[0,0,0]]
                final_cost = transport_3(final_truck_list,distance_1, 0, driver_num_1, 0)
                trans_cost = trans_cost.append([[pair[0], pair[1], final_truck_list, final_cost]])
            else:
                final_truck_list = [[0,0,0],initial_truck(initial_truck_list, weight_2),[0,0,0]]
                final_cost = transport_3(final_truck_list,0, distance_2, 0, driver_num_2)
                trans_cost = trans_cost.append([[pair[1], pair[0], final_truck_list, final_cost]])
        # 往返都有直达邮路且运量都大于0
        else:
            final_truck_list = []
            final_cost = 1000000000
            k_min = min(k_1,k_2)
            for z_1 in range(1,int(k_min)):
                for z_2 in range(min(m_2,int(k_min) - z_1)):
                    for z_3 in range(min(m_3,int(k_min) - z_1 - z_2)):
                        for x_1 in range(max(0,k_1-1-z_1-m_2-m_3),int(k_1) - z_1 - z_2 - z_3):
                            for x_2 in range(min(m_2,int(k_1) - z_1 - z_2 - z_3 - x_1)):
                                for x_3 in range(min(m_3,int(k_1) - z_1 - z_2 - z_3 - x_1 - x_2)):
                                    for y_1 in range(max(0,k_2-1-z_1-m_2-m_3),int(k_2) - z_1 - z_2 - z_3):
                                        for y_2 in range(min(m_2,int(k_2) - z_1 - z_2 - z_3 - y_1)):
                                            for y_3 in range(min(m_3,int(k_2) - z_1 - z_2 - z_3 - y_1 - y_2)):
                                                #print([[x_1,x_2,x_3],[y_1,y_2,y_3],[z_1,z_2,z_3]])
                                                temp_truck_list = [[x_1,x_2,x_3],[y_1,y_2,y_3],[z_1,z_2,z_3]]
                                                if (((x_1 + z_1) * pa.GL_CAP[2] + (x_2 + z_2) * pa.GL_CAP[1] + (x_3 + z_3) * pa.GL_CAP[0]) >= weight_1) & \
                                                     (((y_1 + z_1) * pa.GL_CAP[2] + (y_2 + z_2) * pa.GL_CAP[1] + (y_3 + z_3) * pa.GL_CAP[0]) >= weight_2):

                                                    temp_cost = transport_3(temp_truck_list,distance_1,distance_2,driver_num_1,driver_num_2)
                                                    if temp_cost < final_cost:

                                                        final_cost = temp_cost

                                                        final_truck_list = temp_truck_list

            final_truck_list_1 = [final_truck_list[0],[0,0,0],final_truck_list[2]]
            final_cost_1 = transport_3(final_truck_list_1,distance_1,0,driver_num_1,0)
            final_truck_list_2 = [[0,0,0],final_truck_list[1],final_truck_list[2]]
            final_cost_2 = transport_3(final_truck_list_2,0,distance_2,0,driver_num_2)
            trans_cost = trans_cost.append([[pair[0], pair[1], final_truck_list_1, final_cost_1,1 if final_cost_1 <= final_cost_2 else 0]])
            trans_cost = trans_cost.append([[pair[1], pair[0], final_truck_list_2, final_cost_2,1 if final_cost_1 > final_cost_2 else 0]])
    trans_cost = pd.DataFrame(np.array(trans_cost), columns=['收寄城市', '寄达城市', '车辆使用情况', '车辆成本','小边标记'])
    return trans_cost

def output(hub_list,trans_cost):
    cost_detail = link_route(hub_list)
    cost_detail = pd.merge(cost_detail,trans_cost,how = 'left',on = ['收寄城市','寄达城市'])
    #print(cost_detail)
    for i in range(cost_detail.shape[0]):
        temp_list = cost_detail.loc[i, "车辆使用情况_y"]
        if temp_list is not np.nan:
            #print(temp_list)
            cost_detail.loc[i, "车辆使用情况_x"] = "{0}-{1}的邮路使用{2}辆40t自办车,{3}辆20t自办车,{4}辆12t自办车以及{5}辆40t委办车,{6}辆20t委办车,{7}辆12t委办车".format(cost_detail.iloc[i, 0], cost_detail.iloc[i, 1], temp_list[2][0], temp_list[2][1],temp_list[2][2], temp_list[0][0] + temp_list[1][0], temp_list[0][1] + temp_list[1][1], temp_list[0][2] + temp_list[1][2])
    cost_detail.drop(columns = ['车辆使用情况_y','车辆成本_x'],inplace = True)
    cost_detail.rename(columns={'车辆使用情况_x': '车辆使用情况','车辆成本_y':'车辆成本'}, inplace=True)
    return cost_detail








