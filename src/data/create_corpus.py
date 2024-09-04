import pandas as pd
import re
import os
import argparse
import configparser


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

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

def parse_arguments():
    # Initialize the argument parser
    parser = argparse.ArgumentParser(description="Process some CSV files and output to a file.")
    
    # Define command-line arguments
    parser.add_argument('--input', type=str, help="Comma-separated list of input CSV files.")
    parser.add_argument('--output', type=str, help="Output CSV file path.")
    
    # Parse the arguments
    args = parser.parse_args()

    # Return parsed arguments
    return args

def read_config(config_file='config.ini'):
    # print(os.environ['DATASET_OUTPUT_DIR'])
    # Enable interpolation to allow environment variable substitution
    config = configparser.ConfigParser(os.environ, interpolation=configparser.ExtendedInterpolation())
    config.read(config_file)
    
    
    # Read values from the config file, with environment variables substituted
    input_files = config.get('corpus', 'input',  vars=os.environ)
    output_file = config.get('corpus', 'output',  vars=os.environ)
    
    return input_files, output_file

def create_corpus(inputs, output):
    df_list = []

    # Loop through each file and select only the 'a' and 'b' columns
    for file in inputs:
        df = pd.read_csv(file, usecols=['cn', 'vi'])  # Use usecols to select specific columns
        df_list.append(df)

    # Concatenate the DataFrames into one
    df = pd.concat(df_list, ignore_index=True)
    cn_vi_pairs = df[['cn', 'vi']]
    with open(output, 'w', encoding='utf-8') as f:
        for index, row in cn_vi_pairs.iterrows():
            cn_sentences = row['cn'].split('\n')
            vi_sentences = row['vi'].split('\n')
            
            if len(cn_sentences) != len(vi_sentences):
                print(f"Warning: The number of sentences in 'cn' and 'vi' do not match in row {index}")
            
            for cn_sentence, vi_sentence in zip(cn_sentences, vi_sentences):
                cn_sentence = normalize_text(cn_sentence)
                cn_sentence = ''.join([char + ' ' if is_chinese(char) else '' for char in cn_sentence]).strip()
                vi_sentence = ''.join(char for char in vi_sentence if is_vietnamese(char) or char == ' ' or char.isalnum())
                vi_sentence = normalize_text(vi_sentence)
                vi_sentence = replace_underscore_with_space(vi_sentence)
                f.write(f"{cn_sentence}\t{vi_sentence}\t\n")

    print(f"File corpus.txt đã được tạo thành công tại {output}")

def main():
    # Parse command-line arguments
    args = parse_arguments()

    # If no command-line arguments are provided, read from config file
    if not args.input or not args.output:
        if os.path.exists(os.path.join(SCRIPT_DIR, 'config.ini')):
            print("Reading from config.ini...")
            input_files, output_file = read_config(os.path.join(SCRIPT_DIR, 'config.ini'))
        else:
            raise ValueError("No command-line arguments provided and config.ini not found.")
    else:
        input_files = args.input
        output_file = args.output

    # Convert the comma-separated input files to a list
    input_files_list = input_files.split(',')

    print("Input files:", input_files_list)
    print("Output file:", output_file)
    create_corpus(input_files_list, output_file)


if __name__ == "__main__":
    main()    
