from dotenv import load_dotenv
from pathlib import Path
import streamlit as st

load_dotenv(override=True)

VIEW_PATH = Path(__file__).parent / 'view'

st.write(VIEW_PATH)
st.write(VIEW_PATH / 'chat.py')
st.write((VIEW_PATH / 'chat.py').exists())
st.write(type(VIEW_PATH / 'chat.py'))
st.write(type(str(VIEW_PATH / 'chat.py')))

# page_list = [
#     st.Page(str(VIEW_PATH / 'chat.py'), title='Chat', default=True),
# ]

# def get_page(title: str = None):
#     return next(filter(lambda x: x.title == title, page_list))

# pages = st.navigation(page_list, position='top',)
# pages.run()
