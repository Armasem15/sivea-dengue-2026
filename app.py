import os
from datetime import date
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv
from supabase import Client, create_client

# ==============================================================================
# 1. CONFIGURAÇÃO DE PÁGINA & ARQUITETURA VISUAL (SEM SIDEBAR / GRID EDITORIAL)
# ==============================================================================
st.set_page_config(
    page_title="SIVEA // Inteligência Epidemiológica & Ambiental",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@500;700;800&family=Space+Grotesk:wght@500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Space Grotesk', sans-serif;
        color: #0A0A0A;
    }

    /* Fundo técnico quadriculado sutil (estilo prancheta de engenharia/vigilância) */
    .stApp {
        background-color: #F7F7F5;
        background-image:
            linear-gradient(to right, rgba(10, 10, 10, 0.04) 1px, transparent 1px),
            linear-gradient(to bottom, rgba(10, 10, 10, 0.04) 1px, transparent 1px);
        background-size: 28px 28px;
    }

    /* Remove 100% da Sidebar e elementos padrão do Streamlit */
    section[data-testid="stSidebar"],
    div[data-testid="stSidebarCollapsedControl"],
    #MainMenu, footer, header {
        display: none !important;
    }

    .block-container {
        padding-top: 1.2rem !important;
        padding-bottom: 3rem !important;
        max-width: 1380px !important;
    }

    /* Barra Superior Institucional */
    .top-brand-bar {
        background-color: #0A0A0A;
        color: #FFFFFF;
        padding: 1.1rem 1.6rem;
        border: 2px solid #0A0A0A;
        box-shadow: 6px 6px 0px #FFD600;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 1rem;
        margin-bottom: 1rem;
    }
    .brand-left {
        display: flex;
        align-items: center;
        gap: 14px;
    }
    .brand-square {
        background-color: #FFD600;
        color: #0A0A0A;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 800;
        font-size: 1.25rem;
        padding: 0.45rem 0.75rem;
        border: 2px solid #FFFFFF;
    }
    .brand-title {
        font-size: 1.45rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin: 0;
        line-height: 1.1;
        color: #FFFFFF;
    }
    .brand-sub {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.78rem;
        color: #A3A3A3;
        margin-top: 3px;
    }
    .status-pill {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.78rem;
        font-weight: 700;
        background-color: #171717;
        color: #FFD600;
        border: 1px solid #FFD600;
        padding: 0.4rem 0.8rem;
    }

    /* Navegação Horizontal Customizada (Transforma st.radio em Navbar) */
    div[data-testid="stRadio"] > div[role="radiogroup"] {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        background-color: #FFD600;
        padding: 8px;
        border: 2px solid #FFD600;
        margin-bottom: 1.2rem;
    }
    div[data-testid="stRadio"] > div[role="radiogroup"] > label {
        background-color: #1A1A1A !important;
        border: 1px solid #333333 !important;
        border-radius: 0px !important;
        padding: 0.55rem 1rem !important;
        margin: 0 !important;
        cursor: pointer;
        transition: all 0.15s ease;
    }
    div[data-testid="stRadio"] > div[role="radiogroup"] > label:hover {
        border-color: #FFD600 !important;
        background-color: #262626 !important;
    }
    div[data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:checked) {
        background-color: #FFD600 !important;
        border-color: #FFD600 !important;
    }
    div[data-testid="stRadio"] > div[role="radiogroup"] > label p {
        color: #FFFFFF !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 700 !important;
        font-size: 0.88rem !important;
    }
    div[data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:checked) p {
        color: #0A0A0A !important;
        font-weight: 800 !important;
    }
    div[data-testid="stRadio"] > div[role="radiogroup"] > label > div:first-child {
        display: none !important;
    }

    /* Blocos de Métricas Assimétricos (Preto, Amarelo e Branco) */
    .metric-card-white {
        background-color: #FFFFFF;
        border: 2px solid #0A0A0A;
        box-shadow: 5px 5px 0px #0A0A0A;
        padding: 1.2rem;
        height: 100%;
    }
    .metric-card-yellow {
        background-color: #FFD600;
        border: 2px solid #0A0A0A;
        box-shadow: 5px 5px 0px #0A0A0A;
        padding: 1.2rem;
        height: 100%;
    }
    .metric-card-black {
        background-color: #0A0A0A;
        color: #FFFFFF;
        border: 2px solid #0A0A0A;
        box-shadow: 5px 5px 0px #FFD600;
        padding: 1.2rem;
        height: 100%;
    }
    .m-code {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        opacity: 0.75;
    }
    .m-val {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.2rem;
        font-weight: 800;
        line-height: 1.1;
        margin: 0.35rem 0;
    }
    .m-tag {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.76rem;
        font-weight: 700;
        padding: 2px 6px;
        display: inline-block;
    }

    /* Painéis de Seção e Gavetas de Cadastro */
    .section-header {
        background-color: #FFFFFF;
        border: 2px solid #0A0A0A;
        border-left: 10px solid #FFD600;
        padding: 0.9rem 1.3rem;
        margin-bottom: 1.2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .section-header h2 {
        margin: 0;
        font-size: 1.35rem;
        font-weight: 800;
        color: #0A0A0A;
    }
    .section-header p {
        margin: 0;
        font-size: 0.88rem;
        color: #404040;
    }

    /* Formulários Estilo Prancheta */
    div[data-testid="stForm"] {
        background-color: #FFFFFF;
        border: 2px solid #0A0A0A;
        box-shadow: 6px 6px 0px #FFD600;
        border-radius: 0px;
        padding: 1.4rem;
        margin-bottom: 1.5rem;
    }

    /* Botões com Sombra Sólida */
    div.stButton > button, div.stDownloadButton > button, div[data-testid="stFormSubmitButton"] > button {
        background-color: #FFD600 !important;
        color: #0A0A0A !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 800 !important;
        border: 2px solid #0A0A0A !important;
        border-radius: 0px !important;
        box-shadow: 3px 3px 0px #0A0A0A !important;
        transition: all 0.1s ease !important;
    }
    div.stButton > button:hover, div[data-testid="stFormSubmitButton"] > button:hover {
        background-color: #0A0A0A !important;
        color: #FFD600 !important;
        box-shadow: 3px 3px 0px #FFD600 !important;
    }

    /* Cards de Ocorrências / Casos / Diagnóstico */
    .editorial-box {
        background-color: #FFFFFF;
        border: 2px solid #0A0A0A;
        box-shadow: 5px 5px 0px #0A0A0A;
        padding: 1.3rem;
        margin-bottom: 1rem;
    }
    .badge-yellow {
        background-color: #FFD600;
        color: #0A0A0A;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
        font-size: 0.75rem;
        padding: 2px 8px;
        border: 1px solid #0A0A0A;
    }
    .badge-black {
        background-color: #0A0A0A;
        color: #FFD600;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
        font-size: 0.75rem;
        padding: 2px 8px;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. CONEXÃO COM O BANCO DE DADOS (SUPABASE)
# ==============================================================================
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("Configure SUPABASE_URL e SUPABASE_KEY no arquivo .env.")
    st.stop()

@st.cache_resource
def init_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

def carregar_locais():
    res = supabase.table("locais_coleta").select("*").order("id").execute()
    return pd.DataFrame(res.data)

def carregar_residuos():
    res = supabase.table("registros_residuos").select("*, locais_coleta(nome, bairro)").order("id", desc=True).execute()
    df = pd.DataFrame(res.data)
    if not df.empty and "locais_coleta" in df.columns:
        df["local_nome"] = df["locais_coleta"].apply(lambda x: x["nome"] if isinstance(x, dict) else "Removido")
        df["bairro"] = df["locais_coleta"].apply(lambda x: x["bairro"] if isinstance(x, dict) else "-")
        df = df.drop(columns=["locais_coleta"])
    return df

def carregar_vetores():
    res = supabase.table("vigilancia_vetorial").select("*, locais_coleta(nome, bairro)").order("id", desc=True).execute()
    df = pd.DataFrame(res.data)
    if not df.empty and "locais_coleta" in df.columns:
        df["local_nome"] = df["locais_coleta"].apply(lambda x: x["nome"] if isinstance(x, dict) else "Removido")
        df["bairro"] = df["locais_coleta"].apply(lambda x: x["bairro"] if isinstance(x, dict) else "-")
        df = df.drop(columns=["locais_coleta"])
    return df

def carregar_casos():
    res = supabase.table("casos_dengue").select("*").order("id", desc=True).execute()
    return pd.DataFrame(res.data)

def carregar_ocorrencias():
    res = supabase.table("ocorrencias_ambientais").select("*").order("id", desc=True).execute()
    return pd.DataFrame(res.data)

df_locais = carregar_locais()
df_residuos = carregar_residuos()
df_vetores = carregar_vetores()
df_casos = carregar_casos()
df_ocorrencias = carregar_ocorrencias()

# Controle de gavetas retráteis de cadastro
if "abrir_form" not in st.session_state:
    st.session_state.abrir_form = False

# ==============================================================================
# 3. CABEÇALHO SUPERIOR + BARRA DE NAVEGAÇÃO HORIZONTAL
# ==============================================================================
st.markdown(f"""
<div class="top-brand-bar">
    <div class="brand-left">
        <div class="brand-square">SV//26</div>
        <div>
            <div class="brand-title">SIVEA — VIGILÂNCIA AMBIENTAL & EPIDEMIOLÓGICA</div>
            <div class="brand-sub">SISTEMA INTEGRADO DE CONTROLE DE RESÍDUOS, VETORES E DENGUE</div>
        </div>
    </div>
    <div class="status-pill">● SUPABASE DB ATIVO | {date.today().strftime('%d/%m/%Y')}</div>
</div>
""", unsafe_allow_html=True)

# Exemplo de como deve estar no seu código:
opcoes_menu = [
    "📊 PAINEL DE DADOS",
    "📍 LOCAIS DE COLETA",
    "🗑️ RESÍDUOS",
    "🦟 OVOS, LARVAS E MOSQUITOS",
    "🏥 CASOS DE DENGUE",
    "🚨 OCORRÊNCIAS",
    "📘 GUIA DA DENGUE"
]

pagina = st.radio("Navegação", opcoes_menu, horizontal=True, label_visibility="collapsed")

# E lá embaixo, nos ifs de cada tela, use exatamente a mesma string (ou "in"):
if "LOCAIS DE COLETA" in pagina:
    # código da tela de locais de coleta...
    horizontal=True,
    label_visibility="collapsed"
)

# ==============================================================================
# 1. PAINEL DE DADOS (GRÁFICOS E OBSERVAÇÕES)
# ==============================================================================
if menu == "📊 PAINEL DE DADOS":
    # Barra de filtro rápido no topo do painel
    bairros_set = set()
    for d in [df_locais, df_casos, df_ocorrencias]:
        if not d.empty and "bairro" in d.columns:
            bairros_set.update(d["bairro"].dropna().unique().tolist())

    f_col1, f_col2 = st.columns([2.5, 1])
    with f_col1:
        st.markdown("""
        <div class="section-header">
            <div>
                <h2>CENTRAL DE INTELIGÊNCIA & INDICADORES</h2>
                <p>Cruzamento em tempo real entre descartes irregulares, focos do mosquito e notificações clínicas.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with f_col2:
        bairro_sel = st.selectbox("FILTRAR REGIÃO / BAIRRO:", ["Todos os Bairros"] + sorted(list(bairros_set)))

    def filtrar(df):
        if bairro_sel == "Todos os Bairros" or df.empty or "bairro" not in df.columns:
            return df
        return df[df["bairro"] == bairro_sel]

    df_loc_f = filtrar(df_locais)
    df_res_f = filtrar(df_residuos)
    df_vet_f = filtrar(df_vetores)
    df_cas_f = filtrar(df_casos)
    df_oco_f = filtrar(df_ocorrencias)

    # Cálculos
    tot_recip = int(df_res_f["qtd_recipientes"].sum()) if not df_res_f.empty else 0
    tot_peso = float(df_res_f["peso_kg"].sum()) if not df_res_f.empty else 0.0
    tot_vet = int(df_vet_f["quantidade"].sum()) if not df_vet_f.empty else 0
    tot_casos = len(df_cas_f)
    casos_conf = int((df_cas_f["classificacao"] != "Suspeito").sum()) if not df_cas_f.empty else 0
    oco_abertas = int((df_oco_f["status_resolucao"] != "Resolvida").sum()) if not df_oco_f.empty else 0

    # Grade Assimétrica de 4 Cartões (Preto, Amarelo e Branco)
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""
        <div class="metric-card-black">
            <div class="m-code" style="color:#FFD600;">[01] CRIADOUROS REMOVIDOS</div>
            <div class="m-val" style="color:#FFFFFF;">{tot_recip} un.</div>
            <span class="m-tag" style="background:#FFD600; color:#0A0A0A;">{tot_peso:.1f} KG DE RESÍDUOS</span>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="metric-card-yellow">
            <div class="m-code" style="color:#0A0A0A;">[02] AMOSTRAS VETORIAIS</div>
            <div class="m-val" style="color:#0A0A0A;">{tot_vet}</div>
            <span class="m-tag" style="background:#0A0A0A; color:#FFD600;">OVOS / LARVAS / MOSQUITOS</span>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
        <div class="metric-card-white">
            <div class="m-code">[03] CASOS NOTIFICADOS</div>
            <div class="m-val">{tot_casos}</div>
            <span class="m-tag" style="background:#FFD600; color:#0A0A0A;">{casos_conf} CONFIRMADO(S)</span>
        </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown(f"""
        <div class="metric-card-white">
            <div class="m-code">[04] OCORRÊNCIAS ATIVAS</div>
            <div class="m-val">{oco_abertas}</div>
            <span class="m-tag" style="background:#0A0A0A; color:#FFFFFF;">DE {len(df_oco_f)} DENÚNCIAS</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Gráficos em Preto, Amarelo e Branco
    g1, g2 = st.columns(2)
    with g1:
        if not df_res_f.empty:
            df_cat = df_res_f.groupby("categoria", as_index=False)["qtd_recipientes"].sum().sort_values("qtd_recipientes", ascending=True)
            fig1 = px.bar(
                df_cat,
                x="qtd_recipientes",
                y="categoria",
                orientation="h",
                text_auto=True,
                title="RESÍDUOS DE RISCO RETIRADOS (UNIDADES)",
                labels={"qtd_recipientes": "Recipientes", "categoria": ""},
                color_discrete_sequence=["#0A0A0A"]
            )
            fig1.update_traces(marker_line_color="#FFD600", marker_line_width=2, textfont_color="#0A0A0A")
            fig1.update_layout(
                plot_bgcolor="#FFFFFF",
                paper_bgcolor="#FFFFFF",
                font=dict(family="Space Grotesk", color="#0A0A0A"),
                margin=dict(t=50, b=20, l=10, r=20),
                height=320
            )
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("Sem registros de resíduos nesta área.")

    with g2:
        if not df_vet_f.empty:
            df_vet_g = df_vet_f.groupby("estagio", as_index=False)["quantidade"].sum()
            fig2 = px.bar(
                df_vet_g,
                x="estagio",
                y="quantidade",
                text_auto=True,
                title="INFESTAÇÃO POR ESTÁGIO DO VETOR",
                labels={"estagio": "Estágio", "quantidade": "Quantidade"},
                color="estagio",
                color_discrete_sequence=["#FFD600", "#0A0A0A", "#52525B", "#CA8A04"]
            )
            fig2.update_traces(marker_line_color="#0A0A0A", marker_line_width=1.5)
            fig2.update_layout(
                showlegend=False,
                plot_bgcolor="#FFFFFF",
                paper_bgcolor="#FFFFFF",
                font=dict(family="Space Grotesk", color="#0A0A0A"),
                margin=dict(t=50, b=20, l=20, r=20),
                height=320
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Sem amostras vetoriais nesta área.")

    g3, g4 = st.columns(2)
    with g3:
        if not df_cas_f.empty:
            df_cas_g = df_cas_f.groupby(["bairro", "classificacao"], as_index=False).size()
            fig3 = px.bar(
                df_cas_g,
                x="bairro",
                y="size",
                color="classificacao",
                text_auto=True,
                title="CASOS DE DENGUE POR BAIRRO E GRAVIDADE",
                labels={"bairro": "Bairro", "size": "Casos", "classificacao": "Status"},
                color_discrete_map={
                    "Confirmado": "#0A0A0A",
                    "Dengue com Sinais de Alarme": "#FFD600",
                    "Suspeito": "#A3A3A3"
                }
            )
            fig3.update_traces(marker_line_color="#0A0A0A", marker_line_width=1)
            fig3.update_layout(
                plot_bgcolor="#FFFFFF",
                paper_bgcolor="#FFFFFF",
                font=dict(family="Space Grotesk", color="#0A0A0A"),
                margin=dict(t=50, b=20, l=20, r=20),
                height=320
            )
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("Sem casos de dengue registrados nesta área.")

    with g4:
        if not df_oco_f.empty:
            df_oco_g = df_oco_f.groupby("tipo_ocorrencia", as_index=False).size()
            fig4 = px.pie(
                df_oco_g,
                names="tipo_ocorrencia",
                values="size",
                hole=0.5,
                title="OCORRÊNCIAS E INFRAÇÕES AMBIENTAIS",
                color_discrete_sequence=["#FFD600", "#0A0A0A", "#52525B", "#CA8A04", "#D4D4D8"]
            )
            fig4.update_traces(textposition="inside", textinfo="percent+label", marker=dict(line=dict(color="#0A0A0A", width=2)))
            fig4.update_layout(
                showlegend=False,
                paper_bgcolor="#FFFFFF",
                font=dict(family="Space Grotesk", color="#0A0A0A"),
                margin=dict(t=50, b=20, l=20, r=20),
                height=320
            )
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.info("Sem ocorrências registradas nesta área.")

    # Bloco de Observações Técnicas e Diagnóstico Automático
    obs = []
    if not df_res_f.empty:
        top_mat = df_res_f.groupby("categoria")["qtd_recipientes"].sum().idxmax()
        top_qtd = int(df_res_f.groupby("categoria")["qtd_recipientes"].sum().max())
        obs.append(f"<b>FOCO DE RESÍDUOS:</b> O material <u>{top_mat}</u> representa o maior volume recolhido (<b>{top_qtd} unidades</b>), exigindo fiscalização contínua em borracharias e terrenos.")

    if not df_cas_f.empty:
        top_b = df_cas_f["bairro"].value_counts().idxmax()
        top_c = int(df_cas_f["bairro"].value_counts().max())
        obs.append(f"<b>EPICENTRO EPIDEMIOLÓGICO:</b> O bairro <u>{top_b}</u> concentra <b>{top_c} notificação(ões)</b> de dengue. Recomenda-se bloqueio de criadouros num raio de 300 metros.")

    if not df_vet_f.empty:
        altos = int((df_vet_f["nivel_infestacao"] == "Alto").sum())
        if altos > 0:
            obs.append(f"<b>ALERTA VETORIAL:</b> Foram identificados <b>{altos} ponto(s)</b> com nível <u>ALTO</u> de infestação de ovos ou larvas.")

    if oco_abertas > 0:
        obs.append(f"<b>FISCALIZAÇÃO PENDENTE:</b> Existem <b>{oco_abertas} ocorrência(s)</b> de imprudência ou abandono aguardando vistoria/resolução.")

    if not obs:
        obs.append("Base de dados limpa para o filtro atual. Utilize os módulos superiores para cadastrar novos registros.")

    obs_html = "".join([f"<p style='margin:0.5rem 0; border-bottom:1px solid #E5E5E5; padding-bottom:0.4rem;'>▪ {o}</p>" for o in obs])
    st.markdown(f"""
    <div class="editorial-box" style="border-left: 10px solid #0A0A0A;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.6rem;">
            <span style="font-size:1.1rem; font-weight:800;">📋 OBSERVAÇÕES TÉCNICAS & DIAGNÓSTICO DO SISTEMA</span>
            <span class="badge-yellow">ANÁLISE AUTOMÁTICA</span>
        </div>
        {obs_html}
    </div>
    """, unsafe_allow_html=True)

# ==============================================================================
# 2. LOCAIS DE COLETA
# ==============================================================================
elif menu == "📍 Locais de Coleta":
    h1, h2 = st.columns([3, 1])
    with h1:
        st.markdown("""
        <div class="section-header">
            <div>
                <h2>LOCAIS DE COLETA & PONTOS CRÍTICOS</h2>
                <p>Mapeamento de ecopontos oficiais, escolas e áreas vulneráveis ao acúmulo de água.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with h2:
        if st.button("➕ NOVO LOCAL DE COLETA", use_container_width=True):
            st.session_state.abrir_form = not st.session_state.abrir_form

    # Gaveta Retrátil de Cadastro
    if st.session_state.abrir_form:
        with st.form("form_local", clear_on_submit=True):
            st.markdown("### CADASTRAR NOVO PONTO")
            c1, c2, c3, c4 = st.columns(4)
            nome = c1.text_input("Nome do Local", placeholder="Ex: Ecoponto Sul")
            bairro = c2.text_input("Bairro", placeholder="Ex: Centro")
            tipo = c3.selectbox("Classificação", ["Ecoponto Oficial", "Ponto Crítico", "Unidade Escolar", "Área Comercial"])
            status = c4.selectbox("Status", ["Ativo", "Em Monitoramento", "Inativo"])

            if st.form_submit_button("SALVAR NO BANCO DE DADOS", use_container_width=True):
                if nome and bairro:
                    supabase.table("locais_coleta").insert({
                        "nome": nome, "bairro": bairro, "tipo": tipo, "status": status
                    }).execute()
                    st.session_state.abrir_form = False
                    st.toast("Local salvo!")
                    st.rerun()
                else:
                    st.warning("Preencha nome e bairro.")

    # Listagem Full-Width + Edição
    if not df_locais.empty:
        st.dataframe(df_locais[["id", "nome", "bairro", "tipo", "status"]], use_container_width=True, hide_index=True)

        with st.expander("⚙️ GERENCIAR / EDITAR OU EXCLUIR LOCAL"):
            id_l = st.selectbox("Selecione o ID do Local", df_locais["id"].tolist(), key="ed_loc_id")
            atual = df_locais[df_locais["id"] == id_l].iloc[0]
            u1, u2, u3 = st.columns(3)
            n_nome = u1.text_input("Nome", value=atual["nome"], key="ed_loc_nome")
            n_bairro = u2.text_input("Bairro", value=atual["bairro"], key="ed_loc_bairro")
            sts = ["Ativo", "Em Monitoramento", "Inativo"]
            n_status = u3.selectbox("Status", sts, index=sts.index(atual["status"]) if atual["status"] in sts else 0, key="ed_loc_st")

            b1, b2 = st.columns(2)
            if b1.button("💾 ATUALIZAR LOCAL", key="btn_upd_loc", use_container_width=True):
                supabase.table("locais_coleta").update({"nome": n_nome, "bairro": n_bairro, "status": n_status}).eq("id", id_l).execute()
                st.rerun()
            if b2.button("🗑️ EXCLUIR LOCAL", key="btn_del_loc", use_container_width=True):
                supabase.table("locais_coleta").delete().eq("id", id_l).execute()
                st.rerun()

# ==============================================================================
# 3. REGISTROS DE RESÍDUOS
# ==============================================================================
elif menu == "🗑️ RESÍDUOS":
    h1, h2 = st.columns([3, 1])
    with h1:
        st.markdown("""
        <div class="section-header">
            <div>
                <h2>REGISTROS DE RESÍDUOS RECOLHIDOS</h2>
                <p>Controle de pneus, garrafas, latas e entulhos retirados de circulação.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with h2:
        if st.button("➕ REGISTRAR RESÍDUO", use_container_width=True):
            st.session_state.abrir_form = not st.session_state.abrir_form

    if st.session_state.abrir_form:
        if df_locais.empty:
            st.warning("Cadastre ao menos um local de coleta primeiro.")
        else:
            with st.form("form_residuo", clear_on_submit=True):
                st.markdown("### LANÇAR COLETA DE RESÍDUOS")
                op_locais = {f"{r['nome']} ({r['bairro']})": r["id"] for _, r in df_locais.iterrows()}
                c1, c2, c3, c4, c5 = st.columns([2, 1.5, 1, 1, 1.2])
                loc_esc = c1.selectbox("Local", list(op_locais.keys()))
                cat = c2.selectbox("Categoria", ["Pneus", "Garrafas PET", "Latas/Metais", "Vidros", "Entulho/Plásticos"])
                qtd = c3.number_input("Recipientes", min_value=1, value=10, step=1)
                peso = c4.number_input("Peso (kg)", min_value=0.1, value=5.0, step=0.5)
                dt = c5.date_input("Data", value=date.today())

                if st.form_submit_button("SALVAR COLETA", use_container_width=True):
                    supabase.table("registros_residuos").insert({
                        "local_id": op_locais[loc_esc],
                        "categoria": cat,
                        "qtd_recipientes": int(qtd),
                        "peso_kg": float(peso),
                        "data_coleta": str(dt)
                    }).execute()
                    st.session_state.abrir_form = False
                    st.toast("Resíduo registrado!")
                    st.rerun()

    if not df_residuos.empty:
        st.dataframe(
            df_residuos[["id", "local_nome", "bairro", "categoria", "qtd_recipientes", "peso_kg", "data_coleta"]],
            use_container_width=True,
            hide_index=True
        )
        with st.expander("⚙️ GERENCIAR / EDITAR OU EXCLUIR RESÍDUO"):
            id_r = st.selectbox("Selecione o ID do Registro", df_residuos["id"].tolist(), key="ed_res_id")
            atual = df_residuos[df_residuos["id"] == id_r].iloc[0]
            u1, u2, u3 = st.columns(3)
            cats = ["Pneus", "Garrafas PET", "Latas/Metais", "Vidros", "Entulho/Plásticos"]
            n_cat = u1.selectbox("Categoria", cats, index=cats.index(atual["categoria"]) if atual["categoria"] in cats else 0, key="ed_res_cat")
            n_qtd = u2.number_input("Recipientes", min_value=1, value=int(atual["qtd_recipientes"]), key="ed_res_qtd")
            n_peso = u3.number_input("Peso (kg)", min_value=0.1, value=float(atual["peso_kg"]), key="ed_res_peso")

            b1, b2 = st.columns(2)
            if b1.button("💾 ATUALIZAR RESÍDUO", key="btn_upd_res", use_container_width=True):
                supabase.table("registros_residuos").update({
                    "categoria": n_cat, "qtd_recipientes": int(n_qtd), "peso_kg": float(n_peso)
                }).eq("id", id_r).execute()
                st.rerun()
            if b2.button("🗑️ EXCLUIR RESÍDUO", key="btn_del_res", use_container_width=True):
                supabase.table("registros_residuos").delete().eq("id", id_r).execute()
                st.rerun()

# ==============================================================================
# 4. OVOS, LARVAS E MOSQUITOS ENCONTRADOS
# ==============================================================================
elif menu == "🦟 OVOS, LARVAS E MOSQUITOS":
    h1, h2 = st.columns([3, 1])
    with h1:
        st.markdown("""
        <div class="section-header">
            <div>
                <h2>VIGILÂNCIA VETORIAL — OVOS, LARVAS E MOSQUITOS</h2>
                <p>Registro entomológico de focos ativos encontrados em vistorias e armadilhas.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with h2:
        if st.button("➕ REGISTRAR FOCO VETORIAL", use_container_width=True):
            st.session_state.abrir_form = not st.session_state.abrir_form

    if st.session_state.abrir_form:
        if df_locais.empty:
            st.warning("Cadastre ao menos um local primeiro.")
        else:
            with st.form("form_vetor", clear_on_submit=True):
                st.markdown("### NOVO ACHADO VETORIAL")
                op_locais = {f"{r['nome']} ({r['bairro']})": r["id"] for _, r in df_locais.iterrows()}
                c1, c2, c3, c4, c5, c6 = st.columns([2, 1.4, 1.4, 1, 1.1, 1.2])
                loc_esc = c1.selectbox("Local", list(op_locais.keys()))
                estagio = c2.selectbox("Estágio", ["Ovos (Ovitrampa)", "Larvas", "Pupas", "Mosquito Adulto"])
                especie = c3.selectbox("Espécie", ["Aedes aegypti", "Aedes albopictus", "Em Análise"])
                qtd_v = c4.number_input("Qtd.", min_value=1, value=15, step=1)
                nivel = c5.selectbox("Infestação", ["Baixo", "Médio", "Alto"])
                dt_v = c6.date_input("Data", value=date.today())

                if st.form_submit_button("SALVAR REGISTRO VETORIAL", use_container_width=True):
                    supabase.table("vigilancia_vetorial").insert({
                        "local_id": op_locais[loc_esc],
                        "estagio": estagio,
                        "especie": especie,
                        "quantidade": int(qtd_v),
                        "nivel_infestacao": nivel,
                        "data_registro": str(dt_v)
                    }).execute()
                    st.session_state.abrir_form = False
                    st.toast("Registro vetorial salvo!")
                    st.rerun()

    if not df_vetores.empty:
        st.dataframe(
            df_vetores[["id", "local_nome", "bairro", "estagio", "especie", "quantidade", "nivel_infestacao", "data_registro"]],
            use_container_width=True,
            hide_index=True
        )
        with st.expander("⚙️ GERENCIAR / EDITAR OU EXCLUIR REGISTRO VETORIAL"):
            id_v = st.selectbox("Selecione o ID", df_vetores["id"].tolist(), key="ed_vet_id")
            atual = df_vetores[df_vetores["id"] == id_v].iloc[0]
            u1, u2, u3 = st.columns(3)
            ests = ["Ovos (Ovitrampa)", "Larvas", "Pupas", "Mosquito Adulto"]
            n_est = u1.selectbox("Estágio", ests, index=ests.index(atual["estagio"]) if atual["estagio"] in ests else 0, key="ed_vet_est")
            n_qtd_v = u2.number_input("Quantidade", min_value=1, value=int(atual["quantidade"]), key="ed_vet_qtd")
            nivs = ["Baixo", "Médio", "Alto"]
            n_niv = u3.selectbox("Infestação", nivs, index=nivs.index(atual["nivel_infestacao"]) if atual["nivel_infestacao"] in nivs else 0, key="ed_vet_niv")

            b1, b2 = st.columns(2)
            if b1.button("💾 ATUALIZAR", key="btn_upd_vet", use_container_width=True):
                supabase.table("vigilancia_vetorial").update({
                    "estagio": n_est, "quantidade": int(n_qtd_v), "nivel_infestacao": n_niv
                }).eq("id", id_v).execute()
                st.rerun()
            if b2.button("🗑️ EXCLUIR", key="btn_del_vet", use_container_width=True):
                supabase.table("vigilancia_vetorial").delete().eq("id", id_v).execute()
                st.rerun()

# ==============================================================================
# 5. CASOS DE DENGUE NA REGIÃO
# ==============================================================================
elif menu == "🏥 CASOS DE DENGUE":
    h1, h2 = st.columns([3, 1])
    with h1:
        st.markdown("""
        <div class="section-header">
            <div>
                <h2>NOTIFICAÇÕES DE CASOS DE DENGUE NA REGIÃO</h2>
                <p>Acompanhamento epidemiológico por bairro, faixa etária e evolução clínica.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with h2:
        if st.button("➕ NOTIFICAR CASO", use_container_width=True):
            st.session_state.abrir_form = not st.session_state.abrir_form

    if st.session_state.abrir_form:
        with st.form("form_caso", clear_on_submit=True):
            st.markdown("### NOVA NOTIFICAÇÃO EPIDEMIOLÓGICA")
            c1, c2, c3, c4, c5 = st.columns([1.5, 1.5, 1.2, 1.3, 1.1])
            bairro_c = c1.text_input("Bairro", placeholder="Ex: Jardim Bela Vista")
            classif = c2.selectbox("Classificação", ["Suspeito", "Confirmado", "Dengue com Sinais de Alarme"])
            faixa = c3.selectbox("Faixa Etária", ["0-14 anos", "15-29 anos", "30-59 anos", "60+ anos"])
            situacao = c4.selectbox("Situação", ["Em Acompanhamento", "Recuperado", "Internado"])
            dt_c = c5.date_input("Data", value=date.today())

            if st.form_submit_button("REGISTRAR NOTIFICAÇÃO", use_container_width=True):
                if bairro_c:
                    supabase.table("casos_dengue").insert({
                        "bairro": bairro_c,
                        "classificacao": classif,
                        "faixa_etaria": faixa,
                        "situacao": situacao,
                        "data_notificacao": str(dt_c)
                    }).execute()
                    st.session_state.abrir_form = False
                    st.toast("Caso registrado!")
                    st.rerun()
                else:
                    st.warning("Informe o bairro.")

    if not df_casos.empty:
        st.dataframe(
            df_casos[["id", "bairro", "classificacao", "faixa_etaria", "situacao", "data_notificacao"]],
            use_container_width=True,
            hide_index=True
        )
        with st.expander("⚙️ GERENCIAR / ATUALIZAR OU EXCLUIR CASO"):
            id_c = st.selectbox("Selecione o ID do Caso", df_casos["id"].tolist(), key="ed_cas_id")
            atual = df_casos[df_casos["id"] == id_c].iloc[0]
            u1, u2 = st.columns(2)
            clss = ["Suspeito", "Confirmado", "Dengue com Sinais de Alarme"]
            n_cls = u1.selectbox("Classificação", clss, index=clss.index(atual["classificacao"]) if atual["classificacao"] in clss else 0, key="ed_cas_cls")
            sits = ["Em Acompanhamento", "Recuperado", "Internado"]
            n_sit = u2.selectbox("Situação", sits, index=sits.index(atual["situacao"]) if atual["situacao"] in sits else 0, key="ed_cas_sit")

            b1, b2 = st.columns(2)
            if b1.button("💾 ATUALIZAR CASO", key="btn_upd_cas", use_container_width=True):
                supabase.table("casos_dengue").update({"classificacao": n_cls, "situacao": n_sit}).eq("id", id_c).execute()
                st.rerun()
            if b2.button("🗑️ EXCLUIR CASO", key="btn_del_cas", use_container_width=True):
                supabase.table("casos_dengue").delete().eq("id", id_c).execute()
                st.rerun()

# ==============================================================================
# 6. REGISTROS DE OCORRÊNCIAS (IMPRUDÊNCIA / DENÚNCIAS)
# ==============================================================================
elif menu == "🚨 OCORRÊNCIAS":
    h1, h2 = st.columns([3, 1])
    with h1:
        st.markdown("""
        <div class="section-header">
            <div>
                <h2>REGISTROS DE OCORRÊNCIAS & IRREGULARIDADES</h2>
                <p>Denúncias de imprudência de moradores, terrenos abandonados e focos negligenciados.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with h2:
        if st.button("➕ REGISTRAR OCORRÊNCIA", use_container_width=True):
            st.session_state.abrir_form = not st.session_state.abrir_form

    if st.session_state.abrir_form:
        with st.form("form_ocorrencia", clear_on_submit=True):
            st.markdown("### NOVA OCORRÊNCIA AMBIENTAL")
            c1, c2, c3, c4 = st.columns([1.2, 1.6, 1.5, 1.1])
            bairro_o = c1.text_input("Bairro", placeholder="Ex: Jardim Bela Vista")
            ref_o = c2.text_input("Endereço / Referência", placeholder="Ex: Rua das Acácias, 410")
            tipo_o = c3.selectbox("Infração / Motivo", [
                "Imprudência de Morador",
                "Terreno Baldio Abandonado",
                "Descarte Irregular",
                "Caixa d'água Destampada"
            ])
            status_o = c4.selectbox("Status", ["Aberta", "Notificada", "Resolvida"])
            desc_o = st.text_area("Relato da Ocorrência", placeholder="Descreva os recipientes com água parada ou irregularidade observada...")
            dt_o = st.date_input("Data", value=date.today())

            if st.form_submit_button("REGISTRAR OCORRÊNCIA", use_container_width=True):
                if bairro_o and ref_o and desc_o:
                    supabase.table("ocorrencias_ambientais").insert({
                        "bairro": bairro_o,
                        "local_referencia": ref_o,
                        "tipo_ocorrencia": tipo_o,
                        "descricao": desc_o,
                        "status_resolucao": status_o,
                        "data_ocorrencia": str(dt_o)
                    }).execute()
                    st.session_state.abrir_form = False
                    st.toast("Ocorrência registrada!")
                    st.rerun()
                else:
                    st.warning("Preencha todos os campos.")

    # Cards Visuais de Ocorrências + Tabela
    if not df_ocorrencias.empty:
        for _, row in df_ocorrencias.iterrows():
            badge_cls = "badge-yellow" if row["status_resolucao"] != "Resolvida" else "badge-black"
            st.markdown(f"""
            <div class="editorial-box">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                    <div>
                        <span class="badge-black">ID #{row['id']}</span>
                        <span class="badge-yellow">{row['tipo_ocorrencia'].upper()}</span>
                        <b style="margin-left:8px;">{row['bairro']} — {row['local_referencia']}</b>
                    </div>
                    <span class="{badge_cls}">STATUS: {row['status_resolucao'].upper()} | {row['data_ocorrencia']}</span>
                </div>
                <div style="color:#262626; font-size:0.95rem;">{row['descricao']}</div>
            </div>
            """, unsafe_allow_html=True)

        with st.expander("⚙️ GERENCIAR / ATUALIZAR STATUS OU EXCLUIR OCORRÊNCIA"):
            id_o = st.selectbox("Selecione o ID da Ocorrência", df_ocorrencias["id"].tolist(), key="ed_oco_id")
            atual = df_ocorrencias[df_ocorrencias["id"] == id_o].iloc[0]
            u1, u2 = st.columns([1, 2])
            sts_o = ["Aberta", "Notificada", "Resolvida"]
            n_st_o = u1.selectbox("Status", sts_o, index=sts_o.index(atual["status_resolucao"]) if atual["status_resolucao"] in sts_o else 0, key="ed_oco_st")
            n_desc_o = u2.text_input("Atualizar Relato", value=atual["descricao"], key="ed_oco_desc")

            b1, b2 = st.columns(2)
            if b1.button("💾 ATUALIZAR OCORRÊNCIA", key="btn_upd_oco", use_container_width=True):
                supabase.table("ocorrencias_ambientais").update({
                    "status_resolucao": n_st_o, "descricao": n_desc_o
                }).eq("id", id_o).execute()
                st.rerun()
            if b2.button("🗑️ EXCLUIR OCORRÊNCIA", key="btn_del_oco", use_container_width=True):
                supabase.table("ocorrencias_ambientais").delete().eq("id", id_o).execute()
                st.rerun()

# ==============================================================================
# 7. GUIA SOBRE A DENGUE
# ==============================================================================
elif menu == "📘 GUIA DA DENGUE":
    st.markdown("""
    <div class="section-header">
        <div>
            <h2>GUIA TÉCNICO DE VIGILÂNCIA E PREVENÇÃO À DENGUE</h2>
            <p>Protocolo de identificação vetorial, eliminação de criadouros e sinais clínicos de alerta.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    g1, g2, g3 = st.columns(3, gap="medium")
    with g1:
        st.markdown("""
        <div class="editorial-box" style="border-top: 8px solid #0A0A0A;">
            <span class="badge-black">ETAPA 01 • BIOLOGIA</span>
            <h3 style="margin-top:0.6rem;">Ciclo de 7 a 10 Dias</h3>
            <p>O <i>Aedes aegypti</i> desenvolve-se rapidamente em água parada limpa ou pouco poluída:</p>
            <ul>
                <li><b>Ovos:</b> Resistem até 450 dias em ambiente seco aguardando contato com água.</li>
                <li><b>Larvas e Pupas:</b> Fase aquática que dura de 5 a 7 dias.</li>
                <li><b>Adulto:</b> A fêmea pode colocar até 400 ovos durante sua vida de 30 dias.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with g2:
        st.markdown("""
        <div class="editorial-box" style="border-top: 8px solid #FFD600;">
            <span class="badge-yellow">ETAPA 02 • AMBIENTAL</span>
            <h3 style="margin-top:0.6rem;">Controle de Resíduos</h3>
            <p>A eliminação física dos recipientes é o método mais eficaz de bloqueio:</p>
            <ul>
                <li><b>Pneus:</b> Devem ser armazenados em locais cobertos ou entregues em Ecopontos.</li>
                <li><b>Garrafas e Latas:</b> Descartar em sacos fechados ou encaminhar à reciclagem.</li>
                <li><b>Caixas d'água e Calhas:</b> Manter totalmente vedadas e livres de folhas.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with g3:
        st.markdown("""
        <div class="editorial-box" style="border-top: 8px solid #0A0A0A;">
            <span class="badge-black">ETAPA 03 • SAÚDE</span>
            <h3 style="margin-top:0.6rem;">Sintomas e Sinais de Alarme</h3>
            <p><b>Sintomas Iniciais:</b> Febre alta (39°C–40°C), dor atrás dos olhos, dor muscular e manchas vermelhas.</p>
            <div style="background:#FFD600; padding:0.7rem; border:1.5px solid #0A0A0A; font-size:0.88rem;">
                <b>⚠️ PROCURE ATENDIMENTO IMEDIATO SE HOUVER:</b> Dor abdominal intensa, vômitos persistentes, tontura ou sangramento nasal/gengival.
            </div>
        </div>
        """, unsafe_allow_html=True)
