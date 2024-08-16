from features.translate.translation_method import TranslateMethod
from utils import Utils
import subprocess
import sqlite3
import os
import json
import re
import platform
import uuid


class TranslateMethodMoses(TranslateMethod):

   _TRANSLATION_METHOD = "Moses"
   SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
   DICT_FILE_PATH = os.path.join(os.environ.get("REFS_DIR"), 'Hanzi2HanVietDB.db')
   MOSES_BIN = os.path.join(os.environ.get("MODELS_DIR"), 'moses/bin/moses')
   MOSES_MODEL = os.path.join(os.environ.get("MODELS_DIR"), 'moses/train/model/moses.ini')

   def __init__(self):
      self.conn = sqlite3.connect(TranslateMethodMoses.DICT_FILE_PATH)
   
   def __del__(self):
      self.quit()

   def translate(self, han_sentence):
      hanviet_sentence = self.translate_hanviet(han_sentence)
      vietnamese_sentence = self.translate_vietnamese(han_sentence)
      response = {
         "cn": han_sentence,
         "sv": hanviet_sentence,
         "vi": vietnamese_sentence
      }

      res = json.dumps(response)

      return json.dumps(response)

   def remove_spaces(self, text):
      return re.sub(r'\s+', '', text)

   def translate_hanviet(self, han_sentence):     
      conn = sqlite3.connect(TranslateMethodMoses.DICT_FILE_PATH) 
      c = conn.cursor()
      viet_translation = []
      for hanzi in han_sentence:
         if hanzi == "\n":
               viet_translation.append(';\n')
         else:
               c.execute('SELECT sv FROM translations WHERE cn=?', (hanzi,))
               result = c.fetchone()
               if result:
                  viet_translation.append(result[0])
               # else:
               #    viet_translation.append('[UNKNOWN]')
      if viet_translation[-1] != ".":
         viet_translation.append(".")

      return Utils.capitalize_after_newline(' '.join(viet_translation))

   def ensure_spaces_between_hanzi(self, text):
      """
      Kiểm tra và thêm khoảng trắng giữa các ký tự Hán tự trong một câu nếu chưa có.

      Tham số:
      text (str): Câu cần kiểm tra và xử lý.

      Trả về:
      str: Câu đã được thêm khoảng trắng giữa các ký tự Hán tự nếu cần thiết.
      """
      hanzi_ranges = [
        (0x4e00, 0x9fff),   # CJK Unified Ideographs
        (0x3400, 0x4dbf),   # CJK Unified Ideographs Extension A
        (0x20000, 0x2a6df), # CJK Unified Ideographs Extension B
        (0x2a700, 0x2b73f), # CJK Unified Ideographs Extension C
        (0x2b740, 0x2b81f), # CJK Unified Ideographs Extension D
        (0x2b820, 0x2ceaf), # CJK Unified Ideographs Extension E
        (0x2ceb0, 0x2ebef), # CJK Unified Ideographs Extension F
        (0x30000, 0x3134f), # CJK Unified Ideographs Extension G
        (0x31350, 0x323af), # CJK Unified Ideographs Extension H
        (0x2ebf0, 0x2ee5f), # CJK Unified Ideographs Extension I
        (0xf900, 0xfaff)    # CJK Compatibility Ideographs
    ]

      # Tạo regex pattern từ các dải mã Unicode
      pattern = ''.join([f'\\u{start:04x}-\\u{end:04x}' for start, end in hanzi_ranges])
      regex_pattern = f'(?<=[{pattern}])(?=[{pattern}])'

      # Thay thế bằng khoảng trắng giữa các ký tự Hán tự nếu chưa có
      return re.sub(regex_pattern, ' ', text)

   def delete_file(self, file_path):
    try:
        os.remove(file_path)
        print(f"File {file_path} has been deleted.")
    except FileNotFoundError:
        print(f"File {file_path} not found.")
    except PermissionError:
        print(f"Permission denied: cannot delete {file_path}.")
    except Exception as e:
        print(f"An error occurred while deleting the file: {e}")

   def create_file_with_uuid(self):
    # Tạo một UUID ngẫu nhiên
    unique_filename = str(uuid.uuid4()) + ".txt"
    
    # Tạo file với tên UUID
    with open(unique_filename, 'w') as file:
        file.write("This is a file with a UUID name.")
    
    print(f"File created: {unique_filename}")
    return unique_filename


   def translate_vietnamese(self, han_sentence):
      # print(f"input before:'{han_sentence}'")
      han_sentence = self.ensure_spaces_between_hanzi(han_sentence)
      # print(f"input trans: {han_sentence}")
      han_sentences = han_sentence.split("\n")
      translated_text = ''
      for sentence in han_sentences:
         # Ghi câu cần dịch vào tệp tạm thời
         trans_file = self.create_file_with_uuid()
         with open(trans_file, 'w', encoding='utf-8') as f:
            f.write(sentence + "\n")
         
         # Gọi Moses để dịch
         current_os = platform.system()
         if current_os == "Windows":
            proc = subprocess.Popen(['wsl.exe', 'bash'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")
         elif current_os == "Linux":
            proc = subprocess.Popen(['bash'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")

         # Gửi lệnh đến shell session
         commands = [f' {TranslateMethodMoses.MOSES_BIN}', 
                     ' -f', 
                     f' {TranslateMethodMoses.MOSES_MODEL}', 
                     ' -input-file', 
                     f' {trans_file}']

         # Gửi từng lệnh một đến shell
         for command in commands:
            proc.stdin.write(command)

         if current_os == "Windows":
            # Đóng stdin để kết thúc session
            proc.stdin.close()

         # Đọc và hiển thị kết quả
         stdout, stderr = proc.communicate()
         translated_text += stdout.strip()
         translated_text += "\n"
         # print(stderr)

         os.remove(trans_file)
         if current_os == "Linux":
            proc.stdin.close()
      # result = subprocess.run(["wsl.exe", '/home/ugc1hc/Master/NLP/mosesdecoder/bin/moses', '-f', 'moses.ini', '-input-file', 'trans.txt'], stdout=subprocess.PIPE, text=True)
      # result = subprocess.run(["wsl.exe", wsl_command], capture_output=True, text=True)
      # Đọc kết quả dịch
      
      return translated_text

   def quit(self):
      if self.conn:
         self.conn.close()
