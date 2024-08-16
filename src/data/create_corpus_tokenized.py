import pandas as pd
import re
import os
import py_vncorenlp
import spacy
from utils import *

OUT_DIR = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + "..\\..\\..\\output")
# Đường dẫn đến file CSV
# csv_file_path = OUT_DIR + '\\data\\dataset\\caudoi_dataset.csv'
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DATASET_PATH = os.path.abspath(SCRIPT_DIR + "\\..\\..\\output\\data\\dataset\\train.csv")

csv_file_path = DEFAULT_DATASET_PATH #"D:\\Document\\Master\\NLP\\Project\\source\\results\\train_dataset.csv"
corpus_file_path = OUT_DIR + '\\data\\corpus\\corpus.txt'

vi_rdrsegmenter = py_vncorenlp.VnCoreNLP(annotators=["wseg"], save_dir='D:\\Document\\Master\\NLP\\Project\\tools\\data_crawl\\vncorenlp')
nlp_ner = spacy.load("D:\\Document\\Master\\NLP\\Project\\output\\model\\NER\\model-best")
nlp_tok = spacy.load("zh_core_web_lg")


# Đọc file CSV
df = pd.read_csv(csv_file_path)

# Trích xuất cột 'cn' và 'vi'
cn_vi_pairs = df[['cn', 'vi']]

# Tạo file corpus.txt và ghi dữ liệu vào file

def normalize_text(text):
    # Loại bỏ khoảng trắng ở đầu và cuối dòng
    text = text.strip()
    # Thay thế nhiều khoảng trắng bằng một khoảng trắng
    text = re.sub(r'\s+', ' ', text)
    # Loại bỏ các ký tự không mong muốn (nếu có)
    # text = re.sub(r'[^\w\s.,!?]', '', text)  # Giữ lại dấu chấm câu cần thiết
    return text

def replace_underscore_with_space(text):
    # Thay thế tất cả các gạch dưới bằng khoảng trắng
    return text.replace('_', ' ')

def is_chinese(text):
    # Simple check to see if the text contains Chinese characters
    ranges = [
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
    
    return any(any(start <= ord(char) <= end for start, end in ranges) for char in text)

def is_vietnamese(char):
    vietnamese_characters = (
        "ÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚÝàáâãèéêìíòóôõùúý"
        "ĂăĐđĨĩŨũƠơƯưẠ-ỹ"
        "ĂẮẰẲẴẶăắằẳẵặ"
        "Đđ"
        "ÊẾỀỂỄỆêếềểễệ"
        "ƠỚỜỞỠỢơớờởỡợ"
        "ƯỨỪỬỮỰưứừửữự"
    )
    return char in vietnamese_characters

def chinese_tokenizer_with_ner(nlp_tokenizer, nlp_ner, text):
   # Step 1: Tokenize the text using zh_core_web_lg
   doc = nlp_tokenizer(text)
   tokens = [token.text for token in doc]
   print(f"Token: {tokens}")
   token_offsets = [(token.idx, token.idx + len(token.text)) for token in doc]

   # Step 2: Named Entities detected
   doc_ent = nlp_ner(text)
   entities = doc_ent.ents
   print(f"Ner: {entities}")

   # Step 3: Adjust the tokens based on the detected entities
   final_tokens = []
   i = 0

   while i < len(tokens):
      token_start, token_end = token_offsets[i]
      merged = False
      for entity in entities:
         ent_start = entity.start
         ent_end = entity.end

         # Check if the token overlaps with the entity span
         if token_start >= ent_start and token_end <= ent_end:
            merged_token = ''
            # Collect all tokens that fall within the entity span
            while i < len(tokens) and token_offsets[i][0] >= ent_start and token_offsets[i][1] <= ent_end:
                merged_token += tokens[i]
                i += 1
            final_tokens.append(merged_token)
            merged = True
            break
      
      if not merged:
         final_tokens.append(tokens[i])
         i += 1

   return final_tokens


with open(corpus_file_path, 'w', encoding='utf-8') as f:
    for index, row in cn_vi_pairs.iterrows():
        cn_sentences = row['cn'].split('\n')
        vi_sentences = row['vi'].split('\n')
        
        if len(cn_sentences) != len(vi_sentences):
            print(f"Warning: The number of sentences in 'cn' and 'vi' do not match in row {index}")
        
        for cn_sentence, vi_sentence in zip(cn_sentences, vi_sentences):
            cn_sentence = normalize_text(cn_sentence)
            cn_sentence = remove_spaces(cn_sentence)
            # cn_sentence = ''.join([char + ' ' if is_chinese(char) else '' for char in cn_sentence]).strip()
            cn_sentence = ' '.join(chinese_tokenizer_with_ner(nlp_tok, nlp_ner, cn_sentence))
            vi_sentence = ''.join(char for char in vi_sentence if is_vietnamese(char) or char == ' ' or char.isalnum())
            vi_sentence = normalize_text(vi_sentence)
            vi_sentence = replace_underscore_with_space(vi_sentence)
            # test = vi_rdrsegmenter.word_segment(vi_sentence)
            vi_sentence = ''.join(vi_rdrsegmenter.word_segment(vi_sentence))
            f.write(f"{cn_sentence}\t{vi_sentence}\t\n")

print(f"File corpus.txt đã được tạo thành công tại {corpus_file_path}")
