from features.translate.translation_method import TranslateMethod
from utils import Utils
import subprocess
import sqlite3
import os
import json
import re
import platform
import uuid
import pexpect
# import wexpect


class TranslateMethodMoses(TranslateMethod):

   _TRANSLATION_METHOD = "Moses"
   SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
   DICT_FILE_PATH = os.path.join(os.environ.get("REFS_DIR"), 'Hanzi2HanVietDB.db')
   MOSES_BIN = os.path.join(os.environ.get("MODELS_DIR"), 'moses/bin/moses')
   MOSES_MODEL_VI = os.path.join(os.environ.get("MODELS_DIR"), 'moses/CN2VI/model/moses.ini')
   MOSES_MODEL_SV = os.path.join(os.environ.get("MODELS_DIR"), 'moses/CN2SV/model/moses.ini')

   def __init__(self):
      self.conn = sqlite3.connect(TranslateMethodMoses.DICT_FILE_PATH)
      self.moses_sv_process = None
      self.moses_vi_process = None
      self.create_moses_process()

   def create_moses_process(self):
      current_os = platform.system()
      if current_os == "Windows":
         self.moses_sv_process =  wexpect.spawn(f'wsl.exe {self._windows_to_wsl_path(TranslateMethodMoses.MOSES_BIN)} -f {self._windows_to_wsl_path(TranslateMethodMoses.MOSES_MODEL_SV)}', encoding="utf-8")
         self.moses_vi_process =  wexpect.spawn(f'wsl.exe {self._windows_to_wsl_path(TranslateMethodMoses.MOSES_BIN)} -f {self._windows_to_wsl_path(TranslateMethodMoses.MOSES_MODEL_VI)}', encoding="utf-8")         
      elif current_os == "Linux":
         self.moses_sv_process =  pexpect.spawn(f'{self._windows_to_wsl_path(TranslateMethodMoses.MOSES_BIN)} -f {self._windows_to_wsl_path(TranslateMethodMoses.MOSES_MODEL_SV)}', encoding="utf-8")
         self.moses_vi_process =  pexpect.spawn(f'{self._windows_to_wsl_path(TranslateMethodMoses.MOSES_BIN)} -f {self._windows_to_wsl_path(TranslateMethodMoses.MOSES_MODEL_VI)}', encoding="utf-8")

   def extract_translation(self, text):
      # Biểu thức chính quy để trích xuất văn bản giữa "BEST TRANSLATION:" và "[" với dãy số bên trong
      match = re.search(r'BEST TRANSLATION:\s*(.*?)\s*\[\d+\]', text, re.DOTALL|re.MULTILINE)
      
      # Nếu tìm thấy kết quả, trả về phần văn bản trích xuất được
      if match:
         return match.group(1).strip()
      else:
         return None
   
   def __del__(self):
      if self.moses_sv_process:
         self.moses_sv_process.terminate()

      if self.moses_vi_process:
         self.moses_vi_process.terminate()
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

   def _windows_to_wsl_path(self, windows_path):
      # Replace backslashes with forward slashes
      wsl_path = windows_path.replace("\\", "/")
      
      # Convert the drive letter to WSL format (e.g., C:\ -> /mnt/c/)
      if len(wsl_path) > 1 and wsl_path[1] == ':':
         drive_letter = wsl_path[0].lower()
         wsl_path = f"/mnt/{drive_letter}{wsl_path[2:]}"
      
      return wsl_path

   def _translate_use_moses(self, han_sentence, moses_process):
      # print(f"input before:'{han_sentence}'")
      han_sentence = self.ensure_spaces_between_hanzi(han_sentence)
      han_sentences = han_sentence.split("\n")
      translated_text = ''
      if moses_process:
         for sentence in han_sentences:
            moses_process.sendline(sentence)
            
             # Chờ cho đến khi dòng 'Translation took ...' xuất hiện
            moses_process.expect(r'Translation took .*', timeout=None)

            # Đọc toàn bộ đầu ra cho đến thời điểm này
            output = moses_process.before
            translated_sentence = self.extract_translation(output)
            if translated_sentence:
               translated_sentence = translated_sentence.replace('\r\n', '')  # Loại bỏ '\r\n'
               translated_sentence = translated_sentence.replace('\n', '')    # Loại bỏ '\n'
               # Loại bỏ các phần |UNK|UNK|UNK nếu có
               translated_sentence = translated_sentence.replace("|UNK|UNK|UNK", "").strip()
            else:
               translated_sentence = ''
               print(sentence)

            # Lọc và lấy câu dịch từ các dòng trả về
            # translated_sentence = None
            # lines = output.splitlines()
            # for line in lines:
            #    if "BEST TRANSLATION:" in line:
            #       # translated_sentence = line.split(":", 1)[1].split("[")[0].strip()
            #       translated_sentence =  self.extract_translation(line)
            #       # Loại bỏ các phần |UNK|UNK|UNK nếu có
            #       translated_sentence = translated_sentence.replace("|UNK|UNK|UNK", "").strip()
            #       break

            translated_text += translated_sentence
            translated_text += "\n"
         
         translated_text = translated_text[:-1]
         if translated_text[-1] != ".":
            translated_text += "."
         translated_text = Utils.capitalize_after_newline(translated_text.lower())
         translated_text = self.translate_chinese_in_sentence(translated_text)
      return translated_text

   def translate_chinese_in_sentence(self, sentence):
      translated_sentence = ""
      for char in sentence:
         if Utils.is_chinese_char(char):
               # Nếu là ký tự tiếng Trung, dịch và thay thế nó
               translated_sentence += self.translate_chinese_char(char)
         else:
               # Nếu không, giữ nguyên ký tự
               translated_sentence += char
      return translated_sentence
   
   def translate_chinese_char(self, hanzi):
      trans = hanzi
      conn = sqlite3.connect(TranslateMethodMoses.DICT_FILE_PATH) 
      c = conn.cursor()
      c.execute('SELECT sv FROM translations WHERE cn=?', (hanzi,))
      result = c.fetchone()
      if result:
         trans = result[0]
      conn.close()
      return trans

   # def translate_hanviet(self, han_sentence):     
   #    conn = sqlite3.connect(TranslateMethodMoses.DICT_FILE_PATH) 
   #    c = conn.cursor()
   #    viet_translation = []
   #    for hanzi in han_sentence:
   #       if hanzi == "\n":
   #             viet_translation.append(';\n')
   #       else:
   #             c.execute('SELECT sv FROM translations WHERE cn=?', (hanzi,))
   #             result = c.fetchone()
   #             if result:
   #                viet_translation.append(result[0])
   #             # else:
   #             #    viet_translation.append('[UNKNOWN]')
   #    if viet_translation[-1] != ".":
   #       viet_translation.append(".")

   #    return Utils.capitalize_after_newline(' '.join(viet_translation))
   def translate_hanviet(self, han_sentence):
      translated_text = self._translate_use_moses(han_sentence, self.moses_sv_process)
      return translated_text

   def translate_vietnamese(self, han_sentence):
      translated_text = self._translate_use_moses(han_sentence, self.moses_vi_process)
      return translated_text

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
  

   def quit(self):
      if self.conn:
         self.conn.close()
