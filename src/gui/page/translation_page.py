import streamlit as st
import os
import sys
import importlib
import pkgutil
from utils import Utils
from features.translate.translation_method import TranslateMethod
from features.translate.translation_manager import TranslationManager
from features.evaluation import *
from streamlit_server_state import server_state, server_state_lock

# Cấu hình trang để sử dụng layout rộng
st.set_page_config(layout="wide")

# Tiêu đề của ứng dụng
st.title("Dịch câu đối Hán sang chữ Quốc ngữ hiện đại")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Khởi tạo session state cho lựa chọn hiện tại nếu chưa có
if 'translation_manager' not in st.session_state:
   st.session_state.translation_manager = TranslationManager()

if 'current_method' not in st.session_state:
   st.session_state.current_method = None

if 'method_list' not in st.session_state:
   st.session_state.method_list = st.session_state.translation_manager.get_supported_method_names()#server_state.translation_methods.keys()

if 'translation_method_selected' not in st.session_state:
   st.session_state.translation_method_selected = None

if 'translation_query' not in st.session_state:
   st.session_state.translation_query = None

# if 'translation_method_selected_index' not in st.session_state:
#    st.session_state.translation_method_selected_index = 0

def translate(han_sentence):
   if st.session_state.current_method:
        sv_translation = st.session_state.current_method.translate(han_sentence)#
        sv_translation = Utils().extract_json(sv_translation)
        # Xử lý xuống hàng và viết hoa đầu câu
        sv_lines = sv_translation['sv'].split('\n')
        sv_lines = [line.strip() for line in sv_lines]
        formatted_sv_translation = '\n'.join(sv_lines)        
        vi_lines = sv_translation['vi'].split('\n')
        vi_lines = [line.strip() for line in vi_lines]
        formatted_vi_translation = '\n'.join(vi_lines)


# translation_methods = load_all_trans_supported_method()
# print(f"translate method list: {translation_methods.keys()}")
# translate_method_instance = {}


    

# translation_method = None
def on_select_change():
   method_name = st.session_state.selectbox_value
   if method_name in st.session_state.method_list:
      with st.spinner(f'Đang cấu hình {method_name}...'):
         st.session_state.current_method = st.session_state.translation_manager.get_translation_method(method_name)
         st.session_state.translation_method_selected = st.session_state.selectbox_value
         # if method_name not in translate_method_instance:
         #    translate_method_instance[method_name] = translation_methods[method_name]()
         # current_translation_method = translate_method_instance[method_name]
         # if method_name not in server_state.translation_methods_instance:
         #    with server_state_lock["select_translation_method"]:  
         #       server_state.translation_methods_instance[method_name] = server_state.translation_methods[method_name]()

         # st.session_state.current_method_instance = server_state.translation_methods_instance[method_name]
         # # if translation_method:
         # st.session_state.translation_method_selected_index = list(st.session_state.method_list).index(method_name)
   # Thực hiện các hành động khác với giá trị đã chọn nếu cần
   print(f"Phương pháp đã chọn: {method_name}")

# Tạo 3 cột cho giao diện với tỷ lệ rộng bằng nhau
col1, col2, col3 = st.columns([1, 0.2, 1])
if 'test_df' not in st.session_state:
   # Initial dataset
   st.session_state.test_df = None
# Cột bên trái: text area để nhập câu cần dịch
with col1:
   input_text = st.text_area("Nhập câu cần dịch:", value=st.session_state.translation_query , key='query' )

   st.write("Đánh giá mô hình:")
   uploaded_file = st.file_uploader("Tải lên file test data", type=["csv"])
   def on_evaluate(columns):
      with st.spinner(f"Đang đánh giá {st.session_state.translation_method_selected}..."):
         if df is not None:
            data, evaluation_result, score = evaluate_translation_method(st.session_state.translation_method_selected, df, columns)
            st.session_state.test_df = pd.DataFrame(data, columns=['Nguồn', 'Đích', 'Bản dịch', 'BLEU score'])
            st.write("Kết quả đánh giá mô hình:")
            st.write(score)
            st.dataframe(st.session_state.test_df)
            
   eval_button_sv = st.button("Evaluate dịch âm", key="eval_button_sv", help="Nhấn để đánh giá phương pháp dịch", on_click=lambda: on_evaluate(['cn', 'sv']))
   eval_button_vi = st.button("Evaluate dịch nghĩa", key="eval_button_vi", help="Nhấn để đánh giá phương pháp dịch", on_click=lambda: on_evaluate(['cn', 'vi']))

# Cột giữa: combobox để lựa chọn phương pháp dịch và nút dịch
with col2:
   selectted_idx = None if not st.session_state.translation_method_selected else st.session_state.method_list.index(st.session_state.translation_method_selected)
   translation_method = st.selectbox(
       "Chọn phương pháp dịch:",
       st.session_state.method_list,#.extend(list(translation_methods.keys())),
       key="selectbox_value",
       index=selectted_idx,
       help="Chọn phương pháp dịch",
       on_change=on_select_change
   )
   st.write("")  # Thêm khoảng trống để nút dịch thẳng hàng với combobox
   translate_button = st.button("Dịch", key="translate_button", help="Nhấn để dịch")

# Cột bên phải: 2 read-only text area để hiển thị kết quả dịch
with col3:
    output_text1_placeholder = st.empty()
    output_text2_placeholder = st.empty()




# Khi nhấn nút "Dịch", thực hiện dịch và hiển thị kết quả
if translate_button:     
   if input_text:
      formatted_sv_translation = ''
      formatted_vi_translation = ''
      if st.session_state.current_method:
         sv_translation = st.session_state.current_method.translate(input_text)#         
         sv_translation = Utils().extract_json(sv_translation)
         
         # Xử lý xuống hàng và viết hoa đầu câu
         sv_lines = sv_translation['sv'].split('\n')
         sv_lines = [line.strip() for line in sv_lines]
         formatted_sv_translation = '\n'.join(sv_lines)        

         vi_lines = sv_translation['vi'].split('\n')
         vi_lines = [line.strip() for line in vi_lines]
         formatted_vi_translation = '\n'.join(vi_lines)

        # Cập nhật kết quả dịch vào text area
      with col3:
         output_text1_placeholder.text_area("Phiên âm Hán Việt", value=formatted_sv_translation, height=150, disabled=True)
         output_text2_placeholder.text_area("Diễn nghĩa", value=formatted_vi_translation, height=150, disabled=True)

      st.session_state.translation_query = st.session_state.query


df = None
# Xử lý file CSV đã tải lên
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write("Dữ liệu CSV đã tải lên:")
    st.write(df)


