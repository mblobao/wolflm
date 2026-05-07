from pathlib import Path
import re


def split_md_to_prompt_parameters(file_name: str) -> dict[str, str]:
    with open(file_name, 'r', encoding='utf-8') as f:
        text = f.read()

    pattern = '\n<([A-z]+)>\n'
    sections = re.findall(pattern, text)
    texts = [i for i in re.split(pattern, text)[1:] if i not in sections]
    return {k: v for k, v in zip(sections, texts)}


def build_prompt(
    context: str = None,
    persona: str = None,
    task: str = None,
    input_format: str = None,
    output_format: str = None,
    restrictions: str = None,
    tone: str = None,
    audience: str = None,
    examples: str = None,
    reasoning_instructions: str = None
) -> str:
    
    def get_value(value):
        if isinstance(value, (str, Path)) and str(value).lower().endswith('.md'):
            with open(value, 'r', encoding='utf-8') as f:
                return f.read()
        elif isinstance(value, str):
            return value

        raise TypeError(f'invalid value type {type(value)}')
        
    prompt_parts = []
    
    if context:
        prompt_parts.append('## CONTEXTO')
        prompt_parts.append(get_value(context))

    if persona:
        prompt_parts.append('## PAPEL')
        prompt_parts.append(get_value(persona))

    if task:
        prompt_parts.append('## OBJETIVO')
        prompt_parts.append(get_value(task))

    if input_format:
        prompt_parts.append('## FORMATO DOS DADOS DE ENTRADA')
        prompt_parts.append(get_value(input_format))

    if output_format:
        prompt_parts.append('## FORMATO DA RESPOSTA')
        prompt_parts.append(get_value(output_format))

    if tone:
        prompt_parts.append('## TOM E ESTILO')
        prompt_parts.append(get_value(tone))

    if restrictions:
        prompt_parts.append('## RESTRIÇÕES')
        prompt_parts.append(get_value(restrictions))

    if audience:
        prompt_parts.append('## PÚBLICO-ALVO')
        prompt_parts.append(get_value(audience))

    if examples:
        prompt_parts.append('## EXEMPLOS')
        prompt_parts.append(get_value(examples))

    if reasoning_instructions:
        prompt_parts.append('## INSTRUÇÕES DE RACIOCÍNIO')
        prompt_parts.append(get_value(reasoning_instructions))
    
    return "\n\n".join(prompt_parts)