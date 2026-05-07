from wolflm.controller.prompt_builder import assembly_prompt
from wolflm.utils import SKILLS_PATH
import streamlit as st
import re


@st.cache_data
def get_system_prompt():
    with open(SKILLS_PATH / 'presentation_helper.md', 'r', encoding='utf-8') as f:
        texto = f.read()

    pattern = '.*?'.join(( '<CONTEXTO>(.*?)</CONTEXTO>', '<PAPEL>(.*?)</PAPEL>',
        '<TAREFA>(.*?)</TAREFA>', '<FORMATO>(.*?)</FORMATO>',
        '<RESTRIÇÕES>(.*?)</RESTRIÇÕES>', '<TOM>(.*?)</TOM>',
        '<PÚBLICO>(.*?)</PÚBLICO>', '<INSTRUÇÕES DE RACIOCÍNIO>(.*?)</INSTRUÇÕES DE RACIOCÍNIO>'
    ))
    contexto_0, papel, tarefa, formato, restricoes, tom, publico_0, raciocinio = re.search(pattern, texto, re.DOTALL).groups()

    task_pattern = '[0-9]+. (.*?)\n'
    
    roteiros, argumentacao, alinhamento, discursos, simulacao = re.findall(task_pattern, tarefa, re.DOTALL)
    return (
        contexto_0, papel, tarefa, formato, restricoes, tom, publico_0, raciocinio,
        (roteiros, argumentacao, alinhamento, discursos, simulacao)
    )


def process(descricao, contexto, files, publico, objetivo):
    # progress = st.progress(0, text="Processando...")
    (
        contexto_0, papel, tarefa, formato, restricoes, tom, publico_0, raciocinio,
        (roteiros, argumentacao, alinhamento, discursos, simulacao)
    ) = get_system_prompt()
    
    system_instruction = assembly_prompt(
        contexto=contexto_0,
        objetivo=tarefa,
        papel=papel,
        formato=formato,
        restricoes=restricoes,
        tom=tom,
        publico=publico_0,
        raciocinio=raciocinio,
    )
