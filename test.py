import requests
import pandas as pd
from io import StringIO

file_path = "C:/Users/julia/Desktop/wei/test.csv"

# 將CSV格式的字符串轉換成DataFrame
data = pd.read_csv(file_path, header=None)
    
# 為DataFrame添加標題行
data.columns = ['TimeInterval', 'GantryID', 'Direction', 'VehicleType', 'TrafficVolume']

# 根據 GantryID 分組並處理 VehicleType
for gantry_id, group_data in data.groupby('GantryID'):
    large_car, small_car = 0, 0
    for vt, tv in zip(group_data['VehicleType'], group_data['TrafficVolume']):
        if vt in [41, 42, 5]:
            large_car += tv
        else:
            small_car += tv
    pcu = large_car * 1.4 + small_car
    # 設置每個分組的最後一行的 'PCU' 欄位
    last_row_index = group_data.tail(1).index
    data.loc[last_row_index, 'PCU'] = pcu

# 將修改後的 DataFrame 寫入 CSV 文件，不添加索引和空行
data.to_csv('trafficvolume_data_with_PCU.csv', index=False, encoding='utf_8_sig')
