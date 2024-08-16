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