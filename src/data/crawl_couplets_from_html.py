import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import configparser
import argparse
import re
import os
from pyvi import ViTokenizer


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE_PATH = os.path.join(SCRIPT_DIR, 'crawl_couplets_from_html.ini')

def parse_config(file_path):
    config = configparser.ConfigParser()
    config.read(file_path)
    
    # Xử lý URL list để nối các dòng lại với nhau
    url_list = config.get('settings', 'url_list').replace('\\\n', '').replace(' ', '').split(',')
    
    return {
        'url_list': url_list,
        'tag_id': config.get('settings', 'tag_id', fallback=None),
        'structure': config.get('settings', 'structure'),
        'filter': config.get('settings', 'filter', fallback=None),
        'output_list': config.get('settings', 'output_list').split(','),
        'skip_first_n': config.getint('settings', 'skip_first_n', fallback=0),
        'skip_last_n': config.getint('settings', 'skip_last_n', fallback=0),
        'max_blocks': config.getint('settings', 'max_blocks', fallback=None)
    }

def parse_args():
    parser = argparse.ArgumentParser(description='Crawl data from given URLs.')
    parser.add_argument('--config', type=str, help='Path to the config file', default=CONFIG_FILE_PATH)
    parser.add_argument('--urls', type=str, help='Comma-separated list of URLs to crawl')
    parser.add_argument('--tag_id', type=str, help='ID of the div to search within', default=None)
    parser.add_argument('--structure', type=str, help='Structure to extract data (e.g., 2H-2HV-2V)')
    parser.add_argument('--filter', type=str, help='Pattern to filter out unwanted lines', default=None)
    parser.add_argument('--output_list', type=str, help='Comma-separated list of output file paths')
    parser.add_argument('--skip_first_n', type=int, help='Number of initial tags to skip', default=0)
    parser.add_argument('--skip_last_n', type=int, help='Number of final tags to skip', default=0)
    parser.add_argument('--max_blocks', type=int, help='Maximum number of blocks to extract', default=None)
    args = parser.parse_args()
    if args.urls:
        return {
            'url_list': args.urls.split(','),
            'tag_id': args.tag_id,
            'structure': args.structure,
            'filter': args.filter,
            'output_list': args.output_list.split(','),
            'skip_first_n': args.skip_first_n,
            'skip_last_n': args.skip_last_n,
            'max_blocks': args.max_blocks
        }
    else:
        return parse_config(args.config)

def is_chinese(text):
    # Simple check to see if the text contains Chinese characters
    return any('\u4e00' <= char <= '\u9fff' for char in text)

def crawl_data(url, tag_id, structure, filter_pattern, skip_first_n, skip_last_n, max_blocks):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    if tag_id:
        div = soup.find(id=tag_id)
        if not div:
            print(f'No div found with id {tag_id}')
            return []
        elements = div.find_all(recursive=False)
    else:
        elements = soup.find_all(recursive=False)

    # Replace <br> with newline
    for br in soup.find_all("br"):
        br.replace_with("\n")

    # Skip the first n elements
    elements = elements[skip_first_n:]

    # Skip the last n elements
    if skip_last_n > 0:
        elements = elements[:-skip_last_n]

    text_lines = [element.get_text().strip() for element in elements if element.get_text().strip()]
    # print(text_lines[0].split("\xa0"))
    new_text_line = []
    new_text_line.extend(word for line in text_lines for word in line.split("\n"))
    text_lines = new_text_line
    # print(text_lines)
    if filter_pattern:
        text_lines = [line for line in text_lines if not re.match(filter_pattern, line)]
    # print(text_lines)

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
                    if tag == "V":
                        current_line = ViTokenizer.tokenize(current_line)
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

def main():
    config = parse_args()
    all_data = []

    for url in config['url_list']:
        data = crawl_data(url, config['tag_id'], config['structure'], config['filter'], config['skip_first_n'], config['skip_last_n'], config['max_blocks'])
        all_data.extend(data)
      #   if config['max_blocks'] and len(all_data) >= config['max_blocks']:
      #       all_data = all_data[:config['max_blocks']]
      #       break

    for output_file in config['output_list']:
        if output_file.endswith('.json'):
            save_to_json(all_data, output_file)
        elif output_file.endswith('.csv'):
            save_to_csv(all_data, output_file)

if __name__ == '__main__':
    main()
