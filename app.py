import streamlit as st
import requests
import json
import re
import graphviz as graphviz_lib

# ==========================================
# 🔐 ÁREA DE SEGURANÇA
# ==========================================
API_KEY_FIXA = "AIzaSyAjbsaiRmACVhH0vXwuoV-NteCdo4I99VE"  # <--- COLE SUA CHAVE AQUI
# ==========================================

# --- CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="Gerador A4 Pro", page_icon="🌿", layout="wide")

st.markdown("""
<style>
    /* Fundo Geral Claro */
    .main { background-color: #f4f4f4; }
    .stApp { background-color: #f4f4f4; }
    
    /* Ajuste de Texto */
    h1, h2, h3, p, label { color: #333 !important; }
    
    /* Estilo para centralizar o gráfico na tela */
    .stGraphvizChart {
        display: flex;
        justify-content: center;
        background-color: white;
        padding: 40px;
        border-radius: 2px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        margin-top: 20px;
        min-height: 800px;
    }
    
    /* Rodapé personalizado */
    .footer {
        text-align: center;
        font-size: 12px;
        color: #666;
        margin-top: 50px;
        font-weight: bold;
        text-transform: uppercase;
    }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("📝 Dados do Documento")
    # Simplificado: Apenas Empresa e Título
    empresa = st.text_input("Empresa:", value="SUA EMPRESA ENGENHARIA")
    titulo_doc = st.text_input("Título do Fluxo:", value="Fluxograma do Processo Produtivo")
    
    st.markdown("---")
    st.header("🎨 Layout")
    orientacao = st.radio("Orientação:", ["Retrato (Vertical)", "Paisagem (Horizontal)"])
    st.markdown("---")
    st.info("Sistema rodando com Gemini 2.5 Flash")

st.title("🖨️ Gerador de Fluxogramas A4 (PDF Engine)")

col_input, col_preview = st.columns([1, 2])

with col_input:
    st.subheader("Lógica do Processo")
    texto_padrao = """Início.
Recebimento de Matéria-Prima.
Inspeção de Qualidade.
Aprovado?
Se sim, Armazenamento.
Se não, Devolução ao Fornecedor.
Produção.
Embalagem.
Fim."""
    descricao = st.text_area("Descreva as etapas:", value=texto_padrao, height=300)
    gerar = st.button("Gerar Documento PDF", type="primary", use_container_width=True)
    st.warning("Nota: O PDF gerado já incluirá o cabeçalho e as margens corretas para impressão.")

with col_preview:
    if gerar:
        if not API_KEY_FIXA:
            st.error("❌ ERRO: Você esqueceu de colocar a API Key na linha 10 do código!")
        else:
            if "Retrato" in orientacao:
                rankdir = "TB"
                size_attr = 'size="8.27,11.69!"'
            else:
                rankdir = "LR"
                size_attr = 'size="11.69,8.27!"'

            prompt = f"""
            Crie um código Graphviz (DOT) para este processo: "{descricao}"
            
            REGRAS OBRIGATÓRIAS DE ESTRUTURA:
            1. Use HTML-like Labels para criar um cabeçalho profissional NO TOPO do gráfico.
            2. Configuração do Graph:
               graph [
                 fontname="Helvetica"; fontsize=10;
                 {size_attr}; 
                 margin=0.5;
                 rankdir={rankdir}; 
                 splines=ortho; 
                 nodesep=0.8; 
                 ranksep=0.8; 
                 label=<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" WIDTH="100%">
                   <TR>
                     <TD BGCOLOR="#EEEEEE" ALIGN="CENTER" HEIGHT="40"><B><FONT POINT-SIZE="20">{empresa}</FONT></B></TD>
                   </TR>
                   <TR>
                     <TD ALIGN="CENTER" BGCOLOR="#333333" HEIGHT="30"><FONT COLOR="WHITE" POINT-SIZE="14"><B>{titulo_doc}</B></FONT></TD>
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
            
            5. Retorne APENAS o código DOT.
            """

            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY_FIXA}"
            
            with st.spinner("Renderizando vetorização A4..."):
                try:
                    response = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
                    
                    if response.status_code == 200:
                        texto = response.json()['candidates'][0]['content']['parts'][0]['text']
                        
                        # --- LIMPEZA SEGURA ---
                        inicio = texto.find("digraph")
                        
                        if inicio != -1:
                            codigo_limpo = texto[inicio:]
                            codigo_limpo = re.sub(r'`+$', '', codigo_limpo.strip())
                            
                            # 1. Visualização na Tela
                            st.graphviz_chart(codigo_limpo, use_container_width=True)
                            
                            # 2. Geração do PDF
                            try:
                                src = graphviz_lib.Source(codigo_limpo)
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
                                st.error("Erro na conversão PDF.")
                                st.code(str(e))
                        else:
                            st.error("Não encontrei um código 'digraph' válido na resposta.")
                            st.write(texto)
                            
                    else:
                        st.error(f"Erro API: {response.status_code}")
                except Exception as e:
                    st.error(f"Erro: {e}")

st.markdown('<div class="footer">Desenvolvido por Metal Química Consultoria</div>', unsafe_allow_html=True)
