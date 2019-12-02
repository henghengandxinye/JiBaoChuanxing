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
city_list = pd.read_csv("各快递公司省会间直连情况-顺丰特惠.csv",encoding = 'UTF-8')
prohub_list = pd.read_csv("prohub_list.csv",encoding = 'UTF-8')
end = time.time()
print("输入表格读取完毕，总用时：",(end-start))
#————————————————————————————————————————————————————————————————————————————————————————————-
province_city_list = list(prohub_list['城市名称'][0:31])
def route_handle_back(city_list,province_city_list):
    zhida = city_list[city_list.是否直连 == 1]
    zhida.reset_index(drop=True, inplace=True)
    row_zhida = zhida.shape[0]
    zhida_list = []
    for k in range(row_zhida):
        zhida_list.append(zhida.iloc[k,0]+ '-' + zhida.iloc[k,1])
    start_list = list(city_list['起点省会'])
    end_list = list(city_list['终点省会'])
    num = list(city_list['邮件量'])
    row = city_list.shape[0]
    route_zhida = pd.DataFrame()
    for i in range(0, row):
        print(i)
        route_1 = start_list[i] + '-' + end_list[i]
        route_2 = end_list[i] + '-' + start_list[i]
        if ((route_1 in zhida_list) and (route_2 in zhida_list)):
            route_zhida = route_zhida.append([[start_list[i],end_list[i],'1']])

    row_city_list = len(province_city_list)
    all_detail = pd.DataFrame()
    for m in range(0,row_city_list):
        for n in range(0,row_city_list):
            start = province_city_list[m]
            end = province_city_list[n]
            all_detail = all_detail.append([[start, end, num[m*row_city_list+n]]])
    all_detail = pd.DataFrame(np.array(all_detail), columns=['起点省会', '终点省会','邮件量'])
    route_zhida = pd.DataFrame(np.array(route_zhida), columns=['起点省会','终点省会','是否双向'])
    final_detail = pd.merge(all_detail,route_zhida,how = 'left' , on = ['起点省会','终点省会'])
    final_detail.replace(np.nan,0,inplace = True)
    orders = ['起点省会','终点省会','是否双向','邮件量']
    final_detail = final_detail[orders]
    return final_detail
final_detail = route_handle_back(city_list,province_city_list)
final_detail.to_csv("各快递公司省会间双向直连情况-顺丰特惠.csv",index = 0,encoding = 'utf_8_sig')