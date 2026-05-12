from wolflm.view.agents import generate_presentation_helper, generate_prompt_builder
from streamlit.runtime.uploaded_file_manager import UploadedFile
from wolflm.controller import generate_content
import streamlit_antd_components as sac
from wolflm.utils import SKILLS_PATH
from wolflm.llm.models import Model
from wolflm.chat.base import Role
from wolflm.chat import Chat
import streamlit as st


def get_model() -> None:
    with st.container(border=True):
        st.selectbox('Familia', options=['Claude', 'Gemini', 'OpenAI', 'DeepSeek'], key='family')

        if st.session_state.model:
            model_name = Model.query(f'CodeStr == "{st.session_state.model}"').Name.iloc[0]
        else:
            model_name = ''

        with st.expander(f'Modelo: {model_name}'):
            cols = st.columns(2)
            with cols[0]:
                max_context = float(Model.DataSet.ContextWindow.max())
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
                models = Model.query(qry)['Name']
                selected_model = sac.tree(show_line=False,
                    items=[sac.TreeItem(model_name) for model_name in models]
                )
            if selected_model is not None:
                st.session_state.model = Model.query(f'Name == "{selected_model}"').CodeStr.iloc[0]
                st.session_state.model_name = Model.query(f'Name == "{selected_model}"').Name.iloc[0]
        
        family = (
            'Gemini' if st.session_state.family == 'Gemini' else
            'Anthropic' if st.session_state.family == 'Claude' else
            'OpenAI' if st.session_state.family == 'OpenAI' else
            'DeepSeek' if st.session_state.family == 'DeepSeek' else
            None
        )
        st.text_input(f'{family} API Key', key='api_key')


def new_chat_button() -> None:
    def new_chat():
        st.session_state.skill = None
        st.session_state.chat_index += 1
        st.session_state[f'chat_{st.session_state.chat_index}'] = None
    
    def popover() -> None:
        with st.popover('Nova Conversa', type='tertiary'):
            st.write('Você irá perder qualquer mensagem de chat não salva, carregar?')
            if st.button('Sim ', on_click=new_chat):
                st.session_state.agent = None
                st.rerun()

    if st.session_state.agent:
        popover()

    elif st.session_state[f'chat_{st.session_state.chat_index}']:
        if len(st.session_state[f'chat_{st.session_state.chat_index}']):
            popover()
    
    else:
        st.button('Nova Conversa', on_click=new_chat, type='tertiary', disabled=True)


def agents_choice() -> None:
    with st.expander('Agentes'):
        if st.button('Construtor de Prompts', type='tertiary'):
            st.session_state.agent = 'prompt_builder'
            st.rerun()
        # if st.button('Auxiliador de Apresentação', type='tertiary'):
        #     st.session_state.agent = 'presentation_helper'



def generate_page():
    if st.session_state.family in {'OpenAI', 'Claude', 'DeepSeek'}:
        st.error(f'A família de LLM {st.session_state.family} ainda não está disponível')

    elif st.session_state.agent == 'prompt_builder':
        generate_prompt_builder()
    elif st.session_state.agent == 'presentation_helper':
        generate_presentation_helper()
    else:
        user_prompt = generate_standard_chat()

        if user_prompt:
            st.rerun()


def skill_choice() -> None:
    with st.expander('Habilidades'):
        if st.button('Nenhuma', type='tertiary'):
            st.session_state.skill = None
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

        st.title(matrix[st.session_state.skill], text_alignment='center')
    
    else:  # Conversa Genérica
        st.title("Bem Vindo", text_alignment='center')
        st.session_state.system_instruction = None


def get_chat() -> Chat:
    chat_state = f'chat_{st.session_state.chat_index}'
    uploader_state = f'Uploader_{st.session_state.chat_index}'

    if st.session_state[chat_state] is None:
        st.session_state[chat_state] = Chat()

    with st.expander('Conversas'):
        uploaded_chat = st.file_uploader('Upload Chat', accept_multiple_files=False, type='json', key=uploader_state)
        if uploaded_chat is not None:
            if st.session_state[chat_state] is not None:
                if len(st.session_state[chat_state]):
                    st.write('Você irá perder qualquer mensagem de chat não salva, prosseguir?')
                    if st.button('Sim'):
                        st.session_state[chat_state] = Chat.load(uploaded_chat.read())
                else:
                    st.session_state[chat_state] = Chat.load(uploaded_chat.read())

            else:
                st.session_state[chat_state] = Chat.load(uploaded_chat.read())

        elif st.session_state[chat_state] is None:
            st.session_state[chat_state] = Chat()


def generate_standard_chat() -> None | dict[str, str | list[UploadedFile]]:
    get_skill()

    cols = st.columns((4, 1, 1))

    with cols[0]:  # Opções de pesquisa e raciocício
        st.toggle('Pesquisa Online', key='research', disabled=(len(st.session_state[f'chat_{st.session_state.chat_index}']) > 0))
        st.toggle('Raciocínio', key='thinking', disabled=(len(st.session_state[f'chat_{st.session_state.chat_index}']) > 0))

    # Definição de Chat Geral
    for message in st.session_state[f'chat_{st.session_state.chat_index}'].generate_chat():
        avatar = 'user' if message.role == 'USER' else 'assistant'
        if isinstance(message.content, list):
            for part in filter(lambda x: isinstance(x, str), message.content):
                st.chat_message(avatar).write(part)
        elif isinstance(message.content, str):
            st.chat_message(avatar).write(message.content)
    
    
    check_continue = True
    if len(st.session_state[f'chat_{st.session_state.chat_index}']) and st.session_state[f'chat_{st.session_state.chat_index}'].messages[-1].role == Role.USER:
        check_continue, response = generate_content()

    if check_continue:    
        if len(st.session_state[f'chat_{st.session_state.chat_index}']):
            with cols[1]:
                with st.popover('Salvar Chat'):
                    filename = st.text_input('Nome do arquivo', 'Chat')
                    st.download_button('OK ', data=st.session_state[f'chat_{st.session_state.chat_index}'].to_json_str(), file_name=f'{filename}.json')
            with cols[2]:
                with st.popover('Salvar Resposta'):
                    filename = st.text_input('Nome do arquivo ', 'Chat')
                    st.download_button('OK  ', data=st.session_state[f'chat_{st.session_state.chat_index}'].messages[-1].content, file_name=f'{filename}.md')
        
        user_prompt = st.chat_input(accept_file='multiple')

        if user_prompt:
            st.session_state[f'chat_{st.session_state.chat_index}'].user_prompt_message(text=user_prompt.text, files=user_prompt.files)

        return user_prompt

    else:
        st.toast('Fornça uma chave API válida para continuar')
        return False
