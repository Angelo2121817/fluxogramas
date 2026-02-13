import streamlit as st
import requests
import json
import re
import base64

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gerador de Fluxograma A4 Profissional", layout="wide")

# --- ESTILIZAÇÃO CSS ---
st.markdown("""
    <style>
    /* Estilo do fundo */
    .main { background-color: #f0f2f6 !important; }
    
    /* Centralização da Folha */
    .a4-wrapper {
        display: flex;
        justify-content: center;
        padding: 20px;
    }

    /* A FOLHA A4 - Tamanho fixo e contenção total */
    .a4-page {
        background-color: white !important;
        width: 210mm !important;
        height: 297mm !important;
        padding: 15mm !important;
        box-shadow: 0 0 15px rgba(0,0,0,0.1);
        display: flex;
        flex-direction: column;
        overflow: hidden !important;
        box-sizing: border-box;
        border: 1px solid #ddd;
    }

    /* CABEÇALHO TÉCNICO */
    .header-box {
        width: 100%;
        border: 2px solid #333;
        margin-bottom: 20px;
        font-family: Arial, sans-serif;
    }
    .header-row-top {
        background-color: #f8f9fa;
        border-bottom: 2px solid #333;
        padding: 10px;
        text-align: center;
        font-size: 18pt;
        font-weight: bold;
    }
    .header-row-bottom {
        display: flex;
        width: 100%;
    }
    .header-cell {
        flex: 1;
        padding: 8px;
        border-right: 1px solid #333;
    }
    .header-cell:last-child { border-right: none; }
    .label { font-size: 8pt; color: #666; font-weight: bold; display: block; text-transform: uppercase; }
    .value { font-size: 11pt; font-weight: bold; color: #000; }

    /* CONTENÇÃO DO GRÁFICO */
    .chart-area {
        flex-grow: 1;
        width: 100%;
        display: flex;
        justify-content: center;
        align-items: center;
        overflow: hidden !important;
    }
    
    /* Força o SVG do Graphviz a caber na folha */
    [data-testid="stGraphvizChart"] svg {
        max-width: 100% !important;
        max-height: 200mm !important;
        width: auto !important;
        height: auto !important;
    }

    /* Estilo para Impressão */
    @media print {
        .no-print, header, footer, .stSidebar, .stButton, [data-testid="stHeader"] {
            display: none !important;
        }
        .main, .block-container { background-color: white !important; padding: 0 !important; margin: 0 !important; }
        .a4-wrapper { padding: 0 !important; }
        .a4-page {
            box-shadow: none !important;
            border: none !important;
            margin: 0 !important;
            width: 210mm !important;
            height: 297mm !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("📋 Dados do Documento")
    empresa = st.text_input("Nome da Empresa:", "SUA EMPRESA LTDA")
    cliente = st.text_input("Nome do Cliente:", "CLIENTE EXEMPLO")
    projeto = st.text_input("Título do Projeto:", "FLUXOGRAMA DE PROCESSO")
    
    st.markdown("---")
    api_key = st.text_input("Cole sua API Key do Gemini:", type="password")
    
    st.markdown("---")
    st.header("🎨 Personalização")
    direcao = st.selectbox("Orientação do Fluxo:", ["Vertical", "Horizontal"])
    rankdir = "TB" if direcao == "Vertical" else "LR"
    cor_box = st.color_picker("Cor dos Processos:", "#E1F5FE")
    cor_dec = st.color_picker("Cor das Decisões:", "#FFF9C4")

# --- INTERFACE PRINCIPAL ---
st.title("📊 Gerador de Fluxogramas A4")

col_txt, col_act = st.columns([3, 1])

with col_txt:
    texto_processo = st.text_area("Descreva o processo linha por linha:", 
                                  "Início.\nReceber material.\nVerificar qualidade.\nSe aprovado, estocar.\nSe reprovado, devolver.\nFim.", 
                                  height=100)

with col_act:
    st.write("###")
    gerar = st.button("🚀 GERAR FLUXOGRAMA", use_container_width=True, type="primary")
    
    if 'dot' in st.session_state:
        # Botão de Impressão/PDF com script de segurança
        st.markdown("""
            <button onclick="window.print()" style="width:100%; height:3.5em; background-color:#28a745; color:white; border:none; border-radius:5px; cursor:pointer; font-weight:bold; font-size:14px;">
                📥 SALVAR COMO PDF
            </button>
        """, unsafe_allow_html=True)
        st.caption("Dica: No destino, escolha 'Salvar como PDF'.")

# --- LÓGICA DE GERAÇÃO ---
if gerar:
    if not api_key:
        st.error("⚠️ Por favor, insira sua API Key na lateral.")
    else:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        
        # Prompt otimizado para manter o gráfico compacto e dentro dos limites
        prompt = f"""
        Crie um código Graphviz DOT para: "{texto_processo}"
        
        REGRAS DE FORMATAÇÃO:
        1. rankdir={rankdir}
        2. graph [nodesep=0.4, ranksep=0.4, size="7.5,9.5!", ratio=fill]
        3. node [fontname="Arial", fontsize=12]
        4. Início/Fim: shape=ellipse, style=filled, fillcolor="#F5F5F5"
        5. Processo: shape=box, style="filled,rounded", fillcolor="{cor_box}", color="#1976D2"
        6. Decisão: shape=diamond, style=filled, fillcolor="{cor_dec}", color="#F57C00"
        7. Retorne APENAS o código DOT dentro de ```dot ... ```
        """
        
        with st.spinner("IA Processando..."):
            try:
                res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
                if res.status_code == 200:
                    raw_text = res.json()['candidates'][0]['content']['parts'][0]['text']
                    match = re.search(r'```(?:dot)?\s*(.*?)```', raw_text, re.DOTALL)
                    if match:
                        st.session_state.dot = match.group(1)
                    else:
                        st.error("Erro na formatação da resposta.")
                else:
                    st.error(f"Erro na API: {res.status_code}")
            except Exception as e:
                st.error(f"Erro: {e}")

# --- RENDERIZAÇÃO DA FOLHA A4 ---
if 'dot' in st.session_state:
    st.markdown("---")
    st.markdown('<div class="a4-wrapper">', unsafe_allow_html=True)
    
    # Estrutura HTML da Folha
    st.markdown(f"""
        <div class="a4-page">
            <div class="header-box">
                <div class="header-row-top">{empresa.upper()}</div>
                <div class="header-row-bottom">
                    <div class="header-cell">
                        <span class="label">Cliente</span>
                        <span class="value">{cliente.upper()}</span>
                    </div>
                    <div class="header-cell">
                        <span class="label">Projeto</span>
                        <span class="value">{projeto.upper()}</span>
                    </div>
                </div>
            </div>
            <div class="chart-area">
    """, unsafe_allow_html=True)
    
    # O Gráfico do Streamlit - O CSS vai forçar ele a caber
    st.graphviz_chart(st.session_state.dot, use_container_width=True)
    
    st.markdown("""
            </div>
            <div style="text-align:center; font-size:8pt; color:#999; margin-top:10px; border-top:1px solid #eee; padding-top:5px;">
                Gerado via Sistema Profissional de Fluxogramas - Página 1/1
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.info("Preencha os dados e clique em 'Gerar' para visualizar o documento.")
