from wolflm.controller.wolfchat import get_model, get_chat, generate_standard_chat
from wolflm.view.presentation_helper import generate_presentation_helper
from wolflm.view.prompt_builder import generate_prompt_builder
from wolflm.model import user_prompt_to_message
from wolflm.models import Model as ModelBase
import streamlit as st


st.set_page_config(page_title='Wolf Chat', page_icon='🤖', layout='wide')

if 'api_key' not in st.session_state:
    st.session_state.api_key = None
if 'system_instruction' not in st.session_state:
    st.session_state.system_instruction = None
if 'model' not in st.session_state:
    st.session_state.model = 'gemini-2.5-pro'
    st.session_state.model_name = 'Gemini 2.5 Pro'
if 'skill' not in st.session_state:
    st.session_state.skill = None
if 'chat' not in st.session_state:
    st.session_state.chat = None
    st.session_state.chat_index = 0


with st.sidebar:
    st.text_input('Gemini API Key', key='api_key')

    kwargs = {'type': 'tertiary'}
    if st.button('Nova conversa', **kwargs):
        st.session_state.skill = None
        st.session_state.chat = None
        st.session_state.chat_index += 1
    
    # ===================
    # Definição de Agente
    # ===================
    with st.expander('Agentes'):
        presetation_helper = st.button('Auxiliador de Apresentação', **kwargs)
        prompt_builder = st.button('Construtor de Prompts', **kwargs)
    
    # ========================
    # Definição de Habilidades
    # ========================
    with st.expander('Habilidades'):
        if st.button('Tradutor para Português', **kwargs):
            st.session_state.skill = 'pt_translator'
        if st.button('Organizador de Ata', **kwargs):
            st.session_state.skill = 'meeting_notes'
    
    # =====================
    # Definição de Conversa
    # =====================
    with st.expander('Conversas'):
        get_chat()

# ==================
# Seleção de Modelos
# ==================
cols = st.columns((4, 1, 1))
with cols[0]:
    model_name = ModelBase.query(f'CodeStr == "{st.session_state.model}"').Name.iloc[0]
    with st.expander(f'Modelo: {model_name}'):
        get_model()
if len(st.session_state.chat):
    with cols[1]:
        st.download_button('Salvar Chat', data=st.session_state.chat.to_json_str(), file_name='Chat.json')
    with cols[2]:
        st.download_button('Salvar Resposta', data=st.session_state.chat.messages[-1].content, file_name='Chat.md')
# =======================
# Configuração de Agentes
# =======================
if presetation_helper:
    generate_presentation_helper()
elif prompt_builder:
    generate_prompt_builder()
else:
    user_prompt = generate_standard_chat()

    if user_prompt:
        st.session_state.chat.user_message(user_prompt_to_message(text=user_prompt.text, files=user_prompt.files))
        st.rerun()
