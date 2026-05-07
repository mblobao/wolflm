from dotenv import load_dotenv
from pathlib import Path
import streamlit as st

load_dotenv(override=True)

VIEW_PATH = Path(__file__).parent / 'view'


page_list = [
    st.Page(VIEW_PATH / 'chat.py', title='Chat', default=True),
]

def get_page(title: str = None):
    return next(filter(lambda x: x.title == title, page_list))

pages = st.navigation(page_list, position='top',)
pages.run()
