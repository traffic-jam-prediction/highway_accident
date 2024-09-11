# WEKA Preprocessing

`integrate_categorized_data.py` 將先前整合的所有資訊，由數值類型資料轉換為類別資料，方便後續使用 weka 做資料分析

`integrate_categorized_data.py` 輸出的檔案格式如下:
| RoadSection | Highway | Direction | Midpoint | M03A_PCU | M03A_PCU_BigGap | M05A_PCU | Accident | Holiday | Week | WindSpeed_Category | Temperature_Category | Humidity_Category | Previous_10min | Previous_20min | Speed | DateTime_1 | DateTime_2 |
| -------- | -------- | -------- | -------- | -------- | -------- | -------- | -------- | ------- | ------ | ------ | -------- | -------- | -------- | -------- | -------- | -------- | -------- |
| 基隆端-基隆交流道 | 國道1號 | N | 0.5 | 低流量 | 差異小 | 低流量 | 不易 | 無放假 | 平日 | medium | medium | low | 無差異 | 無差異 | 車速快 | 0-6 | 離峰 |
| 基隆端-基隆交流道 | 國道1號 | S | 0.5 | 低流量 | 差異小 | 低流量 | 不易 | 無放假 | 平日 | medium | medium | low | 無差異 | 無差異 | 車速快 | 0-6 | 離峰 |
| 基隆交流道-八堵交流道 | 國道1號 | N | 1.5 | 低流量 | 差異小 | 低流量 | 不易 | 無放假 | 平日 | medium | medium | low | 無差異 | 無差異 | 車速快 | 0-6 | 離峰 |
| 基隆交流道-八堵交流道 | 國道1號 | S | 1.5 | 低流量 | 差異小 | 低流量 | 不易 | 無放假 | 平日 | medium | medium | low | 無差異 | 無差異 | 車速快 | 0-6 | 離峰 |
| ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |

