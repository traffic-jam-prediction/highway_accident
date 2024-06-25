import pandas as pd
from datetime import datetime


def excel_to_csv():
    accident_type_list = ['A1', 'A2', 'A3']
    for accident_type in accident_type_list:
        data = pd.read_excel(f'{accident_type}_accident.xlsx')
        data.to_csv(f'{accident_type}_accident.csv',
                    index=False, encoding='utf-8-sig')
        print(f'{accident_type}_accident converted to CSV')


def edit_csv_row_pandas(filename, year: int, month: int, date: int,
                        hour: int, minute: int, second: int,
                        accident_type: str, city: str, township: str, highway_name: str,
                        kilometer: int, new_kilometer: int):
    df = pd.read_csv(filename)
    condition = (df['年'] == year) & (df['月'] == month) & (df['日'] == date) & (df['時'] == hour) & (df['分'] == minute) & (df['秒'] == second) & (
        df['事故類別'] == accident_type) & (df[' 縣市'] == city) & (df['市區鄉鎮'] == township) & (df['路線'] == highway_name) & (df['公里'] == kilometer)

    if df[condition].empty:
        print(f"Row not found for year {year}, month {month}, date {date}.")
        return
    # print(df.loc[condition])
    df.loc[condition, '公里'] = new_kilometer
    df.to_csv(filename, index=False)


def edit_error_rows():
    # cause: https://zh.wikipedia-on-ipfs.org/wiki/%E8%B7%AF%E7%AB%B9%E4%BA%A4%E6%B5%81%E9%81%93
    edit_csv_row_pandas('A3_accident.csv', 2023, 4, 30, 18,
                        3, 14, 'A3', '高雄市', '路竹區', '國道1號', 388, 338)
    edit_csv_row_pandas('A3_accident.csv', 2023, 8, 7, 12,
                        45, 53, 'A3', '新北市', '林口區', '國道1號', 414, 41)
    print('error row fixed')

# 定義函式來判斷事件位置
def detect_location(kilometer, highway):
    # 根據所在國道選擇相應的 CSV 檔案
    csv_file = f"../highway_information/{highway}.csv"
    df = pd.read_csv(csv_file, encoding='utf-8')
    for index, row in df.iterrows():
        if row['里程K+000'] <= kilometer <= df.iloc[index+1]['里程K+000']:
            return f"{row['設施名稱']}-{ df.iloc[index+1]['設施名稱']}"

def map_accident_with_road_section():
    for i in range(1, 4):
        df = pd.read_csv(f"A{i}_accident.csv", encoding='utf-8')
        new_df = pd.DataFrame(
            columns=['Date', 'Time', 'Class', 'RoadSection', 'Direction'])

        for index, row in df.iterrows():
            if not pd.isnull(row['公里']):
                row['公里'] = int(row['公里'])
                highway, ai, kilometer, direction = row['路線'], row['事故類別'], row['公里'], 'N' if '北側' in row['向'] else 'S'
                if row[' 道路型態'] == "高架道路" and highway in "國道1號":
                    if kilometer > 71:
                        continue
                    if highway in ["國道1號"]:
                        if kilometer < 13:
                            continue
                        else:
                            highway = highway+"_高架"
                            location = detect_location(kilometer, highway)
                elif highway in ["國道1號", "國道3號", "國道5號"]:
                    location = detect_location(kilometer, highway)
                else:
                    continue

                date = datetime.strptime(
                    f"{int(row['年'])}-{int(row['月'])}-{int(row['日'])}", '%Y-%m-%d')
                time = datetime.strptime(
                    f"{int(row['時'])}:{int(row['分'])}:{int(row['秒'])}", '%H:%M:%S')
                minute = 5 * (time.minute // 5)
                time = f"{time.hour:02d}:{minute:02d}"

                if new_df.empty:
                    new_df = pd.DataFrame({'Date': [date], 'Time': [time], 'Class': [ai], 'RoadSection': [
                                        location], 'Highway': [highway], 'Direction': [direction]})
                else:
                    new_df = pd.concat([new_df, pd.DataFrame({'Date': [date], 'Time': [time], 'Class': [ai], 'RoadSection': [
                                    location], 'Highway': [highway], 'Direction': [direction]})], ignore_index=True)

        accident_info_file_name = f'accident{i}_info.csv'
        new_df.to_csv(accident_info_file_name, index=False, encoding='utf-8-sig')
        print(f"{accident_info_file_name} 已生成。")

if __name__ == '__main__':
    excel_to_csv()
    edit_error_rows()
    map_accident_with_road_section()