import streamlit as st
import google.generativeai as genai
import re

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Fluxograma", layout="wide")
st.title("Fluxograma de Processo Industrial")

# --- BARRA LATERAL (Munição) ---
with st.sidebar:
    st.header("Configuração")
    api_key = st.text_input("Cole sua API Key do Google Gemini:", type="password")
    st.markdown("[Obter chave gratuita aqui](https://aistudio.google.com/app/apikey)")
    st.info("Nota: O sistema não salva sua chave. Ao recarregar a página, cole novamente.")

# --- ÁREA DE COMANDO ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("1. Descreva o Processo")
    texto_padrao = """Recebimento de matéria-prima.
Se a qualidade for boa, vai para o estoque.
Se a qualidade for ruim, devolve para o fornecedor.
Do estoque, vai para a produção.
Embala e envia."""
    
    descricao = st.text_area("Digite as etapas aqui:", value=texto_padrao, height=300)
    gerar = st.button("Gerar Fluxograma", type="primary")

# --- EXECUÇÃO TÁTICA ---
if gerar:
    if not api_key:
        st.error("ERRO: Precisa da API Key no menu lateral pra funcionar, General.")
    else:
        try:
            # Configura a IA
            genai.configure(api_key=api_key)
            
            # MODELO ATUALIZADO (Requer google-generativeai>=0.8.3)
            model = genai.GenerativeModel('gemini-1.5-flash')

            # O PROMPT DE COMANDO
            prompt_sistema = f"""
            Aja como um especialista em engenharia de processos.
            Sua missão: Ler a descrição e criar um código Graphviz (DOT) válido.
            
            Regras visuais obrigatórias:
            1. Use `rankdir=LR` (da esquerda para direita).
            2. Nós de AÇÃO = retangulares (`shape=box`, `style=filled`, `color=lightblue`).
            3. Nós de DECISÃO = diamantes (`shape=diamond`, `style=filled`, `color=orange`).
            4. Nós de INÍCIO/FIM = ovais (`shape=ellipse`).
            5. Use rótulos nas setas de decisão (ex: "Sim", "Não").
            
            Retorne APENAS o código dentro de um bloco markdown ```dot ... ```.
            
            Descrição do processo:
            {descricao}
            """

            with st.spinner('Desenhando a estratégia...'):
                response = model.generate_content(prompt_sistema)
                texto_resposta = response.text
                
                # Extrai o código DOT usando Regex (para ignorar textos extras)
                match = re.search(r'```(?:dot)?\s*(.*?)```', texto_resposta, re.DOTALL)
                
                if match:
                    codigo_dot = match.group(1)
                    
                    # Renderiza na coluna 2
                    with col2:
                        st.subheader("2. Visualização")
                        st.graphviz_chart(codigo_dot)
                        
                        with st.expander("Ver código fonte (DOT)"):
                            st.code(codigo_dot)
                else:
                    st.error("A IA respondeu, mas não mandou o código DOT correto. Tente simplificar o texto.")
                    st.write(texto_resposta) # Mostra o erro se houver
                    
        except Exception as e:
            st.error(f"Falha na missão: {e}")

# Rodapé
st.markdown("---")
st.caption("Ferramenta de uso interno.")
