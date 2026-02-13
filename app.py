import streamlit as st
import requests
import json
import re
import base64

# --- CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="Gerador de Fluxograma A4 Pro", layout="wide")

# Estilo CSS para simular A4 e formatar impressão/layout
st.markdown("""
    <style>
    /* Estilo para a folha A4 na tela */
    .a4-page {
        background-color: white;
        width: 210mm;
        min-height: 297mm;
        padding: 15mm;
        margin: 20px auto;
        box-shadow: 0 0 15px rgba(0,0,0,0.2);
        display: flex;
        flex-direction: column;
        font-family: 'Segoe UI', Arial, sans-serif;
        border: 1px solid #ddd;
        overflow: hidden; /* Garante que nada saia da folha */
    }
    
    .header-table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 20px;
        border: 2px solid #2c3e50;
    }
    
    .header-table td {
        border: 1px solid #2c3e50;
        padding: 10px;
    }
    
    .header-title {
        font-size: 18pt;
        font-weight: bold;
        text-align: center;
        background-color: #f8f9fa;
        color: #2c3e50;
    }
    
    .info-label {
        font-weight: bold;
        font-size: 9pt;
        color: #7f8c8d;
        display: block;
    }
    
    .info-value {
        font-size: 11pt;
        font-weight: bold;
        color: #2c3e50;
    }
    
    /* Container do Gráfico: Força o conteúdo a caber no A4 */
    .chart-wrapper {
        flex-grow: 1;
        width: 100%;
        display: flex;
        justify-content: center;
        align-items: flex-start;
        padding-top: 20px;
    }
    
    /* Esconde elementos na impressão */
    @media print {
        .stButton, .stSidebar, header, footer, .stDownloadButton, .no-print {
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
            height: auto !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("🏢 Identificação")
    nome_empresa = st.text_input("Nome da Empresa:", value="SUA EMPRESA LTDA")
    nome_cliente = st.text_input("Nome do Cliente:", value="CLIENTE EXEMPLO")
    titulo_fluxo = st.text_input("Título do Processo:", value="FLUXOGRAMA OPERACIONAL")
    
    st.markdown("---")
    st.header("🔑 Configuração")
    api_key = st.text_input("API Key do Gemini:", type="password")
    
    st.markdown("---")
    st.header("🎨 Visual")
    cor_box = st.color_picker("Cor dos Processos:", "#E3F2FD")
    cor_dec = st.color_picker("Cor das Decisões:", "#FFF3E0")
    direcao = st.selectbox("Orientação:", ["Vertical", "Horizontal"], index=0)
    rankdir = "TB" if direcao == "Vertical" else "LR"

# --- INTERFACE PRINCIPAL ---
st.title("🛠️ Gerador de Fluxogramas Profissionais")

col_desc, col_ops = st.columns([3, 1])

with col_desc:
    texto_padrao = """Início do Processo.
Análise de Pedido.
Se estoque disponível, separar material.
Se estoque indisponível, solicitar compra.
Embalagem e Envio.
Fim."""
    descricao = st.text_area("Descreva as etapas linha por linha:", value=texto_padrao, height=150)

with col_ops:
    st.write("###")
    gerar = st.button("🚀 Gerar Fluxograma", use_container_width=True, type="primary")
    
    if 'codigo_dot' in st.session_state:
        # Botão de Download PDF (via Print do Navegador para garantir fidelidade visual)
        st.markdown("""
            <button onclick="window.print()" style="width:100%; height:3em; background-color:#28a745; color:white; border:none; border-radius:5px; cursor:pointer; font-weight:bold; margin-bottom:10px;">
                📥 Baixar PDF / Imprimir
            </button>
        """, unsafe_allow_html=True)
        st.info("💡 Na tela que abrir, escolha 'Salvar como PDF' para baixar o arquivo.")

# --- LÓGICA DE GERAÇÃO ---
if gerar:
    if not api_key:
        st.error("⚠️ Insira a API Key na lateral para gerar.")
    else:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        
        # Prompt otimizado para manter o gráfico compacto e dentro do A4
        prompt = f"""
        Crie um código Graphviz DOT para o processo: "{descricao}"
        
        REGRAS PARA CABER NO A4:
        1. Use rankdir={rankdir}.
        2. Adicione 'size="7.5,10!"' no início do código (isso força o gráfico a caber na página).
        3. Use 'ratio=fill'.
        4. Estilo:
           - Início/Fim: ellipse, style=filled, fillcolor="#F5F5F5"
           - Processo: box, style="filled,rounded", fillcolor="{cor_box}", color="#1976D2"
           - Decisão: diamond, style=filled, fillcolor="{cor_dec}", color="#F57C00"
        5. Retorne APENAS o código DOT em ```dot ... ```
        """
        
        with st.spinner("Desenhando documento..."):
            try:
                res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
                if res.status_code == 200:
                    texto_ia = res.json()['candidates'][0]['content']['parts'][0]['text']
                    match = re.search(r'```(?:dot)?\s*(.*?)```', texto_ia, re.DOTALL)
                    if match:
                        st.session_state.codigo_dot = match.group(1)
                    else:
                        st.error("Erro ao interpretar resposta da IA.")
                else:
                    st.error(f"Erro na API: {res.status_code}")
            except Exception as e:
                st.error(f"Erro: {e}")

# --- RENDERIZAÇÃO DA FOLHA A4 ---
if 'codigo_dot' in st.session_state:
    st.markdown("---")
    # A estrutura HTML abaixo garante que o cabeçalho e o gráfico fiquem dentro da folha
    st.markdown(f"""
        <div class="a4-page">
            <table class="header-table">
                <tr>
                    <td colspan="2" class="header-title">{nome_empresa.upper()}</td>
                </tr>
                <tr>
                    <td width="50%">
                        <span class="info-label">CLIENTE</span>
                        <span class="info-value">{nome_cliente.upper()}</span>
                    </td>
                    <td width="50%">
                        <span class="info-label">PROCESSO</span>
                        <span class="info-value">{titulo_fluxo.upper()}</span>
                    </td>
                </tr>
            </table>
            <div class="chart-wrapper">
    """, unsafe_allow_html=True)
    
    # O Streamlit renderiza o gráfico aqui. 
    # use_container_width=True faz com que ele respeite os limites da nossa div 'a4-page'
    st.graphviz_chart(st.session_state.codigo_dot, use_container_width=True)
    
    st.markdown("""
            </div>
            <div style="margin-top:20px; text-align:right; font-size:8pt; color:#bdc3c7; border-top:1px solid #eee; padding-top:5px;">
                Gerado via Sistema de Fluxogramas Industrial | Página 1 de 1
            </div>
        </div>
    """, unsafe_allow_html=True)
else:
    st.info("Preencha os dados e clique em 'Gerar Fluxograma' para visualizar o documento.")
