import streamlit as st
import requests
import json
import re

# --- CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="Fluxograma", layout="wide")
st.title("Fluxograma Tático Industrial")

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("Munição (API Key)")
    api_key = st.text_input("Cole a API Key:", type="password")
    st.info("Usando conexão direta via REST API (Sem intermédios).")

# --- ÁREA DE OPERAÇÃO ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Instruções do Processo")
    texto_padrao = """Recebimento de sucata.
Classificação manual.
Se for metal ferroso, vai para a prensa.
Se for não-ferroso, vai para separação magnética.
Expedição para fundição."""
    descricao = st.text_area("Descreva as etapas:", value=texto_padrao, height=300)
    gerar = st.button("Executar Missão", type="primary")

# --- LÓGICA DE COMBATE (REST API) ---
if gerar:
    if not api_key:
        st.error("ERRO: A arma está sem munição (Falta API Key).")
    else:
        # ENDEREÇO DIRETO DO ALVO (Gemini 1.5 Flash)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        
        # O PACOTE DE DADOS (Payload)
        headers = {'Content-Type': 'application/json'}
        prompt = f"""
        Você é um especialista em Graphviz. Crie um fluxograma para este processo:
        "{descricao}"
        
        Regras:
        1. Rankdir=LR.
        2. Nós de decisão = diamantes (diamond).
        3. Ações = caixas (box).
        4. Retorne APENAS o código DOT dentro de ```dot ... ```.
        """
        
        data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }

        with st.spinner('Estabelecendo conexão direta...'):
            try:
                # DISPARO HTTP
                response = requests.post(url, headers=headers, data=json.dumps(data))
                
                if response.status_code == 200:
                    # Extração da resposta
                    resultado = response.json()
                    texto_resposta = resultado['candidates'][0]['content']['parts'][0]['text']
                    
                    # Limpeza do código DOT
                    match = re.search(r'```(?:dot)?\s*(.*?)```', texto_resposta, re.DOTALL)
                    
                    if match:
                        codigo_dot = match.group(1)
                        with col2:
                            st.subheader("Mapa Visual")
                            st.graphviz_chart(codigo_dot)
                            with st.expander("Ver Código Fonte"):
                                st.code(codigo_dot)
                    else:
                        st.warning("A API respondeu, mas não mandou o código formatado. Tente de novo.")
                else:
                    st.error(f"Erro no disparo: {response.status_code}")
                    st.write(response.text)
                    
            except Exception as e:
                st.error(f"Falha na conexão: {e}")

st.markdown("---")
st.caption("Sistema de Mapeamento Direto v2.0")
