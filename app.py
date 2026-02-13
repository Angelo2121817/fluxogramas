import streamlit as st
import requests
import json
import re
import graphviz as graphviz_lib

# ==========================================
# 🔐 ÁREA DE SEGURANÇA (Sua Chave Aqui)
# ==========================================
# Cole sua API Key dentro das aspas abaixo:
API_KEY_FIXA = "AIzaSyB-LCZF_PHau6DHgRUKaZfbcsb82vcsZ4Q" 
# ==========================================

# --- CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="Gerador A4 Pro", layout="wide")

# CSS para visualização na tela (Simulação A4)
st.markdown("""
    <style>
    .main { background-color: #555; } /* Fundo escuro para destacar o papel */
    .stApp { background-color: #555; }
    
    /* Folha A4 na tela */
    .a4-preview {
        background-color: white;
        width: 210mm;
        min-height: 297mm;
        padding: 0; /* O padding será controlado pelo gráfico */
        margin: 0 auto;
        box-shadow: 0 0 20px rgba(0,0,0,0.5);
        display: flex;
        justify-content: center;
        align-items: center;
    }
    
    h1, h2, h3 { color: white !important; }
    .stTextInput > label, .stTextArea > label { color: white !important; }
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
            st.error("❌ ERRO: Você esqueceu de colocar a API Key na linha 7 do código!")
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
                        
                        # Extração Segura
                        padrao = r"""
```(?:dot)?\s*(.*?)
```"""
                        match = re.search(padrao, texto, re.DOTALL)
                        
                        codigo_dot = match.group(1) if match else texto.replace("
```dot", "").replace("
```", "").strip()
                        
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

st.caption("Sistema de Engenharia de Processos v6.0")
