import streamlit as st
import requests
import json
import re
import base64
from fpdf import FPDF
from io import BytesIO

# --- CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="Gerador de Fluxograma Industrial", layout="wide")

# Estilo CSS para simular A4 e formatar impressão
st.markdown("""
    <style>
    /* Esconde elementos do Streamlit na impressão */
    @media print {
        .stButton, .stSidebar, header, footer, .stDownloadButton {
            display: none !important;
        }
        .main .block-container {
            padding: 0 !important;
            margin: 0 !important;
        }
    }
    
    .main {
        background-color: #f0f2f6;
    }
    
    /* Container que simula folha A4 */
    .a4-page {
        background-color: white;
        width: 210mm;
        min-height: 297mm;
        padding: 20mm;
        margin: 20px auto;
        box-shadow: 0 0 15px rgba(0,0,0,0.2);
        display: flex;
        flex-direction: column;
        font-family: 'Arial', sans-serif;
    }
    
    .header-table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 20px;
        border: 2px solid #333;
    }
    
    .header-table td {
        border: 1px solid #333;
        padding: 10px;
    }
    
    .header-title {
        font-size: 18pt;
        font-weight: bold;
        text-align: center;
        background-color: #f8f9fa;
    }
    
    .info-label {
        font-weight: bold;
        font-size: 10pt;
        color: #555;
    }
    
    .info-value {
        font-size: 11pt;
        font-weight: bold;
    }
    
    .chart-container {
        flex-grow: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 1px solid #eee;
        padding: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÃO PARA GERAR PDF ---
def generate_pdf(empresa, cliente, titulo, dot_code):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    
    # Cabeçalho no PDF
    pdf.cell(190, 10, empresa.upper(), border=1, ln=1, align='C')
    pdf.set_font("Arial", "B", 12)
    pdf.cell(95, 10, f"CLIENTE: {cliente}", border=1, ln=0)
    pdf.cell(95, 10, f"PROCESSO: {titulo}", border=1, ln=1)
    
    pdf.ln(10)
    
    # Nota: Como o Streamlit renderiza Graphviz no navegador, 
    # para o PDF vamos adicionar o código DOT como texto ou instrução.
    # Em um ambiente completo, usaríamos 'graphviz' library para converter DOT -> PNG e inserir no PDF.
    # Aqui, vamos focar em deixar o layout pronto para "Imprimir -> Salvar como PDF" do navegador, 
    # que é o método mais fiel ao que o usuário vê na tela.
    
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 5, "Nota: Para exportar com o gráfico perfeito, utilize a função 'Imprimir' (Ctrl+P) do seu navegador e selecione 'Salvar como PDF'. Isso garantirá que o design visual seja preservado exatamente como exibido na tela.")
    
    return pdf.output(dest='S')

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
    st.header("🎨 Estilo")
    cor_box = st.color_picker("Cor dos Processos:", "#E3F2FD")
    cor_dec = st.color_picker("Cor das Decisões:", "#FFF3E0")
    direcao = st.selectbox("Orientação:", ["Vertical", "Horizontal"])
    rankdir = "TB" if direcao == "Vertical" else "LR"

# --- ÁREA DE ENTRADA ---
st.title("🛠️ Gerador de Fluxogramas A4")
col_in, col_btn = st.columns([4, 1])

with col_in:
    texto_padrao = """Início do Processo.
Análise de Pedido.
Se estoque disponível, separar material.
Se estoque indisponível, solicitar compra.
Embalagem e Envio.
Fim."""
    descricao = st.text_area("Descreva o processo (uma etapa por linha):", value=texto_padrao, height=150)

with col_btn:
    st.write("###")
    gerar = st.button("🪄 Gerar Fluxograma", use_container_width=True, type="primary")
    if 'codigo_dot' in st.session_state:
        st.button("🖨️ Imprimir / PDF", on_click=lambda: st.write('<script>window.print();</script>', unsafe_allow_html=True), use_container_width=True)
        st.info("💡 Use Ctrl+P para salvar como PDF")

# --- PROCESSAMENTO ---
if gerar:
    if not api_key:
        st.error("Insira a API Key na lateral.")
    else:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        prompt = f"""
        Crie um código Graphviz DOT profissional para: "{descricao}"
        Estilo:
        - rankdir={rankdir}
        - nodesep=0.5, ranksep=0.5
        - fontname="Arial"
        - Início/Fim: shape=ellipse, style=filled, fillcolor="#F5F5F5"
        - Processo: shape=box, style="filled,rounded", fillcolor="{cor_box}", color="#1976D2"
        - Decisão: shape=diamond, style=filled, fillcolor="{cor_dec}", color="#F57C00"
        - Retorne apenas o código DOT em ```dot ... ```
        """
        
        with st.spinner("Gerando layout..."):
            try:
                res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
                if res.status_code == 200:
                    texto = res.json()['candidates'][0]['content']['parts'][0]['text']
                    match = re.search(r'```(?:dot)?\s*(.*?)```', texto, re.DOTALL)
                    if match:
                        st.session_state.codigo_dot = match.group(1)
                    else:
                        st.error("Erro na formatação da IA.")
                else:
                    st.error("Erro na API.")
            except Exception as e:
                st.error(f"Erro: {e}")

# --- EXIBIÇÃO A4 ---
if 'codigo_dot' in st.session_state:
    # Renderização da "Folha A4"
    st.markdown(f"""
        <div class="a4-page">
            <table class="header-table">
                <tr>
                    <td colspan="2" class="header-title">{nome_empresa.upper()}</td>
                </tr>
                <tr>
                    <td width="50%">
                        <span class="info-label">CLIENTE:</span><br>
                        <span class="info-value">{nome_cliente.upper()}</span>
                    </td>
                    <td width="50%">
                        <span class="info-label">PROCESSO:</span><br>
                        <span class="info-value">{titulo_fluxo.upper()}</span>
                    </td>
                </tr>
            </table>
            <div class="chart-container">
    """, unsafe_allow_html=True)
    
    # O gráfico do Streamlit entra aqui
    st.graphviz_chart(st.session_state.codigo_dot, use_container_width=True)
    
    st.markdown("""
            </div>
            <div style="margin-top: 20px; text-align: right; font-size: 8pt; color: #999;">
                Gerado em: 12/02/2026 | Página 1 de 1
            </div>
        </div>
    """, unsafe_allow_html=True)
else:
    st.info("Preencha os dados e clique em 'Gerar' para visualizar o documento A4.")
