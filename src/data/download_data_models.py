import requests
import zipfile
import os

def download_and_extract_zip(url, extract_to='.'):
    # Tạo tên file tạm thời để lưu file zip
    local_zip_file = os.path.join(extract_to, "temp.zip")

    # Bước 1: Tải file zip về
    print(f"Downloading {url}...")
    proxies = { 
              "http"  : "", 
              "https" : "", 
              "ftp"   : ""
            }
    response = requests.get(url, proxies=proxies)
    if'text/html'in response.headers.get('Content-Type', ''):
        raise ValueError("URL không trỏ tới file ZIP mà trỏ tới một trang web HTML.")
    response.raise_for_status()  # Kiểm tra nếu có lỗi xảy ra khi tải# Lưu file zip về thư mục đích
    with open(local_zip_file, 'wb') as file:
      file.write(response.content)
    print(f"Downloaded to {local_zip_file}")

    # Bước 2: Giải nén file zip
    print(f"Extracting {local_zip_file} to {extract_to}...")
    with zipfile.ZipFile(local_zip_file, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    print(f"Extracted to {extract_to}")

    # Xóa file zip tạm thời sau khi giải nén
    os.remove(local_zip_file)
    print(f"Removed temporary file {local_zip_file}")

# Ví dụ sử dụng
DATA_URL = "https://bit.ly/nlp_couplets_raw_images"
MODELS_URL = "https://bit.ly/nlp_couplets_translate_model"
DATA_FOLDER = os.environ.get("RAW_DATA_DIR")
MODELS_FOLDER = os.environ.get("MODELS_DIR")
# os.makedirs(extract_to_folder, exist_ok=True)

download_and_extract_zip(DATA_URL, DATA_FOLDER)
download_and_extract_zip(MODELS_URL, MODELS_FOLDER)
