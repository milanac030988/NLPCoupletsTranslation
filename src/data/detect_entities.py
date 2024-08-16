import pandas as pd
import argparse
import re
import os
import configparser


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_MAIN_DATASET_PATH = os.path.abspath(SCRIPT_DIR + "\\..\\..\\output\\data\\dataset\\primary_couplets_dataset.csv") + ", D:\\Document\\Master\\NLP\\Project\\data\\raw_data\\data\\NomNaNMT.csv"
DEFAULT_ENTITIES_PATH = os.path.abspath(SCRIPT_DIR + "\\..\\..\\output\\data\\dataset\\entities.csv")

# Hàm làm sạch văn bản, loại bỏ các ký tự đặc biệt
def clean_text(text):
    # Loại bỏ các ký tự đặc biệt
    text = re.sub(r'[^\w\s]', '', text)
    return text

# Hàm tìm chữ viết Hoa giữa câu
# Hàm tìm các từ có chữ cái đầu viết hoa
def find_entities(text):
    entities = []
    text = text.strip()
    # Pattern để tìm tất cả các từ dạng CamelCase
    pattern = r'\b[A-ZAÀÁẢÃẠĂẰẮẲẴẶÂẦẤẨẪẬEÈÉẺẼẸÊỀẾỂỄỆIÌÍỈĨỊOÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢUÙÚỦŨỤƯỪỨỬỮỰYỲÝỶỸỴĐ].*?\b'
    matches = list(re.finditer(pattern, text))

    # Danh sách để lưu các từ hoặc cụm từ đã được xử lý
    temp_entities = []
    

    # Tách câu thành các từ
    words = re.split(r'\s+', text)
    word_starts = [m.start() for m in re.finditer(r'\S+', text)]
    word_map = {start: idx for idx, start in enumerate(word_starts)}

    # Xử lý các từ tìm được
    i = 0
    while i < len(matches):
        try:
            match = matches[i]
            word = match.group().strip()
            start_pos = match.start()
            end_pos = match.end()

            word_index = word_map[start_pos]

            # Nếu từ nằm ở đầu dòng mà từ thứ 2 không viết hoa thì loại bỏ
            is_first_word_of_line = (word_index == 0 or text[start_pos-1] == '\n')
            if is_first_word_of_line and word_index < len(words) - 1:
                next_word_start = word_starts[word_index + 1]
                next_word = words[word_index + 1]
                if not next_word[0].isupper():
                    i += 1
                    continue
            # Kết nối hai từ liền kề thành một cụm
            entity_words = [word]
            while i < len(matches) - 1:
                next_match = matches[i + 1]
                next_word = next_match.group().strip()
                next_word_start_pos = next_match.start()
                next_word_index = word_map[next_word_start_pos]

                # Nếu từ liền kề tiếp theo là từ đầu dòng mới thì không tính
                if text[next_word_start_pos - 1] == '\n':
                    break

                if next_word_index == word_index + len(entity_words):
                    entity_words.append(next_word)
                    end_pos = next_match.end()
                    i += 1
                else:
                    break

            entity_text = ' '.join(entity_words)
            entity_start_word = word_index
            entity_end_word = entity_start_word + len(entity_words)

            temp_entities.append((entity_text, entity_start_word, entity_end_word))
        except Exception as ex:
            raise ex
        i += 1

    return temp_entities

def main(input_file, output_file):
    filelist = input_file.split(",")
    # Initialize an empty list to store DataFrames
    df_list = []
    for file in filelist:
        df = pd.read_csv(file, usecols=['cn', 'sv'])  # Use usecols to select specific columns
        df_list.append(df)

    # Concatenate the DataFrames into one
    df = pd.concat(df_list, ignore_index=True)

    # Đọc file CSV ban đầu
    # df = pd.read_csv(input_file)
    # Tạo dataframe mới
    data = []
    for index, row in df.iterrows():
        cn_sentences = row['cn'].split('\n')
        sv_sentences = clean_text(row['sv']).split('\n')
        # vi_sentences = row['vi'].split('\n')

        # Ensure all lists have the same length to avoid misalignment
        if len(cn_sentences) == len(sv_sentences):
            for cn, sv in zip(cn_sentences, sv_sentences):
                entities = find_entities(sv)
                if entities:  # Chỉ thêm các dòng có entity
                    entity_str = ', '.join([entity[0] for entity in entities])
                    positions_str = ', '.join([f"({entity[1]}: {entity[2]})" for entity in entities])
                    data.append([cn, sv, positions_str, entity_str, ""])
        else:
            print(f"Warning: Mismatch in the number of sentences for row {index}")

    new_df = pd.DataFrame(data, columns=['cn', 'sv', 'entity_position', 'entities', 'entity_type'])

    # Xuất ra file CSV mới
    new_df.to_csv(output_file, index=False, encoding='utf-8-sig')

    print("File CSV mới đã được tạo thành công.")

def parse_arguments():
    parser = argparse.ArgumentParser(description='Detect các entities trong câu đối.')
    parser.add_argument('-i', '--input', default=DEFAULT_MAIN_DATASET_PATH, help='Đường dẫn đến file CSV đầu vào.')
    parser.add_argument('-o', '--output', default=DEFAULT_ENTITIES_PATH, help='Đường dẫn đến file CSV đầu re.')
    return parser.parse_args()

def read_config(config_file='split_mosses_corpus.ini'):
    config = configparser.ConfigParser(os.environ, interpolation=configparser.ExtendedInterpolation())
    config.read(config_file)
    return config

if __name__ == "__main__":
    args = parse_arguments()
    Input = DEFAULT_MAIN_DATASET_PATH
    Output = DEFAULT_ENTITIES_PATH

    config = read_config()
    
    if 'SETTINGS' in config:
        Input = config['SETTINGS'].get('input', input_file, vars=os.environ)
        Output = config['SETTINGS'].get('output', output_folder, vars=os.environ)
    
    # Override with command-line arguments if provided
    if args.input:
        Input = args.input
    if args.output:
        Output = args.output

    main(args.input, args.output)
