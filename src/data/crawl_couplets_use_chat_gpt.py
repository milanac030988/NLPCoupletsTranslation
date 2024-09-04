from fake_chatgpt_api import FakeChatGPTAPI
import os
import argparse
import re


SCRIPT_DIR:str = os.path.dirname(os.path.abspath(__file__))
INI_FILE_PATH:str = os.path.join(SCRIPT_DIR, 'fake_chatgpt_api_img_extract.ini')


# Đường dẫn tới thư mục chứa các ảnh và file output.txt
# image_folder = "D:\\Document\\Master\\NLP\\Project\\data\\raw_data\\MS.K32-5000-CauDoi\\CH\\CauDoiHanNomImg_p2"
output_file = "5000_cau_doi.txt"

# images = [os.path.join(image_folder, f"HanNomCouplets_p2_page-{i:04d}.jpg") for i in range(1, 431)]

fake_api = FakeChatGPTAPI(config_path=INI_FILE_PATH)

start_pattern = "--START EXTRACT--"
end_pattern = "--END EXTRACT--"

def extract_text_between_patterns(text, start_pattern, end_pattern):
    """
    Extracts text between two patterns.
    
    :param text: The input text to search within.
    :param start_pattern: The starting pattern to look for.
    :param end_pattern: The ending pattern to look for.
    :return: The extracted text between the patterns. Returns an empty string if patterns are not found.
    """
    pattern = re.escape(start_pattern) + r'(.*?)' + re.escape(end_pattern)
    matches = re.findall(pattern, text, re.DOTALL)
    concatenated_text = '\n'.join(match.strip() for match in matches)
    return concatenated_text

def parse_arguments():
   parser = argparse.ArgumentParser(description='Thu thập ngữ liệu sử dụng FakeChatGPTAPI.')
   parser.add_argument('-i', '--images_folder', type=str, help='Thư mục chứa ảnh cần trích xuất ngữ liệu.')
   parser.add_argument('-o', '--outfile', type=str, help='Đường dẫn đến file txt đầu ra.')
   parser.add_argument('-s', '--start', type=int, help='Index của ảnh bắt đầu trích xuất ngữ liệu (mặc định là 0).')
   parser.add_argument('-e', '--start', type=int, help='Index của ảnh kết thúc trích xuất ngữ liệu (mặc định là 430).')
   parser.add_argument('-g', '--gap', type=int, help='Số trang bắt đầu đánh số ngữ liệu (mặc định là 0).')
   parser.add_argument('-r', '--range', type=int, help='Số ảnh trích xuất ngữ liệu trong 1 lần (mặc định là 2).')
   parser.add_argument('--use_checkpoint', action='store_true', help='Use checkpoint to resume from last position.')
   return parser.parse_args()

def read_config(config_file='config.ini'):
   config = configparser.ConfigParser(os.environ, interpolation=configparser.ExtendedInterpolation())
   config.read(config_file)
   return config

def get_file_paths(directory):
    # Lấy danh sách đường dẫn đầy đủ của các tệp trong thư mục
    file_paths = [os.path.join(directory, f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    return file_paths

def load_checkpoint():
   if os.path.exists('checkpoint.txt'):
      with open('checkpoint.txt', 'r') as f:
         return int(f.read().strip())
   return None

def save_checkpoint(index):
   with open('checkpoint.txt', 'w') as f:
      f.write(str(index))

def signal_handler(sig, frame):
    global current_index
    print(f"\nReceived signal {sig}. Saving checkpoint and exiting.")
    save_checkpoint(current_index)
    sys.exit(0)

def main():
   global current_index

   # Setup signal handler for Ctrl+C
   signal.signal(signal.SIGINT, signal_handler)

   args = parse_arguments()
    
   # Default values
   images_folder = 'images'
   outfile = './output.txt'
   START = 0
   GAP = 0
   RANGE = 2
   use_checkpoint = args.use_checkpoint
   
   # Read config file if present
   config = read_config(os.path.join(SCRIPT_DIR, 'config.ini'))
    
   if 'crawl_couplets_gpt' in config:
      images_folder = config['crawl_couplets_gpt'].get('images_folder', images_folder, vars=os.environ)
      outfile = config['crawl_couplets_gpt'].get('outfile', outfile, vars=os.environ)
      START = config['crawl_couplets_gpt'].getint('start', START, vars=os.environ)
      GAP = config['crawl_couplets_gpt'].getint('gap', GAP, vars=os.environ)
      RANGE = config['crawl_couplets_gpt'].getint('range', RANGE, vars=os.environ)
    
    # Override with command-line arguments if provided
   if args.images_folder:
      images_folder = args.images_folder
   if args.outfile:
      outfile = args.outfile
   if args.start:
      START = args.start
   if args.gap:
      GAP = args.gap
   if args.range:
      RANGE = args.range

   # Use checkpoint if requested
   if use_checkpoint:
        checkpoint = load_checkpoint()
        if checkpoint is not None:
            START = checkpoint

   # images = [os.path.join(image_folder, f"HanNomCouplets_p2_page-{i:04d}.jpg") for i in range(STA, 431)]
   images = get_file_paths(images_folder)
   try:
      for i in range(START, len(images), RANGE):
         current_index = i
         upload_img_paths = []
         for j in range(RANGE):
            if i + j < len(images):
               image_path = images[i + j]
               upload_img_paths.append(image_path)
         
         fake_api.upload_file(upload_img_paths)
         extracted_text = fake_api.send_request(f"Đánh số trang bắt đầu từ Trang {i + GAP}")
         if not extracted_text:
            print(f"Failed to extract image from {i} to {i + j}")
            raise Exception("Interupt")
         extracted_text = extract_text_between_patterns(extracted_text, start_pattern, end_pattern)
         with open(output_file, "a", encoding="utf-8") as f:
            f.write(extracted_text + "\n\n")
         # Save checkpoint
         save_checkpoint(i)
   except Exception as e:
      print(f"An error occurred: {e}")
      save_checkpoint(current_index)
      raise  # Re-raise the exception after saving checkpoint


if __name__ == '__main__':
   current_index = 0
   main()