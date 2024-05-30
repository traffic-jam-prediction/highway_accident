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
    new_df = pd.DataFrame(columns=['Date','Time','RoadSection','Highway','Direction','Midpoint',
                               'M03A_PCU','M03A_PCU_BigGap','M05A_SpaceMeanSpeed','M05A_PCU'])

    for row in df_dict:
        pcu1, pcu2, speed, pcu_m05a, pcua, pcub = 0, 0, 0, 0, 0, 0
        
        # m03a
        for m03a_data in m03a_dict:
            # 將05FR略過
            if m03a_data['GantryID'] == '05FR113S' or m03a_data['GantryID'] == '05FR143N':
                continue     
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

        # m05a
        for m05a_data in m05a_dict:
            # 將05FR略過
            if  ( m05a_data['GantryFrom'] == '05FR113S' or m05a_data['GantryTo'] == '05FR113S'
                or m05a_data['GantryFrom'] == '05FR143N' or m05a_data['GantryTo'] == '05FR143N' ):
                continue

            if (row['roadsection'] == '汐止端-堤頂交流道' and row['direction']== 'S' 
                and m05a_data['GantryFrom']=='01F0099S' and m05a_data['GantryTo']=='01H0163S'):
                speed += (m05a_data['SpaceMeanSpeed'] * m05a_data['Traffic'])
                if m05a_data['VehicleType'] in [41, 42, 5]:
                    pcua += m05a_data['Traffic'] 
                else:
                    pcub += m05a_data['Traffic']
            elif (((row['roadsection'] == '中壢轉接道-校前路交流道') 
                  or(row['roadsection'] == '校前路交流道-楊梅端')) and row['direction']== 'N'
                  and m05a_data['GantryFrom']=='01F0750N' and m05a_data['GantryTo']=='01H0608N'):
                speed += (m05a_data['SpaceMeanSpeed'] * m05a_data['Traffic'])
                if m05a_data['VehicleType'] in [41, 42, 5]:
                    pcua += m05a_data['Traffic'] 
                else:
                    pcub += m05a_data['Traffic']
            elif (((row['roadsection'] == '南州交流道-林邊交流道') 
                  or(row['roadsection'] == '林邊交流道-大鵬灣端')) and row['direction']== 'N'
                  and m05a_data['GantryFrom']=='03F4259N' and m05a_data['GantryTo']=='03F4232N'):
                speed += (m05a_data['SpaceMeanSpeed'] * m05a_data['Traffic'])
                if m05a_data['VehicleType'] in [41, 42, 5]:
                    pcua += m05a_data['Traffic'] 
                else:
                    pcub += m05a_data['Traffic']
            elif (((row['roadsection'] == '南州交流道-林邊交流道') 
                  or(row['roadsection'] == '林邊交流道-大鵬灣端')) and row['direction']== 'S'
                  and m05a_data['GantryFrom']=='03F4232S' and m05a_data['GantryTo']=='03F4263S'):
                speed += (m05a_data['SpaceMeanSpeed'] * m05a_data['Traffic'])
                if m05a_data['VehicleType'] in [41, 42, 5]:
                    pcua += m05a_data['Traffic'] 
                else:
                    pcub += m05a_data['Traffic']
            elif (row['roadsection'] == '羅東交流道-蘇澳交流道' and row['direction']== 'S'
                 and m05a_data['GantryFrom']=='05F0439S' and m05a_data['GantryTo']=='05F0494S'):
                speed += (m05a_data['SpaceMeanSpeed'] * m05a_data['Traffic'])
                if m05a_data['VehicleType'] in [41, 42, 5]:
                    pcua += m05a_data['Traffic'] 
                else:
                    pcub += m05a_data['Traffic']
            elif row['direction'] == 'S':
                if(m05a_data['GantryFrom'][:3] == row['nearest_gantry1'][:3] and m05a_data['GantryFrom'].endswith('S') 
                    and int(m05a_data['GantryFrom'][3:7])/10 <= row['midpoint'] < int(m05a_data['GantryTo'][3:7])/10) :
                    speed += (m05a_data['SpaceMeanSpeed'] * m05a_data['Traffic'])
                    if m05a_data['VehicleType'] in [41, 42, 5]:
                        pcua += m05a_data['Traffic'] 
                    else:
                        pcub += m05a_data['Traffic']
 
            elif row['direction'] == 'N': 
                if (m05a_data['GantryFrom'][:3] == row['nearest_gantry1'][:3] and m05a_data['GantryFrom'].endswith("N") 
                    and int(m05a_data['GantryTo'][3:7])/10 <= row['midpoint'] < int(m05a_data['GantryFrom'][3:7])/10) :
                    speed += (m05a_data['SpaceMeanSpeed'] * m05a_data['Traffic'])
                    if m05a_data['VehicleType'] in [41, 42, 5]:
                        pcua += m05a_data['Traffic'] 
                    else:
                        pcub += m05a_data['Traffic']
 
        pcu_m05a = pcua * 1.4 + pcub
        
        # m05a資料內交通量為0
        if pcua + pcub ==0:
            speed = 0
            pcu_m05a = 0

        else:
            speed = round(speed/( pcua + pcub ),1)
        date, time = m03a_data['TimeInterval'].split(' ')
        time = datetime.strptime(time, '%H:%M').strftime('%H:%M:%S')
        if new_df.empty:
            new_df = pd.DataFrame({'Date':[date],'Time': [time],'RoadSection':row['roadsection'],
                                   'Highway':row['highway'],'Direction':row['direction'], 'Midpoint':row['midpoint'],
                                   'M03A_PCU':[pcu],'M03A_PCU_BigGap': [biggap],
                                   'M05A_SpaceMeanSpeed': [speed],'M05A_PCU':[pcu_m05a]})
        else:
            new_df = pd.concat([new_df, pd.DataFrame({'Date': [date], 
                                            'Time': [time], 
                                            'RoadSection':row['roadsection'],
                                            'Highway':row['highway'],
                                            'Direction':row['direction'],
                                            'Midpoint':row['midpoint'],
                                            'M03A_PCU':[pcu],
                                            'M03A_PCU_BigGap': [biggap],
                                            'M05A_SpaceMeanSpeed': [speed],
                                            'M05A_PCU':[pcu_m05a]
                                            })], ignore_index=True)
        
    return new_df

