import os
import sys
import importlib
import pkgutil
from utils import Utils
from features.translate.translation_method import TranslateMethod


class TranslationManager:
   def __init__(self):
      self.translation_method_classes = self.load_all_trans_supported_method()
      self.translation_method_instances = {}

   def get_supported_method_names(self):
      return list(self.translation_method_classes.keys())

   def get_translation_method(self, method_name):
      if method_name not in self.translation_method_instances:
         self.translation_method_instances[method_name] = self.translation_method_classes[method_name]()
         
      return self.translation_method_instances.get(method_name)

   def load_all_trans_supported_method(self):
      all_libs = [TranslateMethod.SCRIPT_DIR]
      # sys.path.extend(all_libs)
      for module_loader, name, is_pkg in pkgutil.walk_packages(all_libs):
         # noinspection PyBroadException
         try:
            # print(name)
            if not is_pkg and not name.startswith("setup") and "translation_method" in name:
               importlib.import_module("features.translate." + name)
            elif "translation_method" in name:
               _module = module_loader.find_module(name).load_module(name)
         except Exception as _ex:
            print(_ex)
            pass

      supported_translation_method_list = Utils.get_all_descendant_classes(TranslateMethod)
         #   self.translation_methods = {cls._TRANSLATION_METHOD: cls for cls in supported_translation_method_list}
      return {cls._TRANSLATION_METHOD: cls for cls in supported_translation_method_list}

if __name__ == "__main__":
   trans_manager = TranslationManager()
   trans_method =  trans_manager.get_translation_method("Moses")
   resp = trans_method.translate("甲第鼎新容駟馬")
   print(resp)