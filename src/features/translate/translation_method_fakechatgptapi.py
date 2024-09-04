# *******************************************************************************
#
# File: translation_method_fakechatgptapi.py
#
# Initially created by Nguyen Huynh Tri Cuong / Aug 2024
#
# Description:
#   Implementation cho phương thức dịch sử dụng Fake ChatGPT API.
#
# History:
#
# 01.08.2024 / V 0.1 / Nguyen Huynh Tri Cuong
# - Khởi tạo
#
# *******************************************************************************
from translation_method import TranslateMethod
from libs.FakeChatGPTAPI.fake_chatgpt_api import FakeChatGPTAPI

class TranslateMethodFakeChatGPTAPI(TranslateMethod):

   _TRANSLATION_METHOD = "FakeChatGPTAPI"

   def __init__(self):
      self.fake_api = FakeChatGPTAPI()
   
   def __del__(self):
      self.fake_api.delete_context()

   def translate(self, han_sentence):
      return self.fake_api.send_request(han_sentence)

   def quit(self):
      self.fake_api.delete_context()