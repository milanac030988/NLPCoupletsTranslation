import spacy



nlp_tok = spacy.load("zh_core_web_lg")
nlp_ner = spacy.load("D:\\Document\\Master\\NLP\\FinalProject\\models\\NER\\model-best")
# Example Chinese text
text = """迎 春 正 啓 鹅 山 席
爱 客 偏 浮 缽 場 杯"""

# Use SpaCy to detect entities
doc = nlp_ner(text)
entities = [(ent.text, ent.start_char, ent.end_char, ent.label_) for ent in doc.ents]
print("Detected Entities:", entities)

doc2 = nlp_tok(text)
tokens = [token.text for token in doc2]
print(f"Token: {tokens}")