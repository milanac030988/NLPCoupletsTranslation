import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import configparser
import argparse
import re
import os
import sqlite3
from pyvi import ViTokenizer
from utils import *

class CRAWL_ERR:
    CN_COUPLETS_NOT_EQUAL = "CN_COUPLETS_NOT_EQUAL"
    CN_HV_COUPLETS_NOT_EQUAL = "CN_HV_COUPLETS_NOT_EQUAL"
    HV_COUPLETS_NOT_EQUAL = "HV_COUPLETS_NOT_EQUAL"
    HV_COUPLETS_NOT_SAME_SOUND = "HV_COUPLETS_NOT_SAME_SOUND"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DICT_FILE_PATH = os.path.join(SCRIPT_DIR, 'dictionary.db')

def translate_hanviet(han_sentence):     
      conn = sqlite3.connect(DICT_FILE_PATH) 
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

def verify(han_senetnce, hv_sentence):
    res = []
    han_senetnces = han_senetnce.split("\n")
    hv_sentences = hv_sentence.split("\n")
    if len(han_senetnces) <= 1 or count_chinese_characters(han_senetnces[0]) != count_chinese_characters(han_senetnces[1]):
        res.append(CRAWL_ERR.CN_COUPLETS_NOT_EQUAL)
    if len(hv_sentences) <= 1 or count_chinese_characters(han_senetnces[0]) != count_words(hv_sentences[0]) or count_chinese_characters(han_senetnces[0]) != count_words(hv_sentences[1]):
        res.append(CRAWL_ERR.CN_HV_COUPLETS_NOT_EQUAL)
    if len(hv_sentences) <= 1 or count_words(hv_sentences[0]) != count_words(hv_sentences[1]):
        res.append(CRAWL_ERR.HV_COUPLETS_NOT_EQUAL)
    
    for han, hv in zip(han_senetnces, hv_sentences):
        trans_han = translate_hanviet(han)
        if not compare_vietnamese_strings(trans_han, hv):
            res.append(CRAWL_ERR.HV_COUPLETS_NOT_SAME_SOUND)
            break
    return res

def extract_number_from_trang(text):
    """
    Extract the number from a text line that matches the format "Trang X".
    
    :param text: The text line to check.
    :return: The extracted number if the text matches the format, None otherwise.
    """
    pattern = re.compile(r'^Trang (\d+):')
    match = pattern.match(text)
    if match:
        return int(match.group(1))
    return None


image_folder = "D:\\Document\\Master\\NLP\\Project\\data\\raw_data\\MS.K32-5000-CauDoi\\CH\\CauDoiHanNomImg_p1"
images = [os.path.join(image_folder, f"HanNomCouplets_p1_page-{i:04d}.jpg") for i in range(1, 431)]

def crawl_data(text_lines):
    max_blocks = 5000
    structure = "2H-2HV-2V"
    data = []
    structure_parts = re.findall(r'\d+[A-Z]+', structure)
    indices = { 'H': 'cn', 'HV': 'sv', 'V': 'vi' }
    block = { 'cn': '', 'sv': '', 'vi': '' }
    line_index = 0
    structure_index = 0

    current_page = 1
    while line_index < len(text_lines):
        num_page = extract_number_from_trang(text_lines[line_index])
        if num_page:
            line_index += 1
            current_page = num_page
            continue

        if structure_index >= len(structure_parts):
            structure_index = 0
        
        part = structure_parts[structure_index]
        count, tag = int(re.findall(r'\d+', part)[0]), re.findall(r'[A-Z]+', part)[0]
        
        # for _ in range(count):
        while count > 0:
            if line_index < len(text_lines):
                while not text_lines[line_index].strip():
                    line_index += 1
                    if line_index >= len(text_lines):
                        break
                if line_index < len(text_lines):
                    current_line = text_lines[line_index]
                    num_page = extract_number_from_trang(current_line)
                    if num_page:
                        line_index += 1
                        current_page = num_page
                        continue
                    if current_line:
                        # if tag == "V":
                        #     current_line = ViTokenizer.tokenize(current_line)
                        if tag == 'H' and not is_chinese(current_line):
                            # If expected Chinese but not, skip to next structure part
                            if block[indices[tag]]:
                                break
                            line_index += 1
                            continue
                        if (tag == 'HV' or tag=='V') and is_chinese(current_line):
                            # If expected Chinese but not, skip to next structure part
                            break
                            # if block[indices[tag]]:
                            #     break
                            # line_index += 1
                            # continue
                        if block[indices[tag]]:
                            block[indices[tag]] += '\n' + current_line
                        else:
                            block[indices[tag]] = current_line
                line_index += 1
            count -=1
        
        structure_index += 1
        
        if structure_index >= len(structure_parts):
            block['err'] = 'None'
            block['img'] = images[current_page - 1]
            verify_res = verify(block['cn'], block['sv'])
            if verify_res:
                block['err'] = '\n'.join(verify_res)
            data.append(block)
            block = { 'cn': '', 'sv': '', 'vi': '' }
            if max_blocks and len(data) >= max_blocks:
                return data

    if block != { 'cn': '', 'sv': '', 'vi': '' }:  # add remaining block if exists
        block['err'] = 'None'
        block['img'] = images[current_page - 1]
        verify_res = verify(block['cn'], block['sv'])
        if verify_res:
            block['err'] = '\n'.join(verify_res)
        data.append(block)

    return data

def save_to_json(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def save_to_csv(data, file_path):
    df = pd.DataFrame(data)
    df.to_csv(file_path, index=False, encoding='utf-8-sig')

def read_text_file_to_list(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = file.readlines()
    # Loại bỏ các ký tự xuống dòng và các dòng trống
    data = [line.strip() for line in data if line.strip()]
    return data

def main():
    text_lines = read_text_file_to_list("D:\\Document\\Master\\NLP\\Project\\tools\\data_crawl\\5000_cau_doi.txt")
    all_data = crawl_data(text_lines)
    OUT_DIR = "D:\\Document\\Master\\NLP\\Project\\output\\data\\dataset"
    output_files = [OUT_DIR + "\\5000_couplets_dataset3.csv"]
    for output_file in output_files:
        if output_file.endswith('.json'):
            save_to_json(all_data, output_file)
        elif output_file.endswith('.csv'):
            save_to_csv(all_data, output_file)

if __name__ == '__main__':
    main()
