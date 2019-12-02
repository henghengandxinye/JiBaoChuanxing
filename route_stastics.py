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
route = pd.read_csv("shunfengtehui_route.csv",encoding = 'gbk')
prohub_list = pd.read_csv("prohub_list.csv",encoding = 'UTF-8')
end = time.time()
print("输入表格读取完毕，总用时：",(end-start))
#————————————————————————————————————————————————————————————————————————————————————————————-
province_city_list = list(prohub_list['城市名称'][0:31])
route_list = route['线路轨迹（城市）']
print(route_list[0].split('-'))
# print(province_city_list)
# print(route_list)
print(route_list[0].split('-')[0].replace('市',''))
def route_handle(route_list,province_city_list):
    row_route_list = route_list.shape[0]
    row_city_list = len(province_city_list)
    route_detail = pd.DataFrame()
    all_detail = pd.DataFrame()
    for m in range(0,row_city_list):
        for n in range(0,row_city_list):
            start = province_city_list[m]
            end = province_city_list[n]
            all_detail = all_detail.append([[start, end]])
    all_detail = pd.DataFrame(np.array(all_detail), columns=['起点省会', '终点省会'])
    for i in range(0, row_route_list):
        print(i)
        route_length = len(route_list[i].split('-'))
        route_list_detail = route_list[i].split('-')
        for j in  range(0,route_length-1):
            route_list_detail[j] = route_list_detail[j].replace('市','')
            route_list_detail[j+1] = route_list_detail[j+1].replace('市', '')
            # print(route_list_detail[j])
            if (route_list_detail[j] in province_city_list) and (route_list_detail[j+1] in province_city_list) and (route_list_detail[j] != route_list_detail[j+1]):
                route_detail = route_detail.append([[route_list_detail[j],route_list_detail[j+1],'1','1']])
    route_detail = pd.DataFrame(np.array(route_detail), columns=['起点省会','终点省会','是否直连','邮件量'])
    route_detail = route_detail.groupby([route_detail['起点省会'],route_detail['终点省会']], as_index=False)['邮件量'].count()
    route_detail['是否直连'] = '1'
    final_detail = pd.merge(all_detail,route_detail,how = 'left' , on = ['起点省会','终点省会'])
    final_detail.replace(np.nan,0,inplace = True)
    orders = ['起点省会','终点省会','是否直连','邮件量']
    final_detail = final_detail[orders]
    return route_detail,final_detail
route_detail,final_detail = route_handle(route_list,province_city_list)
final_detail.to_csv("各快递公司省会间直连情况-顺丰特惠.csv",index = 0,encoding = 'utf_8_sig')