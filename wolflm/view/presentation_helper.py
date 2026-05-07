from wolflm.controller.presentation_helper import process
import streamlit as st


st.set_page_config(page_title="Auxiliador de Apresentação", layout="wide")

def generate_presentation_helper():
    st.title("Auxiliador de Apresentação")
    colunas = st.columns(2)

    with colunas[0]:
        descricao = st.text_area('Descreva sua apresentação')
        contexto = st.text_area('Descreva o Contexto da Apresentação')

    with colunas[1]:
        files = st.file_uploader('Upload', accept_multiple_files=True)
        publico = st.text_input('Descreva o Público Alvo')
        objetivo = st.text_input('Descreva o Objetivo da Apresentação')
        tempo = st.number_input('Tempo Estimado de Apresentação em minutos', min_value=0,)

    if st.button('🚀 Gerar', type='primary'):
        process(descricao, contexto, files, publico, objetivo)
