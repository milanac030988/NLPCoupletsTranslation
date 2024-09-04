import re
import string
import json
import stat
import os
import subprocess

class Utils:
   """
Class to implement utilities for supporting development.
   """
   LINUX_OS = "linux"
   WINDOWS_OS = "windows"

   def __init__(self):
      """
Empty constructor.
      """
      pass

   @staticmethod
   def get_all_descendant_classes(cls, should_include_root_class=False):
      """
Get all descendant classes of a class

**Arguments:**
         cls: Input class for finding descendants.

**Returns:**

  / *Type*: list /

  Array of descendant classes.
      """
      trace_class_list = cls.__subclasses__()
      descendant_classes_list = []
      if should_include_root_class:
         descendant_classes_list.append(cls)
      for subclass in trace_class_list:
         descendant_classes_list.append(subclass)
         if len(subclass.__subclasses__()) > 0:
            trace_class_list.extend(subclass.__subclasses__())
      return set(descendant_classes_list)

   @staticmethod
   def get_all_sub_classes(cls):
      """
Get all children classes of a class

**Arguments:**

* ``cls``

  / *Condition*: required / *Type*: class /

  Input class for finding children.

**Returns:**

  / *Type*: list /

  Array of children classes.
      """
      return set(cls.__subclasses__()).union(
         [s for s in cls.__subclasses__()])

   @staticmethod
   def extract_json(text):
      # Regular expression to match the JSON string
      json_regex = re.compile(r'{\s*"cn":.*?}', re.DOTALL)

      # Find the JSON string in the text
      match = json_regex.search(text)
      json_data = None

      if match:
         json_str = match.group()
         # print("Extracted JSON string:")
         # print(json_str)
        
         # Optionally, you can parse the JSON string into a Python dictionary
         json_data = json.loads(json_str)
   #  else:
   #      print("No suitable answer responsed.")
      return json_data

   @staticmethod
   def is_chinese_char(char):
      """
      Check if a character is a Chinese character based on Unicode ranges.
      
      :param char: The character to check.
      :return: True if the character is Chinese, False otherwise.
      """
      ranges = [
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
      return any(start <= ord(char) <= end for start, end in ranges)

   @staticmethod
   def is_chinese(text):
      """
      Check if a sentence contains a Chinese character based on Unicode ranges.
      
      :param text: The sentence to check.
      :return: True if the sentence contains Chinese character, False otherwise.
      """      
      return any(Utils.is_chinese_char(char) for char in text)

   @staticmethod
   def normalize_text(text):
      """
      Normalize the text by converting to lowercase and removing punctuation.
      """
      text = text.lower()
      text = text.translate(str.maketrans('', '', string.punctuation))
      return text

   @staticmethod
   def capitalize_after_newline(text):
      # Tách các đoạn văn bản thành danh sách các câu nhỏ hơn sau mỗi dấu xuống dòng
      sentences = text.split('\n')
      
      # Viết hoa chữ cái đầu của mỗi câu và giữ nguyên các phần còn lại
      capitalized_sentences = [sentence.strip()[0].upper() + sentence.strip()[1:] if sentence else '' for sentence in sentences]
      # Ghép lại các câu với dấu xuống dòng
      return '\n'.join(capitalized_sentences)

   @staticmethod
   def make_executable(file_path):
      """
      Kiểm tra xem file có thể thực thi không. Nếu không, đặt quyền thực thi cho file.
      
      Args:
         file_path (str): Đường dẫn đến file cần kiểm tra và thay đổi quyền truy cập.
      """
      # Kiểm tra xem file có tồn tại không
      if not os.path.isfile(file_path):
         return

      # Lấy thông tin file
      st = os.stat(file_path)

      # Kiểm tra quyền thực thi
      is_executable = bool(st.st_mode & stat.S_IXUSR)  # Kiểm tra quyền thực thi của chủ sở hữu (user)

      if not is_executable:
         # Thêm quyền thực thi cho chủ sở hữu (user), nhóm (group), và người dùng khác (others)
         os.chmod(file_path, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

   @staticmethod
   def make_executable_wsl(file_path):
      """
      Sử dụng wsl.exe để kiểm tra xem file có thể thực thi trên WSL không. 
      Nếu không, đặt quyền thực thi cho file trên WSL.
      
      Args:
         file_path (str): Đường dẫn đến file trên hệ thống tệp WSL cần kiểm tra và thay đổi quyền truy cập.
      """
      try:
         # Kiểm tra xem file có quyền thực thi không trên WSL
         check_command = f"test -x {file_path} && echo 'Executable' || echo 'Not Executable'"
         result = subprocess.run(['wsl.exe', check_command], capture_output=True, text=True)
         
         if 'Not Executable' in result.stdout:
               # Nếu file không có quyền thực thi, thêm quyền thực thi
               subprocess.run(['wsl.exe', f"chmod +x {file_path}"])
               # print(f"Đã đặt quyền thực thi cho file '{file_path}' trên WSL.")
      except subprocess.CalledProcessError as e:
         print(f"Lỗi khi thực thi lệnh trên WSL: {e}")
