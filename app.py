import streamlit as st
import requests
import json
import re

# --- CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="Gerador de Fluxograma Industrial", layout="wide")

# Estilo CSS para simular A4 e formatar impressão
st.markdown("""
    <style>
    /* Esconde elementos do Streamlit na impressão */
    @media print {
        div[data-testid="stSidebar"], 
        div[data-testid="stHeader"], 
        .stButton, 
        footer,
        header {
            display: none !important;
        }
        .main .block-container {
            padding: 0 !important;
            margin: 0 !important;
        }
        .a4-page {
            margin: 0 !important;
            box-shadow: none !important;
            border: none !important;
            width: 100% !important;
        }
    }
    
    .main {
        background-color: #f0f2f6;
    }
    
    /* Container que simula folha A4 na tela */
    .a4-page {
        background-color: white;
        width: 210mm;
        min-height: 297mm;
        padding: 15mm;
        margin: 20px auto;
        box-shadow: 0 0 15px rgba(0,0,0,0.2);
        display: flex;
        flex-direction: column;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        border: 1px solid #ddd;
    }
    
    .header-table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 20px;
        border: 2px solid #2c3e50;
    }
    
    .header-table td {
        border: 1px solid #2c3e50;
        padding: 12px;
    }
    
    .header-title {
        font-size: 20pt;
        font-weight: bold;
        text-align: center;
        background-color: #ecf0f1;
        color: #2c3e50;
        text-transform: uppercase;
    }
    
    .info-label {
        font-weight: bold;
        font-size: 9pt;
        color: #7f8c8d;
        text-transform: uppercase;
        display: block;
        margin-bottom: 2px;
    }
    
    .info-value {
        font-size: 12pt;
        font-weight: bold;
        color: #2c3e50;
    }
    
    .chart-container {
        flex-grow: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 20px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("🏢 Dados do Cabeçalho")
    nome_empresa = st.text_input("Nome da Empresa:", value="SUA EMPRESA LTDA")
    nome_cliente = st.text_input("Nome do Cliente:", value="CLIENTE EXEMPLO")
    titulo_fluxo = st.text_input("Título do Processo:", value="FLUXOGRAMA OPERACIONAL")
    
    st.markdown("---")
    st.header("🔑 API Gemini")
    api_key = st.text_input("API Key:", type="password")
    
    st.markdown("---")
    st.header("🎨 Estilo do Gráfico")
    cor_box = st.color_picker("Cor dos Processos:", "#E3F2FD")
    cor_dec = st.color_picker("Cor das Decisões:", "#FFF3E0")
    direcao = st.selectbox("Orientação do Fluxo:", ["Vertical (Cima para Baixo)", "Horizontal (Esquerda para Direita)"])
    rankdir = "TB" if "Vertical" in direcao else "LR"

# --- ÁREA DE ENTRADA ---
st.title("📊 Gerador de Fluxogramas Profissionais")
st.info("Preencha os dados e clique em 'Gerar'. Para salvar em PDF, use o botão de imprimir e selecione 'Salvar como PDF'.")

col_in, col_btn = st.columns([3, 1])

with col_in:
    texto_padrao = """Início do Processo.
Análise de Pedido.
Se estoque disponível, separar material.
Se estoque indisponível, solicitar compra.
Embalagem e Envio.
Fim."""
    descricao = st.text_area("Descreva as etapas (uma por linha):", value=texto_padrao, height=150)

with col_btn:
    st.write("###")
    gerar = st.button("🪄 Gerar Fluxograma", use_container_width=True, type="primary")
    
    if 'codigo_dot' in st.session_state:
        # Botão que aciona o print do navegador
        st.markdown("""
            <button onclick="window.print()" style="width: 100%; height: 3em; background-color: #28a745; color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: bold;">
                🖨️ Exportar para PDF
            </button>
        """, unsafe_allow_html=True)

# --- PROCESSAMENTO COM IA ---
if gerar:
    if not api_key:
        st.error("Por favor, insira sua API Key na barra lateral.")
    else:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        
        # Prompt otimizado para Graphviz estético
        prompt = f"""
        Crie um código Graphviz DOT profissional para o seguinte processo: "{descricao}"
        
        REGRAS DE ESTILO:
        1. Orientação: rankdir={rankdir}
        2. Fonte: fontname="Segoe UI, Arial"
        3. Nós de Início/Fim: shape=ellipse, style=filled, fillcolor="#F5F5F5", color="#7F8C8D", penwidth=2
        4. Nós de Processo: shape=box, style="filled,rounded", fillcolor="{cor_box}", color="#1976D2", penwidth=1.5
        5. Nós de Decisão: shape=diamond, style=filled, fillcolor="{cor_dec}", color="#F57C00", penwidth=1.5
        6. Linhas (Arestas): color="#34495E", arrowhead=vee, fontname="Segoe UI", fontsize=10
        7. Retorne APENAS o código DOT dentro de um bloco de código ```dot ... ```
        """
        
        with st.spinner("A IA está desenhando seu fluxograma..."):
            try:
                res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
                if res.status_code == 200:
                    data = res.json()
                    texto = data['candidates'][0]['content']['parts'][0]['text']
                    match = re.search(r'```(?:dot)?\s*(.*?)```', texto, re.DOTALL)
                    if match:
                        st.session_state.codigo_dot = match.group(1)
                    else:
                        st.error("A IA não formatou o código corretamente. Tente novamente.")
                else:
                    st.error(f"Erro na API do Gemini: {res.status_code}")
            except Exception as e:
                st.error(f"Erro de conexão: {e}")

# --- EXIBIÇÃO DO DOCUMENTO A4 ---
if 'codigo_dot' in st.session_state:
    st.markdown("---")
    # Renderização da "Folha A4" usando HTML/CSS
    st.markdown(f"""
        <div class="a4-page">
            <table class="header-table">
                <tr>
                    <td colspan="2" class="header-title">{nome_empresa}</td>
                </tr>
                <tr>
                    <td width="50%">
                        <span class="info-label">Cliente</span>
                        <span class="info-value">{nome_cliente}</span>
                    </td>
                    <td width="50%">
                        <span class="info-label">Processo</span>
                        <span class="info-value">{titulo_fluxo}</span>
                    </td>
                </tr>
            </table>
            <div class="chart-container">
    """, unsafe_allow_html=True)
    
    # Renderiza o gráfico do Graphviz
    st.graphviz_chart(st.session_state.codigo_dot, use_container_width=True)
    
    st.markdown("""
            </div>
            <div style="margin-top: 20px; text-align: right; font-size: 8pt; color: #bdc3c7; border-top: 1px solid #eee; padding-top: 5px;">
                Documento Gerado Automaticamente | Sistema de Fluxogramas Pro
            </div>
        </div>
    """, unsafe_allow_html=True)
else:
    st.info("Aguardando geração do fluxograma...")

st.markdown("---")
st.caption("v5.2 - Otimizado para Impressão A4 e Exportação PDF Direta")
