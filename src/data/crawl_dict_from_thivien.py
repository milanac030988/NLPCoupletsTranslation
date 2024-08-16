import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import time
import re

# Hàm để lấy dữ liệu từ từ điển online
def fetch_data(unicode_code):
    hanzi = chr(unicode_code)
    url = f'https://hvdic.thivien.net/whv/{hanzi}'
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        meaning_div = soup.find('div', class_='hvres-meaning')
        if meaning_div:
            # Tìm phần tử chứa văn bản "Âm Hán Việt:"
            sv_text = meaning_div.find(string=re.compile(r"Âm Hán Việt:"))
            if sv_text:
                # Lấy giá trị kế tiếp của nó
                sv = sv_text.find_next().get_text(strip=True)
                detail = meaning_div.get_text(separator='\n', strip=True)
                print(".", end='', flush=True)
                return hanzi, sv, detail
        print("x", end='', flush=True)
    if response.status_code != 200:
      print("e", end='', flush=True)                
    return None

# Khởi tạo danh sách để lưu dữ liệu
data = []

# Dải mã Unicode của Hán tự (ví dụ: CJK Unified Ideographs)
unicode_start = 0x6A22
unicode_end = 0x7F38  # Giới hạn nhỏ để demo, bạn có thể mở rộng


stop = False
# Lặp qua các mã Unicode và lấy dữ liệu
for unicode_code in range(unicode_start, unicode_end + 1):
    try:
      result = fetch_data(unicode_code)
    except requests.exceptions.ConnectionError as ex:
      break
    if result:
        hanzi, sv, detail = result
        data.append({'cn': hanzi, 'sv': sv, 'detail': detail})
    time.sleep(0.5)  # Thêm thời gian chờ giữa các request để tránh bị chặn

# Lưu dữ liệu thành file JSON
json_file_path = 'output2.json'
with open(json_file_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

# Lưu dữ liệu thành file CSV
df = pd.DataFrame(data)
csv_file_path = 'output2.csv'
df.to_csv(csv_file_path, index=False, encoding='utf-8-sig')

print(f"Data has been successfully saved to {json_file_path} and {csv_file_path}")
