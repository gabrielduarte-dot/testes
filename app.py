import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import StringIO
import requests
from datetime import datetime, timedelta
import numpy as np
import json

st.set_page_config(
    page_title="Dashboard de Vendas · Grupo Seculus",
    page_icon="⌚",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,300&family=DM+Mono:wght@400;500&display=swap');
html,body,[class*="css"]{font-family:'DM Sans',sans-serif;}
.stApp{background-color:#080c14;color:#e2e8f0;}
[data-testid="stSidebar"]{display:none;}
[data-testid="stMetric"]{background:linear-gradient(135deg,#111827 0%,#131e35 100%);border:1px solid #1e2d4a;border-radius:14px;padding:20px 24px;transition:all .25s;}
[data-testid="stMetric"]:hover{border-color:#3b6fff;box-shadow:0 0 20px rgba(59,111,255,.15);}
[data-testid="stMetricLabel"]{color:#64748b!important;font-size:.73rem!important;font-weight:600!important;text-transform:uppercase;letter-spacing:.1em;}
[data-testid="stMetricValue"]{color:#f1f5f9!important;font-size:1.55rem!important;font-weight:700!important;font-family:'DM Mono',monospace!important;}
[data-testid="stMetricDelta"]{font-size:.8rem!important;}
h1,h2,h3,h4{color:#f1f5f9!important;}
h1{font-weight:700!important;letter-spacing:-.025em;}
hr{border-color:#1a2540!important;}
.stTabs [data-baseweb="tab-list"]{background:transparent!important;border-bottom:1px solid #1a2540!important;gap:0;padding:0;}
.stTabs [data-baseweb="tab"]{color:#64748b!important;font-weight:500!important;font-size:.88rem!important;padding:10px 20px!important;border-radius:0!important;border-bottom:2px solid transparent!important;}
.stTabs [aria-selected="true"]{color:#e2e8f0!important;border-bottom:2px solid #3b6fff!important;background:transparent!important;}
.stTabs [data-baseweb="tab"]:hover{color:#94a3b8!important;background:rgba(59,111,255,.05)!important;}
.stDataFrame{border:1px solid #1e2d4a!important;border-radius:12px!important;}

.topbar{background:linear-gradient(90deg,#0d1321 0%,#111827 100%);border-bottom:1px solid #1a2540;padding:0 24px;display:flex;align-items:center;justify-content:space-between;height:60px;margin:-1rem -1rem 1.5rem -1rem;position:sticky;top:0;z-index:999;}
.topbar-brand{display:flex;align-items:center;gap:10px;font-size:1rem;font-weight:700;color:#f1f5f9;letter-spacing:-.02em;}
.topbar-brand span{color:#3b6fff;}
.topnav{display:flex;align-items:center;gap:4px;}
.nav-pill{padding:6px 16px;border-radius:8px;font-size:.82rem;font-weight:500;color:#64748b;cursor:pointer;transition:all .2s;border:1px solid transparent;text-decoration:none;white-space:nowrap;}
.nav-pill:hover{color:#e2e8f0;background:rgba(59,111,255,.1);}
.nav-pill.active{color:#fff;background:rgba(59,111,255,.2);border-color:#3b6fff;}
.topbar-right{display:flex;align-items:center;gap:12px;font-size:.75rem;color:#475569;font-family:'DM Mono',monospace;}
.dot-live{width:7px;height:7px;border-radius:50%;background:#10b981;display:inline-block;animation:pulse 2s infinite;}
@keyframes pulse{0%,100%{opacity:1;}50%{opacity:.4;}}

.section-header{display:flex;align-items:center;gap:10px;margin:24px 0 16px 0;}
.section-header h3{margin:0!important;font-size:.95rem!important;font-weight:600!important;color:#94a3b8!important;text-transform:uppercase;letter-spacing:.08em;}
.section-header .divider{flex:1;height:1px;background:linear-gradient(90deg,#1e2d4a,transparent);}

.kpi-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:14px;margin-bottom:20px;}
.kpi-card{background:linear-gradient(135deg,#111827,#131e35);border:1px solid #1e2d4a;border-radius:14px;padding:20px;transition:all .25s;cursor:default;}
.kpi-card:hover{border-color:#3b6fff;box-shadow:0 0 20px rgba(59,111,255,.12);}
.kpi-label{font-size:.72rem;font-weight:600;text-transform:uppercase;letter-spacing:.1em;color:#64748b;margin-bottom:8px;}
.kpi-value{font-size:1.5rem;font-weight:700;color:#f1f5f9;font-family:'DM Mono',monospace;line-height:1.1;}
.kpi-delta{font-size:.78rem;margin-top:6px;font-family:'DM Mono',monospace;}
.kpi-delta.up{color:#10b981;}
.kpi-delta.down{color:#f43f5e;}
.kpi-delta.neutral{color:#64748b;}

.platform-badge{display:inline-flex;align-items:center;gap:6px;padding:3px 10px;border-radius:6px;font-size:.75rem;font-weight:600;font-family:'DM Mono',monospace;}
.badge-ec{background:rgba(59,111,255,.15);color:#6b9fff;border:1px solid rgba(59,111,255,.3);}
.badge-mp{background:rgba(245,158,11,.15);color:#fbbf24;border:1px solid rgba(245,158,11,.3);}
.badge-green{background:rgba(16,185,129,.15);color:#34d399;border:1px solid rgba(16,185,129,.3);}
.badge-red{background:rgba(244,63,94,.15);color:#fb7185;border:1px solid rgba(244,63,94,.3);}
.badge-gray{background:rgba(100,116,139,.15);color:#94a3b8;border:1px solid rgba(100,116,139,.2);}

.insight-card{background:linear-gradient(135deg,#0f1c35,#111e38);border:1px solid #1e3a5f;border-left:3px solid #3b6fff;border-radius:0 12px 12px 0;padding:14px 18px;margin:8px 0;font-size:.88rem;color:#93c5fd;line-height:1.6;}
.warn-card{background:linear-gradient(135deg,#1a1505,#1f1a06);border:1px solid #3d2e00;border-left:3px solid #f59e0b;border-radius:0 12px 12px 0;padding:14px 18px;margin:8px 0;font-size:.88rem;color:#fde68a;line-height:1.6;}
.alert-card{background:linear-gradient(135deg,#1a0510,#1f0614);border:1px solid #4a0d20;border-left:3px solid #f43f5e;border-radius:0 12px 12px 0;padding:14px 18px;margin:8px 0;font-size:.88rem;color:#fca5a5;line-height:1.6;}

.upload-zone{background:linear-gradient(135deg,#0f1421,#111827);border:1px dashed #2a3a5a;border-radius:16px;padding:36px;text-align:center;}
.upload-zone h3{color:#f1f5f9!important;margin-bottom:8px!important;}
.upload-zone p{color:#64748b;font-size:.88rem;}

.filter-bar{background:linear-gradient(90deg,#0d1321,#111827);border:1px solid #1a2540;border-radius:12px;padding:16px 20px;margin-bottom:20px;display:flex;align-items:center;gap:16px;flex-wrap:wrap;}

.source-row{display:flex;align-items:center;justify-content:space-between;padding:10px 0;border-bottom:1px solid #1a2540;}
.source-row:last-child{border-bottom:none;}
.source-dot{width:8px;height:8px;border-radius:50%;display:inline-block;margin-right:6px;}
.connected{background:#10b981;}
.disconnected{background:#374151;}
</style>
""", unsafe_allow_html=True)

EXCLUIR_MARKETPLACE = ["Site Mondaine", "Site Seculus", "Site Timex"]

EC_COLS = [
    "order", "created_at", "customer_name", "state", "status",
    "utmsource", "marketingtags", "payment_method", "installments",
    "quantity_sku", "phone", "sku", "product_name",
    "sku_selling_price", "sku_total_price", "discount_tags", "brand", "livelo_tag"
]

COR_CANAL = {
    "google-shopping": "#4a7cff",
    "Facebook ads":    "#f59e0b",
    "crmback":         "#10b981",
    "ig":              "#ec4899",
    "mais":            "#8b5cf6",
    "Direto":          "#64748b",
    "Outros":          "#475569",
}

COR_MP = {
    "Livelo":       "#fbbf24",
    "Shopee":       "#f97316",
    "Mercado Livre":"#facc15",
    "Amazon":       "#fb923c",
    "Outros":       "#64748b",
}

_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#94a3b8", family="DM Sans", size=12),
    title_font=dict(color="#f1f5f9", size=13, family="DM Sans"),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#94a3b8", size=11)),
    xaxis=dict(gridcolor="#1a2540", linecolor="#1e2d4a", tickcolor="#1e2d4a", zeroline=False),
    yaxis=dict(gridcolor="#1a2540", linecolor="#1e2d4a", tickcolor="#1e2d4a", zeroline=False),
    margin=dict(l=20, r=20, t=45, b=20),
)

def L(**extra):
    d = dict(_BASE)
    d.update(extra)
    return d

def L_inv(**extra):
    d = dict(_BASE)
    d["yaxis"] = dict(_BASE["yaxis"], autorange="reversed")
    d.update(extra)
    return d

def hex_rgba(h, a=0.15):
    h = h.lstrip("#")
    r, g, b = int(h[:2],16), int(h[2:4],16), int(h[4:6],16)
    return f"rgba({r},{g},{b},{a})"

def pct(v, t):
    return v / t * 100 if t else 0

def var_pct(atual, ant):
    if not ant or ant == 0:
        return None
    return (atual - ant) / ant * 100

def fmt_var(v):
    if v is None:
        return None
    return f"{v:+.1f}%"

def fmt_brl(v):
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

for k, d in [
    ("df_ec_raw", None), ("df_mp_raw", None),
    ("url_ec", ""), ("url_mp", ""),
    ("ts_ec", None), ("ts_mp", None),
    ("page", "visao_geral"),
]:
    if k not in st.session_state:
        st.session_state[k] = d

@st.cache_data(ttl=300)
def load_url_csv(url: str, tipo: str):
    try:
        url = url.strip()
        if "docs.google.com" in url:
            sheet_id = url.split("/d/")[1].split("/")[0]
            gid = url.split("gid=")[1].split("&")[0].split("#")[0] if "gid=" in url else None
            url = (f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
                   + (f"&gid={gid}" if gid else ""))
        r = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        try:
            text = r.content.decode("utf-8")
        except UnicodeDecodeError:
            text = r.content.decode("latin-1")
        if tipo == "ec":
            df = pd.read_csv(StringIO(text), header=None, names=EC_COLS)
        else:
            df = pd.read_csv(StringIO(text))
        return df, datetime.now().strftime("%d/%m/%Y %H:%M")
    except Exception as e:
        st.error(f"Erro ao carregar: {e}")
        return None, None

def load_uploaded_ec(file):
    try:
        text = file.read().decode("utf-8")
    except UnicodeDecodeError:
        file.seek(0)
        text = file.read().decode("latin-1")
    return pd.read_csv(StringIO(text), header=None, names=EC_COLS)

def load_uploaded_mp(file):
    try:
        text = file.read().decode("utf-8")
    except UnicodeDecodeError:
        file.seek(0)
        text = file.read().decode("latin-1")
    return pd.read_csv(StringIO(text))

def prep_ec(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["sku_selling_price"] = pd.to_numeric(
        df["sku_selling_price"].astype(str).str.replace(",", ".", regex=False), errors="coerce"
    ).fillna(0)
    df["quantity_sku"] = pd.to_numeric(df["quantity_sku"], errors="coerce").fillna(0)
    df["line_total"] = df["sku_selling_price"] * df["quantity_sku"]
    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce", utc=True)
    df["data"] = df["created_at"].dt.tz_localize(None).dt.normalize()
    livelo_mask = df["livelo_tag"].astype(str).str.strip().str.lower() == "livelo"
    df = df[~livelo_mask].copy()
    df["status"] = df["status"].astype(str).str.strip()
    df["faturado"] = df["status"].isin(["Faturado", "faturado", "Aprovado", "Entregue"])
    df["utmsource"] = df["utmsource"].fillna("Direto")
    df["brand"] = df["brand"].fillna("Seculus")
    df["marketingtags"] = df["marketingtags"].fillna("")
    return df

def prep_mp(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [c.strip().upper() for c in df.columns]
    if "MARKETPLACE" not in df.columns:
        for alt in ["CANAL", "PLATAFORMA", "SOURCE"]:
            if alt in df.columns:
                df = df.rename(columns={alt: "MARKETPLACE"})
                break
    df = df[~df["MARKETPLACE"].isin(EXCLUIR_MARKETPLACE)].copy()
    valor_col = "VALOR" if "VALOR" in df.columns else df.columns[3]
    qty_col   = "QUANTIDADE" if "QUANTIDADE" in df.columns else df.columns[2]
    nota_col  = "NOTA" if "NOTA" in df.columns else df.columns[1]
    data_col  = "DATA" if "DATA" in df.columns else df.columns[0]
    df["valor_num"] = (
        df[valor_col].astype(str)
        .str.replace(r"\.", "", regex=True)
        .str.replace(",", ".", regex=False)
        .pipe(pd.to_numeric, errors="coerce")
        .fillna(0)
    )
    df["qty_num"]  = pd.to_numeric(df[qty_col], errors="coerce").fillna(1)
    df["line_total"] = df["valor_num"] * df["qty_num"]
    df["nota"]    = df[nota_col].astype(str).str.strip()
    df["data"]    = pd.to_datetime(df[data_col], dayfirst=True, errors="coerce")
    df["faturado"] = True
    return df

def agg_ec_orders(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    return (
        df.groupby("order")
        .agg(
            data=("data", "first"),
            status=("status", "first"),
            faturado=("faturado", "first"),
            brand=("brand", "first"),
            utmsource=("utmsource", "first"),
            receita=("line_total", "sum"),
            itens=("quantity_sku", "sum"),
            state=("state", "first"),
        )
        .reset_index()
    )

def agg_mp_notas(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    return (
        df.groupby(["nota", "MARKETPLACE"])
        .agg(
            data=("data", "first"),
            receita=("line_total", "sum"),
            itens=("qty_num", "sum"),
            faturado=("faturado", "first"),
        )
        .reset_index()
    )

def filter_period(df, d_ini, d_fim):
    if df.empty or "data" not in df.columns:
        return df
    return df[(df["data"] >= pd.Timestamp(d_ini)) & (df["data"] <= pd.Timestamp(d_fim))]

def prev_period(ini, fim, modo):
    if modo == "Período anterior equivalente":
        delta = fim - ini
        return ini - delta - timedelta(days=1), ini - timedelta(days=1)
    elif modo == "Mês anterior":
        p = ini.replace(day=1)
        fe = p - timedelta(days=1)
        return fe.replace(day=1), fe
    elif modo == "Mesmo período ano anterior":
        try:
            return ini.replace(year=ini.year-1), fim.replace(year=fim.year-1)
        except ValueError:
            return ini - timedelta(days=365), fim - timedelta(days=365)
    return ini, fim

def kpi_metrics(orders_df):
    if orders_df.empty:
        return {"total":0,"fat":0,"pend":0,"receita":0,"ticket":0,"itens":0}
    fat = orders_df[orders_df["faturado"]]
    total = len(orders_df)
    fat_n = len(fat)
    receita = float(fat["receita"].sum()) if "receita" in fat.columns else 0
    ticket = float(fat["receita"].mean()) if fat_n > 0 else 0
    itens = int(fat["itens"].sum()) if "itens" in fat.columns else fat_n
    pend = total - fat_n
    return {"total":total,"fat":fat_n,"pend":pend,"receita":receita,"ticket":ticket,"itens":itens}

def sparkline(serie, cor="#3b6fff", w=70, h=22):
    s = serie.fillna(0).values
    if len(s) < 2 or s.max() == s.min():
        return ""
    xs = [int(i/(len(s)-1)*w) for i in range(len(s))]
    mn, mx = s.min(), s.max()
    ys = [int(h - (v-mn)/(mx-mn)*(h-4) - 2) for v in s]
    pts = " ".join(f"{x},{y}" for x,y in zip(xs,ys))
    return (f'<svg width="{w}" height="{h}" style="vertical-align:middle">'
            f'<polyline points="{pts}" fill="none" stroke="{cor}" stroke-width="1.8" '
            f'stroke-linecap="round" stroke-linejoin="round"/></svg>')

has_ec = st.session_state.df_ec_raw is not None
has_mp = st.session_state.df_mp_raw is not None

ts_ec = st.session_state.ts_ec or "—"
ts_mp = st.session_state.ts_mp or "—"

st.markdown(f"""
<div class="topbar">
  <div class="topbar-brand">⌚ <span>Seculus</span> · Sales Intelligence</div>
  <div class="topbar-right">
    <span class="dot-live"></span>
    <span>E-com: {ts_ec}</span>
    <span style="color:#1a2540">|</span>
    <span>MKT: {ts_mp}</span>
  </div>
</div>
""", unsafe_allow_html=True)

with st.expander("⚙️  Fontes de Dados & Configurações", expanded=not (has_ec or has_mp)):
    cfg_c1, cfg_c2, cfg_c3 = st.columns([2, 2, 1])

    with cfg_c1:
        st.markdown("**🛒 E-commerce**")
        ec_url = st.text_input("URL Google Sheets / CSV", key="ec_url_inp",
                               placeholder="https://docs.google.com/spreadsheets/d/...")
        ec_file = st.file_uploader("ou upload CSV", type="csv", key="ec_upload")
        if st.button("Carregar E-commerce", use_container_width=True):
            if ec_file:
                df_raw = load_uploaded_ec(ec_file)
                st.session_state.df_ec_raw = df_raw
                st.session_state.ts_ec = datetime.now().strftime("%d/%m/%Y %H:%M")
                st.success(f"✅ {len(df_raw)} linhas carregadas")
                st.rerun()
            elif ec_url.strip():
                with st.spinner("Carregando..."):
                    df_raw, ts = load_url_csv(ec_url.strip(), "ec")
                if df_raw is not None:
                    st.session_state.df_ec_raw = df_raw
                    st.session_state.ts_ec = ts
                    st.success(f"✅ {len(df_raw)} linhas carregadas")
                    st.rerun()

    with cfg_c2:
        st.markdown("**🏪 Marketplace**")
        mp_url = st.text_input("URL Google Sheets / CSV", key="mp_url_inp",
                               placeholder="https://docs.google.com/spreadsheets/d/...")
        mp_file = st.file_uploader("ou upload CSV", type="csv", key="mp_upload")
        if st.button("Carregar Marketplace", use_container_width=True):
            if mp_file:
                df_raw = load_uploaded_mp(mp_file)
                st.session_state.df_mp_raw = df_raw
                st.session_state.ts_mp = datetime.now().strftime("%d/%m/%Y %H:%M")
                st.success(f"✅ {len(df_raw)} linhas carregadas")
                st.rerun()
            elif mp_url.strip():
                with st.spinner("Carregando..."):
                    df_raw, ts = load_url_csv(mp_url.strip(), "mp")
                if df_raw is not None:
                    st.session_state.df_mp_raw = df_raw
                    st.session_state.ts_mp = ts
                    st.success(f"✅ {len(df_raw)} linhas carregadas")
                    st.rerun()

    with cfg_c3:
        st.markdown("**📋 Template**")
        template_ec = """order,created_at,customer_name,state,status,utmsource,marketingtags,payment_method,installments,quantity_sku,phone,sku,product_name,sku_selling_price,sku_total_price,discount_tags,brand,livelo_tag
PED001,2025-01-01 10:00:00Z,Cliente A,SP,Faturado,google-shopping,PRIMEIRACOMPRA,Pix,1,1,,SKU001,Relógio Slim,350.00,350.00,,Seculus,
PED001,2025-01-01 10:00:00Z,Cliente A,SP,Faturado,google-shopping,PRIMEIRACOMPRA,Pix,1,1,,SKU002,Pulseira Extra,80.00,80.00,,Seculus,"""
        template_mp = """DATA,NOTA,QUANTIDADE,VALOR,MARKETPLACE
01/01/2025,NF001,1,269.10,Livelo
01/01/2025,NF001,2,180.00,Shopee"""
        st.download_button("⬇️ Template E-com", data=template_ec,
                           file_name="template_ecommerce.csv", mime="text/csv",
                           use_container_width=True)
        st.download_button("⬇️ Template MKT", data=template_mp,
                           file_name="template_marketplace.csv", mime="text/csv",
                           use_container_width=True)
        if has_ec or has_mp:
            st.markdown("**Status:**")
            st.markdown(
                f"{'🟢' if has_ec else '🔴'} E-commerce &nbsp;&nbsp; "
                f"{'🟢' if has_mp else '🔴'} Marketplace",
                unsafe_allow_html=True,
            )

if not has_ec and not has_mp:
    st.markdown("""
    <div class="upload-zone">
        <h3>Nenhum dado carregado</h3>
        <p>Use o painel acima para carregar os dados de E-commerce e Marketplace.<br>
        Abra "Fontes de Dados & Configurações" e insira os links ou faça upload dos CSVs.</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

df_ec = prep_ec(st.session_state.df_ec_raw) if has_ec else pd.DataFrame()
df_mp = prep_mp(st.session_state.df_mp_raw) if has_mp else pd.DataFrame()

ec_orders_all = agg_ec_orders(df_ec) if has_ec else pd.DataFrame()
mp_notas_all  = agg_mp_notas(df_mp)  if has_mp else pd.DataFrame()

st.markdown("---")
filter_row = st.columns([2, 2, 2, 1, 1, 1, 1, 1])
with filter_row[0]:
    hoje = datetime.today().date()
    data_inicio = st.date_input("De", value=hoje - timedelta(days=30), key="fi")
with filter_row[1]:
    data_fim = st.date_input("Até", value=hoje, key="ff")
with filter_row[2]:
    comp_modo = st.selectbox("Comparar com",
        ["Período anterior equivalente","Mês anterior","Mesmo período ano anterior"])
with filter_row[3]:
    if st.button("7d"):
        st.session_state.fi = hoje - timedelta(days=7)
        st.session_state.ff = hoje
        st.rerun()
with filter_row[4]:
    if st.button("30d"):
        st.session_state.fi = hoje - timedelta(days=30)
        st.session_state.ff = hoje
        st.rerun()
with filter_row[5]:
    if st.button("Mês"):
        st.session_state.fi = hoje.replace(day=1)
        st.session_state.ff = hoje
        st.rerun()
with filter_row[6]:
    if st.button("Ano"):
        st.session_state.fi = hoje.replace(month=1, day=1)
        st.session_state.ff = hoje
        st.rerun()
with filter_row[7]:
    if st.button("Hoje"):
        st.session_state.fi = hoje
        st.session_state.ff = hoje
        st.rerun()

ini_ant, fim_ant = prev_period(data_inicio, data_fim, comp_modo)

ec_period      = filter_period(ec_orders_all, data_inicio, data_fim)
mp_period      = filter_period(mp_notas_all,  data_inicio, data_fim)
ec_period_ant  = filter_period(ec_orders_all, ini_ant, fim_ant)
mp_period_ant  = filter_period(mp_notas_all,  ini_ant, fim_ant)

ec_m  = kpi_metrics(ec_period)
mp_m  = kpi_metrics(mp_period)
ec_ma = kpi_metrics(ec_period_ant)
mp_ma = kpi_metrics(mp_period_ant)

total_receita = ec_m["receita"] + mp_m["receita"]
total_receita_ant = ec_ma["receita"] + mp_ma["receita"]

st.markdown("---")

tab_geral, tab_ec, tab_mp, tab_produtos = st.tabs([
    "📊 Visão Geral",
    "🛒 E-commerce",
    "🏪 Marketplace",
    "🏆 Produtos & SKUs",
])

with tab_geral:
    st.markdown("""
    <div class="section-header">
      <h3>KPIs Consolidados</h3>
      <div class="divider"></div>
    </div>""", unsafe_allow_html=True)

    g1, g2, g3, g4, g5, g6 = st.columns(6)
    g1.metric("💰 Receita Total", fmt_brl(total_receita),
              delta=fmt_var(var_pct(total_receita, total_receita_ant)))
    g2.metric("🛒 E-commerce",    fmt_brl(ec_m["receita"]),
              delta=fmt_var(var_pct(ec_m["receita"], ec_ma["receita"])))
    g3.metric("🏪 Marketplace",   fmt_brl(mp_m["receita"]),
              delta=fmt_var(var_pct(mp_m["receita"], mp_ma["receita"])))
    g4.metric("📦 Pedidos E-com",  f"{ec_m['total']:,}",
              delta=fmt_var(var_pct(ec_m["total"], ec_ma["total"])))
    g5.metric("🎟️ Ticket E-com",  fmt_brl(ec_m["ticket"]),
              delta=fmt_var(var_pct(ec_m["ticket"], ec_ma["ticket"])))
    g6.metric("📑 NFs Marketplace", f"{mp_m['total']:,}",
              delta=fmt_var(var_pct(mp_m["total"], mp_ma["total"])))

    st.markdown("<br>", unsafe_allow_html=True)

    v_ec  = ec_m["receita"]
    v_mp  = mp_m["receita"]
    v_tot = v_ec + v_mp
    if v_tot > 0:
        st.markdown(
            f"<div class='insight-card'>"
            f"📐 <strong>Mix de canal:</strong> E-commerce responde por "
            f"<strong>{pct(v_ec,v_tot):.1f}%</strong> da receita do período "
            f"(R$ {v_ec:,.0f}) e Marketplace por "
            f"<strong>{pct(v_mp,v_tot):.1f}%</strong> (R$ {v_mp:,.0f}).</div>",
            unsafe_allow_html=True,
        )

    if ec_m["total"] > 0:
        taxa_fat_ec = pct(ec_m["fat"], ec_m["total"])
        if taxa_fat_ec < 70:
            st.markdown(
                f"<div class='warn-card'>⚠️ Taxa de faturamento E-commerce em "
                f"<strong>{taxa_fat_ec:.1f}%</strong> — {ec_m['pend']} pedidos pendentes.</div>",
                unsafe_allow_html=True,
            )

    st.markdown("---")

    col_ev1, col_ev2 = st.columns([3, 1])
    with col_ev1:
        st.markdown("""<div class="section-header"><h3>Evolução de Receita</h3><div class="divider"></div></div>""", unsafe_allow_html=True)
        fig_ev = go.Figure()
        if not ec_period.empty and "data" in ec_period.columns:
            ec_ts = (ec_period[ec_period["faturado"]]
                     .groupby("data")["receita"].sum().reset_index())
            fig_ev.add_trace(go.Scatter(
                x=ec_ts["data"], y=ec_ts["receita"], name="E-commerce",
                mode="lines", fill="tozeroy",
                line=dict(color="#3b6fff", width=2.5, shape="spline", smoothing=1.2),
                fillcolor="rgba(59,111,255,0.08)",
            ))
        if not mp_period.empty and "data" in mp_period.columns:
            mp_ts = mp_period.groupby("data")["receita"].sum().reset_index()
            fig_ev.add_trace(go.Scatter(
                x=mp_ts["data"], y=mp_ts["receita"], name="Marketplace",
                mode="lines", fill="tozeroy",
                line=dict(color="#f59e0b", width=2.5, shape="spline", smoothing=1.2),
                fillcolor="rgba(245,158,11,0.06)",
            ))
        fig_ev.update_layout(**L())
        st.plotly_chart(fig_ev, use_container_width=True)

    with col_ev2:
        st.markdown("""<div class="section-header"><h3>Share por Canal</h3><div class="divider"></div></div>""", unsafe_allow_html=True)
        share_data = []
        if v_ec > 0:
            share_data.append({"canal": "E-commerce", "receita": v_ec})
        if v_mp > 0:
            share_data.append({"canal": "Marketplace", "receita": v_mp})
        if share_data:
            df_share = pd.DataFrame(share_data)
            fig_share = px.pie(df_share, names="canal", values="receita",
                               color="canal",
                               color_discrete_map={"E-commerce":"#3b6fff","Marketplace":"#f59e0b"},
                               hole=0.62)
            fig_share.update_traces(textinfo="percent+label", textfont_size=11)
            fig_share.update_layout(**L(margin=dict(l=10,r=10,t=30,b=10)))
            st.plotly_chart(fig_share, use_container_width=True)

    st.markdown("---")

    col_bar1, col_bar2 = st.columns(2)
    with col_bar1:
        st.markdown("""<div class="section-header"><h3>E-com: Receita por Origem (UTM)</h3><div class="divider"></div></div>""", unsafe_allow_html=True)
        if not ec_period.empty and "utmsource" in ec_period.columns:
            utm_g = (ec_period[ec_period["faturado"]]
                     .groupby("utmsource")
                     .agg(receita=("receita","sum"), pedidos=("order","count"))
                     .reset_index()
                     .sort_values("receita", ascending=True))
            fig_utm = px.bar(utm_g, x="receita", y="utmsource", orientation="h",
                             color="utmsource", color_discrete_map=COR_CANAL,
                             labels={"receita":"Receita (R$)","utmsource":"Origem"})
            fig_utm.update_layout(**L_inv())
            st.plotly_chart(fig_utm, use_container_width=True)

    with col_bar2:
        st.markdown("""<div class="section-header"><h3>Marketplace: Receita por Plataforma</h3><div class="divider"></div></div>""", unsafe_allow_html=True)
        if not mp_period.empty and "MARKETPLACE" in mp_period.columns:
            mp_g = (mp_period.groupby("MARKETPLACE")
                    .agg(receita=("receita","sum"))
                    .reset_index()
                    .sort_values("receita", ascending=True))
            fig_mp_bar = px.bar(mp_g, x="receita", y="MARKETPLACE", orientation="h",
                                color="MARKETPLACE", color_discrete_map=COR_MP,
                                labels={"receita":"Receita (R$)","MARKETPLACE":"Plataforma"})
            fig_mp_bar.update_layout(**L_inv())
            st.plotly_chart(fig_mp_bar, use_container_width=True)


with tab_ec:
    if ec_period.empty:
        st.info("Nenhum dado de E-commerce no período.")
        st.stop()

    st.markdown("""<div class="section-header"><h3>Métricas E-commerce</h3><div class="divider"></div></div>""", unsafe_allow_html=True)
    e1,e2,e3,e4,e5,e6 = st.columns(6)
    e1.metric("💰 Receita Fat.",   fmt_brl(ec_m["receita"]),
              delta=fmt_var(var_pct(ec_m["receita"],   ec_ma["receita"])))
    e2.metric("📥 Pedidos",        f"{ec_m['total']:,}",
              delta=fmt_var(var_pct(ec_m["total"],     ec_ma["total"])))
    e3.metric("✅ Faturados",      f"{ec_m['fat']:,}",
              delta=fmt_var(var_pct(ec_m["fat"],       ec_ma["fat"])))
    e4.metric("⏳ Pendentes",      f"{ec_m['pend']:,}")
    e5.metric("🎟️ Ticket Médio",  fmt_brl(ec_m["ticket"]),
              delta=fmt_var(var_pct(ec_m["ticket"],    ec_ma["ticket"])))
    e6.metric("📦 Itens Fat.",     f"{ec_m['itens']:,}",
              delta=fmt_var(var_pct(ec_m["itens"],     ec_ma["itens"])))

    st.markdown("<br>", unsafe_allow_html=True)

    ec_fat = ec_period[ec_period["faturado"]]
    ec_fat_ant = ec_period_ant[ec_period_ant["faturado"]] if not ec_period_ant.empty else pd.DataFrame()

    col_utm1, col_utm2 = st.columns(2)
    with col_utm1:
        st.markdown("""<div class="section-header"><h3>Pedidos Únicos por UTM Source</h3><div class="divider"></div></div>""", unsafe_allow_html=True)
        if not ec_fat.empty and "utmsource" in ec_fat.columns:
            utm_pedidos = (ec_fat.groupby("utmsource")
                          .agg(pedidos=("order","nunique"), receita=("receita","sum"))
                          .reset_index()
                          .sort_values("pedidos", ascending=False))
            utm_pedidos["pct"] = utm_pedidos["pedidos"] / utm_pedidos["pedidos"].sum() * 100
            fig_utm2 = px.bar(utm_pedidos, x="utmsource", y="pedidos",
                              color="utmsource", color_discrete_map=COR_CANAL,
                              labels={"pedidos":"Pedidos Faturados","utmsource":"Origem"},
                              text=utm_pedidos["pedidos"].astype(str) + " (" + utm_pedidos["pct"].map("{:.0f}%".format) + ")")
            fig_utm2.update_traces(textposition="outside")
            fig_utm2.update_layout(**L())
            st.plotly_chart(fig_utm2, use_container_width=True)

            st.markdown("""<div class="section-header"><h3>Receita por UTM: Atual vs Anterior</h3><div class="divider"></div></div>""", unsafe_allow_html=True)
            utm_a = ec_fat.groupby("utmsource")["receita"].sum().reset_index().rename(columns={"receita":"atual"})
            utm_p = ec_fat_ant.groupby("utmsource")["receita"].sum().reset_index().rename(columns={"receita":"anterior"}) if not ec_fat_ant.empty else pd.DataFrame(columns=["utmsource","anterior"])
            utm_comp = utm_a.merge(utm_p, on="utmsource", how="outer").fillna(0)
            fig_utm_comp = go.Figure([
                go.Bar(name="Anterior", x=utm_comp["utmsource"], y=utm_comp["anterior"],
                       marker_color="rgba(100,116,139,0.35)", marker_line_width=0),
                go.Bar(name="Atual",    x=utm_comp["utmsource"], y=utm_comp["atual"],
                       marker_color=[COR_CANAL.get(c,"#3b6fff") for c in utm_comp["utmsource"]],
                       marker_line_width=0),
            ])
            fig_utm_comp.update_layout(barmode="group", **L())
            st.plotly_chart(fig_utm_comp, use_container_width=True)

    with col_utm2:
        st.markdown("""<div class="section-header"><h3>Receita por Origem</h3><div class="divider"></div></div>""", unsafe_allow_html=True)
        if not ec_fat.empty:
            utm_pie = ec_fat.groupby("utmsource")["receita"].sum().reset_index()
            fig_up = px.pie(utm_pie, names="utmsource", values="receita",
                            color="utmsource", color_discrete_map=COR_CANAL, hole=0.55)
            fig_up.update_traces(textinfo="percent+label", textfont_size=11)
            fig_up.update_layout(**L(margin=dict(l=10,r=10,t=30,b=10)))
            st.plotly_chart(fig_up, use_container_width=True)

        st.markdown("""<div class="section-header"><h3>Status dos Pedidos</h3><div class="divider"></div></div>""", unsafe_allow_html=True)
        if not ec_period.empty:
            status_cnt = ec_period["faturado"].map({True:"Faturado",False:"Pendente"}).value_counts().reset_index()
            status_cnt.columns = ["status","qtd"]
            fig_status = px.pie(status_cnt, names="status", values="qtd",
                                color="status",
                                color_discrete_map={"Faturado":"#10b981","Pendente":"#f59e0b"},
                                hole=0.55)
            fig_status.update_traces(textinfo="percent+label", textfont_size=11)
            fig_status.update_layout(**L(margin=dict(l=10,r=10,t=30,b=10)))
            st.plotly_chart(fig_status, use_container_width=True)

    st.markdown("""<div class="section-header"><h3>Evolução Diária — E-commerce</h3><div class="divider"></div></div>""", unsafe_allow_html=True)
    if not ec_fat.empty:
        ec_daily = ec_fat.groupby("data").agg(receita=("receita","sum"), pedidos=("order","count")).reset_index()
        fig_ec_daily = go.Figure()
        fig_ec_daily.add_trace(go.Bar(
            x=ec_daily["data"], y=ec_daily["receita"], name="Receita",
            marker_color="#3b6fff", marker_opacity=0.8, yaxis="y",
        ))
        fig_ec_daily.add_trace(go.Scatter(
            x=ec_daily["data"], y=ec_daily["pedidos"], name="Pedidos",
            mode="lines+markers", line=dict(color="#10b981", width=2),
            yaxis="y2",
        ))
        fig_ec_daily.update_layout(
            **L(),
            yaxis2=dict(overlaying="y", side="right", gridcolor="rgba(0,0,0,0)",
                        tickcolor="#1e2d4a", linecolor="#1e2d4a"),
        )
        st.plotly_chart(fig_ec_daily, use_container_width=True)

    st.markdown("""<div class="section-header"><h3>Detalhamento de Pedidos</h3><div class="divider"></div></div>""", unsafe_allow_html=True)
    ec_disp = ec_period[["order","data","status","utmsource","receita","itens","state"]].copy()
    ec_disp["receita"] = ec_disp["receita"].map(fmt_brl)
    ec_disp = ec_disp.sort_values("data", ascending=False)
    st.dataframe(ec_disp, use_container_width=True, hide_index=True)
    st.download_button("📥 Exportar E-commerce",
                       data=ec_period.to_csv(index=False).encode("utf-8"),
                       file_name="ecommerce_periodo.csv", mime="text/csv")

    if has_ec and not df_ec.empty:
        st.markdown("""<div class="section-header"><h3>Receita por Marca — E-commerce</h3><div class="divider"></div></div>""", unsafe_allow_html=True)
        df_ec_f = filter_period(df_ec, data_inicio, data_fim)
        if not df_ec_f.empty and "brand" in df_ec_f.columns:
            brand_rec = (df_ec_f[df_ec_f["faturado"]]
                        .groupby(["order","brand"])["line_total"].sum()
                        .reset_index()
                        .groupby("brand")["line_total"].sum()
                        .reset_index()
                        .rename(columns={"line_total":"receita"})
                        .sort_values("receita", ascending=False))
            fig_brand = px.bar(brand_rec, x="brand", y="receita",
                               labels={"receita":"Receita (R$)","brand":"Marca"},
                               color="brand",
                               color_discrete_sequence=["#3b6fff","#f59e0b","#10b981","#f43f5e"])
            fig_brand.update_layout(**L())
            st.plotly_chart(fig_brand, use_container_width=True)


with tab_mp:
    if mp_period.empty:
        st.info("Nenhum dado de Marketplace no período.")
        st.stop()

    st.markdown("""<div class="section-header"><h3>Métricas Marketplace</h3><div class="divider"></div></div>""", unsafe_allow_html=True)
    m1,m2,m3,m4 = st.columns(4)
    m1.metric("💰 Receita",        fmt_brl(mp_m["receita"]),
              delta=fmt_var(var_pct(mp_m["receita"], mp_ma["receita"])))
    m2.metric("📑 Notas Fiscais",  f"{mp_m['total']:,}",
              delta=fmt_var(var_pct(mp_m["total"],   mp_ma["total"])))
    m3.metric("📦 Itens",          f"{mp_m['itens']:,}",
              delta=fmt_var(var_pct(mp_m["itens"],   mp_ma["itens"])))
    m4.metric("🎟️ Ticket NF",     fmt_brl(mp_m["ticket"]),
              delta=fmt_var(var_pct(mp_m["ticket"],  mp_ma["ticket"])))

    st.markdown("<br>", unsafe_allow_html=True)

    col_mp1, col_mp2 = st.columns(2)
    with col_mp1:
        st.markdown("""<div class="section-header"><h3>Receita por Plataforma</h3><div class="divider"></div></div>""", unsafe_allow_html=True)
        plat_g = (mp_period.groupby("MARKETPLACE")
                  .agg(receita=("receita","sum"), notas=("nota","nunique"), itens=("itens","sum"))
                  .reset_index()
                  .sort_values("receita", ascending=False))
        fig_plat = px.bar(plat_g, x="MARKETPLACE", y="receita",
                          color="MARKETPLACE", color_discrete_map=COR_MP,
                          labels={"receita":"Receita (R$)","MARKETPLACE":""},
                          text=plat_g["receita"].map(lambda x: f"R$ {x:,.0f}"))
        fig_plat.update_traces(textposition="outside")
        fig_plat.update_layout(**L())
        st.plotly_chart(fig_plat, use_container_width=True)

    with col_mp2:
        st.markdown("""<div class="section-header"><h3>Share por Plataforma</h3><div class="divider"></div></div>""", unsafe_allow_html=True)
        fig_plat_pie = px.pie(plat_g, names="MARKETPLACE", values="receita",
                              color="MARKETPLACE", color_discrete_map=COR_MP, hole=0.55)
        fig_plat_pie.update_traces(textinfo="percent+label", textfont_size=11)
        fig_plat_pie.update_layout(**L(margin=dict(l=10,r=10,t=30,b=10)))
        st.plotly_chart(fig_plat_pie, use_container_width=True)

    st.markdown("""<div class="section-header"><h3>Evolução Diária — Marketplace</h3><div class="divider"></div></div>""", unsafe_allow_html=True)
    mp_daily = mp_period.groupby(["data","MARKETPLACE"])["receita"].sum().reset_index()
    fig_mp_daily = px.area(mp_daily, x="data", y="receita", color="MARKETPLACE",
                           color_discrete_map=COR_MP,
                           labels={"receita":"Receita (R$)","data":""})
    fig_mp_daily.update_layout(**L())
    st.plotly_chart(fig_mp_daily, use_container_width=True)

    st.markdown("""<div class="section-header"><h3>Atual vs Período Anterior — por Plataforma</h3><div class="divider"></div></div>""", unsafe_allow_html=True)
    mp_a_agg = mp_period.groupby("MARKETPLACE")["receita"].sum().reset_index().rename(columns={"receita":"atual"})
    mp_p_agg = (mp_period_ant.groupby("MARKETPLACE")["receita"].sum().reset_index().rename(columns={"receita":"anterior"})
                if not mp_period_ant.empty else pd.DataFrame(columns=["MARKETPLACE","anterior"]))
    mp_comp = mp_a_agg.merge(mp_p_agg, on="MARKETPLACE", how="outer").fillna(0)
    mp_comp["var"] = mp_comp.apply(
        lambda r: fmt_var(var_pct(r["atual"], r["anterior"])) or "—", axis=1)
    fig_mp_comp = go.Figure([
        go.Bar(name="Anterior", x=mp_comp["MARKETPLACE"], y=mp_comp["anterior"],
               marker_color="rgba(100,116,139,0.35)", marker_line_width=0),
        go.Bar(name="Atual",    x=mp_comp["MARKETPLACE"], y=mp_comp["atual"],
               marker_color=[COR_MP.get(c,"#f59e0b") for c in mp_comp["MARKETPLACE"]],
               marker_line_width=0, text=mp_comp["var"], textposition="outside"),
    ])
    fig_mp_comp.update_layout(barmode="group", **L())
    st.plotly_chart(fig_mp_comp, use_container_width=True)

    st.markdown("""<div class="section-header"><h3>Detalhamento por Nota Fiscal</h3><div class="divider"></div></div>""", unsafe_allow_html=True)
    mp_disp = mp_period[["nota","data","MARKETPLACE","receita","itens"]].copy()
    mp_disp["receita"] = mp_disp["receita"].map(fmt_brl)
    mp_disp = mp_disp.sort_values("data", ascending=False)
    st.dataframe(mp_disp, use_container_width=True, hide_index=True)
    st.download_button("📥 Exportar Marketplace",
                       data=mp_period.to_csv(index=False).encode("utf-8"),
                       file_name="marketplace_periodo.csv", mime="text/csv")


with tab_produtos:
    if not has_ec or df_ec.empty:
        st.info("Dados de E-commerce necessários para análise de produtos.")
        st.stop()

    df_ec_f = filter_period(df_ec, data_inicio, data_fim)
    df_ec_f_ant = filter_period(df_ec, ini_ant, fim_ant)

    if df_ec_f.empty:
        st.info("Sem dados de produtos no período.")
        st.stop()

    df_ec_fat = df_ec_f[df_ec_f["faturado"]]

    col_pf1, col_pf2 = st.columns([3,1])
    with col_pf1:
        marcas_disp = sorted(df_ec_fat["brand"].dropna().unique().tolist()) if "brand" in df_ec_fat.columns else []
        marcas_sel_p = st.multiselect("Filtrar por marca", marcas_disp, default=marcas_disp, key="prod_brand")
    with col_pf2:
        top_n_p = st.selectbox("Top N", [5,10,15,20], index=1, key="top_n_prod")

    df_prod = df_ec_fat[df_ec_fat["brand"].isin(marcas_sel_p)] if marcas_sel_p else df_ec_fat

    st.markdown("""<div class="section-header"><h3>Top Produtos por Receita e Quantidade</h3><div class="divider"></div></div>""", unsafe_allow_html=True)
    cp1, cp2 = st.columns(2)
    with cp1:
        top_rec_p = (df_prod.groupby(["brand","product_name"])["line_total"]
                    .sum().reset_index()
                    .sort_values("line_total", ascending=False).head(top_n_p))
        fig_pr = px.bar(top_rec_p, x="line_total", y="product_name", color="brand",
                        orientation="h",
                        color_discrete_sequence=["#3b6fff","#f59e0b","#10b981","#f43f5e"],
                        labels={"line_total":"Receita (R$)","product_name":"","brand":"Marca"})
        fig_pr.update_layout(**L_inv(title="Receita por Produto"))
        st.plotly_chart(fig_pr, use_container_width=True)

    with cp2:
        top_qtd_p = (df_prod.groupby(["brand","product_name"])["quantity_sku"]
                    .sum().reset_index()
                    .sort_values("quantity_sku", ascending=False).head(top_n_p))
        fig_pq = px.bar(top_qtd_p, x="quantity_sku", y="product_name", color="brand",
                        orientation="h",
                        color_discrete_sequence=["#3b6fff","#f59e0b","#10b981","#f43f5e"],
                        labels={"quantity_sku":"Unidades","product_name":"","brand":"Marca"})
        fig_pq.update_layout(**L_inv(title="Volume por Produto"))
        st.plotly_chart(fig_pq, use_container_width=True)

    st.markdown("""<div class="section-header"><h3>Análise 80/20 de Receita</h3><div class="divider"></div></div>""", unsafe_allow_html=True)
    prod_rec = (df_prod.groupby("product_name")["line_total"].sum()
               .sort_values(ascending=False).reset_index())
    total_r = prod_rec["line_total"].sum()
    if total_r > 0:
        prod_rec["cum_pct"] = prod_rec["line_total"].cumsum() / total_r * 100
        prod_rec["pct"]     = prod_rec["line_total"] / total_r * 100
        n80 = int((prod_rec["cum_pct"] <= 80).sum()) + 1
        pct_cat = n80 / len(prod_rec) * 100
        st.markdown(
            f"<div class='insight-card'>📐 <strong>Concentração de Pareto:</strong> "
            f"<strong>{n80} produto(s) ({pct_cat:.0f}% do catálogo)</strong> "
            f"correspondem a 80% da receita faturada no período.</div>",
            unsafe_allow_html=True,
        )
        fig_pareto = go.Figure()
        fig_pareto.add_trace(go.Bar(
            x=prod_rec["product_name"].str[:40], y=prod_rec["line_total"],
            marker_color="#3b6fff", name="Receita", opacity=0.85,
        ))
        fig_pareto.add_trace(go.Scatter(
            x=prod_rec["product_name"].str[:40], y=prod_rec["cum_pct"],
            mode="lines+markers", name="% Acumulado",
            line=dict(color="#f59e0b", width=2),
            yaxis="y2",
        ))
        fig_pareto.add_hline(y=80, line_dash="dot", line_color="#f43f5e",
                             annotation_text="80%", yref="y2",
                             annotation=dict(font_color="#f43f5e"))
        fig_pareto.update_layout(
            **L(),
            xaxis_tickangle=-30,
            yaxis2=dict(overlaying="y", side="right", range=[0,105],
                        ticksuffix="%", gridcolor="rgba(0,0,0,0)",
                        tickcolor="#1e2d4a", linecolor="#1e2d4a"),
        )
        st.plotly_chart(fig_pareto, use_container_width=True)

    st.markdown("""<div class="section-header"><h3>Tabela Detalhada por SKU</h3><div class="divider"></div></div>""", unsafe_allow_html=True)
    sku_tab = (df_prod.groupby(["brand","sku","product_name"])
              .agg(
                  receita=("line_total","sum"),
                  qtd=("quantity_sku","sum"),
                  pedidos=("order","nunique"),
              ).reset_index()
              .sort_values("receita", ascending=False))

    if not df_ec_f_ant.empty:
        df_fat_ant = df_ec_f_ant[df_ec_f_ant["faturado"]]
        sku_ant = (df_fat_ant.groupby("sku")["line_total"].sum()
                  .reset_index().rename(columns={"line_total":"receita_ant"}))
        sku_tab = sku_tab.merge(sku_ant, on="sku", how="left").fillna(0)
        sku_tab["var_vs_ant"] = sku_tab.apply(
            lambda r: fmt_var(var_pct(r["receita"], r["receita_ant"])) or "—", axis=1)
    else:
        sku_tab["var_vs_ant"] = "—"

    sku_tab["ticket_medio"] = (sku_tab["receita"] / sku_tab["pedidos"].replace(0, np.nan)).fillna(0)
    sku_tab_disp = sku_tab.copy()
    sku_tab_disp["receita"]      = sku_tab_disp["receita"].map(fmt_brl)
    sku_tab_disp["ticket_medio"] = sku_tab_disp["ticket_medio"].map(fmt_brl)
    sku_tab_disp = sku_tab_disp.rename(columns={
        "brand":"Marca","sku":"SKU","product_name":"Produto",
        "receita":"Receita","qtd":"Qtd","pedidos":"Pedidos",
        "ticket_medio":"Ticket Médio","var_vs_ant":"Var. vs Ant.",
    })
    st.dataframe(sku_tab_disp, use_container_width=True, hide_index=True)
    st.download_button("📥 Exportar SKUs",
                       data=sku_tab.to_csv(index=False).encode("utf-8"),
                       file_name="skus_periodo.csv", mime="text/csv")

st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#1e2d4a;font-size:.72rem;font-family:DM Mono,monospace;'>"
    "⌚ Grupo Seculus · Sales Intelligence · Cache 5min · "
    "Livelo e sites próprios excluídos automaticamente"
    "</div>",
    unsafe_allow_html=True,
)
