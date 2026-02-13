import streamlit as st
import requests
import json
import re
import graphviz as graphviz_lib

# --- CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="Fluxograma Pro A4", layout="wide")
st.title("Fluxograma Industrial (A4 Ready)")

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("Configuração")
    api_key = st.text_input("Cole sua API Key:", type="password")
    
    st.markdown("---")
    st.markdown("### Ajustes de Impressão")
    orientacao = st.radio("Orientação do Papel:", ["Retrato (Vertical)", "Paisagem (Horizontal)"])
    
    if api_key:
        st.success("Sistema Armado.")

# --- ÁREA DE OPERAÇÃO ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Descreva o Processo")
    texto_padrao = """Recebimento de matéria-prima.
Verificação de qualidade (CQ).
Se aprovado no CQ, vai para o Almoxarifado.
Se reprovado, emite nota de devolução e devolve ao fornecedor.
Do Almoxarifado, segue para pesagem.
Da pesagem vai para o reator de mistura."""
    
    descricao = st.text_area("Etapas:", value=texto_padrao, height=300)
    gerar = st.button("Gerar Fluxograma", type="primary")

# --- EXECUÇÃO TÁTICA ---
if gerar:
    if not api_key:
        st.error("Preciso da chave API para operar, Angelo.")
    else:
        modelo_escolhido = "gemini-2.5-flash"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo_escolhido}:generateContent?key={api_key}"
        
        # Define orientação para o Graphviz
        rankdir = "TB" if "Retrato" in orientacao else "LR"
        
        # Dimensões A4 em polegadas (aprox)
        if "Retrato" in orientacao:
            size_attr = 'size="8.27,11.69!"'
        else:
            size_attr = 'size="11.69,8.27!"'

        headers = {'Content-Type': 'application/json'}
        
        # Prompt Refinado para Engenharia/Processos
        prompt = f"""
        Aja como um Engenheiro de Processos Sênior. Crie um código Graphviz (DOT) para o seguinte processo:
        "{descricao}"
        
        REGRAS RÍGIDAS DE LAYOUT (A4):
        1. O código DEVE começar EXATAMENTE com: digraph G {{ graph [fontname="Helvetica", fontsize=12, splines=ortho, nodesep=0.6, ranksep=0.8, {size_attr}, ratio="fill", margin=0.5]; node [fontname="Helvetica", shape=box, style="filled,rounded", fillcolor="#E3F2FD", penwidth=1.5]; edge [fontname="Helvetica", fontsize=10]; rankdir={rankdir};
        
        REGRAS DE ESTILO:
        2. Início/Fim: shape=ellipse, style="filled", fillcolor="#424242", fontcolor="white".
        3. Processos Normais: shape=box, style="filled,rounded", fillcolor="#FFFFFF", color="#1565C0".
        4. Decisões (Se/Então): shape=diamond, style="filled", fillcolor="#FFF9C4", color="#FBC02D".
        5. Documentos/Notas: shape=note, fillcolor="#F5F5F5".
        
        IMPORTANTE:
        - Use rótulos nas setas para as decisões (ex: "Sim", "Não").
        - Retorne APENAS o código DOT dentro de
```dot ...
```.
        """
        
        data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }

        with st.spinner('Processando lógica do fluxo...'):
            try:
                response = requests.post(url, headers=headers, data=json.dumps(data))
                
                if response.status_code == 200:
                    resultado = response.json()
                    try:
                        texto = resultado['candidates'][0]['content']['parts'][0]['text']
                        
                        # --- CORREÇÃO BLINDADA ---
                        # Usando aspas triplas para evitar erro de quebra de linha
                        padrao_regex = r"""
```(?:dot)?\s*(.*?)
```"""
                        
                        match = re.search(padrao_regex, texto, re.DOTALL)
                        
                        if match:
                            codigo_dot = match.group(1)
                            
                            with col2:
                                st.subheader("Visualização (Preview)")
                                st.graphviz_chart(codigo_dot)
                                
                                # Lógica de PDF
                                try:
                                    src = graphviz_lib.Source(codigo_dot)
                                    pdf_data = src.pipe(format='pdf')
                                    
                                    st.success("Fluxograma gerado com sucesso!")
                                    
                                    st.download_button(
                                        label="📄 Baixar PDF (Formato A4)",
                                        data=pdf_data,
                                        file_name="fluxograma_processo.pdf",
                                        mime="application/pdf"
                                    )
                                except Exception as e_graph:
                                    st.warning("Visualização gerada, mas erro ao criar PDF.")
                                    st.error(f"Erro técnico: {e_graph}")
                                    st.info("Dica: Verifique se o software 'Graphviz' está instalado no sistema operacional.")
                                    
                                with st.expander("Ver Código DOT"):
                                    st.code(codigo_dot)
                        else:
                            st.warning("O modelo respondeu, mas não formatou o código corretamente.")
                            st.write(texto)
                    except Exception as e:
                        st.error(f"Erro ao interpretar resposta: {e}")
                else:
                    st.error(f"Erro na API ({response.status_code}): {response.text}")
                    
            except Exception as e:
                st.error(f"Erro de conexão: {e}")

st.markdown("---")
st.caption("Ferramenta de Processos - A4 Edition")
