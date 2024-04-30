import requests
import pandas as pd
import json
import tarfile
import os
import shutil
import numpy as np
from datetime import datetime, timedelta
from roadsection_with_nearest import find_nearest_detection_points


def download_and_extract_tar(url, extract_path):
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


def get_trafficvolume(m03a_file, m05a_file):
    #header=None，這樣Pandas將不會將第一列視為標籤，而是將其視為數據行
    df = find_nearest_detection_points()
    m03a = pd.read_csv(m03a_file,header=None)
    m03a.columns = ['TimeInterval', 'GantryID', 'Direction', 'VehicleType', 'TrafficVolume']
    m05a = pd.read_csv(m05a_file,header=None)
    m05a.columns = ['TimeInterval','GantryFrom', 'GantryTo', 'VehicleType', 'SpaceMeanSpeed', 'Traffic']
    # 將 data 資料框轉換為字典，每一行轉換為一個字典(為了效率)
    m03a_dict = m03a.to_dict('records')
    m05a_dict = m05a.to_dict('records')
    df_dict = df.to_dict('records')
    new_df = pd.DataFrame(columns=['Date','TimeInterval','RoadSection','Highway','Direction',
                               'M03A_PCU','M03A_PCU_BigGap','M05A_SpaceMeanSpeed','M05A_PCU'])

    for row in df_dict:
        pcu1, pcu2, speed, pcu_m05a, pcua, pcub = 0, 0, 0, 0, 0, 0
        for m03a_data in m03a_dict:
            if m03a_data['GantryID'] == row['nearest_gantry1']:
                if m03a_data['VehicleType'] in [41, 42, 5]:
                    pcu1 += m03a_data['TrafficVolume'] * 1.4
                else:
                    pcu1 += m03a_data['TrafficVolume']
            elif m03a_data['GantryID'] == row['nearest_gantry2']:
                if m03a_data['VehicleType'] in [41, 42, 5]:
                    pcu2 += m03a_data['TrafficVolume'] * 1.4
                else:
                    pcu2 += m03a_data['TrafficVolume']
        if pcu1==0 or pcu2==0:
            pcu=pcu1+pcu2
        else:
            pcu = (pcu1 + pcu2) / 2
        if abs(pcu1-pcu2) > 50:
            biggap = 1
        else:
            biggap = np.nan
    
        for m05a_data in m05a_dict:
            if row['direction'] == 'S':
                if (m05a_data['GantryFrom'][:3] == row['nearest_gantry1'][:3] and m05a_data['GantryFrom'][:3] == '05F'and m05a_data['GantryFrom'].endswith("S") and 
                    int(m05a_data['GantryFrom'][4:7])/10 <= row['midpoint'] < int(m05a_data['GantryTo'][4:7])/10) :
                    speed += (m05a_data['SpaceMeanSpeed'] * m05a_data['Traffic'])
                    if m05a_data['VehicleType'] in [41, 42, 5]:
                        pcua += m05a_data['Traffic'] 
                    else:
                        pcub += m05a_data['Traffic']
                elif(m05a_data['GantryFrom'][:3] == row['nearest_gantry1'][:3] and m05a_data['GantryFrom'][:3] != '05F' and m05a_data['GantryFrom'].endswith('S') and 
                    int(m05a_data['GantryFrom'][3:7])/10 <= row['midpoint'] < int(m05a_data['GantryTo'][3:7])/10) :
                    speed += (m05a_data['SpaceMeanSpeed'] * m05a_data['Traffic'])
                    if m05a_data['VehicleType'] in [41, 42, 5]:
                        pcua += m05a_data['Traffic'] 
                    else:
                        pcub += m05a_data['Traffic']
            elif row['direction'] == 'N': 
                if (m05a_data['GantryFrom'][:3] == row['nearest_gantry1'][:3] and m05a_data['GantryFrom'][:3] == '05F' and m05a_data['GantryFrom'].endswith("N") and 
                    int(m05a_data['GantryTo'][4:7])/10 <= row['midpoint'] < int(m05a_data['GantryFrom'][4:7])/10) :
                    speed += (m05a_data['SpaceMeanSpeed'] * m05a_data['Traffic'])
                    if m05a_data['VehicleType'] in [41, 42, 5]:
                        pcua += m05a_data['Traffic'] 
                    else:
                        pcub += m05a_data['Traffic']
                elif (m05a_data['GantryFrom'][:3] == row['nearest_gantry1'][:3] and m05a_data['GantryFrom'][:3] != '05F' and m05a_data['GantryFrom'].endswith("N") and 
                    int(m05a_data['GantryTo'][3:7])/10 <= row['midpoint'] < int(m05a_data['GantryFrom'][3:7])/10) :
                    speed += (m05a_data['SpaceMeanSpeed'] * m05a_data['Traffic'])
                    if m05a_data['VehicleType'] in [41, 42, 5]:
                        pcua += m05a_data['Traffic'] 
                    else:
                        pcub += m05a_data['Traffic']
        pcu_m05a = pcua * 1.4 + pcub

        if pcua + pcub ==0:
            continue
        else:
            speed = round(speed/( pcua + pcub ),1)
        date, time_interval = m03a_data['TimeInterval'].split(' ')
        if new_df.empty:
            new_df = pd.DataFrame({'Date':[date],'TimeInterval': [time_interval],'RoadSection':row['roadsection'],
                                   'Highway':row['highway'],'Direction':row['direction'],'M03A_PCU':[pcu],
                               'M03A_PCU_BigGap': [biggap],'M05A_SpaceMeanSpeed': [speed],'M05A_PCU':[pcu_m05a]})
        else:
            new_df = pd.concat([new_df, pd.DataFrame({'Date': [date], 
                                            'TimeInterval': [time_interval], 
                                            'RoadSection':row['roadsection'],
                                            'Highway':row['highway'],
                                            'Direction':row['direction'],
                                            'M03A_PCU':[pcu],
                                            'M03A_PCU_BigGap': [biggap],
                                            'M05A_SpaceMeanSpeed': [speed],
                                            'M05A_PCU':[pcu_m05a]
                                            })], ignore_index=True)
        
    return new_df

