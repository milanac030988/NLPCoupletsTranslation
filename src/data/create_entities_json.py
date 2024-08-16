import pandas as pd
import json

# Đọc file CSV đã tạo
input_file_path = 'D:\\Document\\Master\\NLP\\Project\\data\\raw_data\\entities.csv'  # Thay đổi đường dẫn tới file CSV của bạn
df = pd.read_csv(input_file_path)

# Tạo danh sách lưu trữ cấu trúc JSON
json_data = []

# Xử lý từng dòng trong file CSV
for index, row in df.iterrows():
    text = row['cn']
    entity_positions = row['entity_position'].split(', ')

    entities = row['entities'].split(', ')
    if row['entity_type'] and not isinstance(row['entity_type'], float):
        entity_types = row['entity_type'].split(',')
        if len(entity_types) == 1:
            entity_types = entity_types * len(entities)
    else:
        entity_types = ['PERSON'] * len(entities)

    entities_list = []
    for pos, entity, entity_type in zip(entity_positions, entities, entity_types):
        start, end = map(int, pos.strip('()').split(':'))
        entities_list.append({"start": start, "end": end, "label": entity_type.strip()})

    json_data.append({"text": text, "entities": entities_list})

# Lưu kết quả dưới dạng file JSON
output_file_path = 'D:\\Document\\Master\\NLP\\Project\\data\\raw_data\\entities.json'  # Thay đổi đường dẫn lưu file JSON mới
with open(output_file_path, 'w', encoding='utf-8') as f:
    json.dump(json_data, f, ensure_ascii=False, indent=4)

print("File JSON mới đã được tạo thành công.")
