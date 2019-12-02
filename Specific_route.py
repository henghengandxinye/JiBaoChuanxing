import time
import os
import pandas as pd
import numpy as np

os.chdir("C:\\Users\恒恒心页\Desktop\JiBaoChuanxing\Table") # 更改工作目录
# print(os.getcwd()) # 打印当前工作目录
start = time.time()

#————————————————————————————————————————————————————————————————————————————————————————————-
print("开始读取输入表格")
#读取输入表格
route = pd.read_csv("shunfeng_route_new.csv",encoding = 'UTF-8')
prohub_list = pd.read_csv("prohub_list.csv",encoding = 'UTF-8')
end = time.time()
print("输入表格读取完毕，总用时：",(end-start))
#————————————————————————————————————————————————————————————————————————————————————————————-
province_city_list = list(prohub_list['城市名称'][0:31])
route_list = route['线路轨迹（城市）']
# print(route_list[0].split('-'))
# print(province_city_list)
# print(route_list)
# print(route_list[0].split('-')[0].replace('市',''))
print(route)
def specific_route_handle(route_list,province_city_list):
    row_route_list = route_list.shape[0]
    row_city_list = len(province_city_list)
    route_detail = pd.DataFrame()
    all_detail = pd.DataFrame()
    for m in range(0,row_city_list):
        for n in range(0,row_city_list):
            start = province_city_list[m]
            end = province_city_list[n]
            route = []
            num = []
            total_num = 0
            all_detail = all_detail.append([[start,end,route,num,total_num]])
    all_detail = pd.DataFrame(np.array(all_detail), columns=['起点省会', '终点省会', '路由', '邮件量', '总的邮件量'])
    for i in range(0, row_route_list):
        print(i)
        route_length = len(route_list[i].split('-'))
        route_list_detail = route_list[i].split('-')
        for j in  range(0,route_length-1):
            for k in range(j+1,route_length):
                route_list_detail[j] = route_list_detail[j].replace('市','')
                route_list_detail[k] = route_list_detail[k].replace('市', '')
                # print(route_list_detail[j])
                if (route_list_detail[j] in province_city_list) and (route_list_detail[k] in province_city_list) and (route_list_detail[j] != route_list_detail[k]):
                    # print(route_list,type(route_list))
                    # print(route_list.iloc[i])
                    temp_route = route_list_detail[j:(k+1)]
                    temp_route = '-'.join(temp_route)
                    temp_num = 1
                    row_index = all_detail.loc[((all_detail['起点省会'] == route_list_detail[j]) & (all_detail['终点省会'] == route_list_detail[k]))].index.tolist()[0]
                    route = all_detail.iloc[row_index,2]
                    num = all_detail.iloc[row_index,3]
                    total_num = all_detail.iloc[row_index,4]
                    # print(temp_route,type(temp_route),route,type(route))
                    # print(num,type(num))
                    if temp_route in route:
                        # print(222222222)
                        num[route.index(temp_route)] = num[route.index(temp_route)]+ 1
                    else:
                        # print(333333333)
                        route.append(temp_route)
                        num.append(temp_num)
                    total_num = total_num + 1
                    all_detail.iloc[row_index,2] = route
                    all_detail.iloc[row_index,3] = num
                    all_detail.iloc[row_index,4] = total_num
                    # print(route, type(route))
                    # print(num, type(num))
                    # print(num, type(num))
    return all_detail
all_detail = specific_route_handle(route_list,province_city_list)
# print(all_detail)
all_detail.to_csv("各快递公司省会间具体路线情况-顺丰特惠（去除异常）.csv",index = 0,encoding = 'utf_8_sig')