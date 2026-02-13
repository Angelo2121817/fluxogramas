import streamlit as st
import requests
import json
import re

# --- CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="Gerador de Fluxograma Pro", layout="wide")

# Estilo CSS personalizado para melhorar a aparência e simular A4
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #007bff;
        color: white;
    }
    /* Estilo para o container do gráfico para parecer uma folha A4 */
    .a4-container {
        background-color: white;
        padding: 40px;
        box-shadow: 0 0 10px rgba(0,0,0,0.1);
        margin: auto;
        border: 1px solid #ddd;
        min-height: 842px; /* Altura aproximada A4 em pixels */
    }
    </style>
    """, unsafe_allow_html=True)

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("🎨 Personalização")
    titulo_fluxo = st.text_input("Título do Fluxograma:", value="Fluxograma de Processo Industrial")
    
    st.markdown("---")
    st.header("🔑 Configuração API")
    api_key = st.text_input("Cole sua API Key do Gemini:", type="password")
    st.info("Modelo: gemini-2.5-flash")
    
    st.markdown("---")
    st.header("📐 Opções de Layout")
    direcao = st.selectbox("Direção do Fluxo:", ["Horizontal (Esquerda -> Direita)", "Vertical (Cima -> Baixo)"], index=0)
    rankdir = "LR" if "Horizontal" in direcao else "TB"
    
    cor_decisao = st.color_picker("Cor para Decisões (Losango):", "#FFF4E5")
    cor_processo = st.color_picker("Cor para Processos (Retângulo):", "#E1F5FE")
    cor_inicio_fim = st.color_picker("Cor para Início/Fim (Oval):", "#F5F5F5")

# --- ÁREA PRINCIPAL ---
st.title(f"📊 {titulo_fluxo}")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📝 Descrição do Processo")
    texto_padrao = """Recebimento de matéria-prima.
Verificação de qualidade.
Se aprovado, vai para o estoque.
Se reprovado, devolve ao fornecedor.
Do estoque, segue para produção."""
    descricao = st.text_area("Descreva as etapas linha por linha:", value=texto_padrao, height=400)
    gerar = st.button("🚀 Gerar Fluxograma Profissional", type="primary")

with col2:
    st.subheader("🖼️ Visualização (Otimizada A4)")
    
    if gerar:
        if not api_key:
            st.error("⚠️ Por favor, insira sua API Key na barra lateral.")
        else:
            modelo_escolhido = "gemini-2.5-flash"
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo_escolhido}:generateContent?key={api_key}"
            
            headers = {'Content-Type': 'application/json'}
            
            # Prompt aprimorado para Graphviz estético
            prompt = f"""
            Você é um especialista em design de processos e Graphviz. 
            Crie um código DOT para um fluxograma baseado nestas etapas:
            "{descricao}"
            
            REGRAS DE ESTILO OBRIGATÓRIAS:
            1. Layout: rankdir={rankdir}.
            2. Fontes: Use 'Arial' ou 'Helvetica' para um visual limpo.
            3. Nós:
               - Início/Fim: shape=ellipse, style="filled,rounded", fillcolor="{cor_inicio_fim}", color="#333333", penwidth=2.
               - Processos: shape=box, style="filled,rounded", fillcolor="{cor_processo}", color="#01579B", penwidth=1.5.
               - Decisões: shape=diamond, style=filled, fillcolor="{cor_decisao}", color="#E65100", penwidth=1.5.
            4. Arestas (Linhas): color="#555555", fontcolor="#333333", fontsize=10, arrowhead=vee.
            5. Gráfico Geral: label="{titulo_fluxo}", labelloc=t, fontsize=20, fontname="Arial-Bold", splines=ortho, nodesep=0.5, ranksep=0.5.
            6. Otimização A4: Certifique-se de que o layout seja bem distribuído.
            7. Retorne APENAS o código DOT dentro de blocos de código ```dot ... ```.
            """
            
            data = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }]
            }

            with st.spinner('Desenhando seu processo...'):
                try:
                    response = requests.post(url, headers=headers, data=json.dumps(data))
                    
                    if response.status_code == 200:
                        resultado = response.json()
                        texto = resultado['candidates'][0]['content']['parts'][0]['text']
                        
                        match = re.search(r'```(?:dot)?\s*(.*?)```', texto, re.DOTALL)
                        if match:
                            codigo_dot = match.group(1)
                            
                            # Container simulando A4
                            st.markdown('<div class="a4-container">', unsafe_allow_html=True)
                            st.graphviz_chart(codigo_dot, use_container_width=True)
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                            st.success("✅ Fluxograma gerado com sucesso!")
                            
                            with st.expander("🛠️ Opções Avançadas"):
                                st.code(codigo_dot, language="dot")
                                st.info("Dica: Você pode copiar o código acima e colar em 'edwardtufte.github.io/graphviz-visual-editor' para edições manuais finas.")
                        else:
                            st.warning("O modelo não retornou o código formatado corretamente.")
                            st.write(texto)
                    else:
                        st.error(f"Erro na API: {response.status_code}")
                except Exception as e:
                    st.error(f"Ocorreu um erro: {e}")
    else:
        st.info("Aguardando descrição para gerar o gráfico...")

st.markdown("---")
st.caption("Gerador de Fluxogramas Profissional v5.1 | Otimizado para Gemini 2.5")
