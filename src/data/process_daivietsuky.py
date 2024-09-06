import json
import re
from libs.FakeChatGPTAPI.fake_chatgpt_api import FakeChatGPTAPI

# fake_api = FakeChatGPTAPI("D:\\Document\\Master\\NLP\\FinalProject\\src\\data\\fake_chatgpt_daivietsuky.ini")


# def extract_json_from_string(text):
#     """
#     Hàm này nhận vào một chuỗi văn bản, sử dụng regex để trích xuất phần JSON từ chuỗi đó.
#     """
#     try:
#         # Tìm phần JSON bằng biểu thức chính quy
#         json_match = re.search(r'\[\s*{.*?}\s*\]', text, re.DOTALL)
#         if json_match:
#             json_string = json_match.group(0)
#             return json_string
#         else:
#             print("Không tìm thấy JSON trong chuỗi.")
#             return None
#     except Exception as e:
#         print(f"Lỗi khi trích xuất JSON từ chuỗi: {e}")
#         return None

# def process_cnsv_vi_pair(cnsv, vi):
#     """
#     Hàm này nhận vào cặp "cnsv" và "vi", xử lý chúng và trả về một chuỗi text chứa JSON với định dạng {"cn": "abc", "sv": "xyz", "vi": "lmn"}.
#     """
#     # Giả sử chúng ta cần tách "cn" và "sv" từ "cnsv" dựa trên logic cụ thể
#     # Thay đổi logic này theo cách bạn muốn tách "cn" và "sv"
#    #  cn, sv = cnsv.split(' ', 1)  # Ví dụ: tách phần đầu làm "cn" và phần còn lại làm "sv"
#     response = fake_api.send_request(cnsv + "\n" + vi)
    
    
#     # Tạo chuỗi JSON từ kết quả xử lý
#     result_json = extract_json_from_string(response)

#     # Chuyển đổi dictionary thành chuỗi JSON
#     return result_json #json.dumps(result_json, ensure_ascii=False)

# def append_to_output_file(output_file, json_objects):
#     """
#     Hàm này thêm đối tượng JSON vào file output.
#     """
#     try:
#         with open(output_file, 'a', encoding='utf-8') as f:
#             for json_object in json_objects:
#                 f.write(json.dumps(json_object, ensure_ascii=False) + ',\n')
#     except Exception as e:
#         print(f"Lỗi khi ghi vào file {output_file}: {e}")


# def main(input_file, output_file):
#     """
#     Hàm chính đọc file JSON đầu vào, xử lý từng cặp "cnsv" và "vi" và lưu kết quả vào file JSON khác.
#     """
#     try:
#         # Đọc dữ liệu từ file JSON đầu vào
#         with open(input_file, 'r', encoding='utf-8') as f:
#             data = json.load(f)
        
#         # Xử lý từng cặp "cnsv" và "vi"
#         for entry in data:
#             cnsv = entry.get('cnsv')
#             vi = entry.get('vi')
            
#             # Gọi hàm xử lý
#             result = process_cnsv_vi_pair(cnsv, vi)
            
#             if result:
#                 # Chuyển đổi chuỗi JSON đã trích xuất thành danh sách đối tượng JSON
#                 json_objects = json.loads(result)
                
#                 # Append kết quả vào file output
#                 append_to_output_file(output_file, json_objects)

#         print(f"Đã xử lý xong và lưu kết quả vào {output_file}.")

#     except Exception as e:
#         print(f"Lỗi khi xử lý file {input_file}: {e}")

# # Tên file input chứa dữ liệu đầu vào và file output để lưu kết quả
# input_file = 'D:\\Document\\Master\\NLP\\FinalProject\\src\\data\\output_data.json'  # File JSON đầu vào mà bạn đã tạo trước đó
# output_file = 'processed_output.json'  # File JSON output để lưu kết quả

# # Chạy chương trình
# main(input_file, output_file)
import json
import csv
import re

# Bảng chuyển đổi số sang chữ tiếng Việt
number_to_words_vietnamese = {
    0: "không", 1: "một", 2: "hai", 3: "ba", 4: "bốn", 5: "năm",
    6: "sáu", 7: "bảy", 8: "tám", 9: "chín", 10: "mười", 100: "trăm",
    1000: "nghìn", 1000000: "triệu", 1000000000: "tỷ"
}

