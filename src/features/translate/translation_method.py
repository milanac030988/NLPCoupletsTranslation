# *******************************************************************************
#
# File: translation_method.py
#
# Initially created by Nguyen Huynh Tri Cuong / Aug 2024
#
# Description:
#   Abstract class cho các method dịch kế thừa. Khi implement các method dịch,
#   chỉ cần kế thừa lớp TranslateMethod, thay thuộc tính _TRANSLATION_METHOD bằng 
#   tên của method dịch, overwrite method translate và quit. Phương pháp dịch sẽ 
#   được tự động load vào GUI của application.
#
# History:
#
# 01.08.2024 / V 0.1 / Nguyen Huynh Tri Cuong
# - Khởi tạo
#
# *******************************************************************************
import os
from abc import ABC, abstractmethod


# Abstract class TranslateMethod
class TranslateMethod(ABC):
   
   _TRANSLATION_METHOD = "Abstract"
   SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

   @classmethod
   def get_method_name(cls):
      return cls._TRANSLATION_METHOD

   @abstractmethod
   def translate(self, text):
      pass

   @abstractmethod
   def quit(self):
      pass