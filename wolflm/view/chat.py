from wolflm.controller.wolfchat import skill_choice, get_model, get_chat, generate_standard_chat
from wolflm.view.presentation_helper import generate_presentation_helper
from wolflm.view.prompt_builder import generate_prompt_builder
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
if 'chat_index' not in st.session_state:
    st.session_state.chat_index = 0

if f'chat_{st.session_state.chat_index}' not in st.session_state:
    st.session_state[f'chat_{st.session_state.chat_index}'] = None

for state in {'chat', 'Uploader'}:
    for i in range(st.session_state.chat_index):
        if f'{state}_{i}' in st.session_state:
            del st.session_state[f'{state}_{i}']


with st.sidebar:
    st.text_input('Gemini API Key', key='api_key')
    get_model()
    kwargs = {'type': 'tertiary'}
    with st.popover('Nova Conversa', ):
        st.write('Você irá perder qualquer mensagem de chat não salva, carregar?')
        if st.button('Sim '):
            st.session_state.skill = None
            st.session_state.chat_index += 1
            st.session_state[f'chat_{st.session_state.chat_index}'] = None
            st.rerun()
    
    # Definição de Agente
    with st.expander('Agentes'):
        presetation_helper = st.button('Auxiliador de Apresentação', **kwargs)
        prompt_builder = st.button('Construtor de Prompts', **kwargs)
    
    # Definição de Habilidades
    skill_choice()
    
    # Definição de Conversa
    get_chat()


cols = st.columns((4, 1, 1))
# with cols[0]:
#     # Seleção de Modelos
#     get_model()

# User Interface Principal
if presetation_helper:
    generate_presentation_helper()
elif prompt_builder:
    generate_prompt_builder()
else:
    user_prompt = generate_standard_chat()
    if user_prompt:
        st.rerun()
    if user_prompt is not None:
        pass
    elif len(st.session_state[f'chat_{st.session_state.chat_index}']):
        with cols[1]:
            with st.popover('Salvar Chat'):
                filename = st.text_input('Nome do arquivo', 'Chat')
                st.download_button('OK ', data=st.session_state[f'chat_{st.session_state.chat_index}'].to_json_str(), file_name=f'{filename}.json')
        with cols[2]:
            with st.popover('Salvar Resposta'):
                filename = st.text_input('Nome do arquivo ', 'Chat')
                st.download_button('OK  ', data=st.session_state[f'chat_{st.session_state.chat_index}'].messages[-1].content, file_name=f'{filename}.md')
