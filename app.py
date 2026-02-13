import streamlit as st
import requests
import json
import re
import graphviz as graphviz_lib # Necessário: pip install graphviz

# --- CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="Gerador de Fluxograma Pro", layout="wide")

# Estilo CSS personalizado para melhorar a aparência e simular A4 na tela
st.markdown("""
    <style>
    .main {
        background-color: #f0f2f6;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        font-weight: bold;
    }
    /* Estilo para o container do gráfico para parecer uma folha A4 */
    .a4-container {
        background-color: white;
        padding: 1cm; /* Margem visual */
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        margin: auto;
        border: 1px solid #ddd;
        /* Proporção A4 visual */
        aspect-ratio: 210/297; 
        max-width: 800px;
        overflow: hidden; /* Evita que o gráfico estoure o papel visual */
        display: flex;
        align-items: center;
        justify-content: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("🏢 Dados do Cabeçalho")
    cliente = st.text_input("Nome do Cliente:", value="Empresa Modelo Ltda")
    titulo_fluxo = st.text_input("Título do Processo:", value="Fluxo de Produção v1.0")
    
    st.markdown("---")
    st.header("🎨 Estilo & Layout")
    
    # Orientação define o A4
    orientacao = st.radio("Orientação do Papel:", ["Retrato (Vertical)", "Paisagem (Horizontal)"])
    
    # Cores
    col_cor1, col_cor2 = st.columns(2)
    with col_cor1:
        cor_processo = st.color_picker("Processos:", "#E1F5FE")
        cor_decisao = st.color_picker("Decisões:", "#FFF9C4")
    with col_cor2:
        cor_inicio = st.color_picker("Início/Fim:", "#EEEEEE")
        cor_setas = st.color_picker("Setas:", "#424242")

    st.markdown("---")
    st.header("🔑 Sistema")
    api_key = st.text_input("API Key (Gemini):", type="password")

# --- LÓGICA DE TAMANHO A4 ---
# Define dimensões exatas em polegadas para o Graphviz
if "Retrato" in orientacao:
    rankdir = "TB" # Top to Bottom
    # A4 Retrato: 8.27 x 11.69 polegadas
    # O '!' força o Graphviz a preencher essa área
    size_attr = 'size="8.27,11.69!"' 
    ratio_attr = 'ratio="fill"'
else:
    rankdir = "LR" # Left to Right
    # A4 Paisagem: 11.69 x 8.27 polegadas
    size_attr = 'size="11.69,8.27!"'
    ratio_attr = 'ratio="fill"'

# --- ÁREA PRINCIPAL ---
st.title(f"📄 Gerador de Documentação de Processos")

col1, col2 = st.columns([1, 1.5])

with col1:
    st.subheader("1. Descreva o Processo")
    texto_padrao = """Início do turno.
Verificar ordem de produção.
Matéria-prima disponível?
Se sim, iniciar mistura.
Se não, solicitar ao almoxarifado e aguardar.
Mistura concluída.
Envase do produto.
Fim do processo."""
    descricao = st.text_area("Etapas (Linha por linha):", value=texto_padrao, height=450)
    
    st.info("💡 Dica: Seja claro nas condições 'Se... Então...' para gerar as decisões corretamente.")
    
    gerar = st.button("🚀 Gerar Fluxograma A4", type="primary")

with col2:
    st.subheader("2. Visualização & Exportação")
    
    if gerar:
        if not api_key:
            st.error("⚠️ Por favor, insira sua API Key na barra lateral.")
        else:
            modelo_escolhido = "gemini-2.5-flash"
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo_escolhido}:generateContent?key={api_key}"
            headers = {'Content-Type': 'application/json'}
            
            # Prompt Engenharia de Prompt para Graphviz
            prompt = f"""
            Aja como um especialista em documentação técnica. Crie um código Graphviz (DOT) para este processo:
            "{descricao}"
            
            REGRAS OBRIGATÓRIAS DE ESTRUTURA (DOT):
            1. Cabeçalho do Gráfico:
               - label=<<B><FONT POINT-SIZE="24">{titulo_fluxo}</FONT></B><BR/><FONT POINT-SIZE="16">{cliente}</FONT>>;
               - labelloc="t"; (Top)
               - {size_attr}; (Tamanho A4)
               - {ratio_attr};
               - rankdir={rankdir};
               - splines=ortho; (Linhas retas/ortogonais)
               - nodesep=0.6; ranksep=0.6; margin=0.5;
            
            2. Estilo dos Nós:
               - Fonte: Helvetica ou Arial.
               - Início/Fim: shape=ellipse, style="filled", fillcolor="{cor_inicio}", penwidth=2.
               - Ação/Processo: shape=box, style="filled,rounded", fillcolor="{cor_processo}", penwidth=1.5.
               - Decisão (Se/Então): shape=diamond, style="filled", fillcolor="{cor_decisao}", penwidth=1.5.
            
            3. Estilo das Arestas:
               - color="{cor_setas}"; fontcolor="{cor_setas}"; arrowhead=vee;
               - IMPORTANTE: Rotule as arestas de decisão com "Sim", "Não", "Aprovado", etc.
            
            4. SAÍDA:
               - Retorne APENAS o código DOT dentro de blocos
```dot ...
```.
            """
            
            data = {"contents": [{"parts": [{"text": prompt}]}]}

            with st.spinner('Renderizando layout vetorial...'):
                try:
                    response = requests.post(url, headers=headers, data=json.dumps(data))
                    
                    if response.status_code == 200:
                        resultado = response.json()
                        try:
                            texto = resultado['candidates'][0]['content']['parts'][0]['text']
                            
                            # Extração robusta (evita erros de quebra de linha)
                            padrao_regex = r"""
```(?:dot)?\s*(.*?)
```"""
                            match = re.search(padrao_regex, texto, re.DOTALL)
                            
                            codigo_dot = match.group(1) if match else texto.replace("
```dot", "").replace("
```", "").strip()
                            
                            # 1. Renderiza na tela (Visualização Web)
                            st.markdown('<div class="a4-container">', unsafe_allow_html=True)
                            st.graphviz_chart(codigo_dot, use_container_width=True)
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                            # 2. Gera o PDF para Download (Processamento Real)
                            try:
                                src = graphviz_lib.Source(codigo_dot)
                                # Renderiza o PDF em memória
                                pdf_bytes = src.pipe(format='pdf')
                                
                                st.success("✅ Documento gerado com sucesso!")
                                
                                # Botão de Download
                                col_dl1, col_dl2 = st.columns([2,1])
                                with col_dl1:
                                    st.download_button(
                                        label="📄 BAIXAR PDF (PRONTO PARA IMPRESSÃO)",
                                        data=pdf_bytes,
                                        file_name=f"Fluxograma_{cliente.replace(' ', '_')}.pdf",
                                        mime="application/pdf",
                                        use_container_width=True
                                    )
                                with col_dl2:
                                    with st.popover("Ver Código Fonte"):
                                        st.code(codigo_dot, language="dot")
                                        
                            except Exception as e_pdf:
                                st.warning("Visualização criada, mas erro ao gerar arquivo PDF.")
                                st.error(f"Erro: {e_pdf}")
                                st.info("Certifique-se de que o software 'Graphviz' está instalado no servidor/máquina.")

                        except Exception as e_parse:
                            st.error("Erro ao interpretar a resposta do modelo.")
                            st.write(texto)
                    else:
                        st.error(f"Erro na API: {response.status_code}")
                except Exception as e_conn:
                    st.error(f"Erro de conexão: {e_conn}")

st.markdown("---")
st.caption("Gerador de Fluxogramas Pro - Engine: Gemini 2.5 Flash")
