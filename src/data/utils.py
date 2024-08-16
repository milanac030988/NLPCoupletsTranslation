import string
import difflib
import unicodedata
import re

def remove_spaces(text):
    return re.sub(r'\s+', '', text)

def remove_accents(input_str):
    """
    Loại bỏ dấu tiếng Việt từ chuỗi.
    """
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])

def normalize_text(text):
    """
    Normalize the text by converting to lowercase and removing punctuation.
    """
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    return text

def compare_strings(str1, str2, threshold=0.8):
    """
    So sánh hai chuỗi và trả về True nếu mức độ giống nhau lớn hơn hoặc bằng ngưỡng threshold.
    """
    matcher = difflib.SequenceMatcher(None, str1, str2)
    similarity = matcher.ratio()
    # print(f"Độ tương đồng: {similarity}")
    return similarity >= threshold

def compare_strings_ignore_accents(str1, str2, threshold=0.8):
    """
    So sánh hai chuỗi bỏ qua dấu và trả về True nếu mức độ giống nhau lớn hơn hoặc bằng ngưỡng threshold.
    """
    str1_no_accents = remove_accents(str1)
    str2_no_accents = remove_accents(str2)
    
    matcher = difflib.SequenceMatcher(None, str1_no_accents, str2_no_accents)
    similarity = matcher.ratio()
    # print(f"Độ tương đồng: {similarity}")
    return similarity >= threshold


def compare_vietnamese_strings(str1, str2):
    """
    Compare two Vietnamese strings without case sensitivity and punctuation.
    
    :param str1: First string to compare.
    :param str2: Second string to compare.
    :return: True if the strings are equal, False otherwise.
    """
    normalized_str1 = normalize_text(str1)
    normalized_str2 = normalize_text(str2)
    
    return compare_strings_ignore_accents(normalized_str1, normalized_str2)

def normalize_compare_strings(str1, str2, need_remove_space=False, threshold=0.8):
    """
    Compare two strings without case sensitivity and punctuation.
    
    :param str1: First string to compare.
    :param str2: Second string to compare.
    :return: True if the strings are equal, False otherwise.
    """
    normalized_str1 = normalize_text(str1)
    normalized_str2 = normalize_text(str2)
    if need_remove_space:
        normalized_str1 = remove_spaces(normalized_str1)
        normalized_str2 = remove_spaces(normalized_str2)

    return compare_strings(normalized_str1, normalized_str2, threshold)

def count_words(sentence):
    """
    Count the number of words in a given sentence.
    
    :param sentence: The sentence to count words in.
    :return: The number of words in the sentence.
    """
    normalized_sentence = normalize_text(sentence)
    words = normalized_sentence.split()
    return len(words)

def is_chinese_char(char):
    """
    Check if a character is a Chinese character based on Unicode ranges.
    
    :param char: The character to check.
    :return: True if the character is Chinese, False otherwise.
    """
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
    return any(start <= ord(char) <= end for start, end in ranges)

def is_chinese(text):
    """
    Check if a sentence contains a Chinese character based on Unicode ranges.
    
    :param text: The sentence to check.
    :return: True if the sentence contains Chinese character, False otherwise.
    """
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

def count_chinese_characters(sentence):
    """
    Count the number of Chinese characters in a given sentence based on Unicode ranges.
    
    :param sentence: The sentence to count characters in.
    :return: The number of Chinese characters in the sentence.
    """
    return sum(1 for char in sentence if is_chinese_char(char))

def is_vietnamese(char):
    """
    Check if a character is a Vietnamese character.
    
    :param char: The character to check.
    :return: True if the character is Vietnamese, False otherwise.
    """
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

test_str1 ="""天增歲月人增壽
春滿乾坤福滿門"""
test_str2 ="""天 增 歲 月 人 增 壽
春 滿 乾 坤 福 滿 堂"""
print(normalize_compare_strings(test_str1, test_str2, True, 0.8))