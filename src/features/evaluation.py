import argparse
import pandas as pd
import nltk
from nltk.translate.bleu_score import sentence_bleu, corpus_bleu
import os
import re
import importlib
import pkgutil
from utils import Utils
from features.translate.translation_method import TranslateMethod

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def load_all_trans_supported_method():
    all_libs = [SCRIPT_DIR]
    for module_loader, name, is_pkg in pkgutil.walk_packages(all_libs):
        # noinspection PyBroadException
        try:
            if not is_pkg and not name.startswith("setup") and "translation_method" in name:
                importlib.import_module(name)
            elif "translation_method" in name:
                _module = module_loader.find_module(name).load_module(name)
        except Exception as _ex:
            pass

    supported_translation_method_list = Utils.get_all_descendant_classes(TranslateMethod)
    return {cls._TRANSLATION_METHOD: cls for cls in supported_translation_method_list}

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

def evaluate_translation_method(method, data):
    # Dictionary chứa các phương pháp dịch
    translation_methods = load_all_trans_supported_method()

    # Kiểm tra phương pháp dịch được chọn
    if method not in translation_methods:
        raise ValueError(f"Unknown translation method: {method}")

    # Lấy phương pháp dịch được chọn
    translate = translation_methods[method]()

    # Đọc dữ liệu từ file CSV
   #  data = pd.read_csv(csv_path)

    # Tạo danh sách các câu cần dịch và các bản dịch tham khảo
    sources = data['cn'].tolist()
    references = data['vi'].apply(lambda x: x.split()).tolist()

    # Dịch các câu sử dụng phương pháp được chọn
    hypotheses = [translate.translate_vietnamese(ensure_spaces_between_hanzi(source)).split() for source in sources]

    # Tính BLEU score cho từng câu
    sentence_bleu_scores = []
    for ref, hyp in zip(references, hypotheses):
        score = sentence_bleu([ref], hyp)
        sentence_bleu_scores.append(score)
        print(f"BLEU score for the sentence: {score}")

    # Tính BLEU score cho cả tập dữ liệu
    corpus_score = corpus_bleu([[ref] for ref in references], hypotheses)
    print(f"Corpus BLEU score: {corpus_score}")

    return sentence_bleu_scores, corpus_score

if __name__ == "__main__":
    # Sử dụng argparse để xử lý tham số dòng lệnh
    parser = argparse.ArgumentParser(description='Evaluate translation models and calculate BLEU score.')
    parser.add_argument('--method', type=str, required=True, help='Translation method to use.')
    parser.add_argument('--csv_path', type=str, required=True, help='Path to the CSV file with test data.')

    args = parser.parse_args()

    evaluate_translation_method(args.method, args.csv_path)
