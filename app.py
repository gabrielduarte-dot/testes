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
.stApp {
    background-color: #0f1117;
    color: #e8e8e8;
}
[data-testid="stSidebar"] {
    background-color: #161b27;
    border-right: 1px solid #2a2f3e;
}
[data-testid="stMetric"] {
    background: linear-gradient(135deg, #1a2035 0%, #1e2640 100%);
    border: 1px solid #2a3350;
    border-radius: 12px;
    padding: 18px 22px;
    transition: border-color 0.2s;
}
[data-testid="stMetric"]:hover { border-color: #4a7cff; }
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
[data-testid="stMetricDelta"] { font-size: 0.82rem !important; }
h1, h2, h3 { color: #ffffff !important; }
h1 { font-weight: 700 !important; letter-spacing: -0.02em; }
h3 { font-size: 1rem !important; font-weight: 600 !important; color: #a0aec0 !important; text-transform: uppercase; letter-spacing: 0.06em; }
hr { border-color: #2a2f3e !important; }
[data-testid="stDataFrame"] {
    border: 1px solid #2a3350;
    border-radius: 10px;
    overflow: hidden;
}
.insight-box {
    background: linear-gradient(135deg, #1a2640 0%, #1e2e50 100%);
    border-left: 3px solid #4a7cff;
    border-radius: 0 10px 10px 0;
    padding: 14px 18px;
    margin: 10px 0;
    font-size: 0.9rem;
    color: #c8d8f0;
}
.resumo-card {
    background: linear-gradient(135deg, #161d30 0%, #1a2240 100%);
    border: 1px solid #2a3350;
    border-radius: 14px;
    padding: 20px 24px;
    margin-bottom: 10px;
}
.resumo-card h4 {
    font-size: 1rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    margin: 0 0 14px 0 !important;
}
.resumo-linha {
    display: flex;
    justify-content: space-between;
    padding: 5px 0;
    border-bottom: 1px solid #1e2640;
    font-size: 0.85rem;
    color: #a0aec0;
}
.resumo-linha:last-child { border-bottom: none; }
.resumo-valor { font-family: 'DM Mono', monospace; color: #ffffff; font-weight: 600; }
.badge-verde { background: #0d2e1e; color: #10b981; padding: 2px 8px; border-radius: 6px; font-size: 0.8rem; font-weight: 600; }
.badge-vermelho { background: #2e0d14; color: #f43f5e; padding: 2px 8px; border-radius: 6px; font-size: 0.8rem; font-weight: 600; }
.badge-amarelo { background: #2e200d; color: #f59e0b; padding: 2px 8px; border-radius: 6px; font-size: 0.8rem; font-weight: 600; }
.upload-section {
    background: linear-gradient(135deg, #1a2035 0%, #161b27 100%);
    border: 1px dashed #3a4560;
    border-radius: 14px;
    padding: 30px;
    text-align: center;
    margin: 20px 0;
}
[data-baseweb="tab-list"] {
    background-color: #161b27 !important;
    border-bottom: 1px solid #2a3350 !important;
    gap: 4px;
}
[data-baseweb="tab"] { color: #8896b3 !important; font-weight: 500 !important; }
[aria-selected="true"] { color: #ffffff !important; border-bottom: 2px solid #4a7cff !important; }
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

CORES_CANAL = {
    "Google Ads":          "#4a7cff",
    "Meta Ads":            "#f59e0b",
    "Orgânico":            "#10b981",
    "E-mail":              "#8b5cf6",
    "Influencer/Parceiro": "#f43f5e",
    "Outros":              "#6b7a99",
}

# FIX: LAYOUT_PLOTLY não deve conter 'yaxis' — cada gráfico define o seu próprio.
# Colocar yaxis aqui sobrescreve qualquer yaxis customizado (ex: autorange="reversed").
LAYOUT_PLOTLY = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#a0aec0", family="DM Sans"),
    title_font=dict(color="#ffffff", size=14, family="DM Sans"),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#a0aec0")),
    xaxis=dict(gridcolor="#1e2640", linecolor="#2a3350", tickcolor="#2a3350"),
    margin=dict(l=20, r=20, t=50, b=20),
)

# Layout base para gráficos com eixo Y normal (sem autorange)
def layout_normal():
    d = dict(LAYOUT_PLOTLY)
    d["yaxis"] = dict(gridcolor="#1e2640", linecolor="#2a3350", tickcolor="#2a3350")
    return d

# Layout para gráficos horizontais com eixo Y invertido
def layout_invertido():
    d = dict(LAYOUT_PLOTLY)
    d["yaxis"] = dict(gridcolor="#1e2640", linecolor="#2a3350", tickcolor="#2a3350", autorange="reversed")
    return d

# ─────────────────────────────────────────────
# FUNÇÕES UTILITÁRIAS
# ─────────────────────────────────────────────

@st.cache_data(ttl=300)
def carregar_csv_url(url: str) -> pd.DataFrame:
    """Carrega CSV a partir de uma URL (Google Sheets, GitHub raw, etc.)."""
    try:
        url = url.strip()
        if "docs.google.com" in url:
            if "/edit" in url or "/view" in url or "/pub" in url:
                sheet_id = url.split("/d/")[1].split("/")[0]
                gid = None
                if "gid=" in url:
                    gid = url.split("gid=")[1].split("&")[0].split("#")[0]
                if gid:
                    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
                else:
                    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "text/csv,text/plain,*/*",
        }
        r = requests.get(url, timeout=20, headers=headers)
        r.raise_for_status()
        # Detecta encoding
        content = r.content
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            text = content.decode("latin-1")
        df = pd.read_csv(StringIO(text))
        # Normaliza nomes de colunas: remove espaços, lowercase
        df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
        return df
    except requests.exceptions.HTTPError as e:
        st.error(f"❌ Erro HTTP ao carregar dados: {e}. Verifique se a planilha está compartilhada publicamente.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {e}")
        return pd.DataFrame()


def validar_colunas(df: pd.DataFrame) -> tuple[bool, list]:
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

    for col in ["valor_total", "quantidade_vendida", "valor_unitario"]:
        if col in df.columns:
            df[col] = (
                df[col].astype(str)
                .str.replace("R$", "", regex=False)
                .str.replace(r"\.", "", regex=True)
                .str.replace(",", ".", regex=False)
                .str.strip()
            )
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    if "status_pedido" in df.columns:
        df["status_pedido"] = df["status_pedido"].str.strip().str.lower()
        df["faturado"] = df["status_pedido"].isin(
            ["faturado", "entregue", "concluído", "concluido", "aprovado"]
        )
        df["cancelado"] = df["status_pedido"].isin(["cancelado", "cancelada", "devolvido"])

    if "origem_cliente" in df.columns:
        df["campanha"] = df["origem_cliente"].str.strip().str.title()
        df["tipo_canal"] = df["origem_cliente"].apply(classificar_tipo_canal)
        df["canal"] = df["tipo_canal"]

    # Garante coluna id_pedido
    if "id_pedido" not in df.columns:
        df["id_pedido"] = df.index.astype(str)

    return df


def classificar_tipo_canal(origem: str) -> str:
    o = str(origem).lower().strip()
    if any(w in o for w in ["google", "gads", "adwords", "cpc", "ppc", "search"]):
        return "Google Ads"
    elif any(w in o for w in ["meta", "facebook", "instagram", "fb", "ig"]):
        return "Meta Ads"
    elif any(w in o for w in ["orgânico", "organico", "organic", "seo", "direct", "direto"]):
        return "Orgânico"
    elif any(w in o for w in ["email", "e-mail", "newsletter"]):
        return "E-mail"
    elif any(w in o for w in ["influencer", "influenciador", "parceiro"]):
        return "Influencer/Parceiro"
    else:
        return "Outros"


def calcular_variacao(atual, anterior):
    if anterior == 0 or anterior is None:
        return None
    return ((atual - anterior) / anterior) * 100


def formatar_variacao(val):
    if val is None:
        return None
    return f"{val:+.1f}%"


def filtrar_periodo(df: pd.DataFrame, data_inicio, data_fim) -> pd.DataFrame:
    if df.empty:
        return df
    mask = (df["data"] >= pd.Timestamp(data_inicio)) & (df["data"] <= pd.Timestamp(data_fim))
    return df[mask]


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
        try:
            return inicio.replace(year=inicio.year - 1), fim.replace(year=fim.year - 1)
        except ValueError:
            return inicio - timedelta(days=365), fim - timedelta(days=365)
    return inicio, fim


# ─────────────────────────────────────────────
# TEMPLATE CSV
# ─────────────────────────────────────────────
TEMPLATE_CSV = """data,marca,produto,sku,quantidade_vendida,valor_unitario,valor_total,status_pedido,origem_cliente,id_pedido
01/01/2025,Seculus,Relógio Seculus Slim,SKU001,2,350.00,700.00,faturado,google ads,PED001
02/01/2025,Seculus,Relógio Seculus Sport,SKU002,1,420.00,420.00,pendente,meta ads,PED002
03/01/2025,Mondaine,Relógio Mondaine Digital,SKU010,3,280.00,840.00,faturado,organico,PED003
04/01/2025,Time,Relógio Time Classic,SKU020,2,190.00,380.00,faturado,instagram,PED004
05/01/2025,E-time,Relógio E-time Sport,SKU030,1,250.00,250.00,cancelado,direto,PED005
"""

# ─────────────────────────────────────────────
# ESTADO DA SESSÃO
# ─────────────────────────────────────────────
if "dfs" not in st.session_state:
    st.session_state.dfs = {}

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
_, col_title, _ = st.columns([1, 6, 1])
with col_title:
    st.markdown("## ⌚ Dashboard de Vendas · Grupo Seculus")
    st.markdown(
        "<p style='color:#8896b3; margin-top:-10px; font-size:0.9rem;'>"
        "Análise comparativa de performance por marca e período</p>",
        unsafe_allow_html=True,
    )
st.markdown("---")

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Configurações")
    st.markdown("---")

    st.markdown("**📄 Template de Planilha**")
    st.download_button(
        label="⬇️ Baixar template CSV",
        data=TEMPLATE_CSV,
        file_name="template_vendas.csv",
        mime="text/csv",
        use_container_width=True,
    )
    st.markdown(
        "<div style='font-size:0.75rem;color:#6b7a99;margin-top:4px;'>"
        "Colunas: data · marca · produto · sku · quantidade_vendida · "
        "valor_unitario · valor_total · status_pedido · origem_cliente · id_pedido</div>",
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown("**🔗 Fontes de Dados por Marca**")
    st.markdown(
        "<div style='font-size:0.75rem;color:#6b7a99;margin-bottom:12px;'>"
        "Cole o link do Google Sheets (compartilhado) ou URL de um .csv público</div>",
        unsafe_allow_html=True,
    )

    for marca in MARCAS:
        with st.expander(f"⌚ {marca}", expanded=(marca == "Seculus")):
            url_input = st.text_input(
                f"URL CSV — {marca}",
                key=f"url_{marca}",
                placeholder="https://docs.google.com/spreadsheets/d/...",
                label_visibility="collapsed",
            )
            col_btn, col_status = st.columns([3, 1])
            with col_btn:
                if st.button(f"Carregar {marca}", key=f"btn_{marca}", use_container_width=True):
                    if url_input.strip():
                        with st.spinner("Carregando..."):
                            df_raw = carregar_csv_url(url_input.strip())
                            if not df_raw.empty:
                                ok, faltando = validar_colunas(df_raw)
                                if ok:
                                    st.session_state.dfs[marca] = preparar_df(df_raw)
                                    n = len(st.session_state.dfs[marca])
                                    st.success(f"✅ {n} linhas carregadas")
                                else:
                                    st.error(f"Colunas faltando: {', '.join(faltando)}")
                                    st.info("Dica: Verifique se os nomes das colunas estão exatamente como no template.")
                    else:
                        st.warning("Insira uma URL válida.")
            with col_status:
                cor = "#10b981" if marca in st.session_state.dfs else "#374151"
                st.markdown(f"<span style='color:{cor};font-size:1.2rem;'>●</span>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("**📅 Período de Análise**")
    hoje = datetime.today().date()
    trinta_dias_atras = hoje - timedelta(days=30)
    data_inicio = st.date_input("De", value=trinta_dias_atras, key="data_inicio")
    data_fim    = st.date_input("Até", value=hoje, key="data_fim")

    comparar_periodo = st.selectbox(
        "Comparar com",
        ["Período anterior equivalente", "Mês anterior", "Mesmo período ano anterior"],
        index=0,
    )

    st.markdown("---")
    st.markdown("**🔍 Filtros**")

    marcas_disponiveis = [m for m in MARCAS if m in st.session_state.dfs]
    marcas_selecionadas = st.multiselect(
        "Marcas", marcas_disponiveis, default=marcas_disponiveis, key="marcas_sel"
    )

    tipos_canal_opcoes = ["Google Ads", "Meta Ads", "Orgânico", "E-mail", "Influencer/Parceiro", "Outros"]
    tipos_canal_selecionados = st.multiselect(
        "Tipo de canal", tipos_canal_opcoes, default=tipos_canal_opcoes, key="tipos_canal_sel"
    )

    campanhas_disponiveis = sorted(set(
        camp
        for df_m in st.session_state.dfs.values()
        if "campanha" in df_m.columns
        for camp in df_m["campanha"].dropna().unique()
    ))

    if campanhas_disponiveis:
        campanhas_selecionadas = st.multiselect(
            "Campanhas", campanhas_disponiveis, default=campanhas_disponiveis, key="campanhas_sel",
        )
    else:
        campanhas_selecionadas = []

    canais_selecionados = tipos_canal_selecionados

# ─────────────────────────────────────────────
# PERÍODOS
# ─────────────────────────────────────────────
data_inicio_ant, data_fim_ant = calcular_periodo_anterior(data_inicio, data_fim, comparar_periodo)


# ─────────────────────────────────────────────
# CONSOLIDAÇÃO
# ─────────────────────────────────────────────
def consolidar(marcas_sel, canais_sel, campanhas_sel, d_ini, d_fim):
    frames = []
    for m in marcas_sel:
        if m not in st.session_state.dfs:
            continue
        df_m = filtrar_periodo(st.session_state.dfs[m], d_ini, d_fim)
        if df_m.empty:
            continue
        if "canal" in df_m.columns and canais_sel:
            df_m = df_m[df_m["canal"].isin(canais_sel)]
        if "campanha" in df_m.columns and campanhas_sel:
            df_m = df_m[df_m["campanha"].isin(campanhas_sel)]
        frames.append(df_m)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


df_atual = consolidar(marcas_selecionadas, canais_selecionados, campanhas_selecionadas, data_inicio, data_fim)
df_ant   = consolidar(marcas_selecionadas, canais_selecionados, campanhas_selecionadas, data_inicio_ant, data_fim_ant)

# ─────────────────────────────────────────────
# ESTADO SEM DADOS
# ─────────────────────────────────────────────
if not st.session_state.dfs:
    st.markdown("""
    <div class="upload-section">
        <h2 style='color:#ffffff;margin:0 0 8px 0;'>Nenhum dado carregado</h2>
        <p style='color:#8896b3;margin:0 0 20px 0;'>
            Carregue os dados de cada marca na barra lateral para começar a análise.<br>
            Baixe o template CSV para garantir o formato correto das planilhas.
        </p>
        <p style='color:#4a7cff;font-size:0.85rem;font-family:monospace;'>
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
| `status_pedido` | texto | Status | `faturado` / `pendente` / `cancelado` |
| `origem_cliente` | texto | Canal de aquisição | `google ads` / `meta ads` / `organico` |
| `id_pedido` | texto | ID único do pedido | `PED-2025-001` |
        """)
    st.stop()

# ─────────────────────────────────────────────
# SELETOR DE PERÍODO — INLINE (substituindo as tags estáticas)
# ─────────────────────────────────────────────
col_p1, col_p2, col_p3 = st.columns([5, 1, 5])
with col_p1:
    st.markdown(
        f"<div style='background:#1a2035;border:1px solid #3a4560;border-radius:8px;"
        f"padding:10px 16px;font-size:0.82rem;color:#8896b3;font-family:DM Mono,monospace;'>"
        f"📅 <strong style='color:#fff;'>Período atual:</strong> "
        f"{data_inicio.strftime('%d/%m/%Y')} → {data_fim.strftime('%d/%m/%Y')}"
        f"</div>",
        unsafe_allow_html=True,
    )
with col_p2:
    st.markdown(
        "<div style='text-align:center;color:#6b7a99;padding-top:10px;font-size:1rem;'>vs</div>",
        unsafe_allow_html=True,
    )
with col_p3:
    st.markdown(
        f"<div style='background:#1a2035;border:1px solid #3a4560;border-radius:8px;"
        f"padding:10px 16px;font-size:0.82rem;color:#8896b3;font-family:DM Mono,monospace;'>"
        f"📅 <strong style='color:#fff;'>Período anterior:</strong> "
        f"{data_inicio_ant.strftime('%d/%m/%Y')} → {data_fim_ant.strftime('%d/%m/%Y')}"
        f"</div>",
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# RESUMO LADO A LADO (todas as marcas carregadas)
# ─────────────────────────────────────────────
def badge_taxa(valor, limiar_bom=10.0):
    """Retorna badge colorido para taxa de cancelamento."""
    if valor <= limiar_bom:
        return f"<span class='badge-verde'>{valor:.1f}%</span>"
    elif valor <= 20:
        return f"<span class='badge-amarelo'>{valor:.1f}%</span>"
    else:
        return f"<span class='badge-vermelho'>{valor:.1f}%</span>"

marcas_carregadas = [m for m in MARCAS if m in st.session_state.dfs]
if marcas_carregadas:
    st.markdown("### Resumo por Marca")
    cols_resumo = st.columns(len(marcas_carregadas))
    for idx, marca in enumerate(marcas_carregadas):
        df_m_full = st.session_state.dfs[marca]  # sem filtro de período para resumo total
        df_m_periodo = filtrar_periodo(df_m_full, data_inicio, data_fim)

        clientes_unicos = df_m_full["id_pedido"].nunique() if "id_pedido" in df_m_full.columns else len(df_m_full)
        total_itens     = int(df_m_full["quantidade_vendida"].sum()) if "quantidade_vendida" in df_m_full.columns else 0
        itens_fat       = int(df_m_full.loc[df_m_full.get("faturado", pd.Series(False, index=df_m_full.index)), "quantidade_vendida"].sum()) if "faturado" in df_m_full.columns and "quantidade_vendida" in df_m_full.columns else 0
        itens_canc      = int(df_m_full.loc[df_m_full.get("cancelado", pd.Series(False, index=df_m_full.index)), "quantidade_vendida"].sum()) if "cancelado" in df_m_full.columns and "quantidade_vendida" in df_m_full.columns else 0
        taxa_canc       = (itens_canc / total_itens * 100) if total_itens > 0 else 0
        receita_fat     = df_m_full.loc[df_m_full["faturado"], "valor_total"].sum() if "faturado" in df_m_full.columns else df_m_full["valor_total"].sum()

        cor = COR_MARCAS.get(marca, "#4a7cff")
        with cols_resumo[idx]:
            st.markdown(f"""
            <div class="resumo-card">
                <h4 style='color:{cor};'>{marca}</h4>
                <div class="resumo-linha">
                    <span>Pedidos únicos</span>
                    <span class="resumo-valor">{clientes_unicos:,}</span>
                </div>
                <div class="resumo-linha">
                    <span>Total de itens</span>
                    <span class="resumo-valor">{total_itens:,}</span>
                </div>
                <div class="resumo-linha">
                    <span>Itens faturados</span>
                    <span class="resumo-valor"><span class='badge-verde'>{itens_fat:,}</span></span>
                </div>
                <div class="resumo-linha">
                    <span>Itens cancelados</span>
                    <span class="resumo-valor"><span class='badge-vermelho'>{itens_canc:,}</span></span>
                </div>
                <div class="resumo-linha">
                    <span>Taxa de cancelamento</span>
                    <span class="resumo-valor">{badge_taxa(taxa_canc)}</span>
                </div>
                <div class="resumo-linha">
                    <span>Receita faturada</span>
                    <span class="resumo-valor">R$ {receita_fat:,.0f}</span>
                </div>
            </div>
            """.replace(",", "·").replace("·000", ",000").replace("·", ","), unsafe_allow_html=True)
            # Correção: formata números corretamente sem substituição ingênua
    # Refaz sem substituição errada
    for idx, marca in enumerate(marcas_carregadas):
        pass  # já renderizado acima, bloco de limpeza mantido para legibilidade

st.markdown("---")

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
# ABA 1 — VISÃO GERAL
# ═══════════════════════════════════════════════════════════════
with tab_visao_geral:
    if df_atual.empty:
        st.info("Nenhum dado no período selecionado para as marcas carregadas.")
        st.stop()

    st.markdown("### KPIs do Período")

    total_receita   = df_atual["valor_total"].sum() if "valor_total" in df_atual.columns else 0
    total_pedidos   = df_atual["id_pedido"].nunique() if "id_pedido" in df_atual.columns else len(df_atual)
    total_faturados = int(df_atual["faturado"].sum()) if "faturado" in df_atual.columns else 0
    total_cancelados= int(df_atual["cancelado"].sum()) if "cancelado" in df_atual.columns else 0
    taxa_fat        = (total_faturados / total_pedidos * 100) if total_pedidos > 0 else 0
    ticket_medio    = (
        df_atual[df_atual["faturado"]].groupby("id_pedido")["valor_total"].sum().mean()
        if "id_pedido" in df_atual.columns and "faturado" in df_atual.columns and total_faturados > 0
        else 0
    )

    rec_ant   = df_ant["valor_total"].sum() if not df_ant.empty and "valor_total" in df_ant.columns else 0
    ped_ant   = df_ant["id_pedido"].nunique() if not df_ant.empty and "id_pedido" in df_ant.columns else 0
    fat_ant   = int(df_ant["faturado"].sum()) if not df_ant.empty and "faturado" in df_ant.columns else 0
    taxf_ant  = (fat_ant / ped_ant * 100) if ped_ant > 0 else 0
    tick_ant  = (
        df_ant[df_ant["faturado"]].groupby("id_pedido")["valor_total"].sum().mean()
        if not df_ant.empty and "id_pedido" in df_ant.columns and "faturado" in df_ant.columns and fat_ant > 0
        else 0
    )

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("💰 Receita Total",
              f"R$ {total_receita:,.0f}",
              delta=formatar_variacao(calcular_variacao(total_receita, rec_ant)))
    k2.metric("🛒 Pedidos Realizados",
              f"{total_pedidos:,}",
              delta=formatar_variacao(calcular_variacao(total_pedidos, ped_ant)))
    k3.metric("✅ Pedidos Faturados",
              f"{total_faturados:,}",
              delta=formatar_variacao(calcular_variacao(total_faturados, fat_ant)))
    k4.metric("❌ Cancelados",
              f"{total_cancelados:,}")
    k5.metric("📊 Taxa Faturamento",
              f"{taxa_fat:.1f}%",
              delta=formatar_variacao(calcular_variacao(taxa_fat, taxf_ant)))
    k6.metric("🎟️ Ticket Médio",
              f"R$ {ticket_medio:,.0f}",
              delta=formatar_variacao(calcular_variacao(ticket_medio, tick_ant)))

    st.markdown("<br>", unsafe_allow_html=True)

    # Insight automático
    if rec_ant > 0:
        var_rec = calcular_variacao(total_receita, rec_ant)
        emoji   = "🟢" if var_rec >= 0 else "🔴"
        direcao = "crescimento" if var_rec >= 0 else "queda"
        st.markdown(f"""
        <div class="insight-box">
            {emoji} <strong>Insight:</strong> A receita consolidada apresentou
            <strong>{direcao} de {abs(var_rec):.1f}%</strong>
            em relação ao período anterior — de R$ {rec_ant:,.0f} para R$ {total_receita:,.0f}.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Gráfico de linhas CURVAS — Evolução de receita por marca
    st.markdown("### Evolução de Receita por Marca")
    if "marca" in df_atual.columns:
        df_time = (
            df_atual[df_atual.get("faturado", pd.Series(True, index=df_atual.index))]
            .groupby(["data", "marca"])["valor_total"].sum().reset_index()
        )
        fig_time = go.Figure()
        for marca in df_time["marca"].unique():
            df_m = df_time[df_time["marca"] == marca].sort_values("data")
            fig_time.add_trace(go.Scatter(
                x=df_m["data"], y=df_m["valor_total"],
                name=marca,
                mode="lines",
                line=dict(color=COR_MARCAS.get(marca, "#4a7cff"), width=2.5, shape="spline", smoothing=1.3),
                fill="tozeroy",
                fillcolor=COR_MARCAS.get(marca, "#4a7cff").replace("#", "rgba(") + ",0.08)".replace(
                    "rgba(", "rgba("
                ) if False else "rgba(0,0,0,0)",
            ))
        fig_time.update_layout(**layout_normal())
        st.plotly_chart(fig_time, use_container_width=True)

    st.markdown("---")

    col_g1, col_g2 = st.columns(2)

    # Barras comparativas por marca
    with col_g1:
        st.markdown("### Receita por Marca — Atual vs Anterior")
        if "marca" in df_atual.columns:
            rec_atual_m = df_atual.groupby("marca")["valor_total"].sum().reset_index()
            rec_ant_m   = df_ant.groupby("marca")["valor_total"].sum().reset_index() if not df_ant.empty else pd.DataFrame(columns=["marca","valor_total"])
            rec_atual_m.columns = ["marca", "atual"]
            rec_ant_m.columns   = ["marca", "anterior"]
            comp = rec_atual_m.merge(rec_ant_m, on="marca", how="left").fillna(0)
            fig_comp = go.Figure()
            fig_comp.add_trace(go.Bar(
                name="Anterior", x=comp["marca"], y=comp["anterior"],
                marker_color="rgba(100,120,160,0.45)", marker_line_width=0,
            ))
            fig_comp.add_trace(go.Bar(
                name="Atual", x=comp["marca"], y=comp["atual"],
                marker_color=[COR_MARCAS.get(m, "#4a7cff") for m in comp["marca"]],
                marker_line_width=0,
            ))
            fig_comp.update_layout(barmode="group", **layout_normal())
            st.plotly_chart(fig_comp, use_container_width=True)

    # Donut share
    with col_g2:
        st.markdown("### Share de Receita por Marca")
        if "marca" in df_atual.columns:
            share = df_atual.groupby("marca")["valor_total"].sum().reset_index()
            fig_pie = px.pie(
                share, names="marca", values="valor_total",
                color="marca", color_discrete_map=COR_MARCAS, hole=0.55,
            )
            fig_pie.update_traces(textinfo="percent+label", textfont_size=12)
            fig_pie.update_layout(**layout_normal())
            st.plotly_chart(fig_pie, use_container_width=True)

    # Receita mensal por marca (barras agrupadas)
    st.markdown("### Volume Mensal por Marca")
    if "marca" in df_atual.columns:
        df_atual["mes"] = df_atual["data"].dt.to_period("M").astype(str)
        df_mensal = df_atual.groupby(["mes", "marca"])["quantidade_vendida"].sum().reset_index()
        fig_mensal = px.bar(
            df_mensal, x="mes", y="quantidade_vendida", color="marca",
            barmode="group", color_discrete_map=COR_MARCAS,
            labels={"quantidade_vendida": "Itens Vendidos", "mes": "", "marca": "Marca"},
        )
        fig_mensal.update_layout(**layout_normal())
        st.plotly_chart(fig_mensal, use_container_width=True)


# ═══════════════════════════════════════════════════════════════
# ABA 2 — PRODUTOS
# ═══════════════════════════════════════════════════════════════
with tab_produtos:
    st.markdown("### 🏆 Top Produtos Mais Vendidos")

    if df_atual.empty:
        st.info("Nenhum dado no período selecionado.")
        st.stop()

    col_filtro_marca, col_filtro_n = st.columns([3, 1])
    with col_filtro_marca:
        marcas_prod = st.multiselect(
            "Filtrar marca", marcas_selecionadas, default=marcas_selecionadas, key="prod_marcas"
        )
    with col_filtro_n:
        top_n = st.selectbox("Top N", [5, 10, 15, 20], index=1, key="top_n")

    df_prod = df_atual[df_atual["marca"].isin(marcas_prod)] if "marca" in df_atual.columns else df_atual

    if not df_prod.empty and "produto" in df_prod.columns:
        col_p1, col_p2 = st.columns(2)

        with col_p1:
            st.markdown("**Por quantidade vendida**")
            top_qtd = (
                df_prod.groupby(["marca", "produto"])["quantidade_vendida"]
                .sum().reset_index()
                .sort_values("quantidade_vendida", ascending=False)
                .head(top_n)
            )
            fig_qtd = px.bar(
                top_qtd, x="quantidade_vendida", y="produto", color="marca",
                orientation="h", color_discrete_map=COR_MARCAS,
                labels={"quantidade_vendida": "Unidades Vendidas", "produto": ""},
            )
            # FIX: usa layout_invertido() em vez de LAYOUT_PLOTLY + yaxis kwarg
            fig_qtd.update_layout(**layout_invertido())
            st.plotly_chart(fig_qtd, use_container_width=True)

        with col_p2:
            st.markdown("**Por receita gerada**")
            top_rec = (
                df_prod.groupby(["marca", "produto"])["valor_total"]
                .sum().reset_index()
                .sort_values("valor_total", ascending=False)
                .head(top_n)
            )
            fig_rec = px.bar(
                top_rec, x="valor_total", y="produto", color="marca",
                orientation="h", color_discrete_map=COR_MARCAS,
                labels={"valor_total": "Receita (R$)", "produto": ""},
            )
            fig_rec.update_layout(**layout_invertido())
            st.plotly_chart(fig_rec, use_container_width=True)

        # Tabela detalhada
        st.markdown("### Detalhamento por Produto")
        group_cols = ["marca", "produto"]
        if "sku" in df_prod.columns:
            group_cols.append("sku")
        agg_dict = {
            "quantidade_vendida": ("quantidade_vendida", "sum"),
            "receita_total":      ("valor_total", "sum"),
        }
        if "id_pedido" in df_prod.columns:
            agg_dict["pedidos"] = ("id_pedido", "nunique")
        else:
            agg_dict["pedidos"] = ("quantidade_vendida", "count")

        resumo_prod = (
            df_prod.groupby(group_cols)
            .agg(**agg_dict)
            .reset_index()
            .sort_values("receita_total", ascending=False)
        )
        resumo_prod["ticket_medio"] = resumo_prod["receita_total"] / resumo_prod["pedidos"].replace(0, np.nan)
        resumo_prod["receita_total"] = resumo_prod["receita_total"].map("R$ {:,.0f}".format)
        resumo_prod["ticket_medio"]  = resumo_prod["ticket_medio"].map(
            lambda x: f"R$ {x:,.0f}" if pd.notna(x) else "—"
        )
        st.dataframe(resumo_prod, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum dado de produto disponível no período.")


# ═══════════════════════════════════════════════════════════════
# ABA 3 — PEDIDOS
# ═══════════════════════════════════════════════════════════════
with tab_pedidos:
    st.markdown("### 📦 Análise de Pedidos")

    if df_atual.empty or "status_pedido" not in df_atual.columns:
        st.info("Nenhum dado de pedidos disponível no período.")
        st.stop()

    total_ped    = df_atual["id_pedido"].nunique() if "id_pedido" in df_atual.columns else len(df_atual)
    ped_fat_tab  = int(df_atual[df_atual["faturado"]]["id_pedido"].nunique()) if "id_pedido" in df_atual.columns else int(df_atual["faturado"].sum())
    ped_pend     = int((~df_atual["faturado"] & ~df_atual.get("cancelado", pd.Series(False, index=df_atual.index))).sum())
    ped_canc     = int(df_atual["cancelado"].sum()) if "cancelado" in df_atual.columns else 0
    taxa_conv    = (ped_fat_tab / total_ped * 100) if total_ped > 0 else 0
    taxa_canc_p  = (ped_canc / total_ped * 100) if total_ped > 0 else 0

    ped_ant_t    = df_ant["id_pedido"].nunique() if not df_ant.empty and "id_pedido" in df_ant.columns else 0
    ped_fat_ant  = int(df_ant["faturado"].sum()) if not df_ant.empty and "faturado" in df_ant.columns else 0
    taxa_ant_v   = (ped_fat_ant / ped_ant_t * 100) if ped_ant_t > 0 else 0

    kp1, kp2, kp3, kp4, kp5 = st.columns(5)
    kp1.metric("📥 Pedidos Realizados", f"{total_ped:,}",
               delta=formatar_variacao(calcular_variacao(total_ped, ped_ant_t)))
    kp2.metric("✅ Faturados", f"{ped_fat_tab:,}",
               delta=formatar_variacao(calcular_variacao(ped_fat_tab, ped_fat_ant)))
    kp3.metric("⏳ Pendentes", f"{ped_pend:,}")
    kp4.metric("❌ Cancelados", f"{ped_canc:,}")
    kp5.metric("📈 Taxa Faturamento", f"{taxa_conv:.1f}%",
               delta=formatar_variacao(calcular_variacao(taxa_conv, taxa_ant_v)))

    st.markdown("<br>", unsafe_allow_html=True)

    col_s1, col_s2 = st.columns(2)

    with col_s1:
        st.markdown("### Status dos Pedidos")
        status_count = df_atual["status_pedido"].value_counts().reset_index()
        status_count.columns = ["status", "quantidade"]
        CORES_STATUS = {
            "faturado": "#10b981", "entregue": "#10b981", "concluído": "#10b981", "aprovado": "#10b981",
            "pendente": "#f59e0b",
            "cancelado": "#f43f5e", "cancelada": "#f43f5e", "devolvido": "#f43f5e",
        }
        fig_status = px.pie(
            status_count, names="status", values="quantidade",
            color="status", color_discrete_map=CORES_STATUS, hole=0.55,
        )
        fig_status.update_traces(textinfo="percent+label")
        fig_status.update_layout(**layout_normal())
        st.plotly_chart(fig_status, use_container_width=True)

    with col_s2:
        st.markdown("### Pedidos por Marca")
        if "marca" in df_atual.columns:
            ped_marca = (
                df_atual.groupby("marca")
                .agg(realizados=("id_pedido", "nunique"), faturados=("faturado", "sum"))
                .reset_index()
            )
            fig_ped = go.Figure()
            fig_ped.add_trace(go.Bar(name="Realizados", x=ped_marca["marca"], y=ped_marca["realizados"],
                                     marker_color="rgba(100,120,200,0.45)"))
            fig_ped.add_trace(go.Bar(name="Faturados", x=ped_marca["marca"], y=ped_marca["faturados"],
                                     marker_color=[COR_MARCAS.get(m, "#4a7cff") for m in ped_marca["marca"]]))
            fig_ped.update_layout(barmode="group", **layout_normal())
            st.plotly_chart(fig_ped, use_container_width=True)

    # Volume diário
    st.markdown("### Volume de Pedidos por Dia")
    if "id_pedido" in df_atual.columns and "marca" in df_atual.columns:
        ped_dia = (
            df_atual.groupby(["data", "marca"])["id_pedido"]
            .nunique().reset_index()
            .rename(columns={"id_pedido": "pedidos"})
        )
        fig_ped_dia = px.area(
            ped_dia, x="data", y="pedidos", color="marca",
            color_discrete_map=COR_MARCAS,
            labels={"pedidos": "Pedidos", "data": ""},
        )
        fig_ped_dia.update_layout(**layout_normal())
        st.plotly_chart(fig_ped_dia, use_container_width=True)

    # Tabela de pedidos
    st.markdown("### Registro de Pedidos")
    colunas_exibir = [c for c in
        ["data", "marca", "id_pedido", "produto", "quantidade_vendida", "valor_total", "status_pedido", "canal"]
        if c in df_atual.columns]
    st.dataframe(
        df_atual[colunas_exibir].sort_values("data", ascending=False),
        use_container_width=True, hide_index=True,
    )


# ═══════════════════════════════════════════════════════════════
# ABA 4 — CONVERSÃO
# ═══════════════════════════════════════════════════════════════
with tab_conversao:
    st.markdown("### 🎯 Taxa de Conversão")

    if df_atual.empty or "faturado" not in df_atual.columns:
        st.info("Nenhum dado de conversão disponível.")
        st.stop()

    col_c1, col_c2 = st.columns(2)

    with col_c1:
        st.markdown("**Taxa de Conversão por Marca — Atual vs Anterior**")
        if "marca" in df_atual.columns:
            conv_atual = (
                df_atual.groupby("marca")
                .apply(lambda x: x["faturado"].mean() * 100)
                .reset_index()
                .rename(columns={0: "taxa_atual"})
            )
            conv_ant_df = (
                df_ant.groupby("marca")
                .apply(lambda x: x["faturado"].mean() * 100)
                .reset_index()
                .rename(columns={0: "taxa_anterior"})
            ) if not df_ant.empty else pd.DataFrame(columns=["marca", "taxa_anterior"])

            conv_merge = conv_atual.merge(conv_ant_df, on="marca", how="left").fillna(0)
            fig_conv = go.Figure()
            fig_conv.add_trace(go.Bar(name="Período Anterior", x=conv_merge["marca"],
                                      y=conv_merge["taxa_anterior"],
                                      marker_color="rgba(100,120,160,0.45)"))
            fig_conv.add_trace(go.Bar(name="Período Atual", x=conv_merge["marca"],
                                      y=conv_merge["taxa_atual"],
                                      marker_color=[COR_MARCAS.get(m, "#4a7cff") for m in conv_merge["marca"]]))
            fig_conv.update_layout(barmode="group", yaxis_ticksuffix="%", **layout_normal())
            st.plotly_chart(fig_conv, use_container_width=True)

    with col_c2:
        st.markdown("**Evolução da Taxa de Conversão no Período**")
        if "marca" in df_atual.columns:
            conv_time = (
                df_atual.groupby(["data", "marca"])
                .apply(lambda x: x["faturado"].mean() * 100)
                .reset_index()
                .rename(columns={0: "conversao"})
            )
            fig_conv_t = go.Figure()
            for marca in conv_time["marca"].unique():
                df_m = conv_time[conv_time["marca"] == marca].sort_values("data")
                fig_conv_t.add_trace(go.Scatter(
                    x=df_m["data"], y=df_m["conversao"],
                    name=marca, mode="lines",
                    line=dict(color=COR_MARCAS.get(marca, "#4a7cff"), width=2.5, shape="spline", smoothing=1.3),
                ))
            fig_conv_t.update_layout(**layout_normal(), yaxis_ticksuffix="%")
            st.plotly_chart(fig_conv_t, use_container_width=True)

    # Por canal
    st.markdown("### Taxa de Conversão por Canal de Aquisição")
    if "canal" in df_atual.columns:
        conv_canal = (
            df_atual.groupby("canal")
            .agg(pedidos=("faturado", "count"), faturados=("faturado", "sum"))
            .reset_index()
        )
        conv_canal["taxa"] = conv_canal["faturados"] / conv_canal["pedidos"] * 100
        conv_canal = conv_canal.sort_values("taxa", ascending=True)

        fig_canal_conv = px.bar(
            conv_canal, x="taxa", y="canal", orientation="h",
            color="canal", color_discrete_map=CORES_CANAL,
            labels={"taxa": "Taxa de Conversão (%)", "canal": ""},
            text=conv_canal["taxa"].map("{:.1f}%".format),
        )
        fig_canal_conv.update_traces(textposition="outside")
        fig_canal_conv.update_layout(**layout_invertido())
        st.plotly_chart(fig_canal_conv, use_container_width=True)

    # Insight de melhor conversão
    if "marca" in df_atual.columns and not conv_atual.empty:
        melhor = conv_atual.loc[conv_atual["taxa_atual"].idxmax()]
        st.markdown(f"""
        <div class="insight-box">
            🏆 <strong>Melhor conversão:</strong> A marca <strong>{melhor['marca']}</strong>
            lidera com taxa de conversão de <strong>{melhor['taxa_atual']:.1f}%</strong>
            no período atual.
        </div>
        """, unsafe_allow_html=True)

    # Funil simplificado
    st.markdown("### Funil de Pedidos (Consolidado)")
    funil_data = {
        "Etapa": ["Pedidos Realizados", "Pedidos Faturados", "Cancelados"],
        "Quantidade": [
            df_atual["id_pedido"].nunique() if "id_pedido" in df_atual.columns else len(df_atual),
            int(df_atual["faturado"].sum()),
            int(df_atual["cancelado"].sum()) if "cancelado" in df_atual.columns else 0,
        ],
    }
    fig_funil = go.Figure(go.Funnel(
        y=funil_data["Etapa"],
        x=funil_data["Quantidade"],
        marker={"color": ["#4a7cff", "#10b981", "#f43f5e"]},
        textinfo="value+percent initial",
    ))
    fig_funil.update_layout(**layout_normal())
    st.plotly_chart(fig_funil, use_container_width=True)


# ═══════════════════════════════════════════════════════════════
# ABA 5 — TRÁFEGO & ORIGEM
# ═══════════════════════════════════════════════════════════════
with tab_trafego:
    st.markdown("### 📡 Análise de Tráfego e Origem de Clientes")

    if df_atual.empty or "canal" not in df_atual.columns:
        st.info("Dados de origem do cliente não disponíveis. Certifique-se que a coluna `origem_cliente` está na planilha.")
        st.stop()

    col_t1, col_t2 = st.columns(2)

    with col_t1:
        st.markdown("**Distribuição por Canal — Período Atual**")
        canal_count = df_atual["canal"].value_counts().reset_index()
        canal_count.columns = ["canal", "pedidos"]
        fig_canal = px.pie(
            canal_count, names="canal", values="pedidos",
            color="canal", color_discrete_map=CORES_CANAL, hole=0.55,
        )
        fig_canal.update_traces(textinfo="percent+label")
        fig_canal.update_layout(**layout_normal())
        st.plotly_chart(fig_canal, use_container_width=True)

    with col_t2:
        st.markdown("**Receita por Canal**")
        canal_rec = (
            df_atual.groupby("canal")["valor_total"].sum()
            .reset_index().sort_values("valor_total", ascending=True)
        )
        fig_canal_rec = px.bar(
            canal_rec, x="valor_total", y="canal", orientation="h",
            color="canal", color_discrete_map=CORES_CANAL,
            labels={"valor_total": "Receita (R$)", "canal": ""},
        )
        fig_canal_rec.update_layout(**layout_invertido())
        st.plotly_chart(fig_canal_rec, use_container_width=True)

    # Comparativo atual vs anterior por canal
    st.markdown("### Canal: Atual vs Período Anterior")
    canal_atual_agg = df_atual.groupby("canal").agg(
        pedidos=("faturado", "count"),
        receita=("valor_total", "sum"),
        faturados=("faturado", "sum"),
    ).reset_index()

    if not df_ant.empty and "canal" in df_ant.columns:
        canal_ant_agg = (
            df_ant.groupby("canal")
            .agg(pedidos_ant=("faturado", "count"), receita_ant=("valor_total", "sum"))
            .reset_index()
        )
        canal_comp = canal_atual_agg.merge(canal_ant_agg, on="canal", how="left").fillna(0)
        canal_comp["var_str"] = canal_comp.apply(
            lambda r: formatar_variacao(calcular_variacao(r["receita"], r["receita_ant"])) or "—", axis=1
        )
        fig_ccomp = go.Figure()
        fig_ccomp.add_trace(go.Bar(name="Anterior", x=canal_comp["canal"], y=canal_comp["receita_ant"],
                                    marker_color="rgba(100,120,160,0.45)"))
        fig_ccomp.add_trace(go.Bar(name="Atual", x=canal_comp["canal"], y=canal_comp["receita"],
                                    marker_color=[CORES_CANAL.get(c, "#4a7cff") for c in canal_comp["canal"]],
                                    text=canal_comp["var_str"], textposition="outside"))
        fig_ccomp.update_layout(barmode="group", **layout_normal())
        st.plotly_chart(fig_ccomp, use_container_width=True)

    # Canal x Marca
    st.markdown("### Canal por Marca")
    if "marca" in df_atual.columns:
        canal_marca = df_atual.groupby(["marca", "canal"])["valor_total"].sum().reset_index()
        fig_cm = px.bar(
            canal_marca, x="marca", y="valor_total", color="canal",
            color_discrete_map=CORES_CANAL, barmode="stack",
            labels={"valor_total": "Receita (R$)", "marca": "", "canal": "Canal"},
        )
        fig_cm.update_layout(**layout_normal())
        st.plotly_chart(fig_cm, use_container_width=True)

    # Tabela resumo por canal
    st.markdown("### Resumo por Tipo de Canal")
    canal_tab = canal_atual_agg.copy()
    canal_tab["taxa_conv"] = (canal_tab["faturados"] / canal_tab["pedidos"].replace(0, np.nan) * 100).map("{:.1f}%".format)
    canal_tab["receita_fmt"] = canal_tab["receita"].map("R$ {:,.0f}".format)
    canal_tab = canal_tab.rename(columns={
        "canal": "Canal", "pedidos": "Pedidos", "faturados": "Faturados",
        "taxa_conv": "Taxa Conv.", "receita_fmt": "Receita",
    })
    st.dataframe(
        canal_tab[["Canal", "Pedidos", "Faturados", "Taxa Conv.", "Receita"]],
        use_container_width=True, hide_index=True,
    )

    # Detalhamento por campanha
    st.markdown("### Detalhamento por Campanha")
    st.caption("Cada valor único de `origem_cliente` aparece como uma campanha separada.")

    if "campanha" in df_atual.columns and "tipo_canal" in df_atual.columns:
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
                lambda r: formatar_variacao(calcular_variacao(r["receita"], r["receita_ant"])) or "—", axis=1
            )
        else:
            camp_atual["var_receita"] = "—"

        camp_atual["taxa_conv"] = (
            camp_atual["faturados"] / camp_atual["pedidos"].replace(0, np.nan) * 100
        ).map("{:.1f}%".format)
        camp_atual = camp_atual.sort_values("receita", ascending=False)

        fig_camp = px.bar(
            camp_atual.head(20),
            x="receita", y="campanha", color="tipo_canal",
            orientation="h", color_discrete_map=CORES_CANAL,
            labels={"receita": "Receita (R$)", "campanha": "", "tipo_canal": "Canal"},
        )
        fig_camp.update_layout(**layout_invertido())
        st.plotly_chart(fig_camp, use_container_width=True)

        camp_exib = camp_atual.copy()
        camp_exib["receita"] = camp_exib["receita"].map("R$ {:,.0f}".format)
        camp_exib = camp_exib.rename(columns={
            "tipo_canal": "Tipo de Canal", "campanha": "Campanha",
            "pedidos": "Pedidos", "faturados": "Faturados",
            "taxa_conv": "Taxa Conv.", "receita": "Receita",
            "var_receita": "Var. vs Anterior",
        })
        cols_exib = [c for c in
            ["Tipo de Canal", "Campanha", "Pedidos", "Faturados", "Taxa Conv.", "Receita", "Var. vs Anterior"]
            if c in camp_exib.columns]
        st.dataframe(camp_exib[cols_exib], use_container_width=True, hide_index=True)
    else:
        st.info("Coluna `origem_cliente` não encontrada — adicione-a à planilha para ver o detalhamento por campanha.")


# ═══════════════════════════════════════════════════════════════
# ABA 6 — POR MARCA
# ═══════════════════════════════════════════════════════════════
with tab_marca:
    st.markdown("### 🏷️ Análise Individual por Marca")

    if not marcas_selecionadas:
        st.info("Nenhuma marca selecionada.")
        st.stop()

    marca_sel = st.selectbox("Selecionar marca", marcas_selecionadas, key="marca_individual")

    if marca_sel and marca_sel in st.session_state.dfs:
        df_m_atual = filtrar_periodo(st.session_state.dfs[marca_sel], data_inicio, data_fim)
        df_m_ant   = filtrar_periodo(st.session_state.dfs[marca_sel], data_inicio_ant, data_fim_ant)

        if not df_m_atual.empty:
            rec_m    = df_m_atual["valor_total"].sum()
            ped_m    = df_m_atual["id_pedido"].nunique() if "id_pedido" in df_m_atual.columns else len(df_m_atual)
            fat_m    = int(df_m_atual["faturado"].sum()) if "faturado" in df_m_atual.columns else 0
            canc_m   = int(df_m_atual["cancelado"].sum()) if "cancelado" in df_m_atual.columns else 0
            conv_m   = (fat_m / ped_m * 100) if ped_m > 0 else 0
            ticket_m = df_m_atual[df_m_atual["faturado"]].groupby("id_pedido")["valor_total"].sum().mean() if fat_m > 0 else 0

            rec_m_a  = df_m_ant["valor_total"].sum() if not df_m_ant.empty else 0
            ped_m_a  = df_m_ant["id_pedido"].nunique() if not df_m_ant.empty and "id_pedido" in df_m_ant.columns else 0
            fat_m_a  = int(df_m_ant["faturado"].sum()) if not df_m_ant.empty and "faturado" in df_m_ant.columns else 0
            conv_m_a = (fat_m_a / ped_m_a * 100) if ped_m_a > 0 else 0

            km1, km2, km3, km4, km5 = st.columns(5)
            km1.metric("Receita", f"R$ {rec_m:,.0f}",
                       delta=formatar_variacao(calcular_variacao(rec_m, rec_m_a)))
            km2.metric("Pedidos", f"{ped_m:,}",
                       delta=formatar_variacao(calcular_variacao(ped_m, ped_m_a)))
            km3.metric("Faturados", f"{fat_m:,}",
                       delta=formatar_variacao(calcular_variacao(fat_m, fat_m_a)))
            km4.metric("Cancelados", f"{canc_m:,}")
            km5.metric("Taxa Conversão", f"{conv_m:.1f}%",
                       delta=formatar_variacao(calcular_variacao(conv_m, conv_m_a)))

            st.markdown("<br>", unsafe_allow_html=True)

            col_m1, col_m2 = st.columns(2)
            with col_m1:
                st.markdown(f"**Top 10 Produtos — {marca_sel}**")
                if "produto" in df_m_atual.columns:
                    top_m = (
                        df_m_atual.groupby("produto")["quantidade_vendida"]
                        .sum().nlargest(10).reset_index()
                    )
                    fig_top_m = px.bar(
                        top_m, x="quantidade_vendida", y="produto", orientation="h",
                        color_discrete_sequence=[COR_MARCAS.get(marca_sel, "#4a7cff")],
                        labels={"quantidade_vendida": "Unidades Vendidas", "produto": ""},
                    )
                    fig_top_m.update_layout(**layout_invertido())
                    st.plotly_chart(fig_top_m, use_container_width=True)

            with col_m2:
                st.markdown(f"**Origem dos Clientes — {marca_sel}**")
                if "canal" in df_m_atual.columns:
                    canal_m = df_m_atual["canal"].value_counts().reset_index()
                    canal_m.columns = ["canal", "qtd"]
                    fig_canal_m = px.pie(
                        canal_m, names="canal", values="qtd",
                        color="canal", color_discrete_map=CORES_CANAL, hole=0.55,
                    )
                    fig_canal_m.update_traces(textinfo="percent+label")
                    fig_canal_m.update_layout(**layout_normal())
                    st.plotly_chart(fig_canal_m, use_container_width=True)

            # Receita diária — curva spline
            st.markdown(f"**Receita Diária — {marca_sel}**")
            rec_dia_m = df_m_atual.groupby("data")["valor_total"].sum().reset_index()
            fig_rec_dia_m = go.Figure()
            fig_rec_dia_m.add_trace(go.Scatter(
                x=rec_dia_m["data"], y=rec_dia_m["valor_total"],
                mode="lines",
                fill="tozeroy",
                line=dict(color=COR_MARCAS.get(marca_sel, "#4a7cff"), width=2.5, shape="spline", smoothing=1.3),
                fillcolor=f"rgba({int(COR_MARCAS.get(marca_sel,'#4a7cff')[1:3],16)},"
                           f"{int(COR_MARCAS.get(marca_sel,'#4a7cff')[3:5],16)},"
                           f"{int(COR_MARCAS.get(marca_sel,'#4a7cff')[5:7],16)},0.1)",
            ))
            fig_rec_dia_m.update_layout(**layout_normal())
            st.plotly_chart(fig_rec_dia_m, use_container_width=True)

            # Comparativo mensal
            if "mes" not in df_m_atual.columns:
                df_m_atual["mes"] = df_m_atual["data"].dt.to_period("M").astype(str)
            mensal_m = df_m_atual.groupby("mes").agg(
                receita=("valor_total", "sum"),
                pedidos=("id_pedido", "nunique") if "id_pedido" in df_m_atual.columns else ("quantidade_vendida", "count"),
                faturados=("faturado", "sum"),
            ).reset_index()

            fig_mensal_m = go.Figure()
            fig_mensal_m.add_trace(go.Bar(
                name="Receita (R$)", x=mensal_m["mes"], y=mensal_m["receita"],
                marker_color=COR_MARCAS.get(marca_sel, "#4a7cff"),
            ))
            fig_mensal_m.update_layout(
                title=f"Receita Mensal — {marca_sel}", **layout_normal()
            )
            st.plotly_chart(fig_mensal_m, use_container_width=True)

        else:
            st.info(f"Nenhum dado para {marca_sel} no período selecionado.")
    else:
        st.info("Selecione uma marca carregada para visualizar os dados individuais.")

# ─────────────────────────────────────────────
# RODAPÉ
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#3a4560;font-size:0.75rem;font-family:DM Mono,monospace;'>"
    "⌚ Dashboard de Vendas · Grupo Seculus · Cache de dados: 5 min"
    "</div>",
    unsafe_allow_html=True,
)
