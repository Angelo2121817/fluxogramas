import streamlit as st
import google.generativeai as genai
import re

st.set_page_config(page_title="Fluxograma", layout="wide")
st.title("Fluxograma de Processo Industrial")

with st.sidebar:
    st.header("Configuração")
    api_key = st.text_input("Cole sua API Key:", type="password")

col1, col2 = st.columns([1, 2])

with col1:
    descricao = st.text_area("Descreva o processo:", height=300)
    gerar = st.button("Gerar Fluxograma", type="primary")

if gerar and api_key:
    try:
        genai.configure(api_key=api_key)
        # O PULO DO GATO: Usando o modelo FLASH
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        Crie um código Graphviz (DOT) válido para este processo.
        Use rankdir=LR. Nós de decisão em diamante, ações em caixa.
        Retorne APENAS o código dentro de ```dot ... ```.
        Processo: {descricao}
        """
        
        response = model.generate_content(prompt)
        match = re.search(r'```(?:dot)?\s*(.*?)```', response.text, re.DOTALL)
        if match:
            st.graphviz_chart(match.group(1))
        else:
            st.error("Erro na leitura da resposta.")
            
    except Exception as e:
        st.error(f"Erro: {e}")
