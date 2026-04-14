import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import StringIO
import requests
from datetime import datetime, timedelta
import numpy as np

# ─────────────────────────────────────────────
# PÁGINA
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard · Grupo Seculus",
    page_icon="⌚",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
# ESTILOS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@400;500&family=DM+Sans:wght@300;400;500&display=swap');

*, html, body { box-sizing: border-box; }
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

/* ── App background ── */
.stApp { background: #0a0b0f; color: #e2e4ea; }
[data-testid="stAppViewContainer"] { background: #0a0b0f; }
[data-testid="stHeader"] { background: transparent; }
section[data-testid="stSidebar"] { display: none !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #0a0b0f; }
::-webkit-scrollbar-thumb { background: #2a2d3a; border-radius: 4px; }

/* ── Top navigation bar ── */
.nav-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 18px 32px;
    background: rgba(14,15,20,0.95);
    border-bottom: 1px solid #1e2030;
    backdrop-filter: blur(12px);
    position: sticky;
    top: 0;
    z-index: 999;
    margin: -1rem -1rem 0 -1rem;
}
.nav-logo {
    font-family: 'Syne', sans-serif;
    font-size: 1.1rem;
    font-weight: 800;
    color: #fff;
    letter-spacing: -0.02em;
    display: flex;
    align-items: center;
    gap: 10px;
}
.nav-logo span { color: #6366f1; }
.nav-tabs {
    display: flex;
    gap: 4px;
    background: #13141a;
    border: 1px solid #1e2030;
    border-radius: 10px;
    padding: 4px;
}
.nav-tab {
    padding: 7px 18px;
    border-radius: 7px;
    font-size: .82rem;
    font-weight: 500;
    color: #6b7280;
    cursor: pointer;
    transition: all .2s;
    border: none;
    background: transparent;
    font-family: 'DM Sans', sans-serif;
    white-space: nowrap;
}
.nav-tab:hover { color: #e2e4ea; }
.nav-tab.active {
    background: #1e2030;
    color: #fff;
    box-shadow: 0 1px 4px rgba(0,0,0,.4);
}
.nav-right {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: .75rem;
    font-family: 'IBM Plex Mono', monospace;
    color: #3d4155;
}
.nav-dot { width: 6px; height: 6px; background: #22c55e; border-radius: 50%; display: inline-block; }

/* ── Page header ── */
.page-header {
    padding: 36px 0 24px 0;
}
.page-title {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    color: #fff;
    margin: 0;
    letter-spacing: -0.03em;
}
.page-subtitle {
    font-size: .85rem;
    color: #4b5268;
    margin-top: 4px;
    font-family: 'IBM Plex Mono', monospace;
}

/* ── Period badge ── */
.period-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: #13141a;
    border: 1px solid #1e2030;
    border-radius: 8px;
    padding: 8px 14px;
    font-size: .78rem;
    font-family: 'IBM Plex Mono', monospace;
    color: #6b7280;
}
.period-badge strong { color: #e2e4ea; }
.period-sep { color: #2a2d3a; }

/* ── KPI Cards ── */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 14px;
    margin: 20px 0;
}
.kpi-card {
    background: #0e0f14;
    border: 1px solid #1a1c28;
    border-radius: 14px;
    padding: 22px 24px;
    position: relative;
    overflow: hidden;
    transition: border-color .2s, transform .15s;
}
.kpi-card:hover { border-color: #2d3050; transform: translateY(-1px); }
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: var(--accent, #6366f1);
    opacity: .6;
}
.kpi-label {
    font-size: .72rem;
    font-weight: 500;
    color: #4b5268;
    text-transform: uppercase;
    letter-spacing: .1em;
    margin-bottom: 10px;
}
.kpi-value {
    font-family: 'Syne', sans-serif;
    font-size: 1.75rem;
    font-weight: 700;
    color: #fff;
    letter-spacing: -0.03em;
    margin-bottom: 6px;
}
.kpi-delta {
    font-family: 'IBM Plex Mono', monospace;
    font-size: .72rem;
}
.kpi-delta.pos { color: #22c55e; }
.kpi-delta.neg { color: #ef4444; }
.kpi-delta.neu { color: #4b5268; }

/* ── Section headers ── */
.section-label {
    font-family: 'Syne', sans-serif;
    font-size: .72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: .15em;
    color: #4b5268;
    margin: 32px 0 14px 0;
    display: flex;
    align-items: center;
    gap: 10px;
}
.section-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: #1a1c28;
}

/* ── Platform pills ── */
.platform-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: .75rem;
    font-weight: 600;
    font-family: 'IBM Plex Mono', monospace;
}
.pill-ec  { background: #1a1f3a; color: #818cf8; border: 1px solid #2d3468; }
.pill-mp  { background: #1a2e1a; color: #4ade80; border: 1px solid #2d4a2d; }

/* ── Chart containers ── */
.chart-card {
    background: #0e0f14;
    border: 1px solid #1a1c28;
    border-radius: 14px;
    padding: 22px;
    margin-bottom: 14px;
}
.chart-title {
    font-family: 'Syne', sans-serif;
    font-size: .88rem;
    font-weight: 600;
    color: #9ca3b8;
    margin-bottom: 16px;
    text-transform: uppercase;
    letter-spacing: .06em;
}

/* ── Upload area ── */
.upload-area {
    background: #0e0f14;
    border: 1px dashed #2a2d3a;
    border-radius: 14px;
    padding: 32px;
    text-align: center;
    margin: 10px 0;
}
.upload-title {
    font-family: 'Syne', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    color: #fff;
    margin-bottom: 6px;
}
.upload-sub {
    font-size: .82rem;
    color: #4b5268;
    font-family: 'IBM Plex Mono', monospace;
}

/* ── Insight box ── */
.insight {
    background: #0d1020;
    border-left: 2px solid #6366f1;
    border-radius: 0 10px 10px 0;
    padding: 12px 16px;
    margin: 8px 0;
    font-size: .85rem;
    color: #9ba3c0;
}
.alert-r {
    background: #130c0c;
    border-left: 2px solid #ef4444;
    border-radius: 0 10px 10px 0;
    padding: 12px 16px;
    margin: 6px 0;
    font-size: .82rem;
    color: #fca5a5;
}
.alert-y {
    background: #130f08;
    border-left: 2px solid #f59e0b;
    border-radius: 0 10px 10px 0;
    padding: 12px 16px;
    margin: 6px 0;
    font-size: .82rem;
    color: #fde68a;
}

/* ── Data table overrides ── */
[data-testid="stDataFrame"] {
    border: 1px solid #1a1c28 !important;
    border-radius: 10px !important;
}
iframe { border-radius: 10px; }

/* ── Metric overrides ── */
[data-testid="stMetric"] {
    background: #0e0f14;
    border: 1px solid #1a1c28;
    border-radius: 12px;
    padding: 16px 20px;
}
[data-testid="stMetricLabel"] { color: #4b5268 !important; font-size: .72rem !important; text-transform: uppercase; letter-spacing: .08em; }
[data-testid="stMetricValue"] { color: #fff !important; font-family: 'Syne', sans-serif !important; font-size: 1.6rem !important; font-weight: 700 !important; }

/* ── Tab bar (streamlit native) ── */
[data-baseweb="tab-list"] { background: transparent !important; border-bottom: 1px solid #1a1c28 !important; gap: 0; }
[data-baseweb="tab"] { color: #4b5268 !important; font-weight: 500 !important; font-family: 'DM Sans', sans-serif !important; padding: 10px 20px !important; }
[aria-selected="true"] { color: #fff !important; border-bottom: 2px solid #6366f1 !important; }

/* ── Divider ── */
hr { border-color: #1a1c28 !important; }

/* ── Streamlit input styling ── */
.stTextInput input, .stSelectbox select {
    background: #13141a !important;
    border-color: #1e2030 !important;
    color: #e2e4ea !important;
    border-radius: 8px !important;
}
.stDateInput input {
    background: #13141a !important;
    border-color: #1e2030 !important;
    border-radius: 8px !important;
}

/* ── Summary rows ── */
.sum-row {
    display: flex;
    justify-content: space-between;
    padding: 7px 0;
    border-bottom: 1px solid #13141a;
    font-size: .84rem;
    color: #6b7280;
}
.sum-row:last-child { border-bottom: none; }
.sum-val { font-family: 'IBM Plex Mono', monospace; color: #e2e4ea; font-weight: 500; }
.sum-card {
    background: #0e0f14;
    border: 1px solid #1a1c28;
    border-radius: 14px;
    padding: 20px 22px;
    margin-bottom: 12px;
}
.sum-card-title {
    font-family: 'Syne', sans-serif;
    font-size: .8rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .1em;
    margin-bottom: 14px;
}

/* ── Badge ── */
.badge-g { background: #0a1f0f; color: #22c55e; padding: 2px 8px; border-radius: 6px; font-size: .75rem; font-weight: 600; }
.badge-r { background: #1f0a0a; color: #ef4444; padding: 2px 8px; border-radius: 6px; font-size: .75rem; font-weight: 600; }
.badge-y { background: #1f1508; color: #f59e0b; padding: 2px 8px; border-radius: 6px; font-size: .75rem; font-weight: 600; }
.badge-n { background: #13141a; color: #6b7280; padding: 2px 8px; border-radius: 6px; font-size: .75rem; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CONSTANTES
# ─────────────────────────────────────────────
MARCAS_IGNORAR_MP = ["site mondaine", "site seculus", "site timex"]

COR_PRIMARY   = "#6366f1"
COR_EC        = "#818cf8"
COR_MP        = "#4ade80"
COR_WARN      = "#f59e0b"
COR_DANGER    = "#ef4444"
COR_MUTED     = "#4b5268"

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#6b7280", family="DM Sans"),
    title_font=dict(color="#9ca3b8", size=12, family="Syne"),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#6b7280"), orientation="h",
                yanchor="bottom", y=1.02, xanchor="left", x=0),
    xaxis=dict(gridcolor="#13141a", linecolor="#1e2030", tickcolor="#1e2030", tickfont=dict(size=11)),
    yaxis=dict(gridcolor="#13141a", linecolor="#1e2030", tickcolor="#1e2030", tickfont=dict(size=11)),
    margin=dict(l=10, r=10, t=48, b=10),
)

PLOTLY_LAYOUT_INV = {**PLOTLY_LAYOUT, "yaxis": {**PLOTLY_LAYOUT["yaxis"], "autorange": "reversed"}}

PALETTE_EC = ["#6366f1","#818cf8","#a5b4fc","#c7d2fe","#e0e7ff"]
PALETTE_MP = ["#4ade80","#22c55e","#16a34a","#15803d","#166534"]
PALETTE_MIX = ["#6366f1","#4ade80","#f59e0b","#ef4444","#8b5cf6","#06b6d4","#f97316","#ec4899"]

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def fmt_brl(v):
    return f"R$ {v:,.0f}"

def fmt_delta(atual, anterior):
    if not anterior or anterior == 0:
        return None, "neu"
    v = (atual - anterior) / anterior * 100
    sign = "+" if v >= 0 else ""
    cls = "pos" if v >= 0 else "neg"
    return f"{sign}{v:.1f}%", cls

def limpar_numero(s):
    return (s.astype(str)
            .str.replace(r"[R$\s]","",regex=True)
            .str.replace(r"\.(?=\d{3})","",regex=True)
            .str.replace(",",".",regex=False)
            .pipe(pd.to_numeric, errors="coerce")
            .fillna(0))

def hex_rgba(h, a=0.12):
    h = h.lstrip("#")
    r,g,b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
    return f"rgba({r},{g},{b},{a})"

def filtrar_data(df, d_ini, d_fim, col="data"):
    if df.empty or col not in df.columns:
        return df
    return df[(df[col] >= pd.Timestamp(d_ini)) & (df[col] <= pd.Timestamp(d_fim))]

# ─────────────────────────────────────────────
# CARREGAMENTO
# ─────────────────────────────────────────────

@st.cache_data(ttl=300)
def carregar_url(url: str):
    try:
        url = url.strip()
        if "docs.google.com" in url:
            if "/edit" in url or "/view" in url or "/pub" in url:
                sid = url.split("/d/")[1].split("/")[0]
                gid = url.split("gid=")[1].split("&")[0].split("#")[0] if "gid=" in url else None
                url = (f"https://docs.google.com/spreadsheets/d/{sid}/export?format=csv"
                       + (f"&gid={gid}" if gid else ""))
        r = requests.get(url, timeout=20, headers={"User-Agent":"Mozilla/5.0"})
        r.raise_for_status()
        try:
            text = r.content.decode("utf-8")
        except UnicodeDecodeError:
            text = r.content.decode("latin-1")
        df = pd.read_csv(StringIO(text))
        df.columns = df.columns.str.strip()
        return df, datetime.now().strftime("%d/%m %H:%M")
    except Exception as e:
        return pd.DataFrame(), str(e)

# ─────────────────────────────────────────────
# PREPARAÇÃO — ECOMMERCE
# ─────────────────────────────────────────────

def preparar_ecommerce(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Colunas esperadas:
    Order, Creation, Client Name, UF, Status, UtmSource, Coupon,
    Payment System Name, Installments, Quantity_SKU, ID_SKU,
    Reference Code, SKU Name, SKU Selling Price, SKU Total Price,
    Discounts Names, Seller Name, marketingTags
    """
    df = df_raw.copy()

    # Normaliza colunas
    col_map = {}
    for c in df.columns:
        cn = c.strip().lower().replace(" ","_")
        col_map[c] = cn
    df = df.rename(columns=col_map)

    # Filtra Livelo
    for col_mt in [c for c in df.columns if "marketingtag" in c]:
        mask_livelo = df[col_mt].astype(str).str.lower().str.contains("livelo", na=False)
        df = df[~mask_livelo]

    # Data
    col_data = next((c for c in df.columns if c in ["creation","data","created_at","date"]), None)
    if col_data:
        df["data"] = pd.to_datetime(df[col_data], dayfirst=True, errors="coerce")
    else:
        df["data"] = pd.NaT
    df = df.dropna(subset=["data"])

    # Preço & qtd
    col_price = next((c for c in df.columns if "sku_selling_price" in c or c=="sku_selling_price"), None)
    col_qty   = next((c for c in df.columns if "quantity_sku" in c or c=="quantity_sku"), None)
    col_total = next((c for c in df.columns if "sku_total_price" in c or c=="sku_total_price"), None)

    if col_price:
        df["valor_unitario"] = limpar_numero(df[col_price])
    if col_qty:
        df["quantidade"] = limpar_numero(df[col_qty])
    if col_price and col_qty:
        df["valor_linha"] = df["valor_unitario"] * df["quantidade"]
    elif col_total:
        df["valor_linha"] = limpar_numero(df[col_total])
    else:
        df["valor_linha"] = 0.0

    # Order
    col_order = next((c for c in df.columns if c in ["order","order_id","id_order","numero_pedido"]), None)
    if col_order:
        df["order"] = df[col_order].astype(str).str.strip()
    else:
        df["order"] = df.index.astype(str)

    # Status
    col_status = next((c for c in df.columns if c in ["status","order_status","situacao"]), None)
    if col_status:
        df["status"] = df[col_status].astype(str).str.strip().str.lower()
        df["faturado"] = df["status"].isin(["faturado","entregue","concluído","concluido","aprovado",
                                             "complete","completed","paid","pago","invoiced"])
        df["cancelado"] = df["status"].isin(["cancelado","cancelada","devolvido","canceled","cancelled"])
    else:
        df["faturado"]  = True
        df["cancelado"] = False

    # UTM Source
    col_utm = next((c for c in df.columns if "utmsource" in c or c=="utm_source"), None)
    if col_utm:
        df["utm_source"] = df[col_utm].astype(str).str.strip().str.title()
    else:
        df["utm_source"] = "Desconhecido"

    # Seller/Marca
    col_seller = next((c for c in df.columns if "seller" in c), None)
    if col_seller:
        df["marca"] = df[col_seller].astype(str).str.strip()

    # Mes
    df["mes"] = df["data"].dt.to_period("M").astype(str)

    return df

# ─────────────────────────────────────────────
# PREPARAÇÃO — MARKETPLACE
# ─────────────────────────────────────────────

def preparar_marketplace(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Colunas esperadas:
    Data do faturamento, Nota Fiscal, Quantidade faturada,
    Valor Unitário Final, Marketplace
    """
    df = df_raw.copy()

    col_map = {}
    for c in df.columns:
        cn = c.strip().lower().replace(" ","_")
        col_map[c] = cn
    df = df.rename(columns=col_map)

    # Filtra sites próprios
    col_mp = next((c for c in df.columns if "marketplace" in c), None)
    if col_mp:
        df["marketplace"] = df[col_mp].astype(str).str.strip()
        df = df[~df["marketplace"].str.lower().isin(MARCAS_IGNORAR_MP)]
    else:
        df["marketplace"] = "Desconhecido"

    # Data faturamento
    col_data = next((c for c in df.columns if "data" in c and "fat" in c), None)
    if not col_data:
        col_data = next((c for c in df.columns if "data" in c), None)
    if col_data:
        df["data"] = pd.to_datetime(df[col_data], dayfirst=True, errors="coerce")
    else:
        df["data"] = pd.NaT
    df = df.dropna(subset=["data"])

    # Nota fiscal (validação de duplicata)
    col_nf = next((c for c in df.columns if "nota" in c or "nf" in c or "fiscal" in c), None)
    if col_nf:
        df["nota_fiscal"] = df[col_nf].astype(str).str.strip()
        df = df.drop_duplicates(subset=["nota_fiscal"])
    else:
        df["nota_fiscal"] = df.index.astype(str)

    # Quantidade faturada
    col_qty = next((c for c in df.columns if "quantidade" in c or "qtd" in c or "qty" in c), None)
    if col_qty:
        df["quantidade"] = limpar_numero(df[col_qty])
    else:
        df["quantidade"] = 1.0

    # Valor unitário final
    col_vl = next((c for c in df.columns if "valor" in c and "unit" in c), None)
    if not col_vl:
        col_vl = next((c for c in df.columns if "valor" in c or "price" in c or "preco" in c), None)
    if col_vl:
        df["valor_unitario"] = limpar_numero(df[col_vl])
    else:
        df["valor_unitario"] = 0.0

    df["valor_linha"] = df["valor_unitario"] * df["quantidade"]
    df["mes"] = df["data"].dt.to_period("M").astype(str)

    return df

# ─────────────────────────────────────────────
# MÉTRICAS
# ─────────────────────────────────────────────

def metricas_ec(df):
    if df.empty:
        return {"receita":0, "pedidos":0, "faturados":0, "cancelados":0,
                "ticket":0, "itens":0}
    # Valor por order = soma de valor_linha
    por_order = df.groupby("order").agg(
        valor=("valor_linha","sum"),
        faturado=("faturado","any"),
        cancelado=("cancelado","any"),
    ).reset_index()
    por_order["status"] = "pendente"
    por_order.loc[por_order["cancelado"] & ~por_order["faturado"], "status"] = "cancelado"
    por_order.loc[por_order["faturado"], "status"] = "faturado"

    fat  = por_order[por_order["status"]=="faturado"]
    canc = por_order[por_order["status"]=="cancelado"]
    receita = float(fat["valor"].sum())
    pedidos = len(por_order)
    faturados = len(fat)
    cancelados = len(canc)
    ticket = float(fat["valor"].mean()) if len(fat) > 0 else 0
    itens = int(df["quantidade"].sum()) if "quantidade" in df.columns else len(df)
    return {"receita":receita,"pedidos":pedidos,"faturados":faturados,
            "cancelados":cancelados,"ticket":ticket,"itens":itens}

def metricas_mp(df):
    if df.empty:
        return {"receita":0, "notas":0, "itens":0, "ticket":0}
    receita = float(df["valor_linha"].sum())
    notas   = int(df["nota_fiscal"].nunique())
    itens   = int(df["quantidade"].sum())
    ticket  = receita / notas if notas > 0 else 0
    return {"receita":receita,"notas":notas,"itens":itens,"ticket":ticket}

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
for k, v in [
    ("df_ec_raw", pd.DataFrame()),
    ("df_mp_raw", pd.DataFrame()),
    ("df_ec", pd.DataFrame()),
    ("df_mp", pd.DataFrame()),
    ("ts_ec", ""),
    ("ts_mp", ""),
    ("active_tab", "overview"),
]:
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────
# TOP NAVIGATION
# ─────────────────────────────────────────────
tabs_def = [
    ("overview",   "Overview"),
    ("ecommerce",  "E-commerce"),
    ("marketplace","Marketplace"),
    ("detailed",   "Detalhado"),
    ("config",     "Configurações"),
]

# Compute active tab from query param or session
tab_labels_html = ""
for tid, tlabel in tabs_def:
    active_cls = "active" if st.session_state.active_tab == tid else ""
    tab_labels_html += f'<button class="nav-tab {active_cls}" onclick="void(0)">{tlabel}</button>'

# Dot status
ec_ok = not st.session_state.df_ec.empty
mp_ok = not st.session_state.df_mp.empty
dot_color = "#22c55e" if (ec_ok or mp_ok) else "#374151"

st.markdown(f"""
<div class="nav-bar">
    <div class="nav-logo">⌚ Grupo <span>Seculus</span></div>
    <div class="nav-right">
        <span style="color:{dot_color};font-size:.9rem;">●</span>
        {"EC ✓" if ec_ok else "EC —"}
        &nbsp;/&nbsp;
        {"MP ✓" if mp_ok else "MP —"}
    </div>
</div>
""", unsafe_allow_html=True)

# Streamlit native tabs (functional)
tab_names = [t[1] for t in tabs_def]
tabs = st.tabs(tab_names)

# ─────────────────────────────────────────────
# CONFIGURAÇÕES (última aba)
# ─────────────────────────────────────────────
with tabs[4]:
    st.markdown('<div class="page-header"><p class="page-title">Configurações</p><p class="page-subtitle">conecte suas planilhas de dados</p></div>', unsafe_allow_html=True)

    col_cfg1, col_cfg2 = st.columns(2)

    with col_cfg1:
        st.markdown('<div class="section-label"><span class="platform-pill pill-ec">E-commerce</span></div>', unsafe_allow_html=True)
        url_ec = st.text_input("URL Google Sheets / CSV — E-commerce",
                               placeholder="https://docs.google.com/spreadsheets/d/...",
                               key="url_ec_input")
        if st.button("Carregar E-commerce", use_container_width=True, key="btn_ec"):
            if url_ec.strip():
                with st.spinner("Carregando..."):
                    df_raw, ts = carregar_url(url_ec.strip())
                if not df_raw.empty:
                    st.session_state.df_ec_raw = df_raw
                    st.session_state.df_ec = preparar_ecommerce(df_raw)
                    st.session_state.ts_ec = ts
                    n = len(st.session_state.df_ec)
                    ped = st.session_state.df_ec["order"].nunique() if "order" in st.session_state.df_ec.columns else 0
                    st.success(f"✅ {n} linhas · {ped} pedidos únicos · {ts}")
                else:
                    st.error(f"Erro: {ts}")
            else:
                st.warning("Insira uma URL.")

        if not st.session_state.df_ec.empty:
            st.markdown("**Preview das colunas detectadas:**")
            st.dataframe(st.session_state.df_ec_raw.head(3), use_container_width=True)

    with col_cfg2:
        st.markdown('<div class="section-label"><span class="platform-pill pill-mp">Marketplace</span></div>', unsafe_allow_html=True)
        url_mp = st.text_input("URL Google Sheets / CSV — Marketplace",
                               placeholder="https://docs.google.com/spreadsheets/d/...",
                               key="url_mp_input")
        if st.button("Carregar Marketplace", use_container_width=True, key="btn_mp"):
            if url_mp.strip():
                with st.spinner("Carregando..."):
                    df_raw, ts = carregar_url(url_mp.strip())
                if not df_raw.empty:
                    st.session_state.df_mp_raw = df_raw
                    st.session_state.df_mp = preparar_marketplace(df_raw)
                    st.session_state.ts_mp = ts
                    n = len(st.session_state.df_mp)
                    nf = st.session_state.df_mp["nota_fiscal"].nunique() if "nota_fiscal" in st.session_state.df_mp.columns else 0
                    st.success(f"✅ {n} linhas · {nf} notas fiscais únicas · {ts}")
                else:
                    st.error(f"Erro: {ts}")
            else:
                st.warning("Insira uma URL.")

        if not st.session_state.df_mp.empty:
            st.markdown("**Preview das colunas detectadas:**")
            st.dataframe(st.session_state.df_mp_raw.head(3), use_container_width=True)

    st.markdown("---")
    st.markdown("**Filtro de período** (configurado nas abas de análise)")
    st.info("As abas de análise possuem seleção de período no topo.")

    # Colunas de referência
    with st.expander("📋 Estrutura esperada das planilhas"):
        st.markdown("""
**E-commerce** — colunas obrigatórias/esperadas:
| Coluna | Uso |
|---|---|
| `Order` | ID do pedido (chave de agrupamento) |
| `Creation` | Data do pedido |
| `Status` | Status do pedido |
| `UtmSource` | Origem do tráfego |
| `Quantity_SKU` | Quantidade do SKU |
| `SKU Selling Price` | Preço unitário do SKU |
| `Seller Name` | Marca / seller |
| `marketingTags` | Pedidos com Livelo são ignorados |

**Marketplace** — colunas obrigatórias/esperadas:
| Coluna | Uso |
|---|---|
| `Data do faturamento` | Data do faturamento |
| `Nota Fiscal` | Identificador único (dedup) |
| `Quantidade faturada` | Quantidade |
| `Valor Unitário Final` | Preço unitário |
| `Marketplace` | Plataforma (Sites próprios são ignorados) |
        """)

# ─────────────────────────────────────────────
# HELPER: seletor de período reutilizável
# ─────────────────────────────────────────────
def seletor_periodo(key_prefix="main"):
    hoje = datetime.today().date()
    col1, col2, col3, col4 = st.columns([2,2,1,1])
    with col1:
        d_ini = st.date_input("De", value=hoje - timedelta(days=30), key=f"{key_prefix}_ini")
    with col2:
        d_fim = st.date_input("Até", value=hoje, key=f"{key_prefix}_fim")
    with col3:
        if st.button("30d", key=f"{key_prefix}_30d", use_container_width=True):
            st.session_state[f"{key_prefix}_ini"] = hoje - timedelta(days=30)
            st.session_state[f"{key_prefix}_fim"] = hoje
            st.rerun()
    with col4:
        if st.button("Mês", key=f"{key_prefix}_mes", use_container_width=True):
            st.session_state[f"{key_prefix}_ini"] = hoje.replace(day=1)
            st.session_state[f"{key_prefix}_fim"] = hoje
            st.rerun()
    return d_ini, d_fim

def periodo_anterior(d_ini, d_fim):
    delta = d_fim - d_ini
    return d_ini - delta - timedelta(days=1), d_ini - timedelta(days=1)

# ─────────────────────────────────────────────
# GUARD: sem dados
# ─────────────────────────────────────────────
def guard_sem_dados():
    st.markdown("""
    <div class="upload-area">
        <p class="upload-title">Nenhum dado carregado</p>
        <p class="upload-sub">Vá para a aba <strong>Configurações</strong> e insira os links das planilhas.</p>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# ABA 0 — OVERVIEW
# ─────────────────────────────────────────────
with tabs[0]:
    st.markdown('<div class="page-header"><p class="page-title">Overview</p><p class="page-subtitle">visão consolidada · e-commerce + marketplace</p></div>', unsafe_allow_html=True)

    if st.session_state.df_ec.empty and st.session_state.df_mp.empty:
        guard_sem_dados()
    else:
        d_ini, d_fim = seletor_periodo("ov")
        d_ini_ant, d_fim_ant = periodo_anterior(d_ini, d_fim)

        df_ec  = filtrar_data(st.session_state.df_ec,  d_ini, d_fim)
        df_mp  = filtrar_data(st.session_state.df_mp,  d_ini, d_fim)
        df_ec_ant = filtrar_data(st.session_state.df_ec, d_ini_ant, d_fim_ant)
        df_mp_ant = filtrar_data(st.session_state.df_mp, d_ini_ant, d_fim_ant)

        m_ec  = metricas_ec(df_ec)
        m_mp  = metricas_mp(df_mp)
        m_ec_ant = metricas_ec(df_ec_ant)
        m_mp_ant = metricas_mp(df_mp_ant)

        rec_total     = m_ec["receita"] + m_mp["receita"]
        rec_total_ant = m_ec_ant["receita"] + m_mp_ant["receita"]
        delta_total, cls_total = fmt_delta(rec_total, rec_total_ant)

        # ── KPI row ──
        st.markdown('<div class="section-label">KPIs Consolidados</div>', unsafe_allow_html=True)

        k1,k2,k3,k4 = st.columns(4)
        with k1:
            dv, dc = fmt_delta(rec_total, rec_total_ant)
            st.markdown(f"""
            <div class="kpi-card" style="--accent:{COR_PRIMARY}">
                <div class="kpi-label">Receita Total</div>
                <div class="kpi-value">{fmt_brl(rec_total)}</div>
                <div class="kpi-delta {dc}">{dv or "—"} vs período ant.</div>
            </div>""", unsafe_allow_html=True)
        with k2:
            dv, dc = fmt_delta(m_ec["receita"], m_ec_ant["receita"])
            st.markdown(f"""
            <div class="kpi-card" style="--accent:{COR_EC}">
                <div class="kpi-label"><span class="platform-pill pill-ec">E-commerce</span></div>
                <div class="kpi-value">{fmt_brl(m_ec['receita'])}</div>
                <div class="kpi-delta {dc}">{dv or "—"} vs período ant.</div>
            </div>""", unsafe_allow_html=True)
        with k3:
            dv, dc = fmt_delta(m_mp["receita"], m_mp_ant["receita"])
            st.markdown(f"""
            <div class="kpi-card" style="--accent:{COR_MP}">
                <div class="kpi-label"><span class="platform-pill pill-mp">Marketplace</span></div>
                <div class="kpi-value">{fmt_brl(m_mp['receita'])}</div>
                <div class="kpi-delta {dc}">{dv or "—"} vs período ant.</div>
            </div>""", unsafe_allow_html=True)
        with k4:
            total_ped = m_ec["pedidos"] + m_mp["notas"]
            total_ped_ant = m_ec_ant["pedidos"] + m_mp_ant["notas"]
            dv, dc = fmt_delta(total_ped, total_ped_ant)
            st.markdown(f"""
            <div class="kpi-card" style="--accent:{COR_WARN}">
                <div class="kpi-label">Pedidos / Notas</div>
                <div class="kpi-value">{total_ped:,}</div>
                <div class="kpi-delta {dc}">{dv or "—"} vs período ant.</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Evolução combinada ──
        st.markdown('<div class="section-label">Evolução de Receita</div>', unsafe_allow_html=True)

        col_ch1, col_ch2 = st.columns([3,1])
        with col_ch1:
            fig_ev = go.Figure()
            if not df_ec.empty and "faturado" in df_ec.columns:
                ev_ec = (df_ec[df_ec["faturado"]]
                         .groupby("data")["valor_linha"].sum().reset_index())
                fig_ev.add_trace(go.Scatter(
                    x=ev_ec["data"], y=ev_ec["valor_linha"],
                    name="E-commerce", mode="lines", fill="tozeroy",
                    line=dict(color=COR_EC, width=2.5, shape="spline", smoothing=1.2),
                    fillcolor=hex_rgba(COR_EC, 0.08),
                ))
            if not df_mp.empty:
                ev_mp = df_mp.groupby("data")["valor_linha"].sum().reset_index()
                fig_ev.add_trace(go.Scatter(
                    x=ev_mp["data"], y=ev_mp["valor_linha"],
                    name="Marketplace", mode="lines", fill="tozeroy",
                    line=dict(color=COR_MP, width=2.5, shape="spline", smoothing=1.2),
                    fillcolor=hex_rgba(COR_MP, 0.06),
                ))
            fig_ev.update_layout(**PLOTLY_LAYOUT, height=280)
            st.plotly_chart(fig_ev, use_container_width=True)

        with col_ch2:
            # Share EC vs MP
            labels = []; values = []; colors = []
            if m_ec["receita"] > 0:
                labels.append("E-commerce"); values.append(m_ec["receita"]); colors.append(COR_EC)
            if m_mp["receita"] > 0:
                labels.append("Marketplace"); values.append(m_mp["receita"]); colors.append(COR_MP)
            if labels:
                fig_sh = go.Figure(go.Pie(
                    labels=labels, values=values,
                    marker=dict(colors=colors, line=dict(color="#0a0b0f", width=2)),
                    hole=0.65, textinfo="percent",
                    textfont=dict(size=11, color="#e2e4ea"),
                ))
                fig_sh.update_layout(**{**PLOTLY_LAYOUT,
                    "showlegend":True,
                    "legend":dict(orientation="v", bgcolor="rgba(0,0,0,0)",
                                  font=dict(color="#6b7280"), x=0.5, y=-0.15,
                                  xanchor="center"),
                    "height":280, "margin":dict(l=0,r=0,t=10,b=30)})
                st.plotly_chart(fig_sh, use_container_width=True)

        # ── Resumo cards ──
        st.markdown('<div class="section-label">Resumo por Plataforma</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            tc_pct = (m_ec["cancelados"]/m_ec["pedidos"]*100) if m_ec["pedidos"] else 0
            taxa_fat = (m_ec["faturados"]/m_ec["pedidos"]*100) if m_ec["pedidos"] else 0
            st.markdown(f"""
            <div class="sum-card">
                <div class="sum-card-title" style="color:{COR_EC}">E-commerce</div>
                <div class="sum-row"><span>Pedidos únicos</span><span class="sum-val">{m_ec['pedidos']:,}</span></div>
                <div class="sum-row"><span>Faturados</span><span class="sum-val"><span class="badge-g">{m_ec['faturados']:,}</span></span></div>
                <div class="sum-row"><span>Cancelados</span><span class="sum-val"><span class="badge-r">{m_ec['cancelados']:,}</span></span></div>
                <div class="sum-row"><span>Taxa faturamento</span><span class="sum-val">{taxa_fat:.1f}%</span></div>
                <div class="sum-row"><span>Receita faturada</span><span class="sum-val">{fmt_brl(m_ec['receita'])}</span></div>
                <div class="sum-row"><span>Ticket médio</span><span class="sum-val">{fmt_brl(m_ec['ticket'])}</span></div>
                <div class="sum-row"><span>Itens vendidos</span><span class="sum-val">{m_ec['itens']:,}</span></div>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="sum-card">
                <div class="sum-card-title" style="color:{COR_MP}">Marketplace</div>
                <div class="sum-row"><span>Notas fiscais únicas</span><span class="sum-val">{m_mp['notas']:,}</span></div>
                <div class="sum-row"><span>Itens faturados</span><span class="sum-val"><span class="badge-g">{m_mp['itens']:,}</span></span></div>
                <div class="sum-row"><span>Receita total</span><span class="sum-val">{fmt_brl(m_mp['receita'])}</span></div>
                <div class="sum-row"><span>Ticket médio/NF</span><span class="sum-val">{fmt_brl(m_mp['ticket'])}</span></div>
            </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# ABA 1 — E-COMMERCE
# ─────────────────────────────────────────────
with tabs[1]:
    st.markdown('<div class="page-header"><p class="page-title">E-commerce</p><p class="page-subtitle">análise de pedidos, UTM source e performance</p></div>', unsafe_allow_html=True)

    if st.session_state.df_ec.empty:
        guard_sem_dados()
    else:
        d_ini, d_fim = seletor_periodo("ec")
        df_ec = filtrar_data(st.session_state.df_ec, d_ini, d_fim)
        df_ec_ant = filtrar_data(st.session_state.df_ec, *periodo_anterior(d_ini, d_fim))

        m     = metricas_ec(df_ec)
        m_ant = metricas_ec(df_ec_ant)

        # KPIs
        k1,k2,k3,k4,k5 = st.columns(5)
        kpis_ec = [
            ("Receita",    fmt_brl(m['receita']),    m['receita'],    m_ant['receita'],    COR_EC),
            ("Pedidos",    f"{m['pedidos']:,}",       m['pedidos'],    m_ant['pedidos'],    COR_PRIMARY),
            ("Faturados",  f"{m['faturados']:,}",     m['faturados'],  m_ant['faturados'],  "#22c55e"),
            ("Cancelados", f"{m['cancelados']:,}",    m['cancelados'], m_ant['cancelados'], COR_DANGER),
            ("Ticket Médio",fmt_brl(m['ticket']),     m['ticket'],     m_ant['ticket'],     COR_WARN),
        ]
        for col, (label, val_str, val, vant, cor) in zip([k1,k2,k3,k4,k5], kpis_ec):
            dv, dc = fmt_delta(val, vant)
            col.markdown(f"""
            <div class="kpi-card" style="--accent:{cor}">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{val_str}</div>
                <div class="kpi-delta {dc}">{dv or "—"}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # UTM Source — contagem por ORDER única
        st.markdown('<div class="section-label">UTM Source — pedidos com vendas reais (faturados)</div>', unsafe_allow_html=True)

        if "utm_source" in df_ec.columns and "order" in df_ec.columns:
            # Deduplicar por order antes de contar UTM
            df_fat = df_ec[df_ec["faturado"]] if "faturado" in df_ec.columns else df_ec
            utm_dedup = df_fat.drop_duplicates(subset=["order"])[["order","utm_source","valor_linha"]].copy()

            # Valor real por order
            val_por_order = df_fat.groupby("order")["valor_linha"].sum().reset_index()
            utm_dedup2 = df_fat.drop_duplicates(subset=["order"])[["order","utm_source"]].merge(val_por_order, on="order")

            utm_agg = (utm_dedup2.groupby("utm_source")
                       .agg(pedidos=("order","nunique"), receita=("valor_linha","sum"))
                       .reset_index().sort_values("receita", ascending=False))
            utm_agg["ticket"] = utm_agg["receita"] / utm_agg["pedidos"].replace(0, np.nan)
            utm_agg["pct"] = utm_agg["receita"] / utm_agg["receita"].sum() * 100

            col_u1, col_u2 = st.columns(2)
            with col_u1:
                fig_utm_bar = px.bar(
                    utm_agg.head(12), x="receita", y="utm_source",
                    orientation="h",
                    color="receita",
                    color_continuous_scale=[[0,"#1a1c28"],[1,COR_EC]],
                    labels={"receita":"Receita (R$)","utm_source":""},
                    text=utm_agg.head(12)["pct"].map("{:.1f}%".format),
                )
                fig_utm_bar.update_traces(textposition="outside", textfont=dict(color="#9ca3b8"))
                fig_utm_bar.update_layout(**{**PLOTLY_LAYOUT_INV, "coloraxis_showscale":False, "height":360})
                st.plotly_chart(fig_utm_bar, use_container_width=True)

            with col_u2:
                fig_utm_pie = px.pie(
                    utm_agg, names="utm_source", values="pedidos",
                    color_discrete_sequence=PALETTE_EC + PALETTE_MIX, hole=0.6,
                    title="Distribuição de Pedidos",
                )
                fig_utm_pie.update_traces(textinfo="percent+label", textfont_size=11)
                fig_utm_pie.update_layout(**{**PLOTLY_LAYOUT, "height":360})
                st.plotly_chart(fig_utm_pie, use_container_width=True)

            # Tabela UTM
            utm_exib = utm_agg.copy()
            utm_exib["receita"] = utm_exib["receita"].map(fmt_brl)
            utm_exib["ticket"]  = utm_exib["ticket"].map(fmt_brl)
            utm_exib["pct"]     = utm_exib["pct"].map("{:.1f}%".format)
            utm_exib = utm_exib.rename(columns={"utm_source":"UTM Source","pedidos":"Pedidos",
                                                  "receita":"Receita","ticket":"Ticket Médio","pct":"Share"})
            st.dataframe(utm_exib, use_container_width=True, hide_index=True)

        # Evolução diária
        st.markdown('<div class="section-label">Receita Diária</div>', unsafe_allow_html=True)
        if "faturado" in df_ec.columns:
            ev = df_ec[df_ec["faturado"]].groupby("data")["valor_linha"].sum().reset_index()
            fig_ev2 = go.Figure(go.Scatter(
                x=ev["data"], y=ev["valor_linha"], mode="lines", fill="tozeroy",
                line=dict(color=COR_EC, width=2.5, shape="spline", smoothing=1.2),
                fillcolor=hex_rgba(COR_EC, 0.08),
            ))
            fig_ev2.update_layout(**{**PLOTLY_LAYOUT, "height":220})
            st.plotly_chart(fig_ev2, use_container_width=True)

        # Funil status
        st.markdown('<div class="section-label">Funil de Conversão</div>', unsafe_allow_html=True)
        fig_fun = go.Figure(go.Funnel(
            y=["Realizados","Faturados","Cancelados"],
            x=[m['pedidos'], m['faturados'], m['cancelados']],
            marker={"color":[COR_PRIMARY, "#22c55e", COR_DANGER]},
            textinfo="value+percent initial",
            textfont=dict(color="#e2e4ea"),
        ))
        fig_fun.update_layout(**{**PLOTLY_LAYOUT, "height":220})
        st.plotly_chart(fig_fun, use_container_width=True)

# ─────────────────────────────────────────────
# ABA 2 — MARKETPLACE
# ─────────────────────────────────────────────
with tabs[2]:
    st.markdown('<div class="page-header"><p class="page-title">Marketplace</p><p class="page-subtitle">análise por plataforma · notas fiscais validadas</p></div>', unsafe_allow_html=True)

    if st.session_state.df_mp.empty:
        guard_sem_dados()
    else:
        d_ini, d_fim = seletor_periodo("mp")
        df_mp = filtrar_data(st.session_state.df_mp, d_ini, d_fim)
        df_mp_ant = filtrar_data(st.session_state.df_mp, *periodo_anterior(d_ini, d_fim))

        m     = metricas_mp(df_mp)
        m_ant = metricas_mp(df_mp_ant)

        k1,k2,k3,k4 = st.columns(4)
        kpis_mp = [
            ("Receita",       fmt_brl(m['receita']),  m['receita'],  m_ant['receita'],  COR_MP),
            ("Notas Fiscais", f"{m['notas']:,}",       m['notas'],    m_ant['notas'],    "#22c55e"),
            ("Itens Fat.",    f"{m['itens']:,}",       m['itens'],    m_ant['itens'],    COR_WARN),
            ("Ticket Médio",  fmt_brl(m['ticket']),   m['ticket'],   m_ant['ticket'],   COR_PRIMARY),
        ]
        for col, (label, val_str, val, vant, cor) in zip([k1,k2,k3,k4], kpis_mp):
            dv, dc = fmt_delta(val, vant)
            col.markdown(f"""
            <div class="kpi-card" style="--accent:{cor}">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{val_str}</div>
                <div class="kpi-delta {dc}">{dv or "—"}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if "marketplace" in df_mp.columns:
            # Receita por plataforma
            st.markdown('<div class="section-label">Receita por Plataforma</div>', unsafe_allow_html=True)
            mp_agg = (df_mp.groupby("marketplace")
                      .agg(receita=("valor_linha","sum"),
                           notas=("nota_fiscal","nunique"),
                           itens=("quantidade","sum"))
                      .reset_index().sort_values("receita", ascending=False))
            mp_agg["ticket"] = mp_agg["receita"] / mp_agg["notas"].replace(0,np.nan)

            col_m1, col_m2 = st.columns(2)
            with col_m1:
                fig_mp_bar = px.bar(
                    mp_agg, x="receita", y="marketplace", orientation="h",
                    color="receita",
                    color_continuous_scale=[[0,"#0d1f0d"],[1,COR_MP]],
                    labels={"receita":"Receita (R$)","marketplace":""},
                    text=mp_agg["receita"].map(fmt_brl),
                )
                fig_mp_bar.update_traces(textposition="outside", textfont=dict(color="#9ca3b8"))
                fig_mp_bar.update_layout(**{**PLOTLY_LAYOUT_INV, "coloraxis_showscale":False, "height":340})
                st.plotly_chart(fig_mp_bar, use_container_width=True)

            with col_m2:
                fig_mp_pie = px.pie(
                    mp_agg, names="marketplace", values="receita",
                    color_discrete_sequence=PALETTE_MP + PALETTE_MIX, hole=0.6,
                )
                fig_mp_pie.update_traces(textinfo="percent+label", textfont_size=11)
                fig_mp_pie.update_layout(**{**PLOTLY_LAYOUT, "height":340})
                st.plotly_chart(fig_mp_pie, use_container_width=True)

            # Evolução por plataforma
            st.markdown('<div class="section-label">Evolução por Plataforma</div>', unsafe_allow_html=True)
            ev_mp = df_mp.groupby(["data","marketplace"])["valor_linha"].sum().reset_index()
            fig_ev_mp = px.line(
                ev_mp, x="data", y="valor_linha", color="marketplace",
                color_discrete_sequence=PALETTE_MP + PALETTE_MIX,
                labels={"valor_linha":"Receita (R$)","data":"","marketplace":""},
            )
            fig_ev_mp.update_traces(line=dict(width=2.5))
            fig_ev_mp.update_layout(**{**PLOTLY_LAYOUT, "height":260})
            st.plotly_chart(fig_ev_mp, use_container_width=True)

            # Tabela detalhada
            st.markdown('<div class="section-label">Detalhamento por Plataforma</div>', unsafe_allow_html=True)
            mp_exib = mp_agg.copy()
            mp_exib["receita"] = mp_exib["receita"].map(fmt_brl)
            mp_exib["ticket"]  = mp_exib["ticket"].map(fmt_brl)
            mp_exib = mp_exib.rename(columns={"marketplace":"Marketplace","receita":"Receita",
                                               "notas":"Notas Fiscais","itens":"Itens","ticket":"Ticket Médio"})
            st.dataframe(mp_exib, use_container_width=True, hide_index=True)
            st.download_button("📥 Exportar Marketplace", data=mp_exib.to_csv(index=False).encode("utf-8"),
                               file_name="marketplace.csv", mime="text/csv")

# ─────────────────────────────────────────────
# ABA 3 — DETALHADO
# ─────────────────────────────────────────────
with tabs[3]:
    st.markdown('<div class="page-header"><p class="page-title">Detalhado</p><p class="page-subtitle">receita por marca (ecommerce) · receita por plataforma (marketplace)</p></div>', unsafe_allow_html=True)

    if st.session_state.df_ec.empty and st.session_state.df_mp.empty:
        guard_sem_dados()
    else:
        d_ini, d_fim = seletor_periodo("det")
        df_ec = filtrar_data(st.session_state.df_ec, d_ini, d_fim)
        df_mp = filtrar_data(st.session_state.df_mp, d_ini, d_fim)
        df_ec_ant = filtrar_data(st.session_state.df_ec, *periodo_anterior(d_ini, d_fim))
        df_mp_ant = filtrar_data(st.session_state.df_mp, *periodo_anterior(d_ini, d_fim))

        # ── E-commerce: receita por marca ──
        if not df_ec.empty:
            st.markdown('<div class="section-label"><span class="platform-pill pill-ec">E-commerce</span> Receita por Marca</div>', unsafe_allow_html=True)

            col_marca = next((c for c in ["marca","seller_name","brand"] if c in df_ec.columns), None)
            if col_marca and col_marca != "marca":
                df_ec = df_ec.rename(columns={col_marca:"marca"})
                col_marca = "marca"

            if col_marca:
                df_fat_ec = df_ec[df_ec["faturado"]] if "faturado" in df_ec.columns else df_ec
                # Valor real por order por marca
                marca_order = df_fat_ec.drop_duplicates(subset=["order","marca"] if "marca" in df_fat_ec.columns else ["order"])
                val_order = df_fat_ec.groupby("order")["valor_linha"].sum().reset_index()
                if "marca" in df_fat_ec.columns:
                    marca_map = df_fat_ec.drop_duplicates("order").set_index("order")["marca"]
                    val_order["marca"] = val_order["order"].map(marca_map)
                    marca_agg = (val_order.groupby("marca")
                                 .agg(receita=("valor_linha","sum"), pedidos=("order","nunique"))
                                 .reset_index().sort_values("receita",ascending=False))
                    marca_agg["ticket"] = marca_agg["receita"] / marca_agg["pedidos"].replace(0,np.nan)
                    marca_agg["pct"]    = marca_agg["receita"] / marca_agg["receita"].sum() * 100

                    col_d1, col_d2 = st.columns([3,2])
                    with col_d1:
                        # Atual vs anterior por marca
                        df_fat_ant = df_ec_ant[df_ec_ant["faturado"]] if ("faturado" in df_ec_ant.columns and not df_ec_ant.empty) else df_ec_ant
                        if not df_ec_ant.empty and "marca" in df_ec_ant.columns:
                            va_order = df_fat_ant.groupby("order")["valor_linha"].sum().reset_index()
                            if not va_order.empty:
                                marca_map_ant = df_fat_ant.drop_duplicates("order").set_index("order").get("marca", pd.Series(dtype=str))
                                va_order["marca"] = va_order["order"].map(marca_map_ant)
                                marca_ant = (va_order.groupby("marca")["valor_linha"].sum()
                                             .reset_index().rename(columns={"valor_linha":"rec_ant"}))
                                m_comp = marca_agg.merge(marca_ant, on="marca", how="left").fillna(0)
                            else:
                                m_comp = marca_agg.copy(); m_comp["rec_ant"] = 0
                        else:
                            m_comp = marca_agg.copy(); m_comp["rec_ant"] = 0

                        fig_mc = go.Figure([
                            go.Bar(name="Período ant.", x=m_comp["marca"], y=m_comp["rec_ant"],
                                   marker_color="rgba(99,102,241,0.18)", marker_line_width=0),
                            go.Bar(name="Atual", x=m_comp["marca"], y=m_comp["receita"],
                                   marker_color=COR_EC, marker_line_width=0),
                        ])
                        fig_mc.update_layout(barmode="group", **{**PLOTLY_LAYOUT, "height":280})
                        st.plotly_chart(fig_mc, use_container_width=True)

                    with col_d2:
                        fig_mc_pie = px.pie(marca_agg, names="marca", values="receita",
                                            color_discrete_sequence=PALETTE_EC + PALETTE_MIX,
                                            hole=0.6)
                        fig_mc_pie.update_traces(textinfo="percent+label", textfont_size=11)
                        fig_mc_pie.update_layout(**{**PLOTLY_LAYOUT, "height":280})
                        st.plotly_chart(fig_mc_pie, use_container_width=True)

                    # Tabela marcas
                    m_exib = marca_agg.copy()
                    m_exib["receita"] = m_exib["receita"].map(fmt_brl)
                    m_exib["ticket"]  = m_exib["ticket"].map(fmt_brl)
                    m_exib["pct"]     = m_exib["pct"].map("{:.1f}%".format)
                    m_exib = m_exib.rename(columns={"marca":"Marca","pedidos":"Pedidos","receita":"Receita",
                                                     "ticket":"Ticket Médio","pct":"Share"})
                    st.dataframe(m_exib, use_container_width=True, hide_index=True)
                    st.download_button("📥 Exportar por Marca",
                                       data=m_exib.to_csv(index=False).encode("utf-8"),
                                       file_name="ec_por_marca.csv", mime="text/csv")
            else:
                st.info("Coluna de marca/seller não encontrada na planilha de e-commerce.")

        # ── Marketplace: receita por plataforma ──
        if not df_mp.empty:
            st.markdown('<div class="section-label" style="margin-top:32px"><span class="platform-pill pill-mp">Marketplace</span> Receita por Plataforma</div>', unsafe_allow_html=True)

            if "marketplace" in df_mp.columns:
                mp_det = (df_mp.groupby("marketplace")
                          .agg(receita=("valor_linha","sum"),
                               notas=("nota_fiscal","nunique"),
                               itens=("quantidade","sum"))
                          .reset_index().sort_values("receita",ascending=False))
                mp_det["ticket"] = mp_det["receita"] / mp_det["notas"].replace(0,np.nan)
                mp_det["pct"]    = mp_det["receita"] / mp_det["receita"].sum() * 100

                # Atual vs anterior
                if not df_mp_ant.empty and "marketplace" in df_mp_ant.columns:
                    mp_ant = (df_mp_ant.groupby("marketplace")["valor_linha"].sum()
                              .reset_index().rename(columns={"valor_linha":"rec_ant"}))
                    mp_comp = mp_det.merge(mp_ant, on="marketplace", how="left").fillna(0)
                else:
                    mp_comp = mp_det.copy(); mp_comp["rec_ant"] = 0

                col_mp1, col_mp2 = st.columns([3,2])
                with col_mp1:
                    fig_mpd = go.Figure([
                        go.Bar(name="Período ant.", x=mp_comp["marketplace"], y=mp_comp["rec_ant"],
                               marker_color="rgba(74,222,128,0.15)", marker_line_width=0),
                        go.Bar(name="Atual", x=mp_comp["marketplace"], y=mp_comp["receita"],
                               marker_color=COR_MP, marker_line_width=0),
                    ])
                    fig_mpd.update_layout(barmode="group", **{**PLOTLY_LAYOUT, "height":280})
                    st.plotly_chart(fig_mpd, use_container_width=True)

                with col_mp2:
                    fig_mpd_pie = px.pie(mp_det, names="marketplace", values="receita",
                                         color_discrete_sequence=PALETTE_MP + PALETTE_MIX, hole=0.6)
                    fig_mpd_pie.update_traces(textinfo="percent+label", textfont_size=11)
                    fig_mpd_pie.update_layout(**{**PLOTLY_LAYOUT, "height":280})
                    st.plotly_chart(fig_mpd_pie, use_container_width=True)

                # Tabela plataformas
                mp_exib2 = mp_det.copy()
                if "rec_ant" in mp_comp.columns:
                    mp_exib2 = mp_exib2.merge(mp_comp[["marketplace","rec_ant"]], on="marketplace", how="left")
                    mp_exib2["var"] = mp_exib2.apply(
                        lambda r: fmt_delta(r["receita"], r.get("rec_ant",0))[0] or "—", axis=1)
                mp_exib2["receita"] = mp_exib2["receita"].map(fmt_brl)
                mp_exib2["ticket"]  = mp_exib2["ticket"].map(fmt_brl)
                mp_exib2["pct"]     = mp_exib2["pct"].map("{:.1f}%".format)
                rename_mp = {"marketplace":"Marketplace","receita":"Receita","notas":"Notas",
                             "itens":"Itens","ticket":"Ticket Médio","pct":"Share","var":"Var. vs Ant."}
                mp_exib2 = mp_exib2.rename(columns=rename_mp)
                cols_show = [c for c in ["Marketplace","Receita","Notas","Itens","Ticket Médio","Share","Var. vs Ant."]
                             if c in mp_exib2.columns]
                st.dataframe(mp_exib2[cols_show], use_container_width=True, hide_index=True)
                st.download_button("📥 Exportar por Plataforma",
                                   data=mp_exib2[cols_show].to_csv(index=False).encode("utf-8"),
                                   file_name="mp_por_plataforma.csv", mime="text/csv")

# ─────────────────────────────────────────────
# RODAPÉ
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#1e2030;font-size:.72rem;"
    "font-family:IBM Plex Mono,monospace;padding:10px 0 20px;'>"
    "⌚ Grupo Seculus · Dashboard v2 · cache 5 min"
    "</div>",
    unsafe_allow_html=True,
)
