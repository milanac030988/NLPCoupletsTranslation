from features.translate.translation_method import TranslateMethod
from transformers import MarianTokenizer, MarianMTModel, AutoModelForSeq2SeqLM, AutoTokenizer, AutoModelForMaskedLM
from utils import Utils
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
   DEFAULT_MODEL_DIR = os.path.join(os.environ.get("MODELS_DIR"), "transformer/opus-mt-zh-vi-fine_tuned_model")

   def __init__(self):
      self.model = MarianMTModel.from_pretrained(TranslateMethodTransformer.DEFAULT_MODEL_DIR)
      self.tokenizer = MarianTokenizer.from_pretrained(TranslateMethodTransformer.DEFAULT_MODEL_DIR)
      device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
      self.model.to(device)
      self.model.eval()
      # self.tokenizer_vi = MarianTokenizer.from_pretrained("Helsinki-NLP/opus-mt-vi-en")
   
   def __del__(self):
      self.quit()

   def remove_spaces(self, text):
      return re.sub(r'\s+', '', text)

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
      han_sentences = han_sentence.split("\n")
      translated_text = ''
      for sentence in han_sentences:
         sentence = sentence.replace(' ','')
         # print(f"-> Câu Hán: {sentence}")
         # Tokenize the input text
         device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
         inputs = self.tokenizer(sentence, return_tensors="pt", max_length=36, truncation=True).to(device)
         # Generate translation
         translated_tokens = self.model.generate(**inputs)         
         trans_setence = self.tokenizer.decode(translated_tokens[0], skip_special_tokens=True)
         # print(f"   Dịch nghĩa: {trans_setence}")
         translated_text += trans_setence
         translated_text += "\n"     

      translated_text = translated_text[:-1]
      if translated_text[-1] != ".":
         translated_text += "."       
      translated_text = Utils.capitalize_after_newline(translated_text.lower())
      return translated_text

   def quit(self):
      # if self.conn:
      #    self.conn.close()
      pass

def clean_tokenization(new_tokens, tokens):
    cleaned_tokens = []
    skip_next = False

    for i, token in enumerate(tokens):
        if skip_next:
            skip_next = False
            continue
        # Kiểm tra nếu token hiện tại là token đặc biệt và token tiếp theo bắt đầu bằng '_'
        if token in new_tokens and i + 1 < len(tokens) and tokens[i + 1].startswith('▁'):
            cleaned_tokens.append(token)
            # cleaned_tokens.append(tokens[i + 1].replace('▁', ''))
            skip_next = True
        else:
            cleaned_tokens.append(token)
    
    return cleaned_tokens

if __name__ == "__main__":
   MODEL_PATH = os.path.join( TranslateMethodTransformer.SCRIPT_DIR, "../../../models/transformer/opus-mt-zh-vi-fine_tuned_model_bk")
   sentence = "四座有高明"
   sentence = sentence.replace(' ','')
   model = MarianMTModel.from_pretrained(MODEL_PATH)
   tokenizer = MarianTokenizer.from_pretrained(MODEL_PATH)
   # Thêm token đặc biệt vào tokenizer
   # # special_tokens = {'additional_special_tokens': ['[KEEP]']}
   # tokenizer.add_tokens("龍橋")
   # new_tokens = ["龍橋"]
   # # Mở rộng mô hình để hỗ trợ token mới
   # model.resize_token_embeddings(len(tokenizer))
   device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
   model.to(device)
   model.eval()
   special_tokens_dict = tokenizer.special_tokens_map
   print("Special Tokens:", special_tokens_dict)
   inputs = tokenizer(sentence, return_tensors="pt", max_length=36, truncation=True).to(device)

   # Kiểm tra và loại bỏ ký tự `_`
   # tokens = tokenizer.convert_ids_to_tokens(inputs['input_ids'][0])
   # cleaned_tokens = clean_tokenization(new_tokens, tokens)

   # # Chuyển đổi lại thành input IDs
   # input_ids = tokenizer.convert_tokens_to_ids(cleaned_tokens)

   # # Đưa vào mô hình
   # inputs = {'input_ids': torch.tensor([input_ids]).to(device)}

   print(f"{tokenizer.convert_ids_to_tokens(inputs['input_ids'][0])}")
   # Generate translation
   translated_tokens = model.generate(**inputs)         
   trans_setence = tokenizer.decode(translated_tokens[0], skip_special_tokens=False)
   print(trans_setence)