def convert_number_to_vietnamese_words(number):
    """
    Hàm này chuyển đổi một số nguyên thành chữ tiếng Việt.
    """
    if number <= 10:
        return number_to_words_vietnamese[number]
    elif number < 20:
        return "mười " + number_to_words_vietnamese[number % 10]
    elif number < 100:
        tens = number // 10
        units = number % 10
        return number_to_words_vietnamese[tens] + " mươi " + (number_to_words_vietnamese[units] if units != 0 else "")
    elif number < 1000:
        hundreds = number // 100
        remainder = number % 100
        return number_to_words_vietnamese[hundreds] + " trăm " + (convert_number_to_vietnamese_words(remainder) if remainder != 0 else "")
    elif number < 1000000:
        thousands = number // 1000
        remainder = number % 1000
        return convert_number_to_vietnamese_words(thousands) + " nghìn " + (convert_number_to_vietnamese_words(remainder) if remainder != 0 else "")
    elif number < 1000000000:
        millions = number // 1000000
        remainder = number % 1000000
        return convert_number_to_vietnamese_words(millions) + " triệu " + (convert_number_to_vietnamese_words(remainder) if remainder != 0 else "")
    else:
        billions = number // 1000000000
        remainder = number % 1000000000
        return convert_number_to_vietnamese_words(billions) + " tỷ " + (convert_number_to_vietnamese_words(remainder) if remainder != 0 else "")

def remove_text_in_brackets(text):
    """
    Hàm này loại bỏ tất cả các đoạn văn bản chứa số trong ngoặc vuông, ví dụ: [1203].
    """
    # Sử dụng regex để loại bỏ văn bản trong ngoặc vuông cùng với dấu ngoặc
    cleaned_text = re.sub(r'\[\d+(?:\s*TCN)?\]', '', text)  # Loại bỏ cả [123] và [123 TCN]
    return cleaned_text.strip()

def convert_numbers_to_words_in_text(text):
    """
    Hàm này tìm và chuyển đổi tất cả các số trong văn bản thành chữ tiếng Việt.
    """
    # Tìm tất cả các số trong chuỗi và chuyển đổi chúng thành chữ tiếng Việt
    def replace_number_with_words(match):
        number = int(match.group(0))
        return convert_number_to_vietnamese_words(number)
    
    # Sử dụng regex để tìm tất cả các số và thay thế chúng bằng chữ
    return re.sub(r'\d+', replace_number_with_words, text)

def clean_and_convert_data(data):
    """
    Hàm này làm sạch dữ liệu và chuyển đổi số thành chữ tiếng Việt trong danh sách các đối tượng JSON.
    """
    for entry in data:
        # Loại bỏ văn bản trong ngoặc vuông
      #   entry['cn'] = remove_text_in_brackets(entry['cn'])
      #   entry['sv'] = remove_text_in_brackets(entry['sv'])
        entry['vi'] = remove_text_in_brackets(entry['vi'])

        # Chuyển đổi số thành chữ tiếng Việt
      #   entry['cn'] = convert_numbers_to_words_in_text(entry['cn'])
      #   entry['sv'] = convert_numbers_to_words_in_text(entry['sv'])
        entry['vi'] = convert_numbers_to_words_in_text(entry['vi'])
    return data

def json_to_csv(json_file, csv_file):
    """
    Chuyển đổi file JSON thành file CSV.
    """
    try:
        # Đọc dữ liệu từ file JSON với utf-8-sig để xử lý BOM
        with open(json_file, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)  # Đọc toàn bộ dữ liệu JSON
        
        # Làm sạch dữ liệu và chuyển đổi số thành chữ tiếng Việt
        cleaned_data = clean_and_convert_data(data)

        # Lấy tên cột từ khóa của đối tượng JSON đầu tiên
        fieldnames = cleaned_data[0].keys()

        # Ghi dữ liệu vào file CSV
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()  # Ghi dòng tiêu đề
            writer.writerows(cleaned_data)  # Ghi dữ liệu
        
        print(f"Đã chuyển đổi thành công {json_file} thành {csv_file}.")
    
    except Exception as e:
        print(f"Lỗi khi chuyển đổi từ JSON sang CSV: {e}")

# Tên file input JSON và output CSV
json_file = 'processed_output.json'  # File JSON đầu vào
csv_file = 'processed_output.csv'  # File CSV output

# Chạy chương trình
json_to_csv(json_file, csv_file)




