import streamlit as st
import requests
import json

st.set_page_config(page_title="Inspetor de Modelos", layout="wide")
st.title("🕵️ Inspetor Geral de Modelos")

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("Insira a Chave")
    api_key = st.text_input("Sua API Key:", type="password")
    
# --- ÁREA DE AÇÃO ---
st.write("Esse aplicativo vai listar exatamente quais modelos sua chave tem permissão para usar.")

if st.button("Listar Modelos Disponíveis"):
    if not api_key:
        st.error("Precisa da chave, General.")
    else:
        # URL oficial para listar modelos
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
        
        try:
            response = requests.get(url)
            
            if response.status_code == 200:
                dados = response.json()
                modelos = dados.get('models', [])
                
                # Filtra apenas os que geram texto (que é o que a gente quer)
                uteis = [m for m in modelos if 'generateContent' in m.get('supportedGenerationMethods', [])]
                
                if uteis:
                    st.success(f"Sucesso! Encontrei {len(uteis)} modelos disponíveis para você.")
                    
                    st.subheader("Copie um destes nomes exatos:")
                    
                    # Mostra a lista bonitinha
                    for m in uteis:
                        nome_real = m['name'].replace('models/', '') # Tira o prefixo pra ficar fácil
                        st.code(nome_real, language="text")
                        st.caption(f"Versão completa: {m['name']}")
                        st.markdown("---")
                else:
                    st.warning("Sua chave funciona, mas não tem modelos de geração de texto habilitados.")
            else:
                st.error(f"Erro ao conectar: {response.status_code}")
                st.json(response.json())
                
        except Exception as e:
            st.error(f"Erro técnico: {e}")
