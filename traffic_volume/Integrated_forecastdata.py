import requests
import pandas as pd
from io import StringIO
import json
import tarfile
import os
import shutil


def download_and_extract_tar(url, extract_path):
    # 下載檔案
    response = requests.get(url)
    response.encoding = 'utf-8'
    if response.status_code == 200:
        # 寫入暫存檔案
        with open("temp.tar", "wb") as f:
            f.write(response.content)

        # 解壓縮檔案
        with tarfile.open("temp.tar", "r") as tar:
            tar.extractall(path=extract_path)
        
        # 刪除暫存檔案
        os.remove("temp.tar")
        print("下載並解壓縮成功！")
    else:
        print("下載失敗！")

def traffic_volume(new_df ,file_path):
    #header=None，這樣Pandas將不會將第一列視為標籤，而是將其視為數據行
    data = pd.read_csv(file_path,header=None)
    data.columns = ['TimeInterval', 'RoadSection', 'Direction', 'VehicleType', 'TrafficVolume']
    #new_df = pd.DataFrame(columns=['TimeInterval', 'RoadSection', 'Direction', 'PCU', 'Week', 'Holiday'])
    
    # 根據 GantryID 分組並分類 VehicleType(非小車*1.4)
    for gantry_id, group_data in data.groupby('RoadSection'):
        if group_data['RoadSection'].values[0][:3] == '03A': 
            continue
        else:
            #print(gantry_id)
            #print(group_data)
            large_car, small_car = 0, 0
            for vt, tv in zip(group_data['VehicleType'], group_data['TrafficVolume']):
                if vt in [41, 42, 5]:
                    large_car += tv
                else:
                    small_car += tv
            pcu = round(large_car * 1.4 + small_car, 2)
            last_row_index = group_data.tail(1).index
            TimeInterval = data.loc[last_row_index, 'TimeInterval'].values[0]  # 使用.values[0]取出值
            RoadSection = data.loc[last_row_index, 'RoadSection'].values[0] 
            Direction = data.loc[last_row_index, 'Direction'].values[0] 
            new_df = pd.concat([new_df, pd.DataFrame({'TimeInterval': [TimeInterval], 'RoadSection':[RoadSection], 'Direction': [Direction], 'PCU': [pcu]})], ignore_index=True)
    return new_df
    # 重設索引以解決問題
   



def delete_file(file_name):
    try:
        shutil.rmtree(file_name)
        print(f"成功刪除目錄及其內容: {file_name}")
    except FileNotFoundError:
        print(f"找不到目錄: {file_name}")
    except PermissionError:
        print(f"權限錯誤。無法刪除目錄及其內容: {file_name}")
    except Exception as e:
        print(f"發生錯誤: {e}")




def find_matching_files(root_dir, prefix, date):
    matching_files = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.startswith(f"TDCS_{prefix}_{date}_") and file.endswith(".csv"):
                matching_files.append(os.path.join(root, file))
    return matching_files

root_dir = r'.\extracted_files\M03A\20230101'
prefix = 'M03A'
date = '20230101'

# 網站.tar檔案的URL
traffic_url = "https://tisvcloud.freeway.gov.tw/history/TDCS/M03A/"
tar_day = "M03A_20230101.tar.gz"
tar_url = os.path.join(traffic_url, tar_day)

# 解壓縮的路徑
extract_path = "./extracted_files"
# 函式下載並解壓縮.tar檔案
download_and_extract_tar(tar_url, extract_path)

# 取得data資訊
new_df = pd.DataFrame(columns=['TimeInterval', 'RoadSection', 'Direction', 'PCU'])
matching_files = find_matching_files(root_dir, prefix, date)
# 輸出找到的檔案路徑
for file_path in matching_files:
    new_df = traffic_volume(new_df, file_path)
    print(file_path)

new_df.reset_index(drop=True, inplace=True)
new_df.to_csv('test.csv', index=False, encoding='utf-8-sig')
print("數據已保存到 'test.csv'")

# 刪除文件
delete_file('extracted_files')