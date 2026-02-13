import streamlit as st
import requests
import json
import re

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gerador de Fluxograma A4 Pro", layout="wide")

# --- CSS DE CONTENÇÃO ABSOLUTA ---
# Este CSS é agressivo para garantir que o gráfico NUNCA saia da folha
st.markdown("""
    <style>
    /* Estilização do fundo para parecer um editor de documentos */
    .main { background-color: #525659 !important; }
    
    /* Centraliza a folha na tela */
    .block-container {
        padding-top: 2rem !important;
        display: flex !important;
        justify-content: center !important;
    }

    /* A FOLHA A4 - Limites Rigorosos */
    .a4-page {
        background-color: white !important;
        width: 210mm !important;
        height: 297mm !important;
        padding: 10mm !important;
        box-shadow: 0 0 20px rgba(0,0,0,0.4);
        display: flex;
        flex-direction: column;
        overflow: hidden !important; /* Corta qualquer coisa que tente sair */
        box-sizing: border-box;
        margin: auto;
    }

    /* FORÇA O GRÁFICO A CABER */
    /* O Streamlit usa um contêiner específico para o Graphviz, vamos domá-lo */
    [data-testid="stGraphvizChart"] {
        width: 100% !important;
        display: flex !important;
        justify-content: center !important;
        overflow: hidden !important;
    }

    [data-testid="stGraphvizChart"] svg {
        width: 100% !important;
        height: auto !important;
        max-height: 230mm !important; /* Deixa espaço para o cabeçalho */
        object-fit: contain !important; /* Mantém a proporção sem cortar */
    }

    /* CABEÇALHO COMPACTO */
    .header-table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 15px;
        border: 2px solid #333;
    }
    .header-table td {
        border: 1px solid #333;
        padding: 8px;
        font-family: 'Arial', sans-serif;
    }
    .title-cell {
        background-color: #f0f0f0;
        text-align: center;
        font-weight: bold;
        font-size: 16pt;
        text-transform: uppercase;
    }
    .label { font-size: 8pt; color: #666; font-weight: bold; display: block; }
    .value { font-size: 10pt; font-weight: bold; color: #000; }

    /* REGRAS DE IMPRESSÃO */
    @media print {
        header, footer, .stSidebar, .stButton, [data-testid="stHeader"], .no-print {
            display: none !important;
        }
        .main, .block-container {
            background-color: white !important;
            padding: 0 !important;
            margin: 0 !important;
        }
        .a4-page {
            box-shadow: none !important;
            border: none !important;
            margin: 0 !important;
            padding: 10mm !important;
            width: 210mm !important;
            height: 297mm !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("⚙️ Configurações")
    empresa = st.text_input("Sua Empresa:", "NOME DA EMPRESA")
    cliente = st.text_input("Nome do Cliente:", "CLIENTE EXEMPLO")
    projeto = st.text_input("Nome do Projeto:", "PROCESSO INDUSTRIAL V1")
    
    st.markdown("---")
    api_key = st.text_input("Gemini API Key:", type="password")
    
    st.markdown("---")
    st.header("🎨 Estilo")
    orientacao = st.selectbox("Fluxo:", ["Vertical", "Horizontal"])
    rankdir = "TB" if orientacao == "Vertical" else "LR"
    cor_proc = st.color_picker("Cor dos Blocos:", "#E1F5FE")
    cor_dec = st.color_picker("Cor dos Losangos:", "#FFF9C4")

# --- INTERFACE ---
st.title("📊 Gerador de Fluxogramas A4")

col_in, col_btn = st.columns([3, 1])
with col_in:
    prompt_texto = st.text_area("Descreva o processo:", "Início.\nReceber pedido.\nSe aprovado, produzir.\nSe negado, cancelar.\nFim.", height=80)
with col_btn:
    st.write("###")
    gerar = st.button("🚀 GERAR FLUXOGRAMA", use_container_width=True, type="primary")
    if 'dot_code' in st.session_state:
        st.markdown("""
            <button onclick="window.print()" style="width:100%; height:3.5em; background-color:#28a745; color:white; border:none; border-radius:5px; cursor:pointer; font-weight:bold;">
                📥 SALVAR COMO PDF
            </button>
        """, unsafe_allow_html=True)

# --- LÓGICA IA ---
if gerar:
    if not api_key:
        st.error("Insira a chave da API.")
    else:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        # Prompt que força o gráfico a ser compacto
        prompt_ia = f"""
        Crie um código Graphviz DOT para: "{prompt_texto}"
        REGRAS:
        - rankdir={rankdir}
        - Adicione no início: graph [ranksep=0.3, nodesep=0.3, size="7,9!"]
        - Início/Fim: ellipse, style=filled, fillcolor="#F5F5F5"
        - Processo: box, style="filled,rounded", fillcolor="{cor_proc}"
        - Decisão: diamond, style=filled, fillcolor="{cor_dec}"
        - Retorne apenas o código DOT entre ```dot ... ```
        """
        try:
            res = requests.post(url, json={"contents": [{"parts": [{"text": prompt_ia}]}]})
            resp = res.json()['candidates'][0]['content']['parts'][0]['text']
            st.session_state.dot_code = re.search(r'```(?:dot)?\s*(.*?)```', resp, re.DOTALL).group(1)
        except:
            st.error("Erro na geração. Verifique sua chave.")

# --- RENDERIZAÇÃO DA FOLHA ---
if 'dot_code' in st.session_state:
    # Este bloco HTML cria a folha e o gráfico dentro dela
    st.markdown(f"""
        <div class="a4-page">
            <table class="header-table">
                <tr><td colspan="2" class="title-cell">{empresa.upper()}</td></tr>
                <tr>
                    <td width="50%"><span class="label">CLIENTE:</span><span class="value">{cliente.upper()}</span></td>
                    <td width="50%"><span class="label">PROJETO:</span><span class="value">{projeto.upper()}</span></td>
                </tr>
            </table>
            <div style="flex-grow:1; display:flex; justify-content:center; align-items:center; overflow:hidden;">
    """, unsafe_allow_html=True)
    
    # O gráfico é injetado aqui
    st.graphviz_chart(st.session_state.dot_code, use_container_width=True)
    
    st.markdown("""
            </div>
            <div style="text-align:center; font-size:7pt; color:#999; margin-top:5px; border-top:1px solid #eee; padding-top:5px;">
                Documento Técnico Industrial - Página 1/1
            </div>
        </div>
    """, unsafe_allow_html=True)
else:
    st.info("Aguardando descrição para gerar o documento A4.")
