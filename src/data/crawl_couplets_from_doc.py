import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import configparser
import argparse
import re
import os
from pyvi import ViTokenizer


def is_chinese(text):
    # Simple check to see if the text contains Chinese characters
    return any('\u4e00' <= char <= '\u9fff' for char in text)

def crawl_data(text_lines):
    max_blocks = 500
    structure = "2H-2HV-2V"
    data = []
    structure_parts = re.findall(r'\d+[A-Z]+', structure)
    indices = { 'H': 'cn', 'HV': 'sv', 'V': 'vi' }
    block = { 'cn': '', 'sv': '', 'vi': '' }
    line_index = 0
    structure_index = 0

    while line_index < len(text_lines):
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
                    # if tag == "V":
                    #     current_line = ViTokenizer.tokenize(current_line)
                    if tag == 'H' and not is_chinese(current_line):
                        # If expected Chinese but not, skip to next structure part
                        if block[indices[tag]]:
                            break
                        line_index += 1
                        continue
                    if block[indices[tag]]:
                        block[indices[tag]] += '\n' + current_line
                    else:
                        block[indices[tag]] = current_line
                line_index += 1
            count -=1
        
        structure_index += 1
        
        if structure_index >= len(structure_parts):
            data.append(block)
            block = { 'cn': '', 'sv': '', 'vi': '' }
            if max_blocks and len(data) >= max_blocks:
                return data

    if block != { 'cn': '', 'sv': '', 'vi': '' }:  # add remaining block if exists
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
    # config = parse_args()
    # all_data = []


    text_lines = read_text_file_to_list("D:\\Document\\Master\\NLP\\Project\\data\\raw_data\\500_cau_doi_Han_Viet.txt")
    all_data = crawl_data(text_lines)

    # for url in config['url_list']:
    #     data = crawl_data(url, config['tag_id'], config['structure'], config['filter'], config['skip_first_n'], config['skip_last_n'], config['max_blocks'])
    #     all_data.extend(data)
    #   #   if config['max_blocks'] and len(all_data) >= config['max_blocks']:
    #   #       all_data = all_data[:config['max_blocks']]
    #   #       break
    OUT_DIR = "D:\\Document\\Master\\NLP\\Project\\output\\data\\dataset"
    output_files = [OUT_DIR + "\\500_couplets_dataset.csv", OUT_DIR + "\\500_couplets_dataset.json"]
    for output_file in output_files:
        if output_file.endswith('.json'):
            save_to_json(all_data, output_file)
        elif output_file.endswith('.csv'):
            save_to_csv(all_data, output_file)

if __name__ == '__main__':
    main()
