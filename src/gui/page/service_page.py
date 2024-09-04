import streamlit as st
import pandas as pd
import streamlit_authenticator as stauth
import pandas as pd
import os
import threading
import time
import requests
import streamlit_authenticator as stauth
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh
from streamlit.runtime.scriptrunner.script_run_context import get_script_run_ctx, add_script_run_ctx
# from translation_service import TranslationService
from streamlit_server_state import server_state, server_state_lock
from api.service_manager import ServiceManager, ServiceStatus

st.set_page_config(layout="wide")
# Khai báo thông tin đăng nhập của người dùng dưới dạng dictionary
credentials = {
    "usernames": {
        "milanac": {"name": "Cuong Nguyen", "password": stauth.Hasher(['030988']).generate()[0]}
    }
}

# Khởi tạo đối tượng xác thực với định nghĩa mới
authenticator = stauth.Authenticate(
    credentials,  # Thông tin người dùng
    "my_app_cookie",  # Tên cookie
    "random_signature_key",  # Khóa cookie bảo mật
    cookie_expiry_days=30  # Thời gian hết hạn cookie
)

# Hiển thị form đăng nhập
# Tùy chỉnh widget đăng nhập
name, authentication_status, username = authenticator.login(
    location="main",  # Hiển thị form đăng nhập ở vị trí chính (main)
    max_concurrent_users=5,  # Giới hạn tối đa 5 người dùng đăng nhập đồng thời
    max_login_attempts=3,  # Giới hạn tối đa 3 lần đăng nhập thất bại
    fields={"username": "Tên đăng nhập", "password": "Mật khẩu", "login": "Đăng nhập"},  # Tùy chỉnh tên trường
    captcha=False,  # Không yêu cầu captcha
    clear_on_submit=True,  # Xóa thông tin nhập khi nhấn Đăng nhập
    key='Login'  # Khóa duy nhất cho widget
)

# Kiểm tra trạng thái đăng nhập
if authentication_status:   
    with server_state_lock["translation_service"]:  # Lock the "count" state for thread-safety
       if "translation_service" not in server_state:
          server_state.translation_service = ServiceManager()#TranslationService("TranslationService")
          server_state.service_status = server_state.translation_service.get_status()
    
    # Khởi tạo session state nếu chưa có
    if 'service_status' not in st.session_state:
       st.session_state.service_status = 'stopped'
       st.session_state.logs = ""
       st.session_state.log_area = ""
       st.session_state.statistics = ""
       st.session_state.selected_file = None
       st.session_state.selected_files = []
    
    # Thiết lập giá trị mặc định cho session state nếu chưa có
    if 'refresh' not in st.session_state:
       st.session_state['refresh'] = False  # Trạng thái làm mới ban đầu là dừng
    
    if 'show_chart' not in st.session_state:
       st.session_state['show_chart'] = False
    
    def toggle_refresh():
        st.session_state['refresh'] = not st.session_state['refresh']
        st.session_state['show_chart'] = not st.session_state['show_chart']
    
    # Hàm ẩn/hiện biểu đồ
    def toggle_chart():
        st.session_state['show_chart'] = not st.session_state['show_chart']
    
    # Hàm cập nhật log
    def update_log_area():
       st.session_state.log_area = st.session_state.logs
    
    # Hàm start service
    def start_service():   
       st.session_state.service_status = ServiceStatus.STARTED
       if server_state.translation_service:
          server_state.translation_service.start_server()
       
       time.sleep(5)
       st.session_state.service_status = server_state.translation_service.get_status()
       st.session_state.logs += "Service started\n"
       update_log_area()
    
    # Hàm stop service
    def stop_service():
       st.session_state.service_status = ServiceStatus.STOPPED
       if server_state.translation_service:
          server_state.translation_service.stop_server()
    
       time.sleep(5)
       st.session_state.service_status = server_state.translation_service.get_status()
       st.session_state.logs += "Service stopped\n"
       update_log_area()
    
    
    requests_translate = "NaN"
    requests_contribute = "NaN"
    total_request ="NaN"
    # Khởi tạo các biến chứa giá trị
    if st.session_state.service_status == ServiceStatus.STARTED:
          response = requests.get("http://127.0.0.1:8000/request_stats")
          if response.status_code == 200:
             data = response.json()
             requests_translate = data['translate_request_count']
             requests_contribute = data['contribute_request_count']
             total_request = requests_translate + requests_contribute
    
    # Tiêu đề chính của trang
    st.title("Translation Service Dashboard")
    
    # Tạo 3 cột cho các thông số dịch vụ
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"<h1 style='text-align: center; color: blue;'>{total_request}</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center;'>Total Request</h3>", unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"<h1 style='text-align: center; color: green;'>{requests_translate}</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center;'>Translate Request</h3>", unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"<h1 style='text-align: center; color: red;'>{requests_contribute}</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center;'>Contribute Request</h3>", unsafe_allow_html=True)
    
    # Tạo dòng để chứa các nút điều khiển và căn giữa chúng
    st.write("---")
    col_empty1, col4, col_empty2, col5, col_empty3, col6, col_empty4 = st.columns([1, 2, 1, 2, 1, 2, 1])
    
    with col4:
        if st.button("REFRESH"):
            st.write("Refreshed!")
    
    with col5:
       stop_button = st.button('⏹ Stop', on_click=stop_service, disabled=(st.session_state.service_status == ServiceStatus.STOPPED))
    
    with col6:
       start_button = st.button('▶️ Start', on_click=start_service, disabled=(st.session_state.service_status == ServiceStatus.STARTED))
    
    # Thêm các nút khác với căn giữa
    st.write("---")
    col7, col8, col9 = st.columns([1, 1, 1])
    
    with col7:
       st.text_area("Log", value=st.session_state.log_area, height=200, disabled=True)
    
    with col8:
       # Kiểm tra trạng thái ẩn/hiện biểu đồ
       if st.session_state['show_chart']:
          if st.session_state.service_status == ServiceStatus.STARTED:
             st.write("Biểu đồ thống kê request thời gian thực")
             response = requests.get("http://127.0.0.1:8000/request_stats")
             if response.status_code == 200:
                data = response.json()
                requests_translate = data['translate_request_count']
                requests_contribute = data['contribute_request_count']
    
                # Chuẩn bị dữ liệu cho biểu đồ
                request_types = ['Translate', 'Contribute']
                request_counts = [requests_translate, requests_contribute]
    
                # Vẽ biểu đồ cột
                fig, ax = plt.subplots()
                ax.bar(request_types, request_counts, color=['blue', 'green'])
    
                # Thiết lập nhãn và tiêu đề
                ax.set_xlabel('Loại Request')
                ax.set_ylabel('Số lượng Request')
                ax.set_title('Số lượng Request Translate và Contribute')
    
                # Hiển thị biểu đồ trên Streamlit
                st.pyplot(fig)

       if st.session_state['show_chart']:
       # print(f"Service status: {server_state.translation_service.get_status()}")
          if server_state.translation_service.get_status() == ServiceStatus.STARTED:
             st.button('Ẩn chart', on_click=toggle_refresh)
             # Tự động làm mới trang mỗi 2 giây khi refresh = True
             st_autorefresh(interval=2000, key="realtime_chart_refresh")
       else:
          st.button('Hiện chart', on_click=toggle_refresh)
    
    with col9:
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


elif authentication_status == False:
    st.error("Tên đăng nhập hoặc mật khẩu không đúng. Vui lòng thử lại.")

elif authentication_status == None:
    st.warning("Vui lòng nhập tên đăng nhập và mật khẩu để truy cập nội dung.")



