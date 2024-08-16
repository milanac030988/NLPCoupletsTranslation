import time
import json
import csv
import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# Hàm tạo driver selenium
def create_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Chạy chế độ không hiển thị trình duyệt
    options.add_argument('--log-level=3')  # Giảm bớt log thông tin
    options.add_experimental_option('excludeSwitches', ['enable-logging'])  # Tắt log không mong muốn
    driver = webdriver.Chrome(options=options)
    return driver

# Hàm để chia nhỏ list thành các group con
def split_list(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

# Hàm để kiểm tra và đóng quảng cáo
def close_ad(driver):
    try:
        close_button = WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "span.aanetwork-pto-btnclose-319"))
        )
        close_button.click()
        # print("Closed advertisement")
    except:
        pass
        # print("No advertisement found or failed to close it")

# Hàm JavaScript để thêm văn bản vào textarea
JS_ADD_TEXT_TO_INPUT = """
  var elm = arguments[0], txt = arguments[1];
  elm.value += txt;
  elm.dispatchEvent(new Event('change'));
  """

# Hàm để lấy kết quả từ trang web
def get_translations(driver, group):
    driver.get("https://hvdic.thivien.net/transcript.php")
    # time.sleep(2)  # Đợi trang load

    # Kiểm tra và đóng quảng cáo nếu có
    close_ad(driver)

    # # Tìm và nhập dữ liệu vào textarea
    # textarea = driver.find_element(By.ID, "han_input")
    # textarea.send_keys(''.join(group))

    # Tìm và nhập dữ liệu vào textarea
    textarea = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "han_input"))
    )
    # Sử dụng JavaScript để nhập dữ liệu vào textarea
    driver.execute_script(JS_ADD_TEXT_TO_INPUT, textarea, ''.join(group))
    
    # Cuộn trang để đảm bảo nút "Thực hiện" hiện ra trong viewport
    driver.execute_script("arguments[0].scrollIntoView(true);", textarea)
    
    # Nhấn nút Thực hiện
    convert_button = driver.find_element(By.ID, "convert")
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "convert")))
    convert_button.click()
    
     # Đợi kết quả load bằng cách chờ phần tử con xuất hiện trong kết quả
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div#result-in i"))
    )

    # Lấy dữ liệu kết quả
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    han_elements = soup.select("div#result-in i")
    latin_elements = soup.select("div#result-out i")
    
    translations = []
    for han, latin in zip(han_elements, latin_elements):
        hanzi = han.text
        han_viet = latin.text
        if hanzi != han_viet:
            translations.append((hanzi, han_viet))
    print(".", end='', flush=True)
    return translations

# Hàm lưu dữ liệu vào CSV, JSON, SQLite
def save_to_files(data):
    # Lưu vào CSV
    with open('dictionary.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['cn', 'sv'])
        csvwriter.writerows(data)

    # Lưu vào JSON
    with open('dictionary.json', 'w', encoding='utf-8') as jsonfile:
        json.dump([{'cn': k, 'sv': v} for k, v in data], jsonfile, ensure_ascii=False, indent=4)

    # Lưu vào SQLite
    conn = sqlite3.connect('dictionary.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS translations (cn TEXT, sv TEXT)''')
    cursor.executemany('INSERT INTO translations VALUES (?, ?)', data)
    conn.commit()
    conn.close()

# Hàm chính
def main():
    unicode_ranges = [
        (0x4E00, 0x9FFF),
        (0x3400, 0x4DBF),
        (0x20000, 0x2A6DF),
        (0x2A700, 0x2B73F),
        (0x2B740, 0x2B81F),
        (0x2B820, 0x2CEAF),
        (0x2CEB0, 0x2EBEF),
        (0x30000, 0x3134F),
        (0x31350, 0x323AF),
        (0x2EBF0, 0x2EE5F),
        (0xF900, 0xFAFF)
    ]
    
    hanzi_list = []
    for start, end in unicode_ranges:
        hanzi_list.extend([chr(i) for i in range(start, end + 1)])
    groups = list(split_list(hanzi_list, 1000))
    
    driver = create_driver()
    
    all_translations = []
    for group in groups:
        translations = get_translations(driver, group)
        all_translations.extend(translations)
    
    driver.quit()
    
    save_to_files(all_translations)
    print("Data saved successfully.")

if __name__ == "__main__":
    main()
