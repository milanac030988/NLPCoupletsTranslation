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