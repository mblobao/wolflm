from wolflm.utils import VIEW_PATH
from pathlib import Path
import streamlit as st

page_list = [
    st.Page(VIEW_PATH / 'chat.py', title='Chat', default=True)
]
position = 'hidden'
if not str(__file__).startswith('wolflm'):
    page_list.append(
        st.Page(VIEW_PATH / 'DEV.py', title='DEV')
    )
    position = 'top'


pages = st.navigation(page_list, position=position)
pages.run()