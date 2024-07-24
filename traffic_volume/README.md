# Traffic Volume
這個程式可以取得高速公路局交通資料庫的交通資訊並整理成以下形式之表格，最後自動存入database
| DateTime | RoadSection | Highway | Direction | Midpoint | M03A_PCU | M03A_PCU_BigGap | M05A_SpaceMeanSpeed | M05A_PCU | Accident | Holiday | Week|
| -------- | -------- | -------- | -------- | -------- | -------- | -------- | -------- | ------- | ------ | ------ | -------- |
| 2023-06-01 00:00:00 | 基隆端-基隆交流道 | 國道1號 | N | 0.5 | 39.7 |  | 92.4 | 29.2 | 0 |  | Thursday |
| 2023-06-01 00:00:00 | 基隆端-基隆交流道 | 國道1號 | S | 0.5 | 28.3 |  | 92.9 | 22.4 | 0 |  |Thursday |
| 2023-06-01 00:00:00 | 基隆交流道-八堵交流道 | 國道1號 | N | 1.5 | 39.7 |  | 92.4 | 29.2 | 0 |  | Thursday |
| 2023-06-01 00:00:00 | 基隆交流道-八堵交流道 | 國道1號 | S | 1.5 | 28.3 |  | 92.9 | 22.4 | 0 |  | Thursday | 
| ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |

## Getting Started

### Install packages

```bash
#!/bin/bash

# Check if Python 3.10 is installed
if ! command -v python3.10 &> /dev/null
then
    echo "Python 3.10 is required but not found. Please install it first."
    exit 1
fi

# Upgrade pip
python3.10 -m pip install --upgrade pip

# Install packages
python3.10 -m pip install pandas==2.2.1
python3.10 -m pip install mariadb==1.1.10
python3.10 -m pip install numpy==1.26.4
python3.10 -m pip install PyMuPDF==1.24.7
python3.10 -m pip install requests==2.25.1

# Check if all installations were successful
if [ $? -eq 0 ]; then
    echo "All packages have been installed successfully."
else
    echo "An error occurred during package installation. Please check the output above for details."
fi
```

### Execution
1. 修改`database_authentication.json`為自定義設定
2. 執行`dataframe_to_mariadb.py`
