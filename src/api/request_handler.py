import logging
import os
from features.translate.translation_manager import TranslationManager
from utils import Utils


# Thiết lập logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RequestHandler:
   SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
   def __init__(self):
      self.running = True
      self.translation_manager = TranslationManager()

   def start(self):
      self.running = True
      logger.info("RequestHandler started.")
      # self.translation_methods = self.load_all_trans_supported_method()
      # self.translation_method_instances = {}
      self.translation_manager = TranslationManager()

   def translate(self, han_sentence, trasnslation_method_name):
      # if trasnslation_method_name not in self.translation_method_instances:
      #    self.translation_method_instances[trasnslation_method_name] = self.translation_methods[trasnslation_method_name]()
      translation_method = self.translation_manager.get_translation_method(trasnslation_method_name)
      if translation_method:
         sv_translation = translation_method.translate(han_sentence)#
         sv_translation = Utils().extract_json(sv_translation)
         # Xử lý xuống hàng và viết hoa đầu câu
         sv_lines = sv_translation['sv'].split('\n')
         sv_lines = [line.strip() for line in sv_lines]
         formatted_sv_translation = '\n'.join(sv_lines)        
         vi_lines = sv_translation['vi'].split('\n')
         vi_lines = [line.strip() for line in vi_lines]
         formatted_vi_translation = '\n'.join(vi_lines)
         return formatted_sv_translation, formatted_vi_translation
   
   # def load_all_trans_supported_method():
   #    all_libs = [TranslateMethod.SCRIPT_DIR]
   #    # sys.path.extend(all_libs)
   #    for module_loader, name, is_pkg in pkgutil.walk_packages(all_libs):
   #       # noinspection PyBroadException
   #       try:
   #          print(name)
   #          if not is_pkg and not name.startswith("setup") and "translation_method" in name:
   #             importlib.import_module("features.translate." + name)
   #          elif "translation_method" in name:
   #             _module = module_loader.find_module(name).load_module(name)
   #       except Exception as _ex:
   #          print(_ex)
   #          pass

   
   def stop(self):
      self.running = False
      logger.info("RequestHandler stopped.")

   def handle_translate(self, source: str, method: str):
      if not self.running:
         raise Exception("Handler is not running.")
      
      # sv_translation = f"Translated_sv_{source}"
      # vi_translation = f"Translated_vi_{source}"
      sv_translation , vi_translation = self.translate(source, method)     
         
      logger.info(f"Translation requested: {source}, method: {method}")
      
      return {
         "type": "translate_rep",
         "target": {
            "sv": sv_translation,
            "vi": vi_translation
         },
         "method": method
      }

   def handle_contribute(self, cn: str, sv: str, vi: str):
      if not self.running:
         raise Exception("Handler is not running.")
      
      # Giả sử có logic kiểm tra đóng góp ở đây
      result = "accept" if cn and sv and vi else "reject"
      logger.info(f"Contribution requested: cn={cn}, sv={sv}, vi={vi}")
      
      return {
         "type": "contribute_rep",
         "result": result
      }

# Tạo instance của RequestHandler để sử dụng trong các file khác
handler_instance = RequestHandler()
