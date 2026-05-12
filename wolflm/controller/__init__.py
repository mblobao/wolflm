from wolflm.llm import gemini, claude, openai, deepseek
from google.genai.errors import ClientError
from wolflm.chat import Chat
from typing import Any
import streamlit as st


def generate_content(
    chat: Chat | None = None,
    system_instruction: str | None = None,
    google_search: bool | None = None,
    thinking: bool | None = None
) -> tuple[bool, Any]:
    module = (
        gemini if st.session_state.family == 'Gemini' else
        claude if st.session_state.family == 'Claude' else
        openai if st.session_state.family == 'OpenAI' else
        deepseek if st.session_state.family == 'DeepSeek' else
        None
    )
    secret_key = (
        'GEMINI_API_KEY' if st.session_state.family == 'Gemini' else
        'ANTHROPIC_API_KEY' if st.session_state.family == 'Claude' else
        'OPENAI_API_KEY' if st.session_state.family == 'OpenAI' else
        'DEEPSEEK_API_KEY' if st.session_state.family == 'DeepSeek' else
        None
    )
    check_continue, response = True, None
    if st.session_state.api_key is None:
        check_continue = False
    else:
        try:
            with st.spinner('Pensando...'):
                response = module.generate_content(
                    api_key=st.session_state.api_key if st.session_state.api_key else st.secrets[secret_key],
                    model=st.session_state.model,
                    chat=chat if chat else st.session_state[f'chat_{st.session_state.chat_index}'],
                    system_instruction=system_instruction if system_instruction else st.session_state.system_instruction,
                    google_search=google_search if google_search else st.session_state.research,
                    thinking=thinking if thinking else st.session_state.thinking
                )
            st.session_state[f'chat_{st.session_state.chat_index}'].model_message(response.text)
            st.chat_message('assistant').write(response.text)
        except (ValueError, ClientError) as e:
            if 'api_key' in str(e) or 'API_KEY_INVALID' in str(e):
                check_continue = False
            else:
                raise
    
    return check_continue, response
    
