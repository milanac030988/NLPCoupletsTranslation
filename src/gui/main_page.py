import streamlit as st

# st.set_page_config(page_title='Chuyển ngữ câu đối Hán Nôm', page_icon=':material/dashboard:', layout='wide')

pages = {
      'Online tool' : [
         st.Page('page/translation_page.py', title='Dịch câu đối online', icon=':material/translate:'),
      ],
      'Service management' : [
         st.Page('page/service_management_page.py', title='Quản lý service', icon=':material/manage_accounts:'),
      ],
      'Phân tích dữ liệu' : [
        
      ],
}

pg = st.navigation(pages)

pg.run()