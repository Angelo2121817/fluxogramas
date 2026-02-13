import streamlit as st
import requests
import json
import re
import graphviz as graphviz_lib

# ==========================================
# 🔐 ÁREA DE SEGURANÇA
# ==========================================
# Cole sua API Key dentro das aspas abaixo:
API_KEY_FIXA = "AIzaSyB-LCZF_PHau6DHgRUKaZfbcsb82vcsZ4Q" 
# ==========================================

# --- CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="Gerador A4 Pro", layout="wide")

# CSS para visualização na tela (Simulação A4)
st.markdown("""
    <style>
    .main { background-color: #555; }
    .stApp { background-color: #555; }
    
    /* Folha A4 na tela */
    .a4-preview {
        background-color: white;
        width: 210mm;
        min-height: 297mm;
        padding: 0;
        margin: 0 auto;
        box-shadow: 0 0 20px rgba(0,0,0,0.5);
        display: flex;
        justify-content: center;
        align-items: center;
    }
    
    h1, h2, h3 { color: white !important; }
    .stTextInput > label, .stTextArea > label { color: white !important; }
    .stMarkdown p { color: #eee !important; }
    </style>
    """, unsafe_allow_html=True)

# --- BARRA LATERAL (INPUTS) ---
with st.sidebar:
    st.header("📝 Dados do Documento")
    empresa = st.text_input("Empresa:", value="SUA EMPRESA ENGENHARIA")
    cliente = st.text_input("Cliente:", value="Cliente Final Ltda")
    titulo_doc = st.text_input("Título do Fluxo:", value="Procedimento Operacional Padrão")
    data_rev = st.text_input("Data/Revisão:", value="Fev/2026 - Rev.01")
    
    st.markdown("---")
    st.header("🎨 Layout")
    orientacao = st.radio("Orientação:", ["Retrato (Vertical)", "Paisagem (Horizontal)"])
    
    st.markdown("---")
    st.info("Sistema rodando com Gemini 2.5 Flash")

# --- ÁREA PRINCIPAL ---
st.title("🖨️ Gerador de Fluxogramas A4 (PDF Engine)")

col_input, col_preview = st.columns([1, 2])

with col_input:
    st.subheader("Lógica do Processo")
    texto_padrao = """Início.
Verificar documentos.
Documentos válidos?
Se sim, aprovar cadastro.
Se não, solicitar revisão.
Fim."""
    descricao = st.text_area("Descreva as etapas:", value=texto_padrao, height=300)
    
    gerar = st.button("Gerar Documento PDF", type="primary", use_container_width=True)
    
    st.warning("Nota: O PDF gerado já incluirá o cabeçalho e as margens corretas para impressão.")

with col_preview:
    if gerar:
        # Verifica se a chave foi colocada no código
        if not API_KEY_FIXA:
            st.error("❌ ERRO: Você esqueceu de colocar a API Key na linha 11 do código!")
        else:
            # Configuração A4 baseada na orientação
            if "Retrato" in orientacao:
                rankdir = "TB"
                # A4 em polegadas com margem de segurança
                size_attr = 'size="8.27,11.69!"'
            else:
                rankdir = "LR"
                size_attr = 'size="11.69,8.27!"'

            # Prompt Avançado: Injeta o cabeçalho HTML dentro do Graphviz
            prompt = f"""
            Crie um código Graphviz (DOT) para este processo: "{descricao}"
            
            REGRAS OBRIGATÓRIAS DE ESTRUTURA:
            1. Use HTML-like Labels para criar um cabeçalho profissional NO TOPO do gráfico.
            2. Configuração do Graph:
               graph [
                 fontname="Helvetica"; fontsize=10;
                 {size_attr}; ratio="fill"; margin=0.5;
                 rankdir={rankdir}; splines=ortho; nodesep=0.6; ranksep=0.6;
                 label=<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" WIDTH="100%">
                   <TR>
                     <TD BGCOLOR="#EEEEEE" ALIGN="CENTER" COLSPAN="2"><B><FONT POINT-SIZE="18">{empresa}</FONT></B></TD>
                   </TR>
                   <TR>
                     <TD ALIGN="LEFT" WIDTH="50%">Cliente: <B>{cliente}</B></TD>
                     <TD ALIGN="RIGHT" WIDTH="50%">Ref: <B>{data_rev}</B></TD>
                   </TR>
                   <TR>
                     <TD ALIGN="CENTER" COLSPAN="2" BGCOLOR="#333333"><FONT COLOR="WHITE"><B>{titulo_doc}</B></FONT></TD>
                   </TR>
                 </TABLE>>;
                 labelloc="t";
               ];
            
            3. Estilo dos Nós:
               node [fontname="Helvetica", shape=box, style="filled,rounded", fillcolor="#E3F2FD", penwidth=1.5];
               edge [fontname="Helvetica", fontsize=9, color="#555555"];
            
            4. Nós Especiais:
               - Início/Fim: shape=ellipse, fillcolor="#444444", fontcolor="white".
               - Decisão: shape=diamond, fillcolor="#FFF9C4".
            
            5. Retorne APENAS o código DOT dentro de
```dot ...
```.
            """

            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY_FIXA}"
            
            with st.spinner("Renderizando vetorização A4..."):
                try:
                    response = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
                    
                    if response.status_code == 200:
                        texto = response.json()['candidates'][0]['content']['parts'][0]['text']
                        
                        # --- CORREÇÃO DE SINTAXE AQUI ---
                        # Usando aspas triplas para o regex (seguro)
                        padrao = r"""
```(?:dot)?\s*(.*?)
```"""
                        match = re.search(padrao, texto, re.DOTALL)
                        
                        codigo_dot = ""
                        
                        if match:
                            codigo_dot = match.group(1)
                        else:
                            # Limpeza manual segura, linha por linha
                            codigo_dot = texto.replace("
```dot", "")
                            codigo_dot = codigo_dot.replace("
```", "")
                            codigo_dot = codigo_dot.strip()
                        
                        # 1. Visualização na Tela (SVG)
                        st.markdown('<div class="a4-preview">', unsafe_allow_html=True)
                        st.graphviz_chart(codigo_dot, use_container_width=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # 2. Geração do PDF Real (Backend)
                        try:
                            src = graphviz_lib.Source(codigo_dot)
                            pdf_bytes = src.pipe(format='pdf')
                            
                            st.success("✅ Documento pronto!")
                            st.download_button(
                                label="⬇️ BAIXAR PDF (A4 FINAL)",
                                data=pdf_bytes,
                                file_name="Fluxograma_A4.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
                        except Exception as e:
                            st.error("Erro na conversão PDF. Verifique se o Graphviz está instalado no sistema.")
                            st.code(str(e))
                            
                    else:
                        st.error(f"Erro API: {response.status_code}")
                except Exception as e:
                    st.error(f"Erro: {e}")

st.caption("Sistema de Engenharia de Processos v6.1")import streamlit as st
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
