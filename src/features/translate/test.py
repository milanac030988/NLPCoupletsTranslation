import spacy
from transformers import (BertTokenizer,BertConfig,BertModel)
from transformers import BertConfig, BertModel

nlp_tok = spacy.load("zh_core_web_lg")
nlp_ner = spacy.load("D:\\Document\\Master\\NLP\\FinalProject\\models\\NER\\model-best")
# Example Chinese text
text = """迎 春 正 啓 鹅 山 席
爱 客 偏 浮 缽 場 杯"""

# Use SpaCy to detect entities
# doc = nlp_ner(text)
# entities = [(ent.text, ent.start_char, ent.end_char, ent.label_) for ent in doc.ents]
# print("Detected Entities:", entities)

# doc2 = nlp_tok(text)
# tokens = [token.text for token in doc2]
# print(f"Token: {tokens}")





# config = BertConfig.from_pretrained("bert-base-uncased")  # Or another appropriate config
# model = BertModel.from_pretrained('D:\\Document\\Master\\NLP\\FinalProject\\src\\features\\translate', config=config, ignore_mismatched_sizes=True)
# # Load the BERT tokenizer
# tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

# # Example input text
# input_text = "太水千秋瞻仰佛"

# # Tokenize the input text
# inputs = tokenizer(input_text, return_tensors="pt")

# # Get the model outputs
# outputs = model(**inputs)

# # Extract the logits and determine the predicted tokens (assuming a classification task, for example)
# logits = outputs.logits
# predicted_class_id = logits.argmax().item()

# # Decode the logits into a sentence
# translated_sentence = tokenizer.decode(predicted_class_id)

# print("Translated Sentence:", translated_sentence)