def count_trafficvolume(countfile_path):
    # 為了保留原始資料路段的排序順序(才能呈現由北到南的順序)
    data1 = find_nearest_detection_points()
    original_order = data1['roadsection'].unique().tolist()
    
    count_file = pd.DataFrame(columns=['RoadSection','Direction','M03A_PCU'])
    data2 = pd.read_csv(countfile_path)
    for (road_section, direction), group_data in data2.groupby(['RoadSection', 'Direction']):
        count_pcu = group_data['M03A_PCU'].sum()
        RoadSection = group_data['RoadSection'].values[0] 
        Direction = group_data['Direction'].values[0]
        count_file = pd.concat([count_file, pd.DataFrame({'RoadSection': [RoadSection],'Direction':[Direction],'M03A_PCU':[count_pcu]})])
    
    count_file = count_file.sort_values(by=['RoadSection'], key=lambda x: x.map({v: i for i, v in enumerate(original_order)}))
    count_file.to_csv('count_file.csv', index=False, encoding='utf-8-sig')
    print("數據已保存到 'count_file.csv'")

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

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)

def find_matching_files(root_dir, prefix, date):
    matching_files = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.startswith(f"TDCS_{prefix}_{date}_") and file.endswith(".csv"):
                matching_files.append(os.path.join(root, file))
    return matching_files


#def integrated_forecastdata():
if __name__ == '__main__':
    with open('traffic_volume_attributes.json', 'r', encoding='utf-8') as file:
        mapping = json.load(file)

    start_date_str = input("請輸入開始日期（格式如20230101）：")
    end_date_str = input("請輸入結束日期（格式如20231031）：")
    start_date = datetime.strptime(start_date_str, "%Y%m%d")
    end_date = datetime.strptime(end_date_str, "%Y%m%d")
    matching_files_m03a = []
    matching_files_m05a = []

    for single_date in daterange(start_date, end_date):
        date = single_date.strftime("%Y%m%d")
        root_dir_m03a = f'./extracted_files/M03A/{date}'
        prefix_m03a = 'M03A'
        root_dir_m05a = f'./extracted_files/M05A/{date}'
        prefix_m05a = 'M05A'

        # 網站.tar檔案的URL組合方式
        m03a_url = "https://tisvcloud.freeway.gov.tw/history/TDCS/M03A/"
        tar_day_m03a = f"M03A_{date}.tar.gz"
        tar_url_m03a = os.path.join(m03a_url, tar_day_m03a)
        m05a_url = "https://tisvcloud.freeway.gov.tw/history/TDCS/M05A/"
        tar_day_m05a = f"M05A_{date}.tar.gz"
        tar_url_m05a = os.path.join(m05a_url, tar_day_m05a)

        # 解壓縮的路徑
        extract_path = "./extracted_files"
        # 函式下載並解壓縮.tar檔案
        download_and_extract_tar(tar_url_m03a, extract_path)
        download_and_extract_tar(tar_url_m05a, extract_path)
        # 取得root_dir目錄下，所有m03a檔案的路徑   
        matching_files_m03a.extend(find_matching_files(root_dir_m03a, prefix_m03a, date))
        matching_files_m05a.extend(find_matching_files(root_dir_m05a, prefix_m05a, date))

    # 取得m03a_data資訊
    new_df = pd.DataFrame(columns=['Date','TimeInterval','RoadSection','Highway','Direction',
                               'M03A_PCU','M03A_PCU_BigGap','M05A_SpaceMeanSpeed','M05A_PCU'])
    for file_m03a, file_m05a in zip(matching_files_m03a, matching_files_m05a):
        new_df = pd.concat([new_df, get_trafficvolume(file_m03a, file_m05a)], ignore_index=True)
        print(file_m03a, file_m05a)

    new_df.to_csv('integrated_data_0101.csv', index=False, encoding='utf-8-sig')
    print("數據已保存到 'integrated_data.csv'")

    # 計算各路段交通量
    countfile_path = 'trafficvolume_0101.csv'
    count_trafficvolume(countfile_path)


    # 刪除文件
    delete_file('extracted_files')

    #return new_df
