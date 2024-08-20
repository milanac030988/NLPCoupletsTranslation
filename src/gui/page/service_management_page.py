import streamlit as st
import pandas as pd
import os
import threading
import time
import requests
from streamlit.runtime.scriptrunner.script_run_context import get_script_run_ctx, add_script_run_ctx
# from translation_service import TranslationService
from streamlit_server_state import server_state, server_state_lock
from api.service_manager import ServiceManager

# Cấu hình trang để sử dụng layout rộng
st.set_page_config(layout="wide")
ctx = get_script_run_ctx()
with server_state_lock["translation_service"]:  # Lock the "count" state for thread-safety
   if "translation_service" not in server_state:
      server_state.translation_service = ServiceManager()#TranslationService("TranslationService")

# Hàm start service
def start_service():
   st.session_state.service_status = 'running'
   st.session_state.logs += "Service started\n"
   if server_state.translation_service:
      server_state.translation_service.start_server()
   update_log_area()

# Hàm stop service
def stop_service():
   st.session_state.service_status = 'stopped'
   if server_state.translation_service:
      server_state.translation_service.stop_server()
   st.session_state.logs += "Service stopped\n"
   update_log_area()

# Hàm cập nhật log
def update_log_area():
   st.session_state.log_area = st.session_state.logs

# Khởi tạo session state nếu chưa có
if 'service_status' not in st.session_state:
   st.session_state.service_status = 'stopped'
   st.session_state.logs = ""
   st.session_state.log_area = ""
   st.session_state.statistics = ""
   st.session_state.selected_file = None
   st.session_state.selected_files = []

# Hàm giả lập cập nhật thống kê
def update_statistics():
   add_script_run_ctx(None, ctx)
   while True:
      if 'service_status' in st.session_state and st.session_state.service_status == 'running':
            response = requests.get("http://127.0.0.1:8000/request_stats")
            if response.status_code == 200:
               data = response.json()
               st.session_state.statistics = f"""Service has been running for {time.strftime('%H:%M:%S', time.gmtime(time.time() - st.session_state.start_time))}
Number of request: {data['translate_request_count']}
Number of contribute: {data['contribute_request_count']}
                                          """
               st.rerun()
      time.sleep(1)

# Start và Stop button với icon
col1, col2 = st.columns([1, 1])
with col1:
   start_button = st.button('▶️ Start', disabled=st.session_state.service_status == 'running')
   if start_button:
        st.session_state.start_time = time.time()
        start_service()
        time.sleep(5)
        threading.Thread(target=update_statistics, daemon=True).start()

with col2:
   stop_button = st.button('⏹ Stop', disabled=st.session_state.service_status == 'stopped')
   if stop_button:
        stop_service()

# Text area để hiển thị log
st.text_area("Log", value=st.session_state.log_area, height=200, disabled=True)

# Text area để hiển thị thống kê
st.text_area("Statistics", value=st.session_state.statistics, height=100, disabled=True)

# Lấy danh sách file CSV trong thư mục
file_list = [f for f in os.listdir() if f.endswith('.csv')]

# Hiển thị danh sách file với checkbox
st.write("Danh sách file CSV:")
for file in file_list:
   if st.checkbox(file, key=file):
       if file not in st.session_state.selected_files:
           st.session_state.selected_files.append(file)
   else:
       if file in st.session_state.selected_files:
           st.session_state.selected_files.remove(file)

# Nút để thực hiện tác vụ với file được chọn
if st.button("Thực hiện tác vụ"):
   if st.session_state.selected_files:
       st.write(f"Thực hiện tác vụ với các file: {', '.join(st.session_state.selected_files)}")
       # Thêm mã để thực hiện tác vụ với các file được chọn
   else:
       st.write("Không có file nào được chọn")

# Hiển thị nội dung file CSV khi click vào
if st.session_state.selected_files:
   st.write("Nội dung file:")
   selected_file = st.session_state.selected_files[0]  # Hiển thị nội dung file đầu tiên được chọn
   df = pd.read_csv(selected_file)
   st.write(df)
