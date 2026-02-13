import streamlit as st
import requests
import json
import re

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gerador de Fluxograma A4", layout="wide")

# --- CSS AVANÇADO PARA FORÇAR O A4 E REDIMENSIONAR O GRÁFICO ---
st.markdown("""
    <style>
    /* Estilo da Folha A4 na tela */
    .a4-container {
        background-color: #525659;
        padding: 30px 0;
        display: flex;
        justify-content: center;
    }
    
    .a4-page {
        background-color: white;
        width: 210mm;
        height: 297mm;
        padding: 15mm;
        box-shadow: 0 0 10px rgba(0,0,0,0.5);
        display: flex;
        flex-direction: column;
        overflow: hidden; /* Impede que o gráfico saia da folha */
        position: relative;
    }

    /* FORÇA O GRÁFICO A CABER NA FOLHA */
    [data-testid="stGraphvizChart"] svg {
        max-width: 100% !important;
        max-height: 180mm !important; /* Limita a altura para sobrar espaço para o cabeçalho */
        height: auto !important;
    }

    .header-table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 20px;
        border: 2px solid #000;
    }
    
    .header-table td {
        border: 1px solid #000;
        padding: 8px;
        font-family: Arial, sans-serif;
    }
    
    .header-title {
        font-size: 16pt;
        font-weight: bold;
        text-align: center;
        background-color: #eee;
    }
    
    .label { font-size: 8pt; font-weight: bold; text-transform: uppercase; display: block; }
    .value { font-size: 10pt; font-weight: bold; }

    /* Esconde tudo na impressão, exceto a folha */
    @media print {
        header, footer, .stSidebar, .stButton, .no-print, [data-testid="stHeader"] {
            display: none !important;
        }
        .main .block-container {
            padding: 0 !important;
            margin: 0 !important;
        }
        .a4-container {
            background-color: white !important;
            padding: 0 !important;
        }
        .a4-page {
            box-shadow: none !important;
            margin: 0 !important;
            border: none !important;
            width: 210mm !important;
            height: 297mm !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("📋 Dados do Documento")
    empresa = st.text_input("Empresa:", "MINHA EMPRESA EXEMPLO")
    cliente = st.text_input("Cliente:", "CLIENTE ABC")
    projeto = st.text_input("Projeto:", "FLUXOGRAMA DE PROCESSO V1")
    
    st.markdown("---")
    api_key = st.text_input("Gemini API Key:", type="password")
    
    st.markdown("---")
    st.header("🎨 Ajustes")
    direcao = st.selectbox("Orientação:", ["Vertical", "Horizontal"])
    rankdir = "TB" if direcao == "Vertical" else "LR"
    cor_proc = st.color_picker("Cor Processo:", "#E1F5FE")
    cor_dec = st.color_picker("Cor Decisão:", "#FFF9C4")

# --- ÁREA DE COMANDO ---
st.title("📊 Gerador de Fluxograma Industrial A4")

col_txt, col_btn = st.columns([3, 1])

with col_txt:
    texto = st.text_area("Descreva as etapas:", "Início.\nVerificar pedido.\nSe ok, enviar.\nSe erro, corrigir.\nFim.", height=100)

with col_btn:
    st.write("###")
    gerar = st.button("🚀 GERAR AGORA", use_container_width=True, type="primary")
    if 'dot' in st.session_state:
        # Botão de impressão que abre a janela de PDF
        st.markdown("""
            <button onclick="window.print()" style="width:100%; height:3em; background-color:#28a745; color:white; border:none; border-radius:5px; cursor:pointer; font-weight:bold;">
                🖨️ SALVAR COMO PDF
            </button>
        """, unsafe_allow_html=True)

# --- LÓGICA DA IA ---
if gerar:
    if not api_key:
        st.error("Insira a API Key.")
    else:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        prompt = f"""
        Crie um código Graphviz DOT para: "{texto}"
        REGRAS:
        - rankdir={rankdir}
        - nodesep=0.4, ranksep=0.4
        - Início/Fim: ellipse, fillcolor="#F5F5F5", style=filled
        - Processo: box, style="filled,rounded", fillcolor="{cor_proc}"
        - Decisão: diamond, style=filled, fillcolor="{cor_dec}"
        - Retorne apenas o código DOT entre ```dot ... ```
        """
        try:
            res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
            raw = res.json()['candidates'][0]['content']['parts'][0]['text']
            st.session_state.dot = re.search(r'```(?:dot)?\s*(.*?)```', raw, re.DOTALL).group(1)
        except:
            st.error("Erro ao gerar. Verifique a chave ou o texto.")

# --- EXIBIÇÃO DA FOLHA ---
if 'dot' in st.session_state:
    st.markdown('<div class="a4-container">', unsafe_allow_html=True)
    st.markdown(f"""
        <div class="a4-page">
            <table class="header-table">
                <tr><td colspan="2" class="header-title">{empresa.upper()}</td></tr>
                <tr>
                    <td width="50%"><span class="label">Cliente:</span><span class="value">{cliente.upper()}</span></td>
                    <td width="50%"><span class="label">Projeto:</span><span class="value">{projeto.upper()}</span></td>
                </tr>
            </table>
            <div style="flex-grow:1; display:flex; justify-content:center; align-items:center;">
    """, unsafe_allow_html=True)
    
    # Renderiza o gráfico - o CSS lá em cima vai forçar ele a caber
    st.graphviz_chart(st.session_state.dot, use_container_width=True)
    
    st.markdown("""
            </div>
            <div style="text-align:center; font-size:7pt; color:#999; margin-top:10px;">
                Documento Gerado via Sistema de Gestão Industrial - Página 1/1
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.info("Clique em Gerar para ver o resultado na folha A4.")
