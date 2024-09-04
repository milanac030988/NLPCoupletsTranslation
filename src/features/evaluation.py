import argparse
import pandas as pd
import nltk
import os
import re
import sys
# Đường dẫn tương đối cần thêm
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
relative_path = SCRIPT_DIR + '/../'

# Chuyển đổi đường dẫn tương đối thành đường dẫn tuyệt đối
absolute_path = os.path.abspath(relative_path)

# Thêm đường dẫn vào sys.path
if absolute_path not in sys.path:
    sys.path.append(absolute_path)
import importlib
import pkgutil
from utils import Utils
from features.translate.translation_method import TranslateMethod
from features.translate.translation_manager import TranslationManager
from nltk.translate.bleu_score import sentence_bleu, corpus_bleu, SmoothingFunction
from stqdm import stqdm


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_TEST_FILE_PATH = os.path.abspath(SCRIPT_DIR + "/../../data/interim/test.csv")
DEFAULT_MODEL = "Transformer"
DEFAULT_COLUMNS = "cn,vi"

trans_manager = TranslationManager()

# def load_all_trans_supported_method():
#     all_libs = [TranslateMethod.SCRIPT_DIR]
#     for module_loader, name, is_pkg in pkgutil.walk_packages(all_libs):
#         # noinspection PyBroadException
#         try:
#             # print(name)
#             if not is_pkg and not name.startswith("setup") and "translation_method" in name:
#                 importlib.import_module("features.translate." + name)
#             elif "translation_method" in name:
#                 _module = module_loader.find_module(name).load_module(name)
#         except Exception as _ex:
#             # print(_ex)
#             pass

#     supported_translation_method_list = Utils.get_all_descendant_classes(TranslateMethod)
#     return {cls._TRANSLATION_METHOD: cls for cls in supported_translation_method_list}

def ensure_spaces_between_hanzi(text):
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

def remove_spaces(text):
      return re.sub(r'\s+', '', text)

def remove_punctuation(text):
    # Sử dụng biểu thức chính quy để thay thế tất cả các dấu câu bằng một chuỗi rỗng
    return re.sub(r'[^\w\s]', '', text)

def evaluate_translation_method(method, data, columns):
    if isinstance(data, str):
        data = pd.read_csv(data, usecols=columns) 
    # Dictionary chứa các phương pháp dịch
    # translation_methods = load_all_trans_supported_method()

    # Kiểm tra phương pháp dịch được chọn
    if method not in trans_manager.get_supported_method_names():
        raise ValueError(f"Unknown translation method: {method}")

    # Lấy phương pháp dịch được chọn
    # translate = translation_methods[method]()
    translate = trans_manager.get_translation_method(method)

    # Tạo danh sách các câu cần dịch và các bản dịch tham khảo
    sources = data[columns[0]].tolist()
    references = data[columns[1]].apply(lambda x: Utils.capitalize_after_newline(remove_punctuation(x).lower()).split()).tolist()

    translate_dict = {
        'sv': translate.translate_hanviet,
        'vi': translate.translate_vietnamese
    }

    # Dịch các câu sử dụng phương pháp được chọn
    hypotheses = []
    origin_scrs = []
    # for source in sources:
    for source in stqdm(sources, desc="Đang dịch câu đối...", backend=True, frontend=True):
        if method == 'Moses':
            preprocess_text = ensure_spaces_between_hanzi(source)
        else:
            preprocess_text = source
        translated_text = remove_punctuation(translate_dict[columns[1]](preprocess_text))
        hypotheses.append(translated_text.split())
        origin_scrs.append(source)

    # hypotheses = [translate.translate_vietnamese(ensure_spaces_between_hanzi(source)).split() for source in sources]

    # Tính BLEU score cho từng câu
    data = []
    sentence_bleu_scores = []
    for ref, hyp, org in zip(references, hypotheses, origin_scrs):
        score = sentence_bleu([ref], hyp, weights=(1./2., 1./2.), smoothing_function=SmoothingFunction().method1)
        sentence_bleu_scores.append(score)
        print(f"BLEU score for the sentence: {score}")
        print(f"ref: {' '.join(ref)}")
        print(f"hyp: {' '.join(hyp)}")
        data.append([org, ' '.join(ref), ' '.join(hyp), score])

    # Tính BLEU score cho cả tập dữ liệu
    corpus_score = corpus_bleu([[ref] for ref in references], hypotheses, weights=(1./2., 1./2.), smoothing_function=SmoothingFunction().method1)
    print(f"Corpus BLEU score: {corpus_score}")

    return data, sentence_bleu_scores, corpus_score

def parse_arguments():
    parser = argparse.ArgumentParser(description='Đánh giá mô hình dịch thông qua điểm BLEU.')
    parser.add_argument('-m', '--model', default=DEFAULT_MODEL, help='Loại model sử dụng để dịch.')
    parser.add_argument('-t', '--test_data', default=DEFAULT_TEST_FILE_PATH, help='File cvs chứa test data.')
    parser.add_argument('-c', '--columns', default=DEFAULT_COLUMNS, help='Tên cột nguồn và đích, cách nhau bởi dấu ",".')
    return parser.parse_args()

if __name__ == "__main__":
    # Sử dụng argparse để xử lý tham số dòng lệnh
    args = parse_arguments()
    model = args.model
    test_file = args.test_data
    columns = args.columns.split(',')

    evaluate_translation_method(model, test_file, columns)

    # evaluate_translation_method("Transformer", 'D:/Document/Master/NLP/FinalProject/data/interim/test.csv', ['cn', 'vi'])
    # evaluate_translation_method("Transformer", '~/Master/NLP/FinalProject/data/interim/test.csv', ['cn', 'vi'])
