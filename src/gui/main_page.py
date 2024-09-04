import streamlit as st

# st.set_page_config(page_title='Chuyển ngữ câu đối Hán Nôm', page_icon=':material/dashboard:', layout='wide')

pages = {
      'Online tool' : [
         st.Page('page/translation_page.py', title='Dịch câu đối online', icon=':material/translate:'),
      ],
      'Quản lý service' : [
         st.Page('page/test.py', title='Translation service', icon=':material/manage_accounts:'),
      ],
}

pg = st.navigation(pages)

pg.run()