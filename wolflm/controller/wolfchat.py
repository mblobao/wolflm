from wolflm.utils import SKILLS_PATH, CHATS_PATH
from wolflm.gemini.base import generate_content
from wolflm.models import Model as ModelBase
import streamlit_antd_components as sac
from wolflm.model.base import Role
from wolflm.model.chat import Chat
import streamlit as st


def get_skill(**kwargs: bool):
    if 'pt_translator' in kwargs and kwargs['pt_translator']:
        with open(SKILLS_PATH / 'pt_translator.md', 'r', encoding='utf-8') as f:
            st.session_state.system_instruction = f.read()
    
    if 'meeting_notes' in kwargs and kwargs['meeting_notes']:
        with open(SKILLS_PATH / 'meeting_notes.md', 'r', encoding='utf-8') as f:
            st.session_state.system_instruction = f.read()
    
    if 'new' in kwargs and kwargs['new']:
        st.session_state.system_instruction = None


def get_chat() -> Chat:
    uploaded_chat = st.file_uploader('Upload Chat', accept_multiple_files=False, type='json',
        key=f'Uploader_{st.session_state.chat_index}'
    )

    if uploaded_chat is not None:
        st.session_state[f'chat_{st.session_state.chat_index}'] = Chat.load(uploaded_chat.read())

    else:
        st.session_state[f'chat_{st.session_state.chat_index}'] = Chat()


def get_model() -> str:
    cols = st.columns(2)
    with cols[0]:
        max_context = float(ModelBase.DataSet.ContextWindow.max())
        ContextWindow = st.slider('ContextWindow', min_value=0., max_value=max_context, value=(0., max_context))
        qry = [f'ContextWindow <= {ContextWindow[1]} & ContextWindow >= {ContextWindow[0]}']
        if st.checkbox('TextInput', value=True):
            qry.append('TextInput')
        if st.checkbox('ImageInput', value=False):
            qry.append('ImageInput')
        if st.checkbox('TextOutput', value=True):
            qry.append('TextOutput')
        if st.checkbox('ImageOutput', value=False):
            qry.append('ImageOutput')
        qry = ' & '.join(qry)
        
    with cols[1]:
        models = ModelBase.query(qry)['Name']
        selected_model = sac.tree(show_line=False,
            items=[sac.TreeItem(model_name) for model_name in models]
        )
    if selected_model is not None:
        st.session_state.model = ModelBase.query(f'Name == "{selected_model}"').CodeStr.iloc[0]
        st.session_state.model_name = ModelBase.query(f'Name == "{selected_model}"').Name.iloc[0]


def generate_standard_chat():
    # ===========================
    # Configuração de Habilidades
    # ===========================
    if st.session_state.skill == 'pt_translator':
        st.title('Tradutor para Português')
        get_skill(pt_translator=True)
    
    elif st.session_state.skill == 'meeting_notes':
        st.title('Organizador de Ata')
        get_skill(meeting_notes=True)
    
    else:  # Conversa Genérica
        st.write("<h1 style='text-align: center;'>🤖 Bem Vindo</h1>", unsafe_allow_html=True)
        get_skill(new=True)

    # =======================
    # Definição de Chat Geral
    # =======================
    for message in st.session_state[f'chat_{st.session_state.chat_index}']:
        avatar = 'user' if message.role.value == 'USER' else 'assistant'
        if isinstance(message.content, list):
            for part in filter(lambda x: isinstance(x, str), message.content):
                st.chat_message(avatar).write(part)
        elif isinstance(message.content, str):
            st.chat_message(avatar).write(message.content)
        
    if len(st.session_state[f'chat_{st.session_state.chat_index}']) and st.session_state[f'chat_{st.session_state.chat_index}'].messages[-1].role == Role.USER:
        response = generate_content(
            api_key=st.session_state.api_key,
            model=st.session_state.model,
            chat=st.session_state[f'chat_{st.session_state.chat_index}'],
            system_instruction=st.session_state.system_instruction
        )
        st.session_state[f'chat_{st.session_state.chat_index}'].model_message(response.text)

        st.chat_message('assistant').write(response.text)
    
    return st.chat_input(accept_file='multiple')