import streamlit as st


st.file_uploader('Fontes', accept_multiple_files=True)

st.write(
'''
A ideia aqui é montar um processo de Vetorização RAG.<br>
Esse processo possibilita a gravação de um banco de dados local para utilização como fonte em uma conversa
''',
unsafe_allow_html=True
)

