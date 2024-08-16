import logging
from features.translate.translation_method import TranslateMethod
from utils import Utils

# Thiết lập logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RequestHandler:
   SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
   def __init__(self):
      self.running = False

   def start(self):
      self.running = True
      logger.info("RequestHandler started.")
      self.translation_methods = self.load_all_trans_supported_method()
      self.translation_method_instances = {}
   
   def load_all_trans_supported_method(self):
      all_libs = [TranslateMethod.SCRIPT_DIR]
      for module_loader, name, is_pkg in pkgutil.walk_packages(all_libs):
         # noinspection PyBroadException
         try:
            if not is_pkg and not name.startswith("setup") and "translation_method" in name:
               importlib.import_module(name)
            elif "translation_method" in name:
               _module = module_loader.find_module(name).load_module(name)
         except Exception as _ex:
            pass

   def stop(self):
      self.running = False
      logger.info("RequestHandler stopped.")

   def handle_translate(self, source: str, method: str):
      if not self.running:
         raise Exception("Handler is not running.")
      
      # Giả sử có logic dịch ở đây
      sv_translation = f"Translated_sv_{source}"
      vi_translation = f"Translated_vi_{source}"
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
