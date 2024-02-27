#偵測站代碼匯入.json
import json

# 讀取文字檔案中的代碼和名稱，並將其組成一個字典
mapping = {}
with open('mapping.txt', 'r', encoding='utf-8') as file:
    for line in file:
        code, name = line.strip().split(' ', 1)
        mapping[code] = name

# 將字典寫入到.json檔案
with open('test.json', 'w', encoding='utf-8') as file:
    json.dump(mapping, file, ensure_ascii=False, indent=4)

print("映射已寫入到 'mapping.json'")
