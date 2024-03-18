import pandas as pd


# 定義函式來判斷事件位置
def detect_location(kilometer, highway):
    # 根據所在國道選擇相應的 CSV 檔案
    csv_file = f"../{highway}.csv"
    df = pd.read_csv(csv_file, encoding='utf-8')
    
    for index, row in df.iterrows():
        if row['里程K+000'] <= kilometer <= df.iloc[index+1]['里程K+000']:
            return f"{row['設施名稱']}-{ df.iloc[index+1]['設施名稱']}"


# 讀取CSV檔案
df = pd.read_csv("A3_accident.csv", encoding='utf-8')
# 生成新的 DataFrame，僅包含時間、路段、方向
new_df = pd.DataFrame(columns=['時間','事故類別', '路段', '方向'])

for index, row in df.iterrows():
    if not pd.isnull(row['公里']):  # 檢查 '公里' 欄位是否為 NaN
        row['公里'] = int(row['公里']) # 確保公里數為整數
        highway, ai, kilometer, direction = row['路線'], row['事故類別'], row['公里'], '北上' if '北側' in row['向'] else '南下'
        if row[' 道路型態'] == "高架道路":
            if kilometer>71:
                continue    # 跳過後續程式碼，處理下一行資料
            if highway in ["國道1號"]:
                if kilometer<13:
                    continue
                else:
                    highway = highway+"_高架"
                    location = detect_location(kilometer, highway) 
                location = location + "(高架)"
                time_info = f"{int(row['年'])}-{int(row['月'])}-{int(row['日'])} {int(row['時'])}:{int(row['分'])}:{int(row['秒'])}"
                new_df = pd.concat([new_df, pd.DataFrame({'時間': [time_info], '事故類別':[ai], '路段': [location], '方向': [direction]})], ignore_index=True)
        else :
            if highway in ["國道1號","國道3號","國道5號"]:
                location = detect_location(kilometer, highway) 
                time_info = f"{int(row['年'])}-{int(row['月'])}-{int(row['日'])} {int(row['時'])}:{int(row['分'])}:{int(row['秒'])}"
                new_df = pd.concat([new_df, pd.DataFrame({'時間': [time_info], '事故類別':[ai], '路段': [location], '方向': [direction]})], ignore_index=True)

# 將新的 DataFrame 寫入 CSV 檔案，指定編碼格式為 UTF-8-BOM
new_df.to_csv('accident3_info.csv', index=False, encoding='utf-8-sig')

print("新的 CSV 檔案已生成。")