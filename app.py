import streamlit as st
import requests
import json
import re

# --- CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="Fluxograma 2.5", layout="wide")
st.title("Fluxograma Industrial (Motor Gemini 2.5)")

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("Configuração")
    # Cole a mesma chave que você usou para listar os modelos
    api_key = st.text_input("Cole sua API Key:", type="password")
    st.success("Sistema calibrado para: gemini-2.5-flash")

# --- ÁREA DE OPERAÇÃO ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Descreva o Processo")
    texto_padrao = """Recebimento de matéria-prima.
Verificação de qualidade.
Se aprovado, vai para o estoque.
Se reprovado, devolve ao fornecedor.
Do estoque, segue para produção."""
    descricao = st.text_area("Etapas:", value=texto_padrao, height=300)
    gerar = st.button("Gerar Fluxograma", type="primary")

# --- EXECUÇÃO TÁTICA ---
if gerar:
    if not api_key:
        st.error("Sem chave, sem jogo, General.")
    else:
        # AQUI ESTÁ A MÁGICA: Usando o modelo que sua lista confirmou que existe
        modelo_escolhido = "gemini-2.5-flash"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo_escolhido}:generateContent?key={api_key}"
        
        # Cabeçalhos e Prompt
        headers = {'Content-Type': 'application/json'}
        prompt = f"""
        Você é um especialista em processos industriais. Crie um código Graphviz (DOT) para:
        "{descricao}"
        
        Regras Visuais:
        1. Layout horizontal (rankdir=LR).
        2. Nós de decisão (Se/Então) = losango (shape=diamond, style=filled, color=orange).
        3. Ações/Processos = retângulo (shape=box, style=filled, color=lightblue).
        4. Início/Fim = oval (shape=ellipse, style=filled, color=lightgrey).
        5. Retorne APENAS o código DOT dentro de ```dot ... ```.
        """
        
        data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }

        with st.spinner(f'Acionando {modelo_escolhido}...'):
            try:
                # Disparo direto
                response = requests.post(url, headers=headers, data=json.dumps(data))
                
                if response.status_code == 200:
                    resultado = response.json()
                    try:
                        texto = resultado['candidates'][0]['content']['parts'][0]['text']
                        
                        # Limpa o texto para pegar só o código do gráfico
                        match = re.search(r'```(?:dot)?\s*(.*?)```', texto, re.DOTALL)
                        if match:
                            codigo_dot = match.group(1)
                            with col2:
                                st.subheader("Visualização")
                                st.graphviz_chart(codigo_dot)
                                with st.expander("Ver Código Fonte"):
                                    st.code(codigo_dot)
                        else:
                            st.warning("O modelo respondeu, mas esqueceu da formatação de código.")
                            st.write(texto)
                    except:
                        st.error("Erro ao interpretar a resposta.")
                else:
                    # Se der erro, mostra o motivo exato
                    erro = response.json()
                    st.error(f"Erro {response.status_code}: {erro.get('error', {}).get('message')}")
                    
            except Exception as e:
                st.error(f"Erro de conexão: {e}")

st.markdown("---")
st.caption("Ferramenta Tática v4.0 - Direct Link")
