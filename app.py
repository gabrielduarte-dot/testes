import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import StringIO
import requests
from datetime import datetime, timedelta
import numpy as np

# ─────────────────────────────────────────────
# CONFIGURAÇÃO DA PÁGINA
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard de Vendas · Grupo Seculus",
    page_icon="⌚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# ESTILOS CUSTOMIZADOS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Fundo escuro elegante */
.stApp {
    background-color: #0f1117;
    color: #e8e8e8;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #161b27;
    border-right: 1px solid #2a2f3e;
}

/* Cards de métricas */
[data-testid="stMetric"] {
    background: linear-gradient(135deg, #1a2035 0%, #1e2640 100%);
    border: 1px solid #2a3350;
    border-radius: 12px;
    padding: 18px 22px;
    transition: border-color 0.2s;
}
[data-testid="stMetric"]:hover {
    border-color: #4a7cff;
}
[data-testid="stMetricLabel"] {
    color: #8896b3 !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}
[data-testid="stMetricValue"] {
    color: #ffffff !important;
    font-size: 1.6rem !important;
    font-weight: 700 !important;
    font-family: 'DM Mono', monospace !important;
}
[data-testid="stMetricDelta"] {
    font-size: 0.82rem !important;
}

/* Títulos */
h1, h2, h3 { color: #ffffff !important; }
h1 { font-weight: 700 !important; letter-spacing: -0.02em; }
h3 { font-size: 1rem !important; font-weight: 600 !important; color: #a0aec0 !important; text-transform: uppercase; letter-spacing: 0.06em; }

/* Separador */
hr { border-color: #2a2f3e !important; }

/* DataFrame */
[data-testid="stDataFrame"] {
    border: 1px solid #2a3350;
    border-radius: 10px;
    overflow: hidden;
}

/* Badges de marca */
.brand-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.05em;
}

/* Alertas */
.insight-box {
    background: linear-gradient(135deg, #1a2640 0%, #1e2e50 100%);
    border-left: 3px solid #4a7cff;
    border-radius: 0 10px 10px 0;
    padding: 14px 18px;
    margin: 10px 0;
    font-size: 0.9rem;
    color: #c8d8f0;
}

/* Período comparativo tag */
.period-tag {
    background-color: #1a2035;
    border: 1px solid #3a4560;
    border-radius: 8px;
    padding: 6px 14px;
    font-size: 0.8rem;
    color: #8896b3;
    font-family: 'DM Mono', monospace;
    display: inline-block;
    margin: 4px 2px;
}

/* Upload area */
.upload-section {
    background: linear-gradient(135deg, #1a2035 0%, #161b27 100%);
    border: 1px dashed #3a4560;
    border-radius: 14px;
    padding: 30px;
    text-align: center;
    margin: 20px 0;
}

/* Selectbox e inputs */
[data-baseweb="select"] {
    background-color: #1a2035 !important;
    border-color: #2a3350 !important;
}

/* Tabs */
[data-baseweb="tab-list"] {
    background-color: #161b27 !important;
    border-bottom: 1px solid #2a3350 !important;
    gap: 4px;
}
[data-baseweb="tab"] {
    color: #8896b3 !important;
    font-weight: 500 !important;
}
[aria-selected="true"] {
    color: #ffffff !important;
    border-bottom: 2px solid #4a7cff !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CONSTANTES E PALETAS
# ─────────────────────────────────────────────
MARCAS = ["Seculus", "Mondaine", "Time", "E-time"]

COR_MARCAS = {
    "Seculus":  "#4a7cff",
    "Mondaine": "#f59e0b",
    "Time":     "#10b981",
    "E-time":   "#f43f5e",
}

LAYOUT_PLOTLY = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#a0aec0", family="DM Sans"),
    title_font=dict(color="#ffffff", size=14, family="DM Sans"),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#a0aec0")),
    xaxis=dict(gridcolor="#1e2640", linecolor="#2a3350", tickcolor="#2a3350"),
    yaxis=dict(gridcolor="#1e2640", linecolor="#2a3350", tickcolor="#2a3350"),
    margin=dict(l=20, r=20, t=50, b=20),
)

# ─────────────────────────────────────────────
# FUNÇÕES UTILITÁRIAS
# ─────────────────────────────────────────────

@st.cache_data(ttl=300)
def carregar_csv_url(url: str) -> pd.DataFrame:
    """Carrega CSV a partir de uma URL (Google Sheets, GitHub raw, etc.)."""
    try:
        if "docs.google.com" in url:
            # Converte link de edição/visualização para exportação CSV
            if "/edit" in url or "/view" in url:
                sheet_id = url.split("/d/")[1].split("/")[0]
                # Tenta identificar gid
                if "gid=" in url:
                    gid = url.split("gid=")[1].split("&")[0].split("#")[0]
                    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
                else:
                    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        return pd.read_csv(StringIO(r.text))
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {e}")
        return pd.DataFrame()


def validar_colunas(df: pd.DataFrame, marca: str) -> tuple[bool, list]:
    """Verifica se o DataFrame possui as colunas mínimas esperadas."""
    colunas_obrigatorias = [
        "data", "marca", "produto", "quantidade_vendida",
        "valor_total", "status_pedido", "origem_cliente"
    ]
    faltando = [c for c in colunas_obrigatorias if c not in df.columns]
    return len(faltando) == 0, faltando


def preparar_df(df: pd.DataFrame) -> pd.DataFrame:
    """Normaliza tipos e cria colunas auxiliares."""
    df = df.copy()
    df["data"] = pd.to_datetime(df["data"], dayfirst=True, errors="coerce")
    df.dropna(subset=["data"], inplace=True)

    # Garante colunas numéricas
    for col in ["valor_total", "quantidade_vendida"]:
        if col in df.columns:
            df[col] = (
                df[col].astype(str)
                .str.replace("R$", "", regex=False)
                .str.replace(".", "", regex=False)
                .str.replace(",", ".", regex=False)
                .str.strip()
            )
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # Normaliza status
    if "status_pedido" in df.columns:
        df["status_pedido"] = df["status_pedido"].str.strip().str.lower()
        df["faturado"] = df["status_pedido"].isin(["faturado", "entregue", "concluído", "concluido"])

    # Normaliza origem — preserva nome da campanha, classifica tipo do canal
    if "origem_cliente" in df.columns:
        # 'campanha': nome original formatado (capitalizado, sem espaços extras)
        df["campanha"] = df["origem_cliente"].str.strip().str.title()
        # 'tipo_canal': plataforma/tipo (Google Ads, Meta Ads, Orgânico…)
        df["tipo_canal"] = df["origem_cliente"].apply(classificar_tipo_canal)
        # 'canal': alias de tipo_canal para compatibilidade com o restante do código
        df["canal"] = df["tipo_canal"]

    return df


def classificar_tipo_canal(origem: str) -> str:
    """Classifica o TIPO do canal (plataforma) a partir da origem.
    O nome completo da campanha é preservado separadamente em 'campanha'."""
    origem_lower = str(origem).lower()
    if any(w in origem_lower for w in ["google", "gads", "adwords", "cpc", "ppc", "search"]):
        return "Google Ads"
    elif any(w in origem_lower for w in ["meta", "facebook", "instagram", "fb", "ig"]):
        return "Meta Ads"
    elif any(w in origem_lower for w in ["orgânico", "organico", "organic", "seo", "direct", "direto"]):
        return "Orgânico"
    elif any(w in origem_lower for w in ["email", "e-mail", "newsletter"]):
        return "E-mail"
    elif any(w in origem_lower for w in ["influencer", "influenciador", "parceiro"]):
        return "Influencer/Parceiro"
    else:
        return "Outros"


# Mantido por compatibilidade com referências existentes no código
def classificar_canal(origem: str) -> str:
    return classificar_tipo_canal(origem)


def calcular_variacao(atual, anterior):
    """Calcula variação percentual com segurança."""
    if anterior == 0:
        return None
    return ((atual - anterior) / anterior) * 100


def formatar_variacao(val):
    """Formata variação para exibição como delta."""
    if val is None:
        return None
    return f"{val:+.1f}%"


def filtrar_periodo(df: pd.DataFrame, data_inicio, data_fim) -> pd.DataFrame:
    return df[(df["data"] >= pd.Timestamp(data_inicio)) & (df["data"] <= pd.Timestamp(data_fim))]


def periodo_anterior(data_inicio, data_fim):
    """Calcula o período imediatamente anterior de mesmo tamanho."""
    delta = data_fim - data_inicio
    return data_inicio - delta - timedelta(days=1), data_inicio - timedelta(days=1)


# ─────────────────────────────────────────────
# TEMPLATE DE ESTRUTURA CSV
# ─────────────────────────────────────────────
TEMPLATE_CSV = """data,marca,produto,sku,quantidade_vendida,valor_unitario,valor_total,status_pedido,origem_cliente,id_pedido
01/01/2025,Seculus,Relógio Seculus Slim,SKU001,2,350.00,700.00,faturado,google ads,PED001
02/01/2025,Seculus,Relógio Seculus Sport,SKU002,1,420.00,420.00,pendente,meta ads,PED002
03/01/2025,Mondaine,Relógio Mondaine Digital,SKU010,3,280.00,840.00,faturado,organico,PED003
"""

# ─────────────────────────────────────────────
# ESTADO DA SESSÃO
# ─────────────────────────────────────────────
if "dfs" not in st.session_state:
    st.session_state.dfs = {}   # {marca: DataFrame}

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
col_logo, col_title, col_spacer = st.columns([1, 6, 1])
with col_title:
    st.markdown("## ⌚ Dashboard de Vendas · Grupo Seculus")
    st.markdown("<p style='color:#8896b3; margin-top:-10px; font-size:0.9rem;'>Análise comparativa de performance por marca e período</p>", unsafe_allow_html=True)

st.markdown("---")

# ─────────────────────────────────────────────
# SIDEBAR — CONFIGURAÇÕES
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Configurações")
    st.markdown("---")

    # ── Download do Template ──
    st.markdown("**📄 Template de Planilha**")
    st.download_button(
        label="⬇️ Baixar template CSV",
        data=TEMPLATE_CSV,
        file_name="template_vendas.csv",
        mime="text/csv",
        use_container_width=True,
        help="Baixe o template e preencha com seus dados antes de carregar"
    )
    st.markdown("<div style='font-size:0.75rem; color:#6b7a99; margin-top:4px;'>Campos: data · marca · produto · sku · quantidade_vendida · valor_unitario · valor_total · status_pedido · origem_cliente · id_pedido</div>", unsafe_allow_html=True)

    st.markdown("---")

    # ── Carregamento de Dados ──
    st.markdown("**🔗 Fontes de Dados por Marca**")
    st.markdown("<div style='font-size:0.75rem; color:#6b7a99; margin-bottom:12px;'>Cole o link do Google Sheets (compartilhado) ou URL de um .csv público</div>", unsafe_allow_html=True)

    for marca in MARCAS:
        with st.expander(f"⌚ {marca}", expanded=(marca == "Seculus")):
            url_input = st.text_input(
                f"URL CSV — {marca}",
                key=f"url_{marca}",
                placeholder="https://docs.google.com/spreadsheets/d/...",
                label_visibility="collapsed"
            )
            col_btn, col_status = st.columns([3, 1])
            with col_btn:
                if st.button(f"Carregar {marca}", key=f"btn_{marca}", use_container_width=True):
                    if url_input.strip():
                        with st.spinner("Carregando..."):
                            df_raw = carregar_csv_url(url_input.strip())
                            if not df_raw.empty:
                                ok, faltando = validar_colunas(df_raw, marca)
                                if ok:
                                    st.session_state.dfs[marca] = preparar_df(df_raw)
                                    st.success(f"✅ {len(st.session_state.dfs[marca])} linhas")
                                else:
                                    st.error(f"Colunas faltando: {', '.join(faltando)}")
                    else:
                        st.warning("Insira uma URL válida.")
            with col_status:
                if marca in st.session_state.dfs:
                    st.markdown(f"<span style='color:#10b981; font-size:1.2rem;'>●</span>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<span style='color:#374151; font-size:1.2rem;'>●</span>", unsafe_allow_html=True)

    st.markdown("---")

    # ── Período de Análise ──
    st.markdown("**📅 Período de Análise**")

    hoje = datetime.today().date()
    trinta_dias_atras = hoje - timedelta(days=30)

    data_inicio = st.date_input("De", value=trinta_dias_atras, key="data_inicio")
    data_fim = st.date_input("Até", value=hoje, key="data_fim")

    comparar_periodo = st.selectbox(
        "Comparar com",
        ["Período anterior equivalente", "Mês anterior", "Mesmo período ano anterior"],
        index=0
    )

    st.markdown("---")

    # ── Filtros Adicionais ──
    st.markdown("**🔍 Filtros**")

    marcas_disponiveis = [m for m in MARCAS if m in st.session_state.dfs]
    marcas_selecionadas = st.multiselect(
        "Marcas",
        marcas_disponiveis,
        default=marcas_disponiveis,
        key="marcas_sel"
    )

    # Tipo de canal (plataforma) — lista fixa
    tipos_canal_opcoes = ["Google Ads", "Meta Ads", "Orgânico", "E-mail", "Influencer/Parceiro", "Outros"]
    tipos_canal_selecionados = st.multiselect(
        "Tipo de canal",
        tipos_canal_opcoes,
        default=tipos_canal_opcoes,
        key="tipos_canal_sel"
    )

    # Campanhas — extraídas dinamicamente dos dados carregados
    campanhas_disponiveis = []
    for m in st.session_state.dfs.values():
        if "campanha" in m.columns:
            campanhas_disponiveis += m["campanha"].dropna().unique().tolist()
    campanhas_disponiveis = sorted(set(campanhas_disponiveis))

    if campanhas_disponiveis:
        campanhas_selecionadas = st.multiselect(
            "Campanhas",
            campanhas_disponiveis,
            default=campanhas_disponiveis,
            key="campanhas_sel",
            help="Filtre por campanha específica. Cada valor único de 'origem_cliente' aparece aqui."
        )
    else:
        campanhas_selecionadas = []

    # Alias usado pelo restante do código
    canais_selecionados = tipos_canal_selecionados

# ─────────────────────────────────────────────
# LÓGICA DE PERÍODOS DE COMPARAÇÃO
# ─────────────────────────────────────────────
def calcular_periodo_anterior(inicio, fim, modo):
    if modo == "Período anterior equivalente":
        delta = fim - inicio
        return inicio - delta - timedelta(days=1), inicio - timedelta(days=1)
    elif modo == "Mês anterior":
        primeiro_dia_mes_atual = inicio.replace(day=1)
        ultimo_dia_mes_anterior = primeiro_dia_mes_atual - timedelta(days=1)
        primeiro_dia_mes_anterior = ultimo_dia_mes_anterior.replace(day=1)
        return primeiro_dia_mes_anterior, ultimo_dia_mes_anterior
    elif modo == "Mesmo período ano anterior":
        return inicio.replace(year=inicio.year - 1), fim.replace(year=fim.year - 1)

data_inicio_ant, data_fim_ant = calcular_periodo_anterior(data_inicio, data_fim, comparar_periodo)

# ─────────────────────────────────────────────
# CONSOLIDAÇÃO DOS DADOS FILTRADOS
# ─────────────────────────────────────────────
def consolidar(marcas_sel, canais_sel, campanhas_sel, d_ini, d_fim):
    """Retorna DataFrame consolidado de todas as marcas selecionadas no período,
    filtrando por tipo de canal E por campanha (quando há campanhas selecionadas)."""
    frames = []
    for m in marcas_sel:
        if m in st.session_state.dfs:
            df_m = filtrar_periodo(st.session_state.dfs[m], d_ini, d_fim)
            # Filtro por tipo de canal (Google Ads, Meta Ads…)
            if "canal" in df_m.columns and canais_sel:
                df_m = df_m[df_m["canal"].isin(canais_sel)]
            # Filtro por campanha individual (nome original)
            if "campanha" in df_m.columns and campanhas_sel:
                df_m = df_m[df_m["campanha"].isin(campanhas_sel)]
            frames.append(df_m)
    if frames:
        return pd.concat(frames, ignore_index=True)
    return pd.DataFrame()

df_atual = consolidar(marcas_selecionadas, canais_selecionados, campanhas_selecionadas, data_inicio, data_fim)
df_ant   = consolidar(marcas_selecionadas, canais_selecionados, campanhas_selecionadas, data_inicio_ant, data_fim_ant)

# ─────────────────────────────────────────────
# ESTADO: SEM DADOS CARREGADOS
# ─────────────────────────────────────────────
if not st.session_state.dfs:
    st.markdown("""
    <div class="upload-section">
        <h2 style='color:#ffffff; margin:0 0 8px 0;'>Nenhum dado carregado</h2>
        <p style='color:#8896b3; margin:0 0 20px 0;'>
            Carregue os dados de cada marca na barra lateral para começar a análise.<br>
            Baixe o template CSV para garantir o formato correto das planilhas.
        </p>
        <p style='color:#4a7cff; font-size:0.85rem; font-family: monospace;'>
            ← Use a barra lateral para inserir os links das planilhas
        </p>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("📋 Ver estrutura esperada das planilhas"):
        st.markdown("""
        | Coluna | Tipo | Descrição | Exemplo |
        |---|---|---|---|
        | `data` | data | Data do pedido | `15/01/2025` |
        | `marca` | texto | Nome da marca | `Seculus` |
        | `produto` | texto | Nome do produto | `Relógio Slim Gold` |
        | `sku` | texto | Código do produto | `SKU001` |
        | `quantidade_vendida` | número | Qtd de unidades | `3` |
        | `valor_unitario` | número | Preço unitário | `350.00` |
        | `valor_total` | número | Valor total do item | `1050.00` |
        | `status_pedido` | texto | Status do pedido | `faturado` / `pendente` |
        | `origem_cliente` | texto | Canal de aquisição | `google ads` / `meta ads` / `organico` |
        | `id_pedido` | texto | ID único do pedido | `PED-2025-001` |
        """)
        st.markdown("""
        **Valores aceitos em `status_pedido`:** `faturado`, `entregue`, `concluído`, `pendente`, `cancelado`
        
        **Valores aceitos em `origem_cliente`:** `google ads`, `meta ads`, `facebook`, `instagram`, `organico`, `email`, `newsletter`, `influencer`, `direto`
        """)
    st.stop()

# ─────────────────────────────────────────────
# MARCADOR DE PERÍODO
# ─────────────────────────────────────────────
col_p1, col_p2, col_p3 = st.columns([3, 1, 3])
with col_p1:
    st.markdown(f"""
    <span class='period-tag'>📅 Período atual: {data_inicio.strftime('%d/%m/%Y')} → {data_fim.strftime('%d/%m/%Y')}</span>
    """, unsafe_allow_html=True)
with col_p2:
    st.markdown("<div style='text-align:center; color:#6b7a99; padding-top:8px;'>vs</div>", unsafe_allow_html=True)
with col_p3:
    st.markdown(f"""
    <span class='period-tag'>📅 Período anterior: {data_inicio_ant.strftime('%d/%m/%Y')} → {data_fim_ant.strftime('%d/%m/%Y')}</span>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# ABAS PRINCIPAIS
# ─────────────────────────────────────────────
tab_visao_geral, tab_produtos, tab_pedidos, tab_conversao, tab_trafego, tab_marca = st.tabs([
    "📊 Visão Geral",
    "🏆 Produtos",
    "📦 Pedidos",
    "🎯 Conversão",
    "📡 Tráfego & Origem",
    "🏷️ Por Marca",
])

# ═══════════════════════════════════════════════════════════════
# ABA 1: VISÃO GERAL
# ═══════════════════════════════════════════════════════════════
with tab_visao_geral:
    if df_atual.empty:
        st.info("Nenhum dado no período selecionado para as marcas carregadas.")
        st.stop()

    # ── KPIs principais ──
    st.markdown("### KPIs do Período")

    total_receita   = df_atual["valor_total"].sum() if "valor_total" in df_atual.columns else 0
    total_pedidos   = df_atual["id_pedido"].nunique() if "id_pedido" in df_atual.columns else len(df_atual)
    total_faturados = df_atual["faturado"].sum() if "faturado" in df_atual.columns else 0
    taxa_fat        = (total_faturados / total_pedidos * 100) if total_pedidos > 0 else 0
    ticket_medio    = (df_atual.groupby("id_pedido")["valor_total"].sum().mean()
                       if "id_pedido" in df_atual.columns and total_pedidos > 0 else 0)

    # KPIs do período anterior
    if not df_ant.empty:
        rec_ant   = df_ant["valor_total"].sum() if "valor_total" in df_ant.columns else 0
        ped_ant   = df_ant["id_pedido"].nunique() if "id_pedido" in df_ant.columns else len(df_ant)
        fat_ant   = df_ant["faturado"].sum() if "faturado" in df_ant.columns else 0
        taxf_ant  = (fat_ant / ped_ant * 100) if ped_ant > 0 else 0
        tick_ant  = (df_ant.groupby("id_pedido")["valor_total"].sum().mean()
                     if "id_pedido" in df_ant.columns and ped_ant > 0 else 0)
    else:
        rec_ant = ped_ant = fat_ant = taxf_ant = tick_ant = 0

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("💰 Receita Total",
              f"R$ {total_receita:,.0f}".replace(",", "."),
              delta=formatar_variacao(calcular_variacao(total_receita, rec_ant)))
    k2.metric("🛒 Pedidos Realizados",
              f"{total_pedidos:,}",
              delta=formatar_variacao(calcular_variacao(total_pedidos, ped_ant)))
    k3.metric("✅ Pedidos Faturados",
              f"{int(total_faturados):,}",
              delta=formatar_variacao(calcular_variacao(total_faturados, fat_ant)))
    k4.metric("📊 Taxa de Faturamento",
              f"{taxa_fat:.1f}%",
              delta=formatar_variacao(calcular_variacao(taxa_fat, taxf_ant)))
    k5.metric("🎟️ Ticket Médio",
              f"R$ {ticket_medio:,.0f}".replace(",", "."),
              delta=formatar_variacao(calcular_variacao(ticket_medio, tick_ant)))

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Insight automático ──
    if rec_ant > 0:
        var_rec = calcular_variacao(total_receita, rec_ant)
        emoji = "🟢" if var_rec >= 0 else "🔴"
        direcao = "crescimento" if var_rec >= 0 else "queda"
        st.markdown(f"""
        <div class="insight-box">
            {emoji} <strong>Insight:</strong> A receita consolidada apresentou <strong>{direcao} de {abs(var_rec):.1f}%</strong> 
            em relação ao período anterior — de R$ {rec_ant:,.0f} para R$ {total_receita:,.0f}.
        </div>
        """.replace(",", "."), unsafe_allow_html=True)

    st.markdown("---")

    # ── Evolução temporal ──
    st.markdown("### Evolução de Receita por Marca")
    if "marca" in df_atual.columns:
        df_time = df_atual.groupby(["data", "marca"])["valor_total"].sum().reset_index()
        fig_time = px.line(
            df_time, x="data", y="valor_total", color="marca",
            color_discrete_map=COR_MARCAS,
            labels={"valor_total": "Receita (R$)", "data": "", "marca": "Marca"}
        )
        fig_time.update_traces(line_width=2.5)
        fig_time.update_layout(**LAYOUT_PLOTLY)
        st.plotly_chart(fig_time, use_container_width=True)

    st.markdown("---")

    # ── Receita por marca (barras comparativas) ──
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.markdown("### Receita por Marca — Atual vs Anterior")
        if "marca" in df_atual.columns:
            rec_atual_marca = df_atual.groupby("marca")["valor_total"].sum().reset_index()
            rec_ant_marca   = df_ant.groupby("marca")["valor_total"].sum().reset_index() if not df_ant.empty else pd.DataFrame(columns=["marca","valor_total"])
            rec_atual_marca.columns = ["marca", "atual"]
            rec_ant_marca.columns   = ["marca", "anterior"]
            comp = rec_atual_marca.merge(rec_ant_marca, on="marca", how="left").fillna(0)

            fig_comp = go.Figure()
            fig_comp.add_trace(go.Bar(
                name="Anterior", x=comp["marca"], y=comp["anterior"],
                marker_color="rgba(100,120,160,0.5)", marker_line_width=0
            ))
            fig_comp.add_trace(go.Bar(
                name="Atual", x=comp["marca"], y=comp["atual"],
                marker_color=[COR_MARCAS.get(m, "#4a7cff") for m in comp["marca"]],
                marker_line_width=0
            ))
            fig_comp.update_layout(barmode="group", **LAYOUT_PLOTLY)
            st.plotly_chart(fig_comp, use_container_width=True)

    with col_g2:
        st.markdown("### Share de Receita por Marca")
        if "marca" in df_atual.columns:
            share = df_atual.groupby("marca")["valor_total"].sum().reset_index()
            fig_pie = px.pie(
                share, names="marca", values="valor_total",
                color="marca", color_discrete_map=COR_MARCAS, hole=0.55
            )
            fig_pie.update_traces(textinfo="percent+label", textfont_size=12)
            fig_pie.update_layout(**LAYOUT_PLOTLY)
            st.plotly_chart(fig_pie, use_container_width=True)


# ═══════════════════════════════════════════════════════════════
# ABA 2: PRODUTOS
# ═══════════════════════════════════════════════════════════════
with tab_produtos:
    st.markdown("### 🏆 Top Produtos Mais Vendidos")

    col_filtro_marca, col_filtro_n = st.columns([3, 1])
    with col_filtro_marca:
        marcas_prod = st.multiselect("Filtrar marca", marcas_selecionadas, default=marcas_selecionadas, key="prod_marcas")
    with col_filtro_n:
        top_n = st.selectbox("Top", [5, 10, 15, 20], index=1, key="top_n")

    df_prod = df_atual[df_atual["marca"].isin(marcas_prod)] if "marca" in df_atual.columns else df_atual

    if not df_prod.empty and "produto" in df_prod.columns:
        col_p1, col_p2 = st.columns(2)

        with col_p1:
            st.markdown("**Por quantidade vendida**")
            top_qtd = (df_prod.groupby(["marca","produto"])["quantidade_vendida"]
                       .sum().reset_index()
                       .sort_values("quantidade_vendida", ascending=False).head(top_n))
            fig_qtd = px.bar(
                top_qtd, x="quantidade_vendida", y="produto", color="marca",
                orientation="h", color_discrete_map=COR_MARCAS,
                labels={"quantidade_vendida": "Unidades Vendidas", "produto": ""}
            )
            fig_qtd.update_layout(**LAYOUT_PLOTLY, yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig_qtd, use_container_width=True)

        with col_p2:
            st.markdown("**Por receita gerada**")
            top_rec = (df_prod.groupby(["marca","produto"])["valor_total"]
                       .sum().reset_index()
                       .sort_values("valor_total", ascending=False).head(top_n))
            fig_rec = px.bar(
                top_rec, x="valor_total", y="produto", color="marca",
                orientation="h", color_discrete_map=COR_MARCAS,
                labels={"valor_total": "Receita (R$)", "produto": ""}
            )
            fig_rec.update_layout(**LAYOUT_PLOTLY, yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig_rec, use_container_width=True)

        # ── Tabela detalhada ──
        st.markdown("### Detalhamento por Produto")
        resumo_prod = (df_prod.groupby(["marca","produto","sku"] if "sku" in df_prod.columns else ["marca","produto"])
                       .agg(
                           qtd_vendida=("quantidade_vendida","sum"),
                           receita_total=("valor_total","sum"),
                           pedidos=("id_pedido","nunique") if "id_pedido" in df_prod.columns else ("quantidade_vendida","count")
                       ).reset_index().sort_values("receita_total", ascending=False))

        resumo_prod["ticket_medio"] = resumo_prod["receita_total"] / resumo_prod["pedidos"]
        resumo_prod["receita_total"] = resumo_prod["receita_total"].map("R$ {:,.0f}".format)
        resumo_prod["ticket_medio"]  = resumo_prod["ticket_medio"].map("R$ {:,.0f}".format)

        st.dataframe(resumo_prod, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum dado de produto disponível no período.")


# ═══════════════════════════════════════════════════════════════
# ABA 3: PEDIDOS
# ═══════════════════════════════════════════════════════════════
with tab_pedidos:
    st.markdown("### 📦 Análise de Pedidos")

    if not df_atual.empty and "status_pedido" in df_atual.columns:
        # ── KPIs de pedidos ──
        total_ped    = df_atual["id_pedido"].nunique() if "id_pedido" in df_atual.columns else len(df_atual)
        ped_fat      = df_atual[df_atual["faturado"]]["id_pedido"].nunique() if "id_pedido" in df_atual.columns else df_atual["faturado"].sum()
        ped_pend     = df_atual[~df_atual["faturado"]]["id_pedido"].nunique() if "id_pedido" in df_atual.columns else (~df_atual["faturado"]).sum()
        taxa_conv    = (ped_fat / total_ped * 100) if total_ped > 0 else 0

        if not df_ant.empty and "faturado" in df_ant.columns:
            ped_ant_t    = df_ant["id_pedido"].nunique() if "id_pedido" in df_ant.columns else len(df_ant)
            ped_fat_ant  = df_ant["faturado"].sum()
            taxa_ant     = (ped_fat_ant / ped_ant_t * 100) if ped_ant_t > 0 else 0
        else:
            ped_ant_t = ped_fat_ant = taxa_ant = 0

        kp1, kp2, kp3, kp4 = st.columns(4)
        kp1.metric("📥 Pedidos Realizados", f"{total_ped:,}",
                   delta=formatar_variacao(calcular_variacao(total_ped, ped_ant_t)))
        kp2.metric("✅ Pedidos Faturados", f"{int(ped_fat):,}",
                   delta=formatar_variacao(calcular_variacao(ped_fat, ped_fat_ant)))
        kp3.metric("⏳ Pedidos Pendentes", f"{int(ped_pend):,}")
        kp4.metric("📈 Taxa de Faturamento", f"{taxa_conv:.1f}%",
                   delta=formatar_variacao(calcular_variacao(taxa_conv, taxa_ant)))

        st.markdown("<br>", unsafe_allow_html=True)

        col_s1, col_s2 = st.columns(2)

        with col_s1:
            st.markdown("### Status dos Pedidos")
            status_count = df_atual["status_pedido"].value_counts().reset_index()
            status_count.columns = ["status", "quantidade"]
            CORES_STATUS = {
                "faturado": "#10b981", "entregue": "#10b981", "concluído": "#10b981",
                "pendente": "#f59e0b", "cancelado": "#f43f5e"
            }
            fig_status = px.pie(
                status_count, names="status", values="quantidade",
                color="status", color_discrete_map=CORES_STATUS, hole=0.55
            )
            fig_status.update_traces(textinfo="percent+label")
            fig_status.update_layout(**LAYOUT_PLOTLY)
            st.plotly_chart(fig_status, use_container_width=True)

        with col_s2:
            st.markdown("### Pedidos por Marca")
            if "marca" in df_atual.columns:
                ped_marca = (df_atual.groupby("marca")
                             .agg(realizados=("id_pedido","nunique"),
                                  faturados=("faturado","sum"))
                             .reset_index())
                fig_ped = go.Figure()
                fig_ped.add_trace(go.Bar(name="Realizados", x=ped_marca["marca"], y=ped_marca["realizados"],
                                         marker_color="rgba(100,120,200,0.5)"))
                fig_ped.add_trace(go.Bar(name="Faturados", x=ped_marca["marca"], y=ped_marca["faturados"],
                                         marker_color=[COR_MARCAS.get(m, "#4a7cff") for m in ped_marca["marca"]]))
                fig_ped.update_layout(barmode="group", **LAYOUT_PLOTLY)
                st.plotly_chart(fig_ped, use_container_width=True)

        # ── Pedidos ao longo do tempo ──
        st.markdown("### Volume de Pedidos por Dia")
        if "id_pedido" in df_atual.columns:
            ped_dia = (df_atual.groupby(["data","marca"])["id_pedido"]
                       .nunique().reset_index()
                       .rename(columns={"id_pedido":"pedidos"}))
            fig_ped_dia = px.area(
                ped_dia, x="data", y="pedidos", color="marca",
                color_discrete_map=COR_MARCAS,
                labels={"pedidos":"Pedidos","data":""}
            )
            fig_ped_dia.update_layout(**LAYOUT_PLOTLY)
            st.plotly_chart(fig_ped_dia, use_container_width=True)

        # ── Tabela de pedidos detalhada ──
        st.markdown("### Registro de Pedidos")
        colunas_exibir = [c for c in ["data","marca","id_pedido","produto","quantidade_vendida","valor_total","status_pedido","canal"]
                          if c in df_atual.columns]
        st.dataframe(df_atual[colunas_exibir].sort_values("data", ascending=False),
                     use_container_width=True, hide_index=True)

    else:
        st.info("Nenhum dado de pedidos disponível no período.")


# ═══════════════════════════════════════════════════════════════
# ABA 4: CONVERSÃO
# ═══════════════════════════════════════════════════════════════
with tab_conversao:
    st.markdown("### 🎯 Taxa de Conversão")

    if not df_atual.empty and "faturado" in df_atual.columns:
        # ── Taxa de conversão geral e por marca ──
        col_c1, col_c2 = st.columns(2)

        with col_c1:
            st.markdown("**Taxa de Conversão Atual vs Anterior por Marca**")
            if "marca" in df_atual.columns:
                conv_atual = (df_atual.groupby("marca")
                              .apply(lambda x: x["faturado"].mean() * 100)
                              .reset_index()
                              .rename(columns={0: "taxa_atual"}))
                conv_ant_df = (df_ant.groupby("marca")
                               .apply(lambda x: x["faturado"].mean() * 100)
                               .reset_index()
                               .rename(columns={0: "taxa_anterior"})) if not df_ant.empty else pd.DataFrame(columns=["marca","taxa_anterior"])
                conv_merge = conv_atual.merge(conv_ant_df, on="marca", how="left").fillna(0)

                fig_conv = go.Figure()
                fig_conv.add_trace(go.Bar(name="Período Anterior", x=conv_merge["marca"],
                                           y=conv_merge["taxa_anterior"], marker_color="rgba(100,120,160,0.5)"))
                fig_conv.add_trace(go.Bar(name="Período Atual", x=conv_merge["marca"],
                                           y=conv_merge["taxa_atual"],
                                           marker_color=[COR_MARCAS.get(m,"#4a7cff") for m in conv_merge["marca"]]))
                fig_conv.update_layout(barmode="group", yaxis_ticksuffix="%", **LAYOUT_PLOTLY)
                st.plotly_chart(fig_conv, use_container_width=True)

        with col_c2:
            st.markdown("**Evolução da Taxa de Conversão no Período**")
            if "marca" in df_atual.columns:
                conv_time = (df_atual.groupby(["data","marca"])
                             .apply(lambda x: x["faturado"].mean() * 100)
                             .reset_index().rename(columns={0:"conversao"}))
                fig_conv_t = px.line(conv_time, x="data", y="conversao", color="marca",
                                      color_discrete_map=COR_MARCAS,
                                      labels={"conversao":"Taxa de Conversão (%)","data":""})
                fig_conv_t.update_traces(line_width=2.5)
                fig_conv_t.update_layout(**LAYOUT_PLOTLY)
                st.plotly_chart(fig_conv_t, use_container_width=True)

        # ── Conversão por canal ──
        st.markdown("### Taxa de Conversão por Canal de Aquisição")
        if "canal" in df_atual.columns:
            conv_canal = (df_atual.groupby("canal")
                          .agg(pedidos=("faturado","count"), faturados=("faturado","sum"))
                          .reset_index())
            conv_canal["taxa"] = conv_canal["faturados"] / conv_canal["pedidos"] * 100

            fig_canal_conv = px.bar(
                conv_canal.sort_values("taxa", ascending=True),
                x="taxa", y="canal", orientation="h",
                color="canal",
                labels={"taxa":"Taxa de Conversão (%)","canal":""},
                text=conv_canal.sort_values("taxa", ascending=True)["taxa"].map("{:.1f}%".format)
            )
            fig_canal_conv.update_traces(textposition="outside")
            fig_canal_conv.update_layout(**LAYOUT_PLOTLY)
            st.plotly_chart(fig_canal_conv, use_container_width=True)

        # ── Insight de conversão ──
        if "marca" in df_atual.columns:
            melhor = conv_atual.loc[conv_atual["taxa_atual"].idxmax()]
            st.markdown(f"""
            <div class="insight-box">
                🏆 <strong>Melhor conversão:</strong> A marca <strong>{melhor['marca']}</strong> apresenta a maior taxa de conversão 
                no período ({melhor['taxa_atual']:.1f}%), indicando maior eficiência no funil de vendas.
            </div>
            """, unsafe_allow_html=True)

    else:
        st.info("Nenhum dado de conversão disponível.")


# ═══════════════════════════════════════════════════════════════
# ABA 5: TRÁFEGO & ORIGEM
# ═══════════════════════════════════════════════════════════════
with tab_trafego:
    st.markdown("### 📡 Análise de Tráfego e Origem de Clientes")

    if not df_atual.empty and "canal" in df_atual.columns:
        col_t1, col_t2 = st.columns(2)

        with col_t1:
            st.markdown("**Distribuição por Canal (Período Atual)**")
            canal_count = df_atual["canal"].value_counts().reset_index()
            canal_count.columns = ["canal", "pedidos"]
            CORES_CANAL = {
                "Google Ads": "#4a7cff",
                "Meta Ads": "#f59e0b",
                "Orgânico": "#10b981",
                "E-mail": "#8b5cf6",
                "Influencer/Parceiro": "#f43f5e",
                "Outros": "#6b7a99",
            }
            fig_canal = px.pie(
                canal_count, names="canal", values="pedidos",
                color="canal", color_discrete_map=CORES_CANAL, hole=0.55
            )
            fig_canal.update_traces(textinfo="percent+label")
            fig_canal.update_layout(**LAYOUT_PLOTLY)
            st.plotly_chart(fig_canal, use_container_width=True)

        with col_t2:
            st.markdown("**Receita por Canal**")
            canal_rec = df_atual.groupby("canal")["valor_total"].sum().reset_index().sort_values("valor_total", ascending=True)
            fig_canal_rec = px.bar(
                canal_rec, x="valor_total", y="canal", orientation="h",
                color="canal", color_discrete_map=CORES_CANAL,
                labels={"valor_total":"Receita (R$)","canal":""}
            )
            fig_canal_rec.update_layout(**LAYOUT_PLOTLY)
            st.plotly_chart(fig_canal_rec, use_container_width=True)

        # ── Comparação atual vs anterior por canal ──
        st.markdown("### Canal: Atual vs Período Anterior")
        canal_atual = df_atual.groupby("canal").agg(
            pedidos=("faturado","count"),
            receita=("valor_total","sum"),
            faturados=("faturado","sum")
        ).reset_index()
        canal_ant = df_ant.groupby("canal").agg(
            pedidos=("faturado","count"),
            receita=("valor_total","sum"),
        ).reset_index().rename(columns={"pedidos":"pedidos_ant","receita":"receita_ant"}) if not df_ant.empty else pd.DataFrame()

        if not canal_ant.empty:
            canal_comp = canal_atual.merge(canal_ant, on="canal", how="left").fillna(0)
            canal_comp["var_receita"] = canal_comp.apply(
                lambda r: calcular_variacao(r["receita"], r["receita_ant"]), axis=1)
            canal_comp["var_str"] = canal_comp["var_receita"].map(
                lambda v: f"{v:+.1f}%" if v is not None else "—")

            fig_ccomp = go.Figure()
            fig_ccomp.add_trace(go.Bar(name="Anterior", x=canal_comp["canal"], y=canal_comp["receita_ant"],
                                        marker_color="rgba(100,120,160,0.5)"))
            fig_ccomp.add_trace(go.Bar(name="Atual", x=canal_comp["canal"], y=canal_comp["receita"],
                                        marker_color=[CORES_CANAL.get(c,"#4a7cff") for c in canal_comp["canal"]],
                                        text=canal_comp["var_str"], textposition="outside"))
            fig_ccomp.update_layout(barmode="group", **LAYOUT_PLOTLY)
            st.plotly_chart(fig_ccomp, use_container_width=True)

        # ── Breakdown canal x marca ──
        st.markdown("### Canal por Marca")
        if "marca" in df_atual.columns:
            canal_marca = df_atual.groupby(["marca","canal"])["valor_total"].sum().reset_index()
            fig_cm = px.bar(
                canal_marca, x="marca", y="valor_total", color="canal",
                color_discrete_map=CORES_CANAL, barmode="stack",
                labels={"valor_total":"Receita (R$)","marca":"","canal":"Canal"}
            )
            fig_cm.update_layout(**LAYOUT_PLOTLY)
            st.plotly_chart(fig_cm, use_container_width=True)

        # ── Tabela resumo por tipo de canal ──
        st.markdown("### Resumo por Tipo de Canal")
        canal_tab = canal_atual.copy()
        canal_tab["taxa_conv"] = (canal_tab["faturados"] / canal_tab["pedidos"] * 100).map("{:.1f}%".format)
        canal_tab["receita"] = canal_tab["receita"].map("R$ {:,.0f}".format)
        canal_tab = canal_tab.rename(columns={
            "canal":"Canal","pedidos":"Pedidos","faturados":"Faturados",
            "receita":"Receita","taxa_conv":"Taxa Conv."
        })
        st.dataframe(canal_tab[["Canal","Pedidos","Faturados","Taxa Conv.","Receita"]],
                     use_container_width=True, hide_index=True)

        # ── Detalhamento por campanha individual ──
        st.markdown("### Detalhamento por Campanha")
        st.markdown("<div style='font-size:0.8rem; color:#8896b3; margin-top:-10px; margin-bottom:12px;'>Cada valor único de <code>origem_cliente</code> aparece como uma campanha separada</div>", unsafe_allow_html=True)

        if "campanha" in df_atual.columns:
            camp_atual = df_atual.groupby(["tipo_canal", "campanha"]).agg(
                pedidos=("faturado", "count"),
                faturados=("faturado", "sum"),
                receita=("valor_total", "sum"),
            ).reset_index()

            if not df_ant.empty and "campanha" in df_ant.columns:
                camp_ant = df_ant.groupby("campanha").agg(
                    receita_ant=("valor_total", "sum"),
                    pedidos_ant=("faturado", "count"),
                ).reset_index()
                camp_atual = camp_atual.merge(camp_ant, on="campanha", how="left").fillna(0)
                camp_atual["var_receita"] = camp_atual.apply(
                    lambda r: calcular_variacao(r["receita"], r["receita_ant"]), axis=1
                ).map(lambda v: f"{v:+.1f}%" if v is not None else "—")
            else:
                camp_atual["var_receita"] = "—"

            camp_atual["taxa_conv"] = (camp_atual["faturados"] / camp_atual["pedidos"] * 100).map("{:.1f}%".format)
            camp_atual = camp_atual.sort_values("receita", ascending=False)

            # Gráfico de barras por campanha
            fig_camp = px.bar(
                camp_atual.head(20),
                x="receita", y="campanha", color="tipo_canal",
                orientation="h",
                color_discrete_map=CORES_CANAL,
                labels={"receita": "Receita (R$)", "campanha": "", "tipo_canal": "Canal"}
            )
            fig_camp.update_layout(**LAYOUT_PLOTLY, yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig_camp, use_container_width=True)

            # Tabela completa
            camp_exib = camp_atual.copy()
            camp_exib["receita"] = camp_exib["receita"].map("R$ {:,.0f}".format)
            camp_exib = camp_exib.rename(columns={
                "tipo_canal": "Tipo de Canal", "campanha": "Campanha",
                "pedidos": "Pedidos", "faturados": "Faturados",
                "taxa_conv": "Taxa Conv.", "receita": "Receita",
                "var_receita": "Var. vs Anterior"
            })
            cols_exib = [c for c in ["Tipo de Canal","Campanha","Pedidos","Faturados","Taxa Conv.","Receita","Var. vs Anterior"]
                         if c in camp_exib.columns]
            st.dataframe(camp_exib[cols_exib], use_container_width=True, hide_index=True)
        else:
            st.info("Coluna `origem_cliente` não encontrada nos dados — adicione-a à planilha para ver o detalhamento por campanha.")
    else:
        st.info("Dados de origem do cliente não disponíveis. Certifique-se que a coluna `origem_cliente` está na planilha.")


# ═══════════════════════════════════════════════════════════════
# ABA 6: POR MARCA
# ═══════════════════════════════════════════════════════════════
with tab_marca:
    st.markdown("### 🏷️ Análise Individual por Marca")

    marca_sel = st.selectbox("Selecionar marca", marcas_selecionadas, key="marca_individual")

    if marca_sel and marca_sel in st.session_state.dfs:
        df_m_atual = filtrar_periodo(st.session_state.dfs[marca_sel], data_inicio, data_fim)
        df_m_ant   = filtrar_periodo(st.session_state.dfs[marca_sel], data_inicio_ant, data_fim_ant)

        if not df_m_atual.empty:
            rec_m   = df_m_atual["valor_total"].sum()
            ped_m   = df_m_atual["id_pedido"].nunique() if "id_pedido" in df_m_atual.columns else len(df_m_atual)
            fat_m   = df_m_atual["faturado"].sum() if "faturado" in df_m_atual.columns else 0
            conv_m  = (fat_m / ped_m * 100) if ped_m > 0 else 0

            rec_m_a  = df_m_ant["valor_total"].sum() if not df_m_ant.empty else 0
            ped_m_a  = df_m_ant["id_pedido"].nunique() if not df_m_ant.empty and "id_pedido" in df_m_ant.columns else 0
            fat_m_a  = df_m_ant["faturado"].sum() if not df_m_ant.empty and "faturado" in df_m_ant.columns else 0
            conv_m_a = (fat_m_a / ped_m_a * 100) if ped_m_a > 0 else 0

            km1, km2, km3, km4 = st.columns(4)
            km1.metric("Receita", f"R$ {rec_m:,.0f}".replace(",","."),
                       delta=formatar_variacao(calcular_variacao(rec_m, rec_m_a)))
            km2.metric("Pedidos", f"{ped_m:,}",
                       delta=formatar_variacao(calcular_variacao(ped_m, ped_m_a)))
            km3.metric("Faturados", f"{int(fat_m):,}",
                       delta=formatar_variacao(calcular_variacao(fat_m, fat_m_a)))
            km4.metric("Taxa Conversão", f"{conv_m:.1f}%",
                       delta=formatar_variacao(calcular_variacao(conv_m, conv_m_a)))

            st.markdown("<br>", unsafe_allow_html=True)

            col_m1, col_m2 = st.columns(2)
            with col_m1:
                st.markdown(f"**Top 10 Produtos — {marca_sel}**")
                if "produto" in df_m_atual.columns:
                    top_m = df_m_atual.groupby("produto")["valor_total"].sum().nlargest(10).reset_index()
                    fig_top_m = px.bar(
                        top_m, x="valor_total", y="produto", orientation="h",
                        color_discrete_sequence=[COR_MARCAS.get(marca_sel,"#4a7cff")],
                        labels={"valor_total":"Receita (R$)","produto":""}
                    )
                    fig_top_m.update_layout(**LAYOUT_PLOTLY, yaxis=dict(autorange="reversed"))
                    st.plotly_chart(fig_top_m, use_container_width=True)

            with col_m2:
                st.markdown(f"**Origem dos Clientes — {marca_sel}**")
                if "canal" in df_m_atual.columns:
                    canal_m = df_m_atual["canal"].value_counts().reset_index()
                    canal_m.columns = ["canal","qtd"]
                    fig_canal_m = px.pie(canal_m, names="canal", values="qtd", hole=0.55)
                    fig_canal_m.update_traces(textinfo="percent+label")
                    fig_canal_m.update_layout(**LAYOUT_PLOTLY)
                    st.plotly_chart(fig_canal_m, use_container_width=True)

            # Evolução temporal da marca
            st.markdown(f"**Receita Diária — {marca_sel}**")
            rec_dia_m = df_m_atual.groupby("data")["valor_total"].sum().reset_index()
            fig_rec_dia_m = px.area(
                rec_dia_m, x="data", y="valor_total",
                color_discrete_sequence=[COR_MARCAS.get(marca_sel,"#4a7cff")],
                labels={"valor_total":"Receita (R$)","data":""}
            )
            fig_rec_dia_m.update_layout(**LAYOUT_PLOTLY)
            st.plotly_chart(fig_rec_dia_m, use_container_width=True)

        else:
            st.info(f"Nenhum dado para {marca_sel} no período selecionado.")
    else:
        st.info("Selecione uma marca carregada para visualizar os dados individuais.")

# ─────────────────────────────────────────────
# RODAPÉ
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#3a4560; font-size:0.75rem; font-family: DM Mono, monospace;'>"
    "⌚ Dashboard de Vendas · Grupo Seculus · Dados atualizados a cada 5 min"
    "</div>",
    unsafe_allow_html=True
)
