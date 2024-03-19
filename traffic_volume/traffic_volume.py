#擷取網頁交通量資訊並加資料標題
import requests
import pandas as pd
from io import StringIO
import json

# 加載映射文件
with open('traffic_volume_attributes.json', 'r', encoding='utf-8') as file:
    mapping = json.load(file)

url = "https://tisvcloud.freeway.gov.tw/history/TDCS/M03A/20240227/15/TDCS_M03A_20240227_153500.csv"
response = requests.get(url)
response.encoding = 'utf-8'

# 確認請求成功
if response.status_code == 200:
    # 將CSV格式的字符串轉換成DataFrame
    data = pd.read_csv(StringIO(response.text), header=None)
    
    # 為DataFrame添加標題行
    data.columns = ['TimeInterval', 'RoadSection', 'Direction', 'VehicleType', 'TrafficVolume']
    
    # 使用映射替換GantryID的值
    data.replace({'RoadSection':mapping['RoadSection']}, inplace=True)
    

    # 根據 GantryID 分組並分類 VehicleType(非小車*1.4)
    for (road_section, direction), group_data in data.groupby(['RoadSection', 'Direction']):
        large_car, small_car = 0, 0
        for vt, tv in zip(group_data['VehicleType'], group_data['TrafficVolume']):
            if vt in [41, 42, 5]:
                large_car += tv
            else:
                small_car += tv
        pcu = round(large_car * 1.4 + small_car, 2)
        last_row_index = group_data.tail(1).index
        data.loc[last_row_index, 'PCU'] = pcu

    # 替換Direction中的值
    data.replace({'Direction':mapping['Direction']}, inplace=True)
    # 轉型態(int64->str)並替換VehicleType中的值
    #data['VehicleType'] = data['VehicleType'].astype(str)
    data.replace({'VehicleType':mapping['VehicleType']}, inplace=True)

    

    # 保存DataFrame到CSV文件
    data.to_csv('trafficvolume_data_with_PCU2.csv', index=False, encoding='utf_8_sig')
    print("數據已保存到 'trafficvolume_data_with_PCU.csv'")
else:
    print("無法從URL獲取數據,請檢查URL或網絡連接.")


#TimeInterval：報表產製時間，依每 5 分鐘為時階統計產出報表
    #顯示方式：2013-11-20 22:55:00
#GantryID：偵測站編號
#Direction：車行方向 (S：南；N：北)
#VehicleType：車種
    #31(小客車) 、32(小貨車) 、41(大客車) 、42(大貨車) 、5(聯結車)
#交通量：計算單一偵測站在此張表之時階範圍內所經過之車流量總量
    