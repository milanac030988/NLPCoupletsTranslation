# *******************************************************************************
#
# File: translation_method_dual_transformer.py
#
# Initially created by Nguyen Huynh Tri Cuong / Aug 2024
#
# Description:
#   Implementation cho phương thức dịch sử dụng hai mô hình transformers. 
#   Mô hình đầu chuyển câu Hán tự đích từ Văn Ngôn sang văn Bạch Thoại. 
#   Mô hình thứ hai sẽ dịch từ câu Bạch Thoại sang Việt ngữ.
#
# History:
#
# 01.08.2024 / V 0.1 / Nguyen Huynh Tri Cuong
# - Khởi tạo
#
# *******************************************************************************
from features.translate.translation_method import TranslateMethod
from transformers import MarianTokenizer, MarianMTModel, AutoModelForSeq2SeqLM, AutoTokenizer, AutoModelForMaskedLM, EncoderDecoderModel
from utils import Utils
import subprocess
import sqlite3
import os
import json
import re
import torch

class TranslateMethodDualTransformer(TranslateMethod):

   _TRANSLATION_METHOD = "DualTransformer"
   SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
   DICT_FILE_PATH = os.path.join(os.environ.get("REFS_DIR"), 'Hanzi2HanVietDB.db')
   ACIENT_2_MODERN_MODEL = "raynardj/wenyanwen-ancient-translate-to-modern"
   DEFAULT_MODEL_DIR = os.path.join(os.environ.get("MODELS_DIR"), "transformer/opus-mt-zh-vi-fine_tuned_model_include_modern")

   def __init__(self):
      self.model = MarianMTModel.from_pretrained(TranslateMethodDualTransformer.DEFAULT_MODEL_DIR)
      self.tokenizer = MarianTokenizer.from_pretrained(TranslateMethodDualTransformer.DEFAULT_MODEL_DIR)
      self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
      self.model.to(self.device)
      self.model.eval()
      self.acient2modern_tokenizer = AutoTokenizer.from_pretrained(TranslateMethodDualTransformer.ACIENT_2_MODERN_MODEL)
      self.acient2modern_model = EncoderDecoderModel.from_pretrained(TranslateMethodDualTransformer.ACIENT_2_MODERN_MODEL)
      self.acient2modern_model.to(self.device)
      self.acient2modern_model.eval()
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
      conn = sqlite3.connect(TranslateMethodDualTransformer.DICT_FILE_PATH) 
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
      
      translated_text = ' '.join(viet_translation)
      if translated_text[-1] != ".":
         translated_text += "."       
      translated_text = Utils.capitalize_after_newline(translated_text.lower())
      return translated_text

   def inference(self, text):
      tk_kwargs = dict(
         truncation=True,
         max_length=128,
         padding="max_length",
         return_tensors='pt')
      
      inputs = self.acient2modern_tokenizer([text,],**tk_kwargs).to(self.device)
      with torch.no_grad():
         return self.acient2modern_tokenizer.batch_decode(
               self.acient2modern_model.generate(
               inputs.input_ids,
               attention_mask=inputs.attention_mask,
               num_beams=3,
               max_length=256,
               bos_token_id=101,
               eos_token_id=self.acient2modern_tokenizer.sep_token_id,
               pad_token_id=self.acient2modern_tokenizer.pad_token_id,
         ), skip_special_tokens=True)

   def normalize_text(self, sentences):
      # sentences = pre_translate[0]
      sentences = sentences.replace(' ','')
      sentences = sentences.replace("《", "").replace("》", "")
      sentences = sentences.replace("、", "").replace("，"," ")
      sentences = sentences.replace(' ','')
      return sentences

   def translate_vietnamese(self, han_sentence):
      han_sentences = han_sentence.split("\n")
      translated_text = ''
      for sentence in han_sentences:
         sentence = sentence.replace(' ','')
         sentence += "."
         ## Tiền xử lý Văn ngôn sang Bạch ngôn
         pre_translate = self.inference(sentence)
         pre_translate = self.normalize_text(pre_translate[0])

         ## Dịch cn -> vi
         inputs = self.tokenizer(pre_translate, return_tensors="pt", max_length=32, truncation=True).to(self.device)
         translated_tokens = self.model.generate(**inputs)         
         trans_setence = self.tokenizer.decode(translated_tokens[0], skip_special_tokens=True)

         translated_text += trans_setence
         translated_text += ";\n"     

      translated_text = translated_text[:-2]
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
   MODEL_PATH = os.path.join( TranslateMethodDualTransformer.SCRIPT_DIR, "../../../models/transformer/opus-mt-zh-vi-fine_tuned_model")
   sentence = """細 訒 如 圖 欲 命 詩."""
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
   # special_tokens_dict = tokenizer.special_tokens_map
   # print("Special Tokens:", special_tokens_dict)
   inputs = tokenizer(sentence, return_tensors="pt", max_length=18, truncation=True).to(device)

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