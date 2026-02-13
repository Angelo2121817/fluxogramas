import streamlit as st
import google.generativeai as genai
import re

# Configuração da página
st.set_page_config(page_title="Fluxograma", layout="wide")
st.title("Fluxograma de Processo Industrial")

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("Configuração")
    api_key = st.text_input("Cole sua API Key do Google Gemini:", type="password")
    st.markdown("[Obter chave gratuita](https://aistudio.google.com/app/apikey)")

# --- ÁREA PRINCIPAL ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Descreva o Processo")
    texto_padrao = """Recebimento de matéria-prima.
Se a qualidade for boa, vai para o estoque.
Se a qualidade for ruim, devolve para o fornecedor.
Do estoque, vai para a produção.
Embala e envia."""
    descricao = st.text_area("Digite as etapas aqui:", value=texto_padrao, height=300)
    gerar = st.button("Gerar Fluxograma", type="primary")

# --- LÓGICA DO PROCESSO ---
if gerar:
    if not api_key:
        st.error("ERRO: Precisa da API Key no menu lateral pra funcionar, General.")
    else:
        try:
            # Configura a IA
            genai.configure(api_key=api_key)
            
            # AQUI ESTAVA O ERRO (Agora corrigido e com modelo PRO)
            model = genai.GenerativeModel('gemini-pro')

            # O PROMPT DE COMANDO
            prompt_sistema = f"""
            Aja como um especialista em engenharia de produção e processos industriais.
            Sua missão: Ler a descrição de um processo e transformá-lo em código Graphviz (DOT) válido.
            
            Regras visuais obrigatórias:
            1. Use `rankdir=LR` (fluxo da esquerda para direita).
            2. Nós de INÍCIO e FIM devem ser ovais (`shape=ellipse`).
            3. Nós de AÇÃO/PROCESSO devem ser retangulares (`shape=box`, `style=filled`, `color=lightblue`).
            4. Nós de DECISÃO (condicionais "se/então") devem ser diamantes (`shape=diamond`, `style=filled`, `color=orange`).
            5. Use setas com rótulos para as decisões (ex: "Sim", "Não", "Aprovado").
            
            Retorne APENAS o código dentro de um bloco de código markdown. Sem conversinha.
            
            Descrição do processo para converter:
            {descricao}
            """

            with st.spinner('Processando a estratégia...'):
                response = model.generate_content(prompt_sistema)
                
                texto_resposta = response.text
                match = re.search(r'```(?:dot)?\s*(.*?)```', texto_resposta, re.DOTALL)
                
                if match:
                    codigo_dot = match.group(1)
                    with col2:
                        st.subheader("Visualização")
                        st.graphviz_chart(codigo_dot)
                        with st.expander("Ver código fonte (DOT)"):
                            st.code(codigo_dot)
                else:
                    st.error("A IA respondeu algo estranho. Tente simplificar o texto.")
                    
        except Exception as e:
            st.error(f"Falha na missão: {e}")

st.markdown("---")
st.caption("Ferramenta interna de mapeamento de processos.")
