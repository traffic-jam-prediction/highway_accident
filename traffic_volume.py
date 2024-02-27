import requests
import pandas as pd
from io import StringIO
import json

# 加載映射文件
with open('mapping.json', 'r', encoding='utf-8') as file:
    mapping = json.load(file)

url = "https://tisvcloud.freeway.gov.tw/history/TDCS/M03A/20240227/13/TDCS_M03A_20240227_133500.csv"
response = requests.get(url)
response.encoding = 'utf-8'

# 確認請求成功
if response.status_code == 200:
    # 將CSV格式的字符串轉換成DataFrame
    data = pd.read_csv(StringIO(response.text), header=None)
    
    # 為DataFrame添加標題行
    data.columns = ['TimeInterval', 'GantryID', 'Direction', 'VehicleType', '交通量']

    # 使用映射替換GantryID的值
    data['GantryID'].replace(mapping['GantryID'], inplace=True)
    # 替換Direction中的值
    data['Direction'].replace(mapping['Direction'], inplace=True)
  

    data['VehicleType'] = data['VehicleType'].astype(str)
    # 替換VehicleType中的值
    data['VehicleType'].replace(mapping['VehicleType'], inplace=True)
    

    # 保存DataFrame到CSV文件
    data.to_csv('trafficvolume_data.csv', index=False, encoding='utf_8_sig')
    print("數據已保存到 'trafficvolume_data.csv'")
else:
    print("無法從URL獲取數據,請檢查URL或網絡連接.")


#TimeInterval：報表產製時間，依每 5 分鐘為時階統計產出報表
    #顯示方式：2013-11-20 22:55:00
#GantryID：偵測站編號
#Direction：車行方向 (S：南；N：北)
#VehicleType：車種
    #31(小客車) 、32(小貨車) 、41(大客車) 、42(大貨車) 、5(聯結車)
#交通量：計算單一偵測站在此張表之時階範圍內所經過之車流量總量