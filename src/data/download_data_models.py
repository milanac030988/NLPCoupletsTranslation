import requests
import zipfile
import os
import argparse
import hashlib
import configparser
from tqdm import tqdm


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def md5_file(file_path):
    """Tính toán MD5 checksum của một tệp với xử lý dòng mới đồng nhất"""
    hasher = hashlib.md5()
    with open(file_path, 'rb') as file:
        while True:
            data = file.read(65536)  # Đọc file theo từng khối (64KB)
            if not data:
                break
            # Xử lý dòng mới thành '\n' để đồng nhất giữa các nền tảng
            data = data.replace(b'\r\n', b'\n')
            hasher.update(data)
    return hasher.hexdigest()

def md5_directory(directory_path):
    """Tính toán MD5 checksum cho toàn bộ thư mục một cách nhất quán trên nhiều nền tảng"""
    hasher = hashlib.md5()
    for root, dirs, files in os.walk(directory_path):
        # Chuẩn hóa đường dẫn và sắp xếp để duyệt thư mục nhất quán
        normalized_root = root.replace(os.sep, '/')
        hasher.update(normalized_root.encode('utf-8'))
        for file_name in sorted(files):
            file_path = os.path.join(root, file_name).replace(os.sep, '/')
            file_hash = md5_file(file_path)
            # Cập nhật hash của tệp vào hash tổng của thư mục
            hasher.update(file_name.encode('utf-8'))
            hasher.update(file_hash.encode('utf-8'))
        for dir_name in sorted(dirs):
            hasher.update(dir_name.encode('utf-8'))
    return hasher.hexdigest()

def compare_md5_checksum(directory_path, checksum_file):
    """So sánh MD5 checksum hiện tại với giá trị đã lưu trữ"""
    current_md5 = md5_directory(directory_path)
    with open(checksum_file, 'r') as f:
        stored_md5 = f.readline().strip().split(': ')[1]

    if current_md5 == stored_md5:
        return True
    else:
        return False

def store_md5_checksum(directory_path, output_file):
    """Lưu trữ MD5 checksum vào file"""
    md5_hash = md5_directory(directory_path)
    with open(output_file, 'w') as f:
        f.write(f"MD5 checksum for directory '{directory_path}': {md5_hash}\n")
    print(f"MD5 checksum stored in {output_file}")

def download_and_extract_zip(url, extract_to='.'):
    if os.path.exists(os.path.join(SCRIPT_DIR, "md5_checksum.txt")): 
         if compare_md5_checksum(extract_to, os.path.join(SCRIPT_DIR, "md5_checksum.txt")):
            print("Models đã được download")
            return
    # Tạo tên file tạm thời để lưu file zip
    local_zip_file = os.path.join(extract_to, "temp.zip")
    
    # Bước 1: Tải file zip về
    print(f"Downloading {url}...")

    # Sử dụng proxies nếu cần thiết
    proxies = { 
        "http": "", 
        "https": "", 
        "ftp": ""
    }

    # Gửi yêu cầu HTTP GET và mở một stream
    response = requests.get(url, proxies=proxies, stream=True)
    
    # Kiểm tra nếu URL không trỏ tới file ZIP
    if 'text/html' in response.headers.get('Content-Type', ''):
        raise ValueError("URL không trỏ tới file ZIP mà trỏ tới một trang web HTML.")
    
    # Kiểm tra nếu có lỗi xảy ra khi tải
    response.raise_for_status()
    
    # Lấy kích thước file từ headers để sử dụng với tqdm
    total_size = int(response.headers.get('Content-Length', 0))

    # Hiển thị thanh tiến trình với tqdm
    with open(local_zip_file, 'wb') as file, tqdm(
        desc="Downloading",
        total=total_size,
        unit='B',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        # Đọc file theo từng chunk và cập nhật thanh tiến trình
        for chunk in response.iter_content(1024):  # Đọc mỗi chunk 1024 bytes
            file.write(chunk)
            bar.update(len(chunk))
    
    print(f"Downloaded to {local_zip_file}")
    
    # Bước 2: Giải nén file zip
    print(f"Extracting {local_zip_file} to {extract_to}...")
    with zipfile.ZipFile(local_zip_file, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    print(f"Extracted to {extract_to}")
    
    # Xóa file zip tạm thời sau khi giải nén
    os.remove(local_zip_file)
    print(f"Removed temporary file {local_zip_file}")
    
    store_md5_checksum(extract_to, os.path.join(SCRIPT_DIR, "md5_checksum.txt"))



# Ví dụ sử dụng
DATA_URL = "https://bit.ly/nlp_couplets_raw_images"
MODELS_URL = "https://bit.ly/nlp_couplets_translate_model"
DATA_FOLDER = os.environ.get("RAW_DATA_DIR")
MODELS_FOLDER = os.environ.get("MODELS_DIR")
# os.makedirs(DATA_FOLDER, exist_ok=True)
# os.makedirs(MODELS_FOLDER, exist_ok=True)

# download_and_extract_zip(DATA_URL, DATA_FOLDER)
# download_and_extract_zip(MODELS_URL, MODELS_FOLDER)

def parse_arguments():
   # Initialize the argument parser
   parser = argparse.ArgumentParser(description="Download raw data và models.")
    
   # Define command-line arguments
   parser.add_argument('--dataUrl', default="", type=str, help="Comma-separated list of input CSV files.")
   parser.add_argument('--modelsUrl', default="", type=str, help="Output CSV file path.")
   
   # Parse the arguments
   args = parser.parse_args()

   # Return parsed arguments
   return args

def read_config(config_file='config.ini'):
   # print(os.environ['DATASET_OUTPUT_DIR'])
   # Enable interpolation to allow environment variable substitution
   config = configparser.ConfigParser(os.environ, interpolation=configparser.ExtendedInterpolation())
   config.read(config_file)    
    
   # Read values from the config file, with environment variables substituted
   data_url = config.get('download', 'dataUrl',  vars=os.environ)
   models_url = config.get('download', 'modelsUrl',  vars=os.environ)
    
   return data_url, models_url

def download_data(data_url="", models_url=""):
   if not data_url or not models_url:
      if os.path.exists(os.path.join(SCRIPT_DIR, 'config.ini')):
         print("Reading from config.ini...")
         data_url, models_url = read_config(os.path.join(SCRIPT_DIR, 'config.ini'))
      else:
         raise ValueError("No command-line arguments provided and config.ini not found.")
   # else:
   #    data_url = args.dataUrl
   #    models_url = args.modelsUrl
   
   if data_url:
      os.makedirs(DATA_FOLDER, exist_ok=True)
      download_and_extract_zip(data_url, DATA_FOLDER)

   if models_url:
      os.makedirs(MODELS_FOLDER, exist_ok=True)
      download_and_extract_zip(models_url, MODELS_FOLDER)

if __name__ == "__main__":
   args = parse_arguments()
   download_data(args.dataUrl, args.modelsUrl)