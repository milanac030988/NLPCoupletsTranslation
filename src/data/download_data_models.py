import requests
import zipfile
import os
import argparse  # Import argparse
import configparser  # Import configparser

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

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
   if 'text/html' in response.headers.get('Content-Type', ''):
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
DATA_FOLDER = os.environ.get("RAW_DATA_DIR", "./data")  # Fallback to "./data" if RAW_DATA_DIR is not set
MODELS_FOLDER = os.environ.get("MODELS_DIR", "./models")  # Fallback to "./models" if MODELS_DIR is not set

def parse_arguments():
   # Initialize the argument parser
   parser = argparse.ArgumentParser(description="Download raw data và models.")
    
   # Define command-line arguments
   parser.add_argument('--dataUrl', default="", type=str, help="URL to download the raw data.")
   parser.add_argument('--modelsUrl', default="", type=str, help="URL to download the models.")
   
   # Parse the arguments
   args = parser.parse_args()

   # Return parsed arguments
   return args

def read_config(config_file='config.ini'):
   # Initialize ConfigParser without passing os.environ directly
   config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
   config.read(config_file)
    
   # Read values from the config file, allowing environment variable substitution when needed
   data_url = config.get('download', 'dataUrl', fallback=None, vars=os.environ)
   models_url = config.get('download', 'modelsUrl', vars=os.environ)
    
   return data_url, models_url

if __name__ == "__main__":
   args = parse_arguments()
   if not args.dataUrl or not args.modelsUrl:
      if os.path.exists(os.path.join(SCRIPT_DIR, 'config.ini')):
         print("Reading from config.ini...")
         data_url, models_url = read_config(os.path.join(SCRIPT_DIR, 'config.ini'))
      else:
         raise ValueError("No command-line arguments provided and config.ini not found.")
   else:
      data_url = args.dataUrl
      models_url = args.modelsUrl
   
   if data_url:
      os.makedirs(DATA_FOLDER, exist_ok=True)
      download_and_extract_zip(data_url, DATA_FOLDER)

   if models_url:
      os.makedirs(MODELS_FOLDER, exist_ok=True)
      download_and_extract_zip(models_url, MODELS_FOLDER)
