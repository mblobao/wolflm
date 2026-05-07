from wolflm.gemini.base import generate_content
from wolflm.models import Model as ModelBase
from google.genai.errors import ClientError
import streamlit_antd_components as sac
from wolflm.utils import SKILLS_PATH
from wolflm.model.base import Role
from wolflm.model.chat import Chat
import streamlit as st


def skill_choice() -> None:
    with st.expander('Habilidades'):
        if st.button('Tradutor para Português', type='tertiary'):
            st.session_state.skill = 'pt_translator'
        if st.button('Organizador de Ata', type='tertiary'):
            st.session_state.skill = 'meeting_notes'


def get_skill() -> None:
    matrix = {
        'pt_translator': 'Tradutor para Português',
        'meeting_notes': 'Organizador de Ata'
    }

    if st.session_state.skill in matrix:
        with open(SKILLS_PATH / f'{st.session_state.skill}.md', 'r', encoding='utf-8') as f:
            st.session_state.system_instruction = f.read()

        st.title(matrix[st.session_state.skill])
    
    else:  # Conversa Genérica
        st.write("<h1 style='text-align: center;'>🤖 Bem Vindo</h1>", unsafe_allow_html=True)
        st.session_state.system_instruction = None


def get_chat() -> Chat:
    chat_index = f'chat_{st.session_state.chat_index}'
    if st.session_state[chat_index] is None:
        st.session_state[chat_index] = Chat()
    with st.expander('Conversas'):
        uploaded_chat = st.file_uploader('Upload Chat', accept_multiple_files=False, type='json',
            key=f'Uploader_{st.session_state.chat_index}'
        )
        if uploaded_chat is not None:
            if st.session_state[f'chat_{st.session_state.chat_index}'] is not None:
                if len(st.session_state[f'chat_{st.session_state.chat_index}']):
                    st.write('Você irá perder qualquer mensagem de chat não salva, prosseguir?')
                    if st.button('Sim'):
                        st.session_state[f'chat_{st.session_state.chat_index}'] = Chat.load(uploaded_chat.read())
                else:
                    st.session_state[f'chat_{st.session_state.chat_index}'] = Chat.load(uploaded_chat.read())

            else:
                st.session_state[f'chat_{st.session_state.chat_index}'] = Chat.load(uploaded_chat.read())

        elif st.session_state[f'chat_{st.session_state.chat_index}'] is None:
            st.session_state[f'chat_{st.session_state.chat_index}'] = Chat()


def get_model() -> str:
    model_name = ModelBase.query(f'CodeStr == "{st.session_state.model}"').Name.iloc[0]
    with st.expander(f'Modelo: {model_name}'):
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
    get_skill()

    # Definição de Chat Geral
    for message in st.session_state[f'chat_{st.session_state.chat_index}']:
        avatar = 'user' if message.role == 'USER' else 'assistant'
        if isinstance(message.content, list):
            for part in filter(lambda x: isinstance(x, str), message.content):
                st.chat_message(avatar).write(part)
        elif isinstance(message.content, str):
            st.chat_message(avatar).write(message.content)
    
    check_continue = True
        
    if len(st.session_state[f'chat_{st.session_state.chat_index}']) and st.session_state[f'chat_{st.session_state.chat_index}'].messages[-1].role == Role.USER:
        if st.session_state.api_key is None:
            check_continue = False
        else:
            try:
                with st.spinner('Pensando...'):
                    response = generate_content(
                        api_key=st.session_state.api_key,
                        model=st.session_state.model,
                        chat=st.session_state[f'chat_{st.session_state.chat_index}'],
                        system_instruction=st.session_state.system_instruction
                    )
                st.session_state[f'chat_{st.session_state.chat_index}'].model_message(response.text)
                st.chat_message('assistant').write(response.text)
            except (ValueError, ClientError) as e:
                if 'api_key' in str(e) or 'API_KEY_INVALID' in str(e):
                    check_continue = False
                else:
                    raise
        
        # st.session_state[f'chat_{st.session_state.chat_index}'].model_message('Testado')
        # st.chat_message('assistant').write('Testado')
    if check_continue:    
        user_prompt = st.chat_input(accept_file='multiple')

        if user_prompt:
            st.session_state[f'chat_{st.session_state.chat_index}'].user_prompt_message(text=user_prompt.text, files=user_prompt.files)
            # st.write(st.session_state[f'chat_{st.session_state.chat_index}'])

        return user_prompt

    else:
        st.toast('Fornça uma chave API válida para continuar')
        return False
