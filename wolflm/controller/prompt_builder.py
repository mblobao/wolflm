from wolflm.controller import generate_content
from wolflm.chat import Chat
from pathlib import Path
import streamlit as st


def assembly_prompt(
    contexto, objetivo, papel, formato, restricoes, tom, publico,
    exemplos: str = None, raciocinio: str = None
) -> str:
    prompt_parts = []
    
    if contexto:
        prompt_parts.append(f"**[CONTEXTO]**\n{contexto}")
    
    if papel:
        prompt_parts.append(f"**[PAPEL]**\nAtue como {papel}")
    
    if objetivo:
        prompt_parts.append(f"**[OBJETIVO]**\n{objetivo}")
    
    if formato:
        prompt_parts.append(f"**[FORMATO]**\n{formato}")
    
    if restricoes:
        prompt_parts.append(f"**[RESTRIÇÕES]**\n{restricoes}")
    
    if tom:
        prompt_parts.append(f"**[TOM E ESTILO]**\n{tom}")
    
    if publico:
        prompt_parts.append(f"**[PÚBLICO-ALVO]**\n{publico}")
    
    if exemplos:
        prompt_parts.append(f"**[EXEMPLOS]**\n{exemplos}")
    
    if raciocinio:
        prompt_parts.append(f"**[INSTRUÇÕES DE RACIOCÍNIO]**\n{raciocinio}")
    
    return "\n\n".join(prompt_parts)


def generate_prompt(prompt_final: str, descricao: str) -> str:
    with open(Path(__file__).parent.parent / 'skills' / 'prompt_builder.md', 'r', encoding='utf-8') as f:
        system_instruction = f.read()
    
    response = generate_content(
        chat=Chat().user_message([descricao, prompt_final]),
        system_instruction=system_instruction,
        thinking=True
    )
    return response.text