def get_accident(main_df):
    accident1_df = pd.read_csv('../accident_road/accident1_info.csv')
    accident2_df = pd.read_csv('../accident_road/accident2_info.csv')
    accident3_df = pd.read_csv('../accident_road/accident3_info.csv')
    accident_merge = pd.concat([accident1_df, accident2_df, accident3_df], ignore_index=True)

    accident_count = accident_merge.groupby(['Date', 'Time', 'RoadSection', 'Highway', 'Direction']).size().reset_index(name='Count')

    merged_df = pd.merge(main_df, accident_count, on=['Date', 'Time', 'RoadSection', 'Highway', 'Direction'], how='left')
    merged_df['Count'] = merged_df['Count'].fillna(0)

    return merged_df

def mark_holiday(date):
    holiday_str = ['2023-01-01', '2023-01-02', '2023-01-07', '2023-01-08', '2023-01-14', '2023-01-15', '2023-01-20', '2023-01-21', '2023-01-22', '2023-01-23',
            '2023-01-24', '2023-01-25', '2023-01-26', '2023-01-27', '2023-02-11', '2023-02-12', '2023-02-19', '2023-02-25', '2023-02-26', '2023-02-27',
            '2023-02-28', '2023-03-04', '2023-03-05', '2023-03-11', '2023-03-12', '2023-03-18', '2023-03-19', '2023-03-26', '2023-04-01', '2023-04-02',
            '2023-04-03', '2023-04-04', '2023-04-05', '2023-04-08', '2023-04-09', '2023-04-15', '2023-04-16', '2023-04-22', '2023-04-23', '2023-04-29', 
            '2023-04-30', '2023-05-06', '2023-05-07', '2023-05-13', '2023-05-14', '2023-05-20', '2023-05-21', '2023-05-27', '2023-05-28', '2023-06-03', 
            '2023-06-04', '2023-06-10', '2023-06-11', '2023-06-18', '2023-06-22', '2023-06-23', '2023-06-24', '2023-06-25', '2023-07-01', '2023-07-02', 
            '2023-07-08', '2023-07-09', '2023-07-15', '2023-07-16', '2023-07-22', '2023-07-23', '2023-07-29', '2023-07-30', '2023-08-05', '2023-08-06', 
            '2023-08-12', '2023-08-13', '2023-08-19', '2023-08-20', '2023-08-26', '2023-08-27', '2023-09-02', '2023-09-03', '2023-09-09', '2023-09-10', 
            '2023-09-16', '2023-09-17', '2023-09-24', '2023-09-29', '2023-09-30', '2023-10-01', '2023-10-07', '2023-10-08', '2023-10-09', '2023-10-10',
            '2023-10-14', '2023-10-15', '2023-10-21', '2023-10-22', '2023-10-28', '2023-10-29'
               ]
    return 1 if date in holiday_str else np.nan

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

# def integrated_forecastdata():
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
    new_df = pd.DataFrame(columns=['Date','Time','RoadSection','Highway','Direction','Midpoint',
                               'M03A_PCU','M03A_PCU_BigGap','M05A_SpaceMeanSpeed','M05A_PCU'])
    for file_m03a, file_m05a in zip(matching_files_m03a, matching_files_m05a):
        new_df = pd.concat([new_df, get_trafficvolume(file_m03a, file_m05a)], ignore_index=True)
        print(file_m03a, file_m05a)

    new_df = get_accident(new_df)
    new_df['Holiday'] = new_df['Date'].apply(mark_holiday)
    new_df['Week'] = pd.to_datetime(new_df['Date'], format='%Y-%m-%d').dt.day_name()

    new_df['DateTime'] = pd.to_datetime(new_df['Date'] + ' ' + new_df['Time'], format='%Y-%m-%d %H:%M:%S').dt.strftime('%Y-%m-%d %H:%M:%S')
    new_df.drop(['Date', 'Time'], axis=1, inplace=True)
    new_df = new_df[['DateTime'] + new_df.columns[:-1].tolist()]  
    # new_df.to_csv('test_06.csv', encoding='utf-8-sig', index=False)
    # print("數據已保存到 'test_06.csv'")

    # 刪除文件
    delete_file('extracted_files')

    # return new_df