from features.translate.translation_method import TranslateMethod
from transformers import MarianTokenizer, MarianMTModel, AutoModelForSeq2SeqLM, AutoTokenizer, AutoModelForMaskedLM
import subprocess
import sqlite3
import os
import json
import re
import torch

class TranslateMethodTransformer(TranslateMethod):

   _TRANSLATION_METHOD = "Transformer"
   SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
   DICT_FILE_PATH = os.path.join(os.environ.get("REFS_DIR"), 'Hanzi2HanVietDB.db')
   DEFAULT_MODEL_DIR = os.path.join(os.environ.get("MODELS_DIR"), "transformer")

   def __init__(self):
      self.model = MarianMTModel.from_pretrained(TranslateMethodTransformer.DEFAULT_MODEL_DIR)
      self.tokenizer = MarianTokenizer.from_pretrained(TranslateMethodTransformer.DEFAULT_MODEL_DIR)
      self.tokenizer_vi = MarianTokenizer.from_pretrained("Helsinki-NLP/opus-mt-vi-en")
   
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

   def translate_hanviet(self, han_sentence):     
      conn = sqlite3.connect(TranslateMethodTransformer.DICT_FILE_PATH) 
      c = conn.cursor()
      viet_translation = []
      for hanzi in han_sentence:
         if hanzi == "\n":
               viet_translation.append('\n')
         else:
               c.execute('SELECT sv FROM translations WHERE cn=?', (hanzi,))
               result = c.fetchone()
               if result:
                  viet_translation.append(result[0])
               # else:
               #    viet_translation.append('[UNKNOWN]')
      
      return ' '.join(viet_translation)

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

   def translate_vietnamese(self, han_sentence):
      # print(f"input before:'{han_sentence}'")
      # han_sentence = self.ensure_spaces_between_hanzi(han_sentence)
      # print(f"input trans: {han_sentence}")
      han_sentences = han_sentence.split("\n")
      translated_text = ''
      for sentence in han_sentences:
         # inputs = self.tokenizer(sentence, return_tensors="pt", padding=True, truncation=True)
         # # Generate translation
         # translated_tokens = self.model.generate(**inputs)
         # translated_text = self.tokenizer.decode(translated_tokens[0], skip_special_tokens=True)         
         device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
         self.model.to(device)
         self.model.eval()
         sentence = sentence.replace(' ','')
         print(f"-> Câu Hán: {sentence}")
         # Tokenize the input text
         inputs = self.tokenizer(sentence, return_tensors="pt", max_length=36, truncation=True).to(device)
         # Generate translation
         translated_tokens = self.model.generate(**inputs)
         
         trans_setence = self.tokenizer_vi.decode(translated_tokens[0], skip_special_tokens=True)
         print(f"   Dịch nghĩa: {trans_setence}")
         translated_text += trans_setence
         translated_text += "\n"

            
      return translated_text

   def quit(self):
      if self.conn:
         self.conn.close()

MODEL_NAME_TO_FINE_TUNE = "Helsinki-NLP/opus-mt-zh-vi"
if __name__ == "__main__":
   # Load the fine-tuned model and tokenizer
   model = AutoModelForSeq2SeqLM.from_pretrained(TranslateMethodTransformer.DEFAULT_MODEL_DIR)
   tokenizer = AutoTokenizer.from_pretrained(TranslateMethodTransformer.DEFAULT_MODEL_DIR)

   # model_name = MODEL_NAME_TO_FINE_TUNE
   # tokenizer = AutoTokenizer.from_pretrained(model_name)
   # model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
   # from torchinfo import summary
   # summary(model)

   device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
   model.to(device)
   model.eval()

   # Example input text
   input_text = "天地英雄气"

   # Tokenize the input text
   inputs = tokenizer(input_text, return_tensors="pt", max_length=36, truncation=True).to(device)
   # print(f"Tokens with spaces: {tokenizer.convert_ids_to_tokens(inputs['input_ids'][0])}")

   # Generate translation
   translated_tokens = model.generate(**inputs)
   tokenizer_vi = MarianTokenizer.from_pretrained("Helsinki-NLP/opus-mt-vi-en")
   translated_text = tokenizer_vi.decode(translated_tokens[0], skip_special_tokens=True)

   print("Translated text:", translated_text)
