from wolflm.view import (
    get_model, new_chat_button, agents_choice, skill_choice,
    generate_page, get_chat
)
import streamlit as st


st.set_page_config(page_title='WolfLM', page_icon=':wolf:', layout='wide')


# ===================== Session State Setup =====================
if True:
    if 'family' not in st.session_state:
        st.session_state.family = 'Gemini'
    if 'model' not in st.session_state:
        st.session_state.model = 'gemini-2.5-pro'
        st.session_state.model_name = 'Gemini 2.5 Pro'

    if 'agent' not in st.session_state:
        st.session_state.agent = None
    if 'skill' not in st.session_state:
        st.session_state.skill = None
    
    if 'api_key' not in st.session_state:
        st.session_state.api_key = None
    if 'system_instruction' not in st.session_state:
        st.session_state.system_instruction = None
    if 'chat_index' not in st.session_state:
        st.session_state.chat_index = 0
    if f'chat_{st.session_state.chat_index}' not in st.session_state:
        st.session_state[f'chat_{st.session_state.chat_index}'] = None

    for state in {'chat', 'Uploader'}:
        for i in range(st.session_state.chat_index):
            if f'{state}_{i}' in st.session_state:
                del st.session_state[f'{state}_{i}']
    
    if 'research' not in st.session_state:
        st.session_state.research = False
    if 'thinking' not in st.session_state:
        st.session_state.thinking = False
# ================================================================


with st.sidebar:
    get_model()
    new_chat_button()
    agents_choice()
    if not st.session_state.agent:
        skill_choice()
        get_chat()

generate_page()
