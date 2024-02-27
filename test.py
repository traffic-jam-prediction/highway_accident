import requests
import pandas as pd
from io import StringIO

url = "https://tisvcloud.freeway.gov.tw/history/TDCS/M03A/20240227/13/TDCS_M03A_20240227_133500.csv"
response = requests.get(url)
response.encoding = 'utf-8'

# 假設 data 是你的 DataFrame，並且 'VehicleType' 列的數據類型是 int64
data = pd.read_csv(StringIO(response.text), header=None)
data.columns = ['TimeInterval', 'GantryID', 'Direction', 'VehicleType', '交通量']

# 將 'VehicleType' 列轉換為對象型態
data['VehicleType'] = data['VehicleType'].astype(object)

# 檢查轉換後的數據類型
print("VehicleType 列的數據類型是:", data['VehicleType'].dtype)
