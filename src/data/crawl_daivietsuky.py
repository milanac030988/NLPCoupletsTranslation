from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json
import time

# Khởi tạo trình duyệt Selenium (nên cài ChromeDriver phù hợp với phiên bản Chrome của bạn)
driver = webdriver.Chrome()

def extract_text_from_element(element):
    """
    Hàm này để lấy text từ phần tử <td> như đã mô tả trong yêu cầu.
    """
    cnsv_text = ''
    vi_text = ''
    
    try:
        # Tìm và tách nội dung phần tử chứa chữ Hán
        cnsv_element = element.find_element(By.CSS_SELECTOR, 'td[align="justify"][width="60%"]')
        cnsv_text = cnsv_element.text

        # Tìm và tách nội dung phần tử chứa dịch Quốc Ngữ
        vi_element = element.find_element(By.CSS_SELECTOR, 'td[align="justify"][colspan="2"]')
        vi_text = vi_element.text

    except Exception as e:
        print(f"Lỗi khi tách nội dung: {e}")

    return cnsv_text, vi_text

def get_content_from_urls(urls):
    """
    Truy cập từng URL trong danh sách đã trích xuất, thu thập dữ liệu từ tất cả các trang
    """
    data = []

    for url in urls:
        driver.get(url)
      #   time.sleep(2)  # Chờ trang tải

        # Xử lý để truy cập các trang bằng cách nhấp vào các nút
        page_number = 1
        while True:
            try:
                # Chờ phần tử cần tìm xuất hiện
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'td[align="justify"]')))

                # Dùng BeautifulSoup để phân tích trang hiện tại
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                # Lấy nội dung từ các ô chứa "Tách câu và Phiên âm" và "Dịch Quốc Ngữ"
                elements_cnsv = soup.select('td[align="justify"][width="60%"]')
                elements_vi = soup.select('td[align="justify"][colspan="2"]')

                for cnsv, vi in zip(elements_cnsv, elements_vi):
                    cnsv_text = cnsv.get_text(separator=" ", strip=True)
                    vi_text = vi.get_text(separator=" ", strip=True)
                    data.append({
                        "cnsv": cnsv_text,
                        "vi": vi_text
                    })

                # Tìm nút "Trang tiếp theo" bằng JavaScript và nhấp vào
                next_button = driver.find_element(By.XPATH, f'//a[contains(@href, "javascript:GotoPage({page_number})")]')
                driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                time.sleep(1)  # Chờ cho cuộn xuống
                next_button.click()
                page_number += 1
               #  time.sleep(2)  # Đợi trang tiếp theo tải
            except Exception as e:
                print(f"Không tìm thấy trang tiếp theo hoặc xảy ra lỗi: {e}")
                break

    return data

def get_data_from_url(url):
    """
    Truy cập trang chứa danh sách các liên kết, thu thập tất cả các URL và sau đó truy cập từng URL để lấy nội dung.
    """
    driver.get(url)
   #  time.sleep(2)  # Chờ trang tải

    # Dùng BeautifulSoup để phân tích trang hiện tại và tìm tất cả các URL từ <ul class="list-unstyled">
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    ul_element = soup.find('ul', class_='list-unstyled')
    links = ul_element.find_all('a', href=True)

    # Tạo danh sách các URL đầy đủ để truy cập
    base_url = "https://chunom.net"  # Thay thế bằng phần đầu của URL gốc nếu cần
    urls = [base_url + link['href'] for link in links]

    # Lấy nội dung từ các URL đã thu thập được
    data = get_content_from_urls(urls)
    return data

def main(url_list):
    """
    Hàm chính để chạy việc thu thập dữ liệu từ danh sách các URL.
    """
    all_data = []

    for url in url_list:
        try:
            data = get_data_from_url(url)
            all_data.extend(data)
        except Exception as e:
            print(f"Lỗi khi xử lý URL {url}: {e}")

    # Lưu dữ liệu vào file JSON
    with open('output_data.json', 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)

    print("Hoàn thành thu thập dữ liệu và lưu vào 'output_data.json'.")

# Danh sách các URL cần xử lý (URL chứa danh sách các liên kết)
url_list = [
    "https://chunom.net/Dai-Viet-su-ky-toan-thu/Quyen-thu.html",
    "https://chunom.net/Dai-Viet-su-ky-toan-thu/Ngoai-ky-toan-thu.html",
    "https://chunom.net/Dai-Viet-su-ky-toan-thu/Ban-ky-toan-thu.html",
    "https://chunom.net/Dai-Viet-su-ky-toan-thu/Ban-ky-thuc-luc.html",
    "https://chunom.net/Dai-Viet-su-ky-toan-thu/Ban-ky-tuc-bien.html"
]

# Chạy chương trình
main(url_list)

# Đóng trình duyệt khi xong
driver.quit()
