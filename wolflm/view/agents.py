from wolflm.controller.prompt_builder import assembly_prompt, generate_prompt
from wolflm.controller.presentation_helper import presentation_helper_process
import streamlit as st


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
        presentation_helper_process(descricao, contexto, files, publico, objetivo)



def generate_prompt_builder():
    st.title("🤖 Construtor de Prompts para LLM")
    st.markdown("### Crie prompts estruturados e eficazes seguindo as melhores práticas")
    st.markdown("---")

    # Layout em colunas
    col1, col2 = st.columns([1, 1])

    with col1:
        st.header("📝 Preencha os Campos")
        
        # Campo 1: Contexto
        with st.expander("1️⃣ Contexto e Cenário", expanded=False):
            st.caption("Explique a situação ou ambiente onde a tarefa se insere")
            contexto = st.text_area(
                "Contexto",
                placeholder="Exemplo: Sou gerente de produto em uma startup de fintech focada em microcrédito...",
                height=100,
                label_visibility="collapsed"
            )
        
        # Campo 2: Objetivo
        with st.expander("2️⃣ Objetivo Claro", expanded=False):
            st.caption("Defina exatamente o que você quer alcançar")
            objetivo = st.text_area(
                "Objetivo",
                placeholder="Exemplo: Preciso criar um email para informar clientes sobre novas taxas de juros",
                height=80,
                label_visibility="collapsed"
            )
        
        # Campo 3: Papel
        with st.expander("3️⃣ Papel ou Perspectiva"):
            st.caption("Indique qual expertise você quer que o LLM adote")
            papel = st.text_input(
                "Papel",
                placeholder="Exemplo: um especialista em comunicação corporativa",
                label_visibility="collapsed"
            )
        
        # Campo 4: Formato
        with st.expander("4️⃣ Formato Desejado"):
            st.caption("Especifique como quer receber a resposta")
            formato = st.text_input(
                "Formato",
                placeholder="Exemplo: Apresente em forma de tabela comparativa com 3 colunas",
                label_visibility="collapsed"
            )
        
        # Campo 5: Restrições
        with st.expander("5️⃣ Restrições e Limitações"):
            st.caption("Indique o que evitar ou limites a respeitar")
            restricoes = st.text_area(
                "Restrições",
                placeholder="Exemplo: Máximo de 200 palavras, evite jargão técnico",
                height=80,
                label_visibility="collapsed"
            )

    with col2:
        st.header("⚙️ Configurações Adicionais")
        
        # Campo 6: Tom
        with st.expander("6️⃣ Tom e Estilo", expanded=False):
            st.caption("Defina a linguagem apropriada")
            tom = st.text_input(
                "Tom",
                placeholder="Exemplo: Tom profissional e empático",
                label_visibility="collapsed"
            )
        
        # Campo 7: Público
        with st.expander("7️⃣ Público-Alvo", expanded=False):
            st.caption("Identifique quem vai consumir a resposta")
            publico = st.text_input(
                "Público",
                placeholder="Exemplo: Para investidores experientes",
                label_visibility="collapsed"
            )
        
        # Campo 8: Exemplos
        with st.expander("8️⃣ Exemplos (opcional)"):
            st.caption("Forneça exemplos do que você quer ou não quer")
            exemplos = st.text_area(
                "Exemplos",
                placeholder="Exemplo: Como este exemplo: [seu exemplo]. Mas evite abordagens como: [contraexemplo]",
                height=100,
                label_visibility="collapsed"
            )
        
        # Campo 9: Raciocínio
        with st.expander("9️⃣ Instruções de Raciocínio (opcional)"):
            st.caption("Para tarefas complexas, peça raciocínio passo a passo")
            raciocinio = st.text_area(
                "Raciocínio",
                placeholder="Exemplo: Antes de responder, analise o problema em etapas",
                height=80,
                label_visibility="collapsed"
            )

    with st.expander("💡 Descrição geral"):
        st.caption('Forneça uma descrição geral de como você deseja o prompt ou de como ele será utilizado')
        descricao = st.text_area("Descrição", height=100, label_visibility="collapsed")

    # Botões de ação
    st.markdown("---")
    col_buttons = st.columns(4)

    with col_buttons[0]:
        gerar = st.button("🚀 Gerar Prompt", type="primary", use_container_width=True,
            help="Gerar um prompt automático com base nos campos acima"
        )

    with col_buttons[1]:
        montar = st.button("📝 Montar Prompt", use_container_width=True,
            help="Apenas organizar as informações com base nos campos acima"
        )

    with col_buttons[2]:
        limpar = st.button("🗑️ Limpar Tudo", use_container_width=True)

    # Lógica para limpar
    if limpar:
        st.rerun()

    prompt_final = assembly_prompt(contexto, objetivo, papel, formato, restricoes, tom, publico, exemplos, raciocinio)

    if not prompt_final:
        st.warning("⚠️ Preencha pelo menos o Contexto e o Objetivo para gerar um prompt!")

    if (montar or gerar) and prompt_final:    
        st.markdown("---")
        
        if gerar:
            prompt_final = generate_prompt(prompt_final, descricao)

        st.markdown(prompt_final)

        st.markdown("---")
        col_copy1, col_copy2 = st.columns([3, 1])
        
        with col_copy1:
            st.text_area(
                "Prompt em texto puro (copie daqui)",
                prompt_final,
                height=200,
                label_visibility="collapsed"
            )
        
        with col_copy2:
            st.metric("Total de caracteres", len(prompt_final))
            st.metric("Total de palavras", len(prompt_final.split()))


    # Sidebar com dicas
    with st.sidebar:
        st.header("💡 Dicas Rápidas")
        
        st.markdown("""
        **Campos Essenciais:**
        - ✅ Contexto
        - ✅ Objetivo
        - ✅ Papel
        
        **Para melhores resultados:**
        - Seja específico e detalhado
        - Use exemplos quando possível
        - Defina restrições claras
        - Itere se necessário
        
        **Lembre-se:**
        > A prática leva à perfeição na criação de prompts!
        """)
        
        st.markdown("---")
        st.markdown("### 📚 Estrutura Recomendada")
        st.code("""
    [CONTEXTO] → Situação
    [PAPEL] → Especialista
    [OBJETIVO] → O que fazer
    [FORMATO] → Como entregar
    [RESTRIÇÕES] → Limites
    [TOM] → Estilo
    [PÚBLICO] → Para quem
        """, language="text")
        
        st.markdown("---")
        st.info("**Criado para otimizar a comunicação com LLMs**")