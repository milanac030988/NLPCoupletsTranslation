import json
import spacy
from spacy.training.example import Example
import random
from spacy.util import minibatch, compounding

# Đọc dữ liệu từ file JSON
input_file_path = 'D:\\Document\\Master\\NLP\\Project\\data\\raw_data\\entities.json'  # Thay đổi đường dẫn tới file JSON của bạn
with open(input_file_path, 'r', encoding='utf-8') as f:
    training_data = json.load(f)

# Chuẩn bị dữ liệu huấn luyện
def convert_data_to_spacy_format(training_data):
    train_data = []
    for entry in training_data:
        text = entry['text'].replace('\n', '')
        entities = [(ent['start'], ent['end'], ent['label']) for ent in entry['entities']]
        train_data.append((text, {"entities": entities}))
    return train_data

train_data = convert_data_to_spacy_format(training_data)

# Tải mô hình ngôn ngữ
nlp = spacy.blank('zh')  # Tạo mô hình trống cho tiếng Việt

# Tạo pipeline 'ner'
if 'ner' not in nlp.pipe_names:
    ner = nlp.create_pipe('ner')
    nlp.add_pipe('ner', last=True)
else:
    ner = nlp.get_pipe('ner')

# Thêm các nhãn (labels) vào bộ nhận diện thực thể (NER)
for _, annotations in train_data:
    for ent in annotations.get('entities'):
        ner.add_label(ent[2])

# Bắt đầu huấn luyện mô hình
optimizer = nlp.begin_training()
for i in range(30):  # Số lần lặp (epochs)
    random.shuffle(train_data)
    losses = {}
    batches = minibatch(train_data, size=compounding(4.0, 32.0, 1.001))
    for batch in batches:
        texts, annotations = zip(*batch)
        examples = [Example.from_dict(nlp.make_doc(text), annotation) for text, annotation in zip(texts, annotations)]
        nlp.update(examples, drop=0.5, losses=losses)
    print(f"Epoch {i+1}, Losses: {losses}")

# Lưu mô hình đã huấn luyện
output_dir = 'D:\\Document\\Master\\NLP\\Project\\model'  # Thay đổi đường dẫn lưu mô hình
nlp.to_disk(output_dir)
print("Model saved to", output_dir)