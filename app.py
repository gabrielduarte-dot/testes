import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import StringIO
import requests
from datetime import datetime, timedelta, date
import numpy as np

st.set_page_config(
    page_title="Dashboard de Vendas · Grupo Seculus",
    page_icon="⌚",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700&family=DM+Mono:wght@400;500&display=swap');
html,body,[class*="css"]{font-family:'DM Sans',sans-serif;}
.stApp{background-color:#080c14;color:#e2e8f0;}
[data-testid="stSidebar"]{display:none;}
[data-testid="stMetric"]{background:linear-gradient(135deg,#111827 0%,#131e35 100%);border:1px solid #1e2d4a;border-radius:14px;padding:20px 24px;transition:all .25s;}
[data-testid="stMetric"]:hover{border-color:#3b6fff;box-shadow:0 0 24px rgba(59,111,255,.14);}
[data-testid="stMetricLabel"]{color:#64748b!important;font-size:.72rem!important;font-weight:600!important;text-transform:uppercase;letter-spacing:.1em;}
[data-testid="stMetricValue"]{color:#f1f5f9!important;font-size:1.5rem!important;font-weight:700!important;font-family:'DM Mono',monospace!important;}
[data-testid="stMetricDelta"]{font-size:.8rem!important;}
h1,h2,h3,h4{color:#f1f5f9!important;}
hr{border-color:#1a2540!important;}
.stTabs [data-baseweb="tab-list"]{background:transparent!important;border-bottom:1px solid #1a2540!important;gap:0;padding:0;}
.stTabs [data-baseweb="tab"]{color:#64748b!important;font-weight:500!important;font-size:.88rem!important;padding:10px 22px!important;border-radius:0!important;border-bottom:2px solid transparent!important;}
.stTabs [aria-selected="true"]{color:#e2e8f0!important;border-bottom:2px solid #3b6fff!important;background:transparent!important;}
.stTabs [data-baseweb="tab"]:hover{color:#94a3b8!important;background:rgba(59,111,255,.05)!important;}
.stDataFrame{border:1px solid #1e2d4a!important;border-radius:12px!important;}
.topbar{background:linear-gradient(90deg,#0d1321,#111827);border-bottom:1px solid #1a2540;padding:0 28px;display:flex;align-items:center;justify-content:space-between;height:58px;margin:-1rem -1rem 1.5rem -1rem;position:sticky;top:0;z-index:999;}
.topbar-brand{display:flex;align-items:center;gap:10px;font-size:1rem;font-weight:700;color:#f1f5f9;letter-spacing:-.02em;}
.topbar-brand span{color:#3b6fff;}
.topbar-right{display:flex;align-items:center;gap:14px;font-size:.73rem;color:#475569;font-family:'DM Mono',monospace;}
.dot{width:7px;height:7px;border-radius:50%;background:#10b981;display:inline-block;animation:blink 2s infinite;}
@keyframes blink{0%,100%{opacity:1;}50%{opacity:.35;}}
.sh{display:flex;align-items:center;gap:10px;margin:22px 0 12px;}
.sh h4{margin:0!important;font-size:.78rem!important;font-weight:700!important;color:#475569!important;text-transform:uppercase;letter-spacing:.1em;}
.sh .ln{flex:1;height:1px;background:linear-gradient(90deg,#1e2d4a,transparent);}
.info{background:linear-gradient(135deg,#0f1c35,#111e38);border:1px solid #1e3a5f;border-left:3px solid #3b6fff;border-radius:0 12px 12px 0;padding:12px 16px;margin:8px 0;font-size:.85rem;color:#93c5fd;line-height:1.6;}
.warn{background:linear-gradient(135deg,#1a1505,#1f1a06);border:1px solid #3d2e00;border-left:3px solid #f59e0b;border-radius:0 12px 12px 0;padding:12px 16px;margin:8px 0;font-size:.85rem;color:#fde68a;line-height:1.6;}
.zone{background:linear-gradient(135deg,#0f1421,#111827);border:1px dashed #2a3a5a;border-radius:16px;padding:40px;text-align:center;}
.zone h3{color:#f1f5f9!important;margin-bottom:8px!important;}
.zone p{color:#64748b;font-size:.88rem;}
.rc{background:linear-gradient(135deg,#111827,#131e35);border:1px solid #1e2d4a;border-radius:14px;padding:20px 22px;}
.rc-title{font-size:.75rem;font-weight:700;text-transform:uppercase;letter-spacing:.1em;margin:0 0 14px 0;}
.rc-row{display:flex;justify-content:space-between;align-items:center;padding:5px 0;border-bottom:1px solid #1a2540;font-size:.83rem;color:#94a3b8;}
.rc-row:last-child{border-bottom:none;}
.rc-val{font-family:'DM Mono',monospace;color:#f1f5f9;font-weight:600;font-size:.88rem;}
.rc-badge{padding:2px 8px;border-radius:6px;font-size:.75rem;font-weight:700;font-family:'DM Mono',monospace;}
.rc-green{background:rgba(16,185,129,.15);color:#34d399;border:1px solid rgba(16,185,129,.25);}
.rc-red{background:rgba(244,63,94,.15);color:#fb7185;border:1px solid rgba(244,63,94,.25);}
.rc-amber{background:rgba(245,158,11,.15);color:#fbbf24;border:1px solid rgba(245,158,11,.25);}
.meta-panel{background:linear-gradient(135deg,#0d1321,#111827);border:1px solid #1e2d4a;border-radius:16px;padding:22px 26px;margin-bottom:16px;}
.meta-panel-title{font-size:.72rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:#475569;margin:0 0 16px 0;}
.meta-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;}
.meta-card{background:linear-gradient(135deg,#111827,#131e35);border:1px solid #1e2d4a;border-radius:12px;padding:16px 18px;transition:border-color .2s;}
.meta-card:hover{border-color:#3b6fff;}
.meta-card-label{font-size:.68rem;font-weight:600;text-transform:uppercase;letter-spacing:.1em;color:#64748b;margin-bottom:6px;}
.meta-card-value{font-size:1.35rem;font-weight:700;font-family:'DM Mono',monospace;color:#f1f5f9;line-height:1.1;margin-bottom:4px;}
.meta-card-sub{font-size:.75rem;font-family:'DM Mono',monospace;font-weight:600;}
.meta-card-sub.pos{color:#10b981;}
.meta-card-sub.neg{color:#f43f5e;}
.meta-card-sub.neu{color:#64748b;}
.meta-card.highlight{border-color:#f43f5e;background:linear-gradient(135deg,#1a0a12,#1f0d18);}
.meta-card.highlight .meta-card-value{color:#f43f5e;}
.meta-card.ok{border-color:#10b981;background:linear-gradient(135deg,#0a1a14,#0d1f18);}
.meta-card.ok .meta-card-value{color:#10b981;}
.meta-bar-wrap{margin-top:10px;height:5px;border-radius:3px;background:#1e2d4a;overflow:hidden;}
.meta-bar-fill{height:100%;border-radius:3px;transition:width .4s;}
.meta-sep{border:none;border-top:1px solid #1a2540;margin:16px 0;}
.prod-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:14px;margin-top:12px;}
.prod-card{background:linear-gradient(135deg,#111827,#131e35);border:1px solid #1e2d4a;border-radius:14px;overflow:hidden;transition:all .25s;display:flex;flex-direction:column;}
.prod-card:hover{border-color:#3b6fff;box-shadow:0 0 20px rgba(59,111,255,.12);transform:translateY(-2px);}
.prod-img-wrap{background:#0d1321;height:160px;display:flex;align-items:center;justify-content:center;overflow:hidden;border-bottom:1px solid #1a2540;}
.prod-img-wrap img{max-height:150px;max-width:100%;object-fit:contain;transition:transform .3s;}
.prod-card:hover .prod-img-wrap img{transform:scale(1.06);}
.prod-img-placeholder{width:60px;height:60px;border-radius:50%;background:#1e2d4a;display:flex;align-items:center;justify-content:center;font-size:1.6rem;color:#3b6fff;}
.prod-info{padding:14px 16px;flex:1;display:flex;flex-direction:column;gap:4px;}
.prod-badge{display:inline-block;padding:2px 8px;border-radius:6px;font-size:.7rem;font-weight:700;font-family:'DM Mono',monospace;margin-bottom:4px;}
.prod-name{font-size:.82rem;font-weight:600;color:#e2e8f0;line-height:1.4;margin-bottom:6px;}
.prod-sku{font-size:.7rem;color:#475569;font-family:'DM Mono',monospace;}
.prod-stats{display:flex;gap:12px;margin-top:auto;padding-top:10px;border-top:1px solid #1a2540;}
.prod-stat{display:flex;flex-direction:column;gap:2px;}
.prod-stat-label{font-size:.65rem;color:#475569;text-transform:uppercase;letter-spacing:.08em;font-weight:600;}
.prod-stat-val{font-size:.85rem;font-weight:700;color:#f1f5f9;font-family:'DM Mono',monospace;}
</style>
""", unsafe_allow_html=True)

ECOM_CANAIS = ["Site Mondaine", "Site Seculus", "Site Timex", "Multimarcas"]
MARCA_MAP   = {
    "Site Mondaine": "Mondaine",
    "Site Seculus":  "Seculus",
    "Site Timex":    "Timex",
    "Multimarcas":   "E-time",
}
COR_UTM = {
    "google-shopping": "#3b6fff",
    "Facebook ads":    "#f59e0b",
    "crmback":         "#10b981",
    "ig":              "#ec4899",
    "mais":            "#8b5cf6",
    "Direto":          "#64748b",
    "Outros":          "#475569",
}
COR_MARCA = {
    "Seculus":  "#3b6fff",
    "Mondaine": "#f59e0b",
    "Timex":    "#10b981",
    "E-time":   "#f43f5e",
}
COR_MP = {
    "Livelo":        "#fbbf24",
    "Shopee":        "#f97316",
    "Mercado Livre": "#facc15",
    "Amazon":        "#fb923c",
    "Outros":        "#64748b",
}
IMG_BASE_URL = "https://storage.googleapis.com/banco-imagens/Relogios"
IMG_EXT      = ".jpg"
META_URL = "https://docs.google.com/spreadsheets/d/1r4WwX_UjF12weYCYn3P5D2BzAJUhXrdJ2oQk95CgupE/export?format=csv"

EC_COLS_19 = [
    "order","created_at","customer_name","state","status","utmsource",
    "marketingtags","payment_method","installments","quantity_sku","phone",
    "sku","product_name","sku_selling_price","sku_total_price",
    "discount_tags","brand","livelo_tag","foto_produto",
]
EC_COLS_18 = [
    "order","created_at","customer_name","state","status","utmsource",
    "marketingtags","payment_method","installments","quantity_sku","phone",
    "sku","product_name","sku_selling_price","sku_total_price",
    "discount_tags","brand","livelo_tag",
]
EC_COLS_18F = [
    "order","created_at","customer_name","state","status","utmsource",
    "payment_method","installments","quantity_sku","phone",
    "sku","product_name","sku_selling_price","sku_total_price",
    "discount_tags","brand","livelo_tag","foto_produto",
]
EC_COLS_17 = [
    "order","created_at","customer_name","state","status","utmsource",
    "payment_method","installments","quantity_sku","phone",
    "sku","product_name","sku_selling_price","sku_total_price",
    "discount_tags","brand","livelo_tag",
]

def _ec_colnames(text: str) -> list:
    first = text.split("\n")[0]
    import csv as _csv
    ncols = len(list(_csv.reader([first]))[0])
    if ncols >= 19: return EC_COLS_19
    if ncols == 18: return EC_COLS_18
    if ncols == 17: return EC_COLS_17
    return EC_COLS_17

_BL = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#94a3b8", family="DM Sans", size=12),
    title_font=dict(color="#f1f5f9", size=13, family="DM Sans"),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#94a3b8", size=11)),
    xaxis=dict(gridcolor="#1a2540", linecolor="#1e2d4a", tickcolor="#1e2d4a", zeroline=False),
    yaxis=dict(gridcolor="#1a2540", linecolor="#1e2d4a", tickcolor="#1e2d4a", zeroline=False),
    margin=dict(l=20, r=20, t=45, b=20),
)
def L(**kw):
    d = dict(_BL); d.update(kw); return d
def Li(**kw):
    d = dict(_BL); d["yaxis"] = dict(_BL["yaxis"], autorange="reversed"); d.update(kw); return d

def brl(v):
    try: return f"R$ {float(v):,.0f}".replace(",","X").replace(".",",").replace("X",".")
    except: return "R$ 0"

def vp(a, b):
    if not b or b == 0: return None
    return (a - b) / b * 100

def fv(v):
    return f"{v:+.1f}%" if v is not None else None

def fdt(df, ini, fim):
    if df is None or df.empty or "data" not in df.columns: return pd.DataFrame()
    return df[(df["data"] >= pd.Timestamp(ini)) & (df["data"] <= pd.Timestamp(fim))].copy()

def prev_p(ini, fim, modo):
    if modo == "Período anterior equivalente":
        d = fim - ini; return ini - d - timedelta(days=1), ini - timedelta(days=1)
    if modo == "Mês anterior":
        p = ini.replace(day=1); fe = p - timedelta(days=1); return fe.replace(day=1), fe
    if modo == "Mesmo período ano anterior":
        try: return ini.replace(year=ini.year-1), fim.replace(year=fim.year-1)
        except: return ini-timedelta(days=365), fim-timedelta(days=365)
    return ini, fim

def sh(title):
    st.markdown(f'<div class="sh"><h4>{title}</h4><div class="ln"></div></div>', unsafe_allow_html=True)

def parse_num_br(s):
    try:
        return float(str(s).replace(".","").replace(",","."))
    except Exception:
        return 0.0

@st.cache_data(ttl=3600)
def load_metas() -> pd.DataFrame:
    try:
        r = requests.get(META_URL, timeout=15, headers={"User-Agent":"Mozilla/5.0"})
        r.raise_for_status()
        try:    text = r.content.decode("utf-8")
        except: text = r.content.decode("latin-1")
        df = pd.read_csv(StringIO(text), dtype=str)
        df.columns = [c.strip() for c in df.columns]
        df["mes_dt"] = pd.to_datetime(df["Mês"], dayfirst=True, errors="coerce")
        for col in ["Meta B2C","Meta MKT PLACE","META TOTAL",
                    "Realizado B2C","Realizado MKT PLACE","Realizado REAL TOTAL","DIF"]:
            if col in df.columns:
                df[col] = df[col].apply(parse_num_br)
        return df.dropna(subset=["mes_dt"])
    except Exception:
        return pd.DataFrame()

def metas_do_mes(df_meta: pd.DataFrame, ano: int, mes: int) -> dict:
    row = df_meta[(df_meta["mes_dt"].dt.year == ano) & (df_meta["mes_dt"].dt.month == mes)]
    if row.empty:
        return {"meta_ec":0,"meta_mkt":0,"meta_total":0,
                "real_ec":0,"real_mkt":0,"real_total":0,"dif":0}
    r = row.iloc[0]
    return {
        "meta_ec":    float(r.get("Meta B2C",0) or 0),
        "meta_mkt":   float(r.get("Meta MKT PLACE",0) or 0),
        "meta_total": float(r.get("META TOTAL",0) or 0),
        "real_ec":    float(r.get("Realizado B2C",0) or 0),
        "real_mkt":   float(r.get("Realizado MKT PLACE",0) or 0),
        "real_total": float(r.get("Realizado REAL TOTAL",0) or 0),
        "dif":        float(r.get("DIF",0) or 0),
    }

def metas_acumulado(df_meta: pd.DataFrame, ano: int, ate_mes: int) -> dict:
    rows = df_meta[(df_meta["mes_dt"].dt.year == ano) & (df_meta["mes_dt"].dt.month <= ate_mes)]
    if rows.empty:
        return {"meta_ec":0,"meta_mkt":0,"meta_total":0,
                "real_ec":0,"real_mkt":0,"real_total":0,"dif":0}
    return {
        "meta_ec":    float(rows["Meta B2C"].sum()),
        "meta_mkt":   float(rows["Meta MKT PLACE"].sum()),
        "meta_total": float(rows["META TOTAL"].sum()),
        "real_ec":    float(rows["Realizado B2C"].sum()),
        "real_mkt":   float(rows["Realizado MKT PLACE"].sum()),
        "real_total": float(rows["Realizado REAL TOTAL"].sum()),
        "dif":        float(rows["DIF"].sum()),
    }

def metas_ano(df_meta: pd.DataFrame, ano: int) -> dict:
    rows = df_meta[df_meta["mes_dt"].dt.year == ano]
    if rows.empty:
        return {"meta_ec":0,"meta_mkt":0,"meta_total":0,
                "real_ec":0,"real_mkt":0,"real_total":0,"dif":0}
    return {
        "meta_ec":    float(rows["Meta B2C"].sum()),
        "meta_mkt":   float(rows["Meta MKT PLACE"].sum()),
        "meta_total": float(rows["META TOTAL"].sum()),
        "real_ec":    float(rows["Realizado B2C"].sum()),
        "real_mkt":   float(rows["Realizado MKT PLACE"].sum()),
        "real_total": float(rows["Realizado REAL TOTAL"].sum()),
        "dif":        float(rows["DIF"].sum()),
    }

for k, v in [("df_mp_raw", None),("df_ec_raw", None),("ts_mp", None),("ts_ec", None)]:
    if k not in st.session_state:
        st.session_state[k] = v

@st.cache_data(ttl=300)
def load_url(url, tipo):
    try:
        url = url.strip()
        if "docs.google.com" in url:
            sid = url.split("/d/")[1].split("/")[0]
            gid = url.split("gid=")[1].split("&")[0].split("#")[0] if "gid=" in url else None
            url = (f"https://docs.google.com/spreadsheets/d/{sid}/export?format=csv"
                   + (f"&gid={gid}" if gid else ""))
        r = requests.get(url, timeout=20, headers={"User-Agent":"Mozilla/5.0"})
        r.raise_for_status()
        try:    raw = r.content.decode("utf-8")
        except: raw = r.content.decode("latin-1")
        df = parse_csv(raw, tipo)
        return df, datetime.now().strftime("%d/%m/%Y %H:%M")
    except Exception as e:
        st.error(f"Erro ao carregar: {e}"); return None, None

def parse_csv(text, tipo):
    if tipo == "ec":
        cols = _ec_colnames(text)
        return pd.read_csv(StringIO(text), header=None, names=cols,
                           dtype=str, keep_default_na=False, na_values=[""])
    return pd.read_csv(StringIO(text), dtype=str, keep_default_na=False, na_values=[""])

def read_upload(f, tipo):
    f.seek(0)
    try:    text = f.read().decode("utf-8")
    except: f.seek(0); text = f.read().decode("latin-1")
    return parse_csv(text, tipo)

def prep_mp(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw.copy()
    df.columns = [str(c).strip() for c in df.columns]

    col_up = {c: c.upper() for c in df.columns}
    df = df.rename(columns=col_up)

    name_map = {}
    for tgt, alts in [
        ("DATA",        ["DATA","DATE","DT","DATA_NF","DATA DO FATURAMENTO","DATA_FATURAMENTO"]),
        ("NOTA",        ["NOTA","NF","INVOICE","ORDER_ID","NUMERO_NF","NUM_NF","NUMERO","NOTA FISCAL"]),
        ("QUANTIDADE",  ["QUANTIDADE","QTY","QUANTITY","QTD","QTDE","QTDADE","QUANTIDADE FATURADA"]),
        ("VALOR",       ["VALOR","PRICE","UNIT_PRICE","VALOR_UNITARIO","VALOR_UNIT","VLR","VALOR UNITÁRIO FINAL","VALOR UNITARIO FINAL"]),
        ("MARKETPLACE", ["MARKETPLACE","CANAL","PLATAFORMA","SOURCE","CHANNEL","LOJA","SELLER","SITE"]),
        ("REFERENCIA",  ["REFERENCIA","REFERÊNCIA","REF","SKU","CODIGO","CÓDIGO","MATERIAL","COD_PRODUTO","CODIGO_PRODUTO"]),
        ("FOTO",        ["FOTO","FOTO DO PRODUTO","FOTO_PRODUTO","IMAGE","IMAGEM","IMG","URL_FOTO","LINK_FOTO"]),
    ]:
        for c in df.columns:
            if c in alts or c == tgt:
                name_map[c] = tgt; break

    df = df.rename(columns=name_map)

    if len(df.columns) >= 5 and not all(r in df.columns for r in ["DATA","NOTA","QUANTIDADE","VALOR","MARKETPLACE"]):
        cols = list(df.columns)
        remap = {}
        if "DATA"        not in df.columns: remap[cols[0]] = "DATA"
        if "NOTA"        not in df.columns: remap[cols[1]] = "NOTA"
        if "QUANTIDADE"  not in df.columns: remap[cols[2]] = "QUANTIDADE"
        if "VALOR"       not in df.columns: remap[cols[3]] = "VALOR"
        if "MARKETPLACE" not in df.columns: remap[cols[4]] = "MARKETPLACE"
        df = df.rename(columns=remap)

    for req in ["DATA","NOTA","QUANTIDADE","VALOR","MARKETPLACE"]:
        if req not in df.columns:
            df[req] = ""

    df["valor_num"] = (
        df["VALOR"].astype(str)
        .str.strip()
        .str.replace(r"\s","",regex=True)
        .str.replace(r"\.(?=\d{3})", "", regex=True)
        .str.replace(",",".",regex=False)
        .pipe(pd.to_numeric, errors="coerce")
        .fillna(0)
    )
    df["qty_num"]    = pd.to_numeric(df["QUANTIDADE"], errors="coerce").fillna(1)
    df["line_total"] = df["valor_num"] * df["qty_num"]
    df["nota"]       = df["NOTA"].astype(str).str.strip()
    df["data"]       = pd.to_datetime(df["DATA"].astype(str).str.strip(),
                                      dayfirst=True, errors="coerce")
    df["canal_tipo"] = df["MARKETPLACE"].apply(
        lambda x: "ecommerce" if str(x).strip() in ECOM_CANAIS else "marketplace"
    )
    df["marca"] = df["MARKETPLACE"].apply(
        lambda x: MARCA_MAP.get(str(x).strip(), str(x).strip())
    )

    if "REFERENCIA" in df.columns:
        df["referencia"] = df["REFERENCIA"].astype(str).str.strip()
    else:
        df["referencia"] = ""

    if "FOTO" in df.columns:
        df["img_url"] = df["FOTO"].astype(str).str.strip().apply(
            lambda u: u if u.startswith("http") else ""
        )
    else:
        df["img_url"] = df.apply(
            lambda r: (f"{IMG_BASE_URL}/{r['marca']}/Baixa/{r['referencia']}{IMG_EXT}"
                       if r["referencia"] else ""),
            axis=1,
        )

    df = df.dropna(subset=["data"])
    return df

def prep_ec(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw.copy()

    ncols = len(df.columns)
    if ncols >= 19:
        expected = EC_COLS_19
    elif ncols == 18:
        expected = EC_COLS_18
    else:
        expected = EC_COLS_17
    if len(df.columns) == len(expected):
        df.columns = expected

    def safe_num(s):
        return pd.to_numeric(
            s.astype(str).str.strip().str.replace(",",".",regex=False),
            errors="coerce"
        ).fillna(0)

    df["sku_selling_price"] = safe_num(df["sku_selling_price"])
    df["quantity_sku"]      = safe_num(df["quantity_sku"])

    suspicious = (df["sku_selling_price"] < 10) & (df["sku_selling_price"] > 0)
    df.loc[suspicious, "sku_selling_price"] = df.loc[suspicious, "sku_selling_price"] * 1000

    df["line_total"] = df["sku_selling_price"] * df["quantity_sku"]
    df["data"]       = pd.to_datetime(df["created_at"].astype(str).str.strip(),
                                      errors="coerce", utc=True)
    df["data"]       = df["data"].dt.tz_localize(None).dt.normalize()
    df["status"]     = df["status"].astype(str).str.strip()
    df["faturado"]   = df["status"].str.lower().isin(
        ["faturado","aprovado","entregue","complete","paid","concluido","concluído"])
    df["cancelado"]  = df["status"].str.lower().isin(
        ["cancelado","cancelada","canceled","cancelled","devolvido","devolvida","returned","recusado"])
    df["livelo"]     = df["livelo_tag"].astype(str).str.strip().str.lower() == "livelo"
    df["utmsource"]  = df["utmsource"].replace("", np.nan).fillna("Direto").astype(str).str.strip()
    df["order"]      = df["order"].astype(str).str.strip()
    df["brand"]      = df["brand"].astype(str).str.strip()

    if "foto_produto" in df.columns:
        df["foto_produto"] = df["foto_produto"].astype(str).str.strip()
        df["img_url"] = df["foto_produto"].apply(
            lambda u: u if u.startswith("http") else ""
        )
    else:
        df["img_url"] = (
            IMG_BASE_URL + "/" + df["brand"] + "/Baixa/" + df["sku"] + IMG_EXT
        )

    df = df.dropna(subset=["data"])
    return df

def agg_nf(df_mp: pd.DataFrame, canal_tipo: str) -> pd.DataFrame:
    sub = df_mp[df_mp["canal_tipo"] == canal_tipo]
    if sub.empty: return pd.DataFrame()
    return (
        sub.groupby(["nota","MARKETPLACE","marca","data"])
        .agg(
            receita=("line_total","sum"),
            itens=("qty_num","sum"),
            referencia=("referencia","first"),
            img_url=("img_url","first"),
        )
        .reset_index()
    )

def kpis(df_nf: pd.DataFrame):
    if df_nf is None or df_nf.empty:
        return dict(total=0, receita=0, ticket=0, itens=0)
    total   = df_nf["nota"].nunique()
    receita = float(df_nf["receita"].sum())
    itens   = int(df_nf["itens"].round().astype(int).sum())
    ticket  = receita / total if total else 0
    return dict(total=total, receita=receita, ticket=ticket, itens=itens)

has_mp = st.session_state.df_mp_raw is not None
has_ec = st.session_state.df_ec_raw is not None
ts_mp  = st.session_state.ts_mp or "—"
ts_ec  = st.session_state.ts_ec or "—"

st.markdown(f"""
<div class="topbar">
  <div class="topbar-brand">⌚ <span>Seculus</span> · Sales Intelligence</div>
  <div class="topbar-right">
    <span class="dot"></span>
    <span>NF: {ts_mp}</span>
    <span style="color:#1a2540">|</span>
    <span>E-com: {ts_ec}</span>
  </div>
</div>
""", unsafe_allow_html=True)

with st.expander("⚙️  Fontes de Dados", expanded=not has_mp):
    c1, c2, c3 = st.columns([2, 2, 1])

    with c1:
        st.markdown("**📋 Planilha de Faturamento (Notas Fiscais)**")
        st.markdown(
            "<div style='font-size:.74rem;color:#64748b;margin-bottom:8px;'>"
            "Fonte principal de receita — colunas esperadas: "
            "<code>DATA · NOTA · QUANTIDADE · VALOR · MARKETPLACE</code><br>"
            "<code>Site Mondaine / Site Seculus / Site Timex / Multimarcas</code> → E-commerce &nbsp;|&nbsp; "
            "demais → Marketplace</div>", unsafe_allow_html=True)
        mp_url  = st.text_input("URL Google Sheets / CSV público", key="mp_url_in",
                                placeholder="https://docs.google.com/spreadsheets/d/...")
        mp_file = st.file_uploader("ou upload direto do arquivo CSV", type=["csv","txt"], key="mp_up")
        if st.button("Carregar Faturamento", use_container_width=True, key="btn_mp"):
            raw = None; ts = None
            if mp_file is not None:
                try:
                    raw = read_upload(mp_file, "mp")
                    ts  = datetime.now().strftime("%d/%m/%Y %H:%M")
                except Exception as e:
                    st.error(f"Erro ao ler arquivo: {e}")
            elif mp_url.strip():
                with st.spinner("Carregando..."):
                    raw, ts = load_url(mp_url.strip(), "mp")
            if raw is not None and not raw.empty:
                st.session_state.df_mp_raw = raw
                st.session_state.ts_mp = ts
                st.success(f"✅ {len(raw)} linhas · colunas: {list(raw.columns)}")
                st.rerun()
            elif raw is not None:
                st.warning("Arquivo carregado mas sem dados.")

    with c2:
        st.markdown("**🛒 Planilha E-commerce (Enriquecimento)**")
        st.markdown(
            "<div style='font-size:.74rem;color:#64748b;margin-bottom:8px;'>"
            "Valida status dos pedidos, UTM Source e ranking de produtos.<br>"
            "Arquivo sem cabeçalho — primeira linha já contém dados.</div>",
            unsafe_allow_html=True)
        ec_url  = st.text_input("URL Google Sheets / CSV público", key="ec_url_in",
                                placeholder="https://docs.google.com/spreadsheets/d/...")
        ec_file = st.file_uploader("ou upload direto do arquivo CSV", type=["csv","txt"], key="ec_up")
        if st.button("Carregar E-commerce", use_container_width=True, key="btn_ec"):
            raw = None; ts = None
            if ec_file is not None:
                try:
                    raw = read_upload(ec_file, "ec")
                    ts  = datetime.now().strftime("%d/%m/%Y %H:%M")
                except Exception as e:
                    st.error(f"Erro ao ler arquivo: {e}")
            elif ec_url.strip():
                with st.spinner("Carregando..."):
                    raw, ts = load_url(ec_url.strip(), "ec")
            if raw is not None and not raw.empty:
                st.session_state.df_ec_raw = raw
                st.session_state.ts_ec = ts
                st.success(f"✅ {len(raw)} linhas")
                st.rerun()
            elif raw is not None:
                st.warning("Arquivo carregado mas sem dados.")

    with c3:
        st.markdown("**📥 Templates**")
        tpl_mp = "DATA,NOTA,QUANTIDADE,VALOR,MARKETPLACE\n01/04/2026,NF001,1,\"269,10\",Livelo\n01/04/2026,NF002,2,\"350,00\",Site Seculus\n01/04/2026,NF003,1,\"180,00\",Multimarcas\n01/04/2026,NF004,1,\"450,00\",Site Mondaine"
        tpl_ec = ",".join(EC_COLS_17)+"\nPED001,2026-04-01 10:00:00Z,Cliente,SP,Faturado,google-shopping,Pix,1,1,,SKU001,Relógio Slim,350.00,350.00,,Seculus,"
        st.download_button("⬇️ Template NF", data=tpl_mp, file_name="template_nf.csv",
                           mime="text/csv", use_container_width=True)
        st.download_button("⬇️ Template EC", data=tpl_ec, file_name="template_ec.csv",
                           mime="text/csv", use_container_width=True)
        st.markdown(f"**Status:**  {'🟢' if has_mp else '🔴'} NF &nbsp; {'🟢' if has_ec else '⚪'} EC",
                    unsafe_allow_html=True)
        if has_mp:
            if st.button("🔄 Limpar dados", use_container_width=True):
                st.session_state.df_mp_raw = None
                st.session_state.df_ec_raw = None
                st.session_state.ts_mp = None
                st.session_state.ts_ec = None
                load_url.clear()
                st.rerun()

if not has_mp:
    st.markdown("""
    <div class="zone">
      <h3>Nenhum dado carregado</h3>
      <p>Carregue a planilha de faturamento (notas fiscais) para começar.<br>
      A planilha E-commerce é opcional — enriquece com status de pedidos, UTM e ranking de produtos.</p>
    </div>""", unsafe_allow_html=True)
    st.stop()

try:
    df_mp = prep_mp(st.session_state.df_mp_raw)
except Exception as e:
    st.error(f"Erro ao processar planilha NF: {e}")
    st.stop()

df_ec = pd.DataFrame()
if has_ec:
    try:
        df_ec = prep_ec(st.session_state.df_ec_raw)
    except Exception as e:
        st.warning(f"Erro ao processar planilha EC: {e}")

if df_mp.empty:
    st.error("Planilha de faturamento carregada mas sem dados válidos. Verifique o formato.")
    with st.expander("Debug — primeiras linhas do arquivo"):
        st.dataframe(st.session_state.df_mp_raw.head(5))
    st.stop()

mp_ecom_all = agg_nf(df_mp, "ecommerce")
mp_mkt_all  = agg_nf(df_mp, "marketplace")

st.markdown("---")
hoje = datetime.today().date()

if "d_ini" not in st.session_state: st.session_state.d_ini = hoje.replace(day=1)
if "d_fim" not in st.session_state: st.session_state.d_fim = hoje

fr = st.columns([2, 2, 3])
with fr[0]: data_ini = st.date_input("De",  value=st.session_state.d_ini, key="d_ini", format="DD/MM/YYYY")
with fr[1]: data_fim = st.date_input("Até", value=st.session_state.d_fim, key="d_fim", format="DD/MM/YYYY")
with fr[2]: comp_modo = st.selectbox("Comparar com",
    ["Período anterior equivalente","Mês anterior","Mesmo período ano anterior"], key="comp")

ini_ant, fim_ant = prev_p(data_ini, data_fim, comp_modo)

ec_p  = fdt(mp_ecom_all, data_ini, data_fim)
mp_p  = fdt(mp_mkt_all,  data_ini, data_fim)
ec_pa = fdt(mp_ecom_all, ini_ant,  fim_ant)
mp_pa = fdt(mp_mkt_all,  ini_ant,  fim_ant)

ec_m  = kpis(ec_p)
mp_m  = kpis(mp_p)
ec_ma = kpis(ec_pa)
mp_ma = kpis(mp_pa)

total_rec     = ec_m["receita"] + mp_m["receita"]
total_rec_ant = ec_ma["receita"] + mp_ma["receita"]

ec_p_ec  = fdt(df_ec, data_ini, data_fim) if not df_ec.empty else pd.DataFrame()
ec_fat   = ec_p_ec[ec_p_ec["faturado"]].copy() if not ec_p_ec.empty else pd.DataFrame()

ec_pa_ec = fdt(df_ec, ini_ant, fim_ant) if not df_ec.empty else pd.DataFrame()
ec_fat_a = ec_pa_ec[ec_pa_ec["faturado"]] if not ec_pa_ec.empty else pd.DataFrame()

st.markdown("---")
tab_geral, tab_metas, tab_ec_tab, tab_mp_tab, tab_prod = st.tabs([
    "📊 Visão Geral", "🎯 Metas", "🛒 E-commerce", "🏪 Marketplace", "🏆 Produtos & SKUs",
])

with tab_geral:
    df_meta = load_metas()
    mes_atual  = hoje.month
    ano_atual  = hoje.year

    if not df_meta.empty:
        m_mes = metas_do_mes(df_meta, ano_atual, mes_atual)
        m_ano = metas_ano(df_meta, ano_atual)
        m_acu = metas_acumulado(df_meta, ano_atual, mes_atual)
        mes_label_atual = date(ano_atual, mes_atual, 1).strftime('%b/%Y')

        def pct_barra(real, meta):
            if meta <= 0: return 0
            return min(real / meta * 100, 100)

        def cor_barra(real, meta):
            if meta <= 0: return "#3b6fff"
            p = real / meta * 100
            return "#10b981" if p >= 100 else ("#f59e0b" if p >= 70 else "#f43f5e")

        def card_class(real, meta):
            if meta <= 0: return ""
            return "ok" if real >= meta else ("highlight" if real/meta < 0.7 else "")

        def dif_html(dif):
            cls = "pos" if dif >= 0 else "neg"
            sinal = "+" if dif >= 0 else ""
            return f"<span class='meta-card-sub {cls}'>{sinal}{brl(dif)}</span>"

        sh("Painel de Metas — Mês Atual vs Meta")

        top1, top2, top3 = st.columns(3)
        # ---- TOTAL
        with top1:
            pct_total_mes = pct_barra(total_rec, m_mes["meta_total"])
            cls = card_class(total_rec, m_mes["meta_total"])
            cor = cor_barra(total_rec, m_mes["meta_total"])
            dif_mes_total = total_rec - m_mes["meta_total"]
            st.markdown(f"""
            <div class="meta-card {cls}">
              <div class="meta-card-label">🎯 Meta Total — {mes_label_atual}</div>
              <div class="meta-card-value">{brl(m_mes['meta_total'])}</div>
              <hr class="meta-sep"/>
              <div class="meta-card-label">📊 Realizado no Período</div>
              <div class="meta-card-value" style="font-size:1.1rem;">{brl(total_rec)}</div>
              <div class="meta-bar-wrap"><div class="meta-bar-fill" style="width:{pct_total_mes:.1f}%;background:{cor};"></div></div>
              <div style="display:flex;justify-content:space-between;margin-top:6px;">
                <span class="meta-card-sub neu">{pct_total_mes:.1f}% da meta</span>
                {dif_html(dif_mes_total)}
              </div>
            </div>""", unsafe_allow_html=True)
        # ---- E-COMMERCE
        with top2:
            pct_ec_mes = pct_barra(ec_m["receita"], m_mes["meta_ec"])
            cls_ec = card_class(ec_m["receita"], m_mes["meta_ec"])
            cor_ec = cor_barra(ec_m["receita"], m_mes["meta_ec"])
            dif_ec = ec_m["receita"] - m_mes["meta_ec"]
            st.markdown(f"""
            <div class="meta-card {cls_ec}" style="border-color:#3b6fff44;">
              <div class="meta-card-label" style="color:#3b6fff;">🛒 Meta E-commerce — {mes_label_atual}</div>
              <div class="meta-card-value">{brl(m_mes['meta_ec'])}</div>
              <hr class="meta-sep"/>
              <div class="meta-card-label">📊 Realizado E-commerce</div>
              <div class="meta-card-value" style="font-size:1.1rem;">{brl(ec_m['receita'])}</div>
              <div class="meta-bar-wrap"><div class="meta-bar-fill" style="width:{pct_ec_mes:.1f}%;background:{cor_ec};"></div></div>
              <div style="display:flex;justify-content:space-between;margin-top:6px;">
                <span class="meta-card-sub neu">{pct_ec_mes:.1f}% da meta</span>
                {dif_html(dif_ec)}
              </div>
            </div>""", unsafe_allow_html=True)
        # ---- MARKETPLACE
        with top3:
            pct_mkt_mes = pct_barra(mp_m["receita"], m_mes["meta_mkt"])
            cls_mkt = card_class(mp_m["receita"], m_mes["meta_mkt"])
            cor_mkt = cor_barra(mp_m["receita"], m_mes["meta_mkt"])
            dif_mkt = mp_m["receita"] - m_mes["meta_mkt"]
            st.markdown(f"""
            <div class="meta-card {cls_mkt}" style="border-color:#f59e0b44;">
              <div class="meta-card-label" style="color:#f59e0b;">🏪 Meta Marketplace — {mes_label_atual}</div>
              <div class="meta-card-value">{brl(m_mes['meta_mkt'])}</div>
              <hr class="meta-sep"/>
              <div class="meta-card-label">📊 Realizado Marketplace</div>
              <div class="meta-card-value" style="font-size:1.1rem;">{brl(mp_m['receita'])}</div>
              <div class="meta-bar-wrap"><div class="meta-bar-fill" style="width:{pct_mkt_mes:.1f}%;background:{cor_mkt};"></div></div>
              <div style="display:flex;justify-content:space-between;margin-top:6px;">
                <span class="meta-card-sub neu">{pct_mkt_mes:.1f}% da meta</span>
                {dif_html(dif_mkt)}
              </div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

    sh("KPIs Consolidados do Período")
    g1, g2, g3, g4, g5 = st.columns(5)
    g1.metric("💰 Receita Total",   brl(total_rec),       delta=fv(vp(total_rec, total_rec_ant)))
    g2.metric("🛒 Receita E-com",   brl(ec_m["receita"]), delta=fv(vp(ec_m["receita"], ec_ma["receita"])))
    g3.metric("🏪 Receita Mkt",     brl(mp_m["receita"]), delta=fv(vp(mp_m["receita"], mp_ma["receita"])))
    g4.metric("📑 NFs E-com",       f"{ec_m['total']:,}", delta=fv(vp(ec_m["total"], ec_ma["total"])))
    g5.metric("📑 NFs Marketplace", f"{mp_m['total']:,}", delta=fv(vp(mp_m["total"], mp_ma["total"])))

    st.markdown("<br>", unsafe_allow_html=True)
    if total_rec > 0:
        pec = ec_m["receita"]/total_rec*100; pmp = mp_m["receita"]/total_rec*100
        st.markdown(
            f"<div class='info'>📐 <strong>Mix de canal:</strong> E-commerce "
            f"<strong>{pec:.1f}%</strong> (R$ {ec_m['receita']:,.0f}) · "
            f"Marketplace <strong>{pmp:.1f}%</strong> (R$ {mp_m['receita']:,.0f})</div>",
            unsafe_allow_html=True)

    if not mp_ecom_all.empty:
        sh("Resumo por Marca")
        MARCAS_ECOM = ["Seculus", "Mondaine", "Timex", "E-time"]
        cols_rc = st.columns(len(MARCAS_ECOM))
        for idx, marca in enumerate(MARCAS_ECOM):
            df_m = ec_p[ec_p["marca"] == marca] if not ec_p.empty else pd.DataFrame()
            notas    = int(df_m["nota"].nunique()) if not df_m.empty else 0
            itens    = int(df_m["itens"].round().sum()) if not df_m.empty else 0
            receita  = float(df_m["receita"].sum()) if not df_m.empty else 0
            ticket   = receita / notas if notas > 0 else 0
            cor = COR_MARCA.get(marca, "#3b6fff")
            with cols_rc[idx]:
                st.markdown(f"""
                <div class="rc">
                  <p class="rc-title" style="color:{cor};">{marca}</p>
                  <div class="rc-row"><span>Notas fiscais</span><span class="rc-val">{notas:,}</span></div>
                  <div class="rc-row"><span>Itens faturados</span><span class="rc-val"><span class="rc-badge rc-green">{itens:,}</span></span></div>
                  <div class="rc-row"><span>Ticket médio NF</span><span class="rc-val">{brl(ticket)}</span></div>
                  <div class="rc-row"><span>Receita faturada</span><span class="rc-val">{brl(receita)}</span></div>
                </div>
                """, unsafe_allow_html=True)

    col_ev, col_sh = st.columns([3, 1])
    with col_ev:
        sh("Evolução de Receita")
        fig_ev = go.Figure()
        if not ec_p.empty:
            ts1 = ec_p.groupby("data")["receita"].sum().reset_index()
            fig_ev.add_trace(go.Scatter(x=ts1["data"], y=ts1["receita"], name="E-commerce",
                mode="lines", fill="tozeroy",
                line=dict(color="#3b6fff", width=2.5, shape="spline", smoothing=1.2),
                fillcolor="rgba(59,111,255,0.07)"))
        if not mp_p.empty:
            ts2 = mp_p.groupby("data")["receita"].sum().reset_index()
            fig_ev.add_trace(go.Scatter(x=ts2["data"], y=ts2["receita"], name="Marketplace",
                mode="lines", fill="tozeroy",
                line=dict(color="#f59e0b", width=2.5, shape="spline", smoothing=1.2),
                fillcolor="rgba(245,158,11,0.06)"))
        fig_ev.update_layout(**L())
        st.plotly_chart(fig_ev, use_container_width=True)

    with col_sh:
        sh("Share por Canal")
        rows = []
        if ec_m["receita"] > 0: rows.append({"Canal":"E-commerce","R":ec_m["receita"]})
        if mp_m["receita"] > 0: rows.append({"Canal":"Marketplace","R":mp_m["receita"]})
        if rows:
            fig_sh = px.pie(pd.DataFrame(rows), names="Canal", values="R",
                            color="Canal",
                            color_discrete_map={"E-commerce":"#3b6fff","Marketplace":"#f59e0b"},
                            hole=0.6)
            fig_sh.update_traces(textinfo="percent+label", textfont_size=11)
            fig_sh.update_layout(**L(margin=dict(l=10,r=10,t=30,b=10)))
            st.plotly_chart(fig_sh, use_container_width=True)

    cb1, cb2 = st.columns(2)
    with cb1:
        sh("E-commerce por Marca")
        if not ec_p.empty:
            em = ec_p.groupby("marca")["receita"].sum().reset_index().sort_values("receita", ascending=True)
            fig_em = px.bar(em, x="receita", y="marca", orientation="h",
                            color="marca", color_discrete_map=COR_MARCA,
                            labels={"receita":"Receita (R$)","marca":""})
            fig_em.update_layout(**Li())
            st.plotly_chart(fig_em, use_container_width=True)

    with cb2:
        sh("Marketplace por Plataforma")
        if not mp_p.empty:
            mm = mp_p.groupby("MARKETPLACE")["receita"].sum().reset_index().sort_values("receita", ascending=True)
            fig_mm = px.bar(mm, x="receita", y="MARKETPLACE", orientation="h",
                            color="MARKETPLACE", color_discrete_map=COR_MP,
                            labels={"receita":"Receita (R$)","MARKETPLACE":""})
            fig_mm.update_layout(**Li())
            st.plotly_chart(fig_mm, use_container_width=True)

    if has_ec and not ec_fat.empty:
        sh("UTM Source — Pedidos Faturados E-commerce")
        utm_g = (ec_fat.drop_duplicates("order")
                 .groupby("utmsource").agg(pedidos=("order","count")).reset_index()
                 .sort_values("pedidos", ascending=False)
                 .head(10))
        utm_g["pct"] = utm_g["pedidos"] / utm_g["pedidos"].sum() * 100
        utm_colors = [COR_UTM.get(s, "#64748b") for s in utm_g["utmsource"]]
        ug1, ug2 = st.columns([2,1])
        with ug1:
            fig_utm = px.bar(utm_g, x="utmsource", y="pedidos",
                             labels={"pedidos":"Pedidos Faturados","utmsource":"UTM Source"},
                             text=utm_g["pedidos"].astype(str)+" ("+utm_g["pct"].map("{:.0f}%".format)+")")
            fig_utm.update_traces(textposition="outside",
                                  marker_color=utm_colors)
            fig_utm.update_layout(**L())
            st.plotly_chart(fig_utm, use_container_width=True)
        with ug2:
            fig_utmp = px.pie(utm_g, names="utmsource", values="pedidos", hole=0.58)
            fig_utmp.update_traces(textinfo="percent+label", textfont_size=11,
                                   marker=dict(colors=utm_colors))
            fig_utmp.update_layout(**L(margin=dict(l=5,r=5,t=30,b=5)))
            st.plotly_chart(fig_utmp, use_container_width=True)


with tab_metas:
    df_meta = load_metas()
    if df_meta.empty:
        st.markdown(
            "<div class='warn'>⚠️ Não foi possível carregar a planilha de metas. "
            "Verifique se o link está acessível publicamente.</div>",
            unsafe_allow_html=True)
        st.stop()

    anos_disp = sorted(df_meta["mes_dt"].dt.year.unique().tolist(), reverse=True)
    col_ano, col_ref = st.columns([1, 3])
    with col_ano:
        ano_meta = st.selectbox("Ano", anos_disp, key="meta_ano")
    with col_ref:
        st.markdown(
            "<div style='font-size:.75rem;color:#475569;padding-top:28px;'>"
            "Dados carregados automaticamente da planilha de metas.</div>",
            unsafe_allow_html=True)

    m_ano_sel = metas_ano(df_meta, ano_meta)
    hoje_meta = datetime.today().date()
    m_acu_sel = metas_acumulado(df_meta, ano_meta, hoje_meta.month)

    def pct_b(r, m): return min(r/m*100, 100) if m > 0 else 0
    def cor_b(r, m):
        if m <= 0: return "#3b6fff"
        p = r/m*100
        return "#10b981" if p >= 100 else ("#f59e0b" if p >= 70 else "#f43f5e")
    def dif_h(d):
        cls = "pos" if d >= 0 else "neg"
        s   = "+" if d >= 0 else ""
        return f"<span class='meta-card-sub {cls}'>{s}{brl(d)}</span>"
    def cls_c(r, m):
        if m <= 0: return ""
        return "ok" if r >= m else ("highlight" if r/m < 0.7 else "")

    sh(f"Visão Anual — {ano_meta}")

    ya1, ya2, ya3 = st.columns(3)
    for col_w, lbl, meta, real, canal_cor in [
        (ya1, "Total", m_ano_sel["meta_total"], m_ano_sel["real_total"], ""),
        (ya2, "E-commerce", m_ano_sel["meta_ec"],    m_ano_sel["real_ec"],    "#3b6fff"),
        (ya3, "Marketplace", m_ano_sel["meta_mkt"],   m_ano_sel["real_mkt"],   "#f59e0b"),
    ]:
        pct = pct_b(real, meta)
        cor = cor_b(real, meta)
        dif = real - meta
        with col_w:
            st.markdown(f"""
            <div class="meta-card {cls_c(real,meta)}">
              <div class="meta-card-label" style="{'color:'+canal_cor+';' if canal_cor else ''}">
                🎯 Meta Anual {lbl}</div>
              <div class="meta-card-value">{brl(meta)}</div>
              <hr class="meta-sep"/>
              <div class="meta-card-label">✅ Realizado no Ano</div>
              <div class="meta-card-value" style="font-size:1.1rem;">{brl(real)}</div>
              <div class="meta-bar-wrap">
                <div class="meta-bar-fill" style="width:{pct:.1f}%;background:{cor};"></div>
              </div>
              <div style="display:flex;justify-content:space-between;margin-top:6px;">
                <span class="meta-card-sub neu">{pct:.1f}% da meta</span>
                {dif_h(dif)}
              </div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    sh(f"Acumulado até {hoje_meta.strftime('%B/%Y')} — {ano_meta}")

    aa1, aa2, aa3 = st.columns(3)
    for col_w, lbl, meta, real, canal_cor in [
        (aa1, "Total",       m_acu_sel["meta_total"], m_acu_sel["real_total"], ""),
        (aa2, "E-commerce",  m_acu_sel["meta_ec"],    m_acu_sel["real_ec"],    "#3b6fff"),
        (aa3, "Marketplace", m_acu_sel["meta_mkt"],   m_acu_sel["real_mkt"],   "#f59e0b"),
    ]:
        pct = pct_b(real, meta)
        cor = cor_b(real, meta)
        dif = real - meta
        with col_w:
            st.markdown(f"""
            <div class="meta-card {cls_c(real,meta)}">
              <div class="meta-card-label" style="{'color:'+canal_cor+';' if canal_cor else ''}">
                📊 Meta Acumulada {lbl}</div>
              <div class="meta-card-value">{brl(meta)}</div>
              <hr class="meta-sep"/>
              <div class="meta-card-label">✅ Realizado Acumulado</div>
              <div class="meta-card-value" style="font-size:1.1rem;">{brl(real)}</div>
              <div class="meta-bar-wrap">
                <div class="meta-bar-fill" style="width:{pct:.1f}%;background:{cor};"></div>
              </div>
              <div style="display:flex;justify-content:space-between;margin-top:6px;">
                <span class="meta-card-sub neu">{pct:.1f}% da meta</span>
                {dif_h(dif)}
              </div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    sh("Detalhe Mensal por Canal")

    df_ano = df_meta[df_meta["mes_dt"].dt.year == ano_meta].copy()
    df_ano["mes_label"] = df_ano["mes_dt"].dt.strftime("%b")

    fig_metas = go.Figure()
    meses = df_ano["mes_label"].tolist()
    fig_metas.add_trace(go.Bar(
        name="Meta Total", x=meses, y=df_ano["META TOTAL"],
        marker_color="rgba(100,116,139,.3)", marker_line_width=0,
    ))
    fig_metas.add_trace(go.Bar(
        name="Realizado Total", x=meses, y=df_ano["Realizado REAL TOTAL"],
        marker_color="#10b981", marker_line_width=0, opacity=0.9,
    ))
    fig_metas.update_layout(barmode="group", **L(
        title=f"Meta vs Realizado Total — {ano_meta}"))
    st.plotly_chart(fig_metas, use_container_width=True)

    mc1, mc2 = st.columns(2)
    with mc1:
        fig_ec = go.Figure([
            go.Bar(name="Meta E-com",  x=meses, y=df_ano["Meta B2C"],
                   marker_color="rgba(59,111,255,.3)", marker_line_width=0),
            go.Bar(name="Real E-com",  x=meses, y=df_ano["Realizado B2C"],
                   marker_color="#3b6fff", opacity=0.9, marker_line_width=0),
        ])
        fig_ec.update_layout(barmode="group", **L(title="E-commerce"))
        st.plotly_chart(fig_ec, use_container_width=True)

    with mc2:
        fig_mkt = go.Figure([
            go.Bar(name="Meta MKT",  x=meses, y=df_ano["Meta MKT PLACE"],
                   marker_color="rgba(245,158,11,.3)", marker_line_width=0),
            go.Bar(name="Real MKT",  x=meses, y=df_ano["Realizado MKT PLACE"],
                   marker_color="#f59e0b", opacity=0.9, marker_line_width=0),
        ])
        fig_mkt.update_layout(barmode="group", **L(title="Marketplace"))
        st.plotly_chart(fig_mkt, use_container_width=True)

    sh("Tabela Mensal de Metas")
    df_tab = df_ano[["Ano/Mês","Meta B2C","Meta MKT PLACE","META TOTAL",
                     "Realizado B2C","Realizado MKT PLACE","Realizado REAL TOTAL","DIF"]].copy()
    for col in ["Meta B2C","Meta MKT PLACE","META TOTAL",
                "Realizado B2C","Realizado MKT PLACE","Realizado REAL TOTAL","DIF"]:
        df_tab[col] = df_tab[col].apply(brl)
    df_tab = df_tab.rename(columns={
        "Ano/Mês":"Mês","Meta B2C":"Meta EC","Meta MKT PLACE":"Meta MKT",
        "META TOTAL":"Meta Total","Realizado B2C":"Real EC",
        "Realizado MKT PLACE":"Real MKT","Realizado REAL TOTAL":"Real Total","DIF":"Diferença",
    })
    st.dataframe(df_tab, use_container_width=True, hide_index=True)


with tab_ec_tab:
    sh("E-commerce — Receita via Notas Fiscais")
    if ec_p.empty:
        st.info("Nenhuma nota fiscal de E-commerce no período selecionado.")
    else:
        e1,e2,e3,e4 = st.columns(4)
        e1.metric("💰 Receita",    brl(ec_m["receita"]), delta=fv(vp(ec_m["receita"], ec_ma["receita"])))
        e2.metric("📑 NFs",        f"{ec_m['total']:,}",  delta=fv(vp(ec_m["total"], ec_ma["total"])))
        e3.metric("📦 Itens",      f"{ec_m['itens']:,}",  delta=fv(vp(ec_m["itens"], ec_ma["itens"])))
        e4.metric("🎟️ Ticket NF", brl(ec_m["ticket"]),  delta=fv(vp(ec_m["ticket"], ec_ma["ticket"])))

        st.markdown("<br>", unsafe_allow_html=True)
        ea1, ea2 = st.columns(2)
        with ea1:
            sh("Receita por Marca")
            em2 = ec_p.groupby("marca")["receita"].sum().reset_index().sort_values("receita", ascending=False)
            fig_em2 = px.bar(em2, x="marca", y="receita",
                             color="marca", color_discrete_map=COR_MARCA,
                             labels={"receita":"Receita (R$)","marca":""},
                             text=em2["receita"].map(lambda x: brl(x)))
            fig_em2.update_traces(textposition="outside")
            fig_em2.update_layout(**L())
            st.plotly_chart(fig_em2, use_container_width=True)
        with ea2:
            sh("Share por Marca")
            fig_em2p = px.pie(em2, names="marca", values="receita",
                              color="marca", color_discrete_map=COR_MARCA, hole=0.58)
            fig_em2p.update_traces(textinfo="percent+label", textfont_size=11)
            fig_em2p.update_layout(**L(margin=dict(l=10,r=10,t=30,b=10)))
            st.plotly_chart(fig_em2p, use_container_width=True)

        sh("Evolução Diária por Marca")
        ec_d = ec_p.groupby(["data","marca"]).agg(receita=("receita","sum")).reset_index()
        fig_edd = px.area(ec_d, x="data", y="receita", color="marca",
                          color_discrete_map=COR_MARCA,
                          labels={"receita":"Receita (R$)","data":"","marca":"Marca"})
        fig_edd.update_layout(**L())
        st.plotly_chart(fig_edd, use_container_width=True)

        sh("Atual vs Período Anterior por Marca")
        ec_a2 = ec_p.groupby("marca")["receita"].sum().reset_index().rename(columns={"receita":"atual"})
        ec_b2 = (ec_pa.groupby("marca")["receita"].sum().reset_index().rename(columns={"receita":"anterior"})
                 if not ec_pa.empty else pd.DataFrame(columns=["marca","anterior"]))
        ec_cmp = ec_a2.merge(ec_b2, on="marca", how="outer").fillna(0)
        ec_cmp["var"] = ec_cmp.apply(lambda r: fv(vp(r["atual"],r["anterior"])) or "—", axis=1)
        fig_ecmp = go.Figure([
            go.Bar(name="Anterior", x=ec_cmp["marca"], y=ec_cmp["anterior"],
                   marker_color="rgba(100,116,139,.35)", marker_line_width=0),
            go.Bar(name="Atual",    x=ec_cmp["marca"], y=ec_cmp["atual"],
                   marker_color=[COR_MARCA.get(m,"#3b6fff") for m in ec_cmp["marca"]],
                   marker_line_width=0, text=ec_cmp["var"], textposition="outside"),
        ])
        fig_ecmp.update_layout(barmode="group", **L())
        st.plotly_chart(fig_ecmp, use_container_width=True)

    if has_ec:
        sh("Status dos Pedidos (Planilha E-commerce)")
        if ec_p_ec.empty:
            st.markdown("<div class='warn'>⚠️ Nenhum pedido encontrado para o período selecionado na planilha E-commerce.</div>", unsafe_allow_html=True)
        else:
            ec_dedup = ec_p_ec.drop_duplicates("order")
            n_fat_ec  = int(ec_dedup["faturado"].sum())
            n_canc_ec = int(ec_dedup["cancelado"].sum()) if "cancelado" in ec_dedup.columns else 0
            st_rows = []
            if n_fat_ec  > 0: st_rows.append({"status":"Faturado",  "qtd":n_fat_ec})
            if n_canc_ec > 0: st_rows.append({"status":"Cancelado", "qtd":n_canc_ec})
            st_cnt = pd.DataFrame(st_rows) if st_rows else pd.DataFrame(columns=["status","qtd"])
            sv1, sv2 = st.columns(2)
            with sv1:
                if not st_cnt.empty:
                    fig_st = px.pie(st_cnt, names="status", values="qtd",
                                    color="status",
                                    color_discrete_map={"Faturado":"#10b981","Cancelado":"#f43f5e"},
                                    hole=0.58)
                    fig_st.update_traces(textinfo="percent+label", textfont_size=11)
                    fig_st.update_layout(**L(margin=dict(l=10,r=10,t=30,b=10)))
                    st.plotly_chart(fig_st, use_container_width=True)
            with sv2:
                sh("UTM Source — Pedidos Faturados")
                if not ec_fat.empty:
                    utm_t = (ec_fat.drop_duplicates("order")
                             .groupby("utmsource").agg(pedidos=("order","count")).reset_index()
                             .sort_values("pedidos", ascending=False)
                             .head(10))
                    utm_t["pct"] = (utm_t["pedidos"]/utm_t["pedidos"].sum()*100).map("{:.1f}%".format)
                    st.dataframe(
                        utm_t.rename(columns={"utmsource":"UTM Source","pedidos":"Pedidos Fat.","pct":"Share"}),
                        use_container_width=True, hide_index=True)
                else:
                    st.markdown("<div class='warn'>⚠️ Nenhum pedido faturado no período.</div>", unsafe_allow_html=True)

        sh("Detalhamento de Pedidos")
        if ec_p_ec.empty:
            st.markdown("<div class='warn'>⚠️ Nenhum pedido encontrado para o período selecionado.</div>", unsafe_allow_html=True)
        else:
            det = (ec_p_ec.drop_duplicates("order")
                   [["order","data","status","utmsource","quantity_sku"]]
                   .rename(columns={"order":"Order ID","data":"Data","status":"Status",
                                    "utmsource":"UTM Source","quantity_sku":"Itens"})
                   .sort_values("Data", ascending=False))
            st.dataframe(det, use_container_width=True, hide_index=True)
            st.download_button("📥 Exportar pedidos",
                               data=det.to_csv(index=False).encode("utf-8"),
                               file_name="pedidos_ecommerce.csv", mime="text/csv")
    else:
        sh("Status dos Pedidos (Planilha E-commerce)")
        st.markdown(
            "<div class='info'>ℹ️ Carregue a <strong>planilha E-commerce</strong> no painel "
            "⚙️ Fontes de Dados para visualizar status de pedidos, UTM Source e detalhamento.</div>",
            unsafe_allow_html=True)

    sh("Notas Fiscais E-commerce")
    if ec_p.empty:
        st.markdown(
            "<div class='warn'>⚠️ Nenhuma nota fiscal de E-commerce no período selecionado. "
            "Verifique se os canais <code>Site Mondaine / Site Seculus / Site Timex / Multimarcas</code> "
            "estão presentes na planilha de faturamento.</div>",
            unsafe_allow_html=True)
    else:
        nf = ec_p[["nota","data","MARKETPLACE","marca","receita","itens"]].copy()
        nf["receita"] = nf["receita"].map(brl)
        nf["itens"]   = nf["itens"].round().astype(int)
        nf = nf.sort_values("data", ascending=False).rename(columns={
            "nota":"Nota Fiscal","data":"Data","MARKETPLACE":"Canal","marca":"Marca",
            "receita":"Receita","itens":"Itens"})
        st.dataframe(nf, use_container_width=True, hide_index=True)
        st.download_button("📥 Exportar NFs E-commerce",
                           data=ec_p.to_csv(index=False).encode("utf-8"),
                           file_name="nf_ecommerce.csv", mime="text/csv")


with tab_mp_tab:
    sh("Marketplace — Receita via Notas Fiscais")
    if mp_p.empty:
        st.info("Nenhuma nota fiscal de Marketplace no período selecionado.")
    else:
        m1,m2,m3,m4 = st.columns(4)
        m1.metric("💰 Receita",      brl(mp_m["receita"]), delta=fv(vp(mp_m["receita"], mp_ma["receita"])))
        m2.metric("📑 NFs",          f"{mp_m['total']:,}",  delta=fv(vp(mp_m["total"], mp_ma["total"])))
        m3.metric("📦 Itens",        f"{mp_m['itens']:,}",  delta=fv(vp(mp_m["itens"], mp_ma["itens"])))
        m4.metric("🎟️ Ticket Médio", brl(mp_m["ticket"]),  delta=fv(vp(mp_m["ticket"], mp_ma["ticket"])))

        st.markdown("<br>", unsafe_allow_html=True)
        mp1, mp2 = st.columns(2)
        with mp1:
            sh("Receita por Plataforma")
            mpp = mp_p.groupby("MARKETPLACE")["receita"].sum().reset_index().sort_values("receita", ascending=False)
            fig_mpp = px.bar(mpp, x="MARKETPLACE", y="receita",
                             color="MARKETPLACE", color_discrete_map=COR_MP,
                             labels={"receita":"Receita (R$)","MARKETPLACE":""},
                             text=mpp["receita"].map(brl))
            fig_mpp.update_traces(textposition="outside")
            fig_mpp.update_layout(**L())
            st.plotly_chart(fig_mpp, use_container_width=True)
        with mp2:
            sh("Share por Plataforma")
            fig_mpp2 = px.pie(mpp, names="MARKETPLACE", values="receita",
                              color="MARKETPLACE", color_discrete_map=COR_MP, hole=0.58)
            fig_mpp2.update_traces(textinfo="percent+label", textfont_size=11)
            fig_mpp2.update_layout(**L(margin=dict(l=10,r=10,t=30,b=10)))
            st.plotly_chart(fig_mpp2, use_container_width=True)

        sh("Evolução Diária por Plataforma")
        mp_d = mp_p.groupby(["data","MARKETPLACE"])["receita"].sum().reset_index()
        fig_mpd = px.area(mp_d, x="data", y="receita", color="MARKETPLACE",
                          color_discrete_map=COR_MP,
                          labels={"receita":"Receita (R$)","data":"","MARKETPLACE":"Plataforma"})
        fig_mpd.update_layout(**L())
        st.plotly_chart(fig_mpd, use_container_width=True)

        sh("Atual vs Período Anterior por Plataforma")
        mp_a2 = mp_p.groupby("MARKETPLACE")["receita"].sum().reset_index().rename(columns={"receita":"atual"})
        mp_b2 = (mp_pa.groupby("MARKETPLACE")["receita"].sum().reset_index().rename(columns={"receita":"anterior"})
                 if not mp_pa.empty else pd.DataFrame(columns=["MARKETPLACE","anterior"]))
        mp_cmp = mp_a2.merge(mp_b2, on="MARKETPLACE", how="outer").fillna(0)
        mp_cmp["var"] = mp_cmp.apply(lambda r: fv(vp(r["atual"],r["anterior"])) or "—", axis=1)
        fig_mpcp = go.Figure([
            go.Bar(name="Anterior", x=mp_cmp["MARKETPLACE"], y=mp_cmp["anterior"],
                   marker_color="rgba(100,116,139,.35)", marker_line_width=0),
            go.Bar(name="Atual",    x=mp_cmp["MARKETPLACE"], y=mp_cmp["atual"],
                   marker_color=[COR_MP.get(c,"#f59e0b") for c in mp_cmp["MARKETPLACE"]],
                   marker_line_width=0, text=mp_cmp["var"], textposition="outside"),
        ])
        fig_mpcp.update_layout(barmode="group", **L())
        st.plotly_chart(fig_mpcp, use_container_width=True)

        sh("Notas Fiscais Marketplace")
        nf_mp = mp_p[["nota","data","MARKETPLACE","receita","itens"]].copy()
        nf_mp["receita"] = nf_mp["receita"].map(brl)
        nf_mp["itens"]   = nf_mp["itens"].round().astype(int)
        nf_mp = nf_mp.sort_values("data", ascending=False).rename(columns={
            "nota":"Nota Fiscal","data":"Data","MARKETPLACE":"Plataforma",
            "receita":"Receita","itens":"Itens"})
        st.dataframe(nf_mp, use_container_width=True, hide_index=True)
        st.download_button("📥 Exportar NFs Marketplace",
                           data=mp_p.to_csv(index=False).encode("utf-8"),
                           file_name="nf_marketplace.csv", mime="text/csv")


with tab_prod:
    all_mp_concat = pd.concat(
        [df for df in [mp_ecom_all, mp_mkt_all] if not df.empty],
        ignore_index=True
    ) if (not mp_ecom_all.empty or not mp_mkt_all.empty) else pd.DataFrame()

    mp_period_all = fdt(all_mp_concat, data_ini, data_fim) if not all_mp_concat.empty else pd.DataFrame()

    has_ref = (not mp_period_all.empty
               and "referencia" in mp_period_all.columns
               and mp_period_all["referencia"].ne("").any())

    if not has_ref:
        st.markdown(
            "<div class='info'>ℹ️ A planilha de faturamento ainda não contém colunas de referência/foto. "
            "Adicione as colunas <code>referencia</code> e <code>foto do produto</code> para "
            "visualizar os itens vendidos com imagens.</div>",
            unsafe_allow_html=True)
    else:
        prod_mp = (
            mp_period_all[mp_period_all["referencia"] != ""]
            .groupby(["referencia", "img_url", "marca"])
            .agg(receita=("receita", "sum"), qtd=("itens", "sum"))
            .reset_index()
            .sort_values("receita", ascending=False)
        )
        prod_mp["qtd"] = prod_mp["qtd"].round().astype(int)

        pf1, pf2, pf3 = st.columns([2, 1, 1])
        with pf1:
            marcas_d = sorted(prod_mp["marca"].unique().tolist())
            marcas_s = st.multiselect("Filtrar por Marca", marcas_d, default=marcas_d, key="pm")
        with pf2:
            ordem_prod = st.selectbox("Ordenar por", ["Receita Total", "Quantidade"], key="po")
        with pf3:
            top_n_mp = st.selectbox("Exibir top", [10, 20, 30, 50, 100], index=1, key="tn")

        prod_filtrado = prod_mp[prod_mp["marca"].isin(marcas_s)] if marcas_s else prod_mp
        sort_col = "receita" if ordem_prod == "Receita Total" else "qtd"
        prod_filtrado = prod_filtrado.sort_values(sort_col, ascending=False).head(top_n_mp).reset_index(drop=True)

        receita_total = prod_filtrado["receita"].sum()
        qtd_total = int(prod_filtrado["qtd"].sum())

        sh("Itens Vendidos")

        table_rows = ""
        for _, row in prod_filtrado.iterrows():
            img_url = str(row.get("img_url", "")).strip()
            cor = COR_MARCA.get(row["marca"], "#64748b")
            ref_full = str(row["referencia"])
            ref_display = ref_full[:20] + ("\u2026" if len(ref_full) > 20 else "")
            onerr = "this.style.display='none';this.nextSibling.style.display='flex';"
            if img_url.startswith("http"):
                foto_td = (
                    f"<td class='foto-cell'>"
                    f"<img src='{img_url}' onerror=\"{onerr}\" "
                    f"style='width:52px;height:52px;object-fit:contain;border-radius:6px;background:#0d1321;'/>"
                    f"<div class='no-img' style='display:none;'>&#8987;</div>"
                    f"</td>"
                )
            else:
                foto_td = "<td class='foto-cell'><div class='no-img'>&#8987;</div></td>"
            table_rows += (
                f"<tr>"
                f"{foto_td}"
                f"<td class='ref' title='{ref_full}'>{ref_display}</td>"
                f"<td class='marca-cell' style='color:{cor};'>{row['marca']}</td>"
                f"<td class='num'>{brl(row['receita'])}</td>"
                f"<td class='num'>{row['qtd']:,}</td>"
                f"</tr>"
            )

        total_row = (
            f"<tr class='total-row'>"
            f"<td colspan='3'><strong>Total geral</strong></td>"
            f"<td class='num'><strong>{brl(receita_total)}</strong></td>"
            f"<td class='num'><strong>{qtd_total:,}</strong></td>"
            f"</tr>"
        )

        st.markdown(f"""
        <style>
        .ptable{{width:100%;border-collapse:collapse;font-family:'DM Sans',sans-serif;}}
        .ptable th{{font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.1em;
                   color:#475569;padding:8px 14px;border-bottom:2px solid #1e2d4a;text-align:left;}}
        .ptable th.num{{text-align:right;}}
        .ptable td{{padding:10px 14px;border-bottom:1px solid #111827;vertical-align:middle;}}
        .ptable tr:hover td{{background:rgba(59,111,255,.04);}}
        .ptable td.num{{text-align:right;font-family:'DM Mono',monospace;color:#f1f5f9;font-size:.88rem;font-weight:600;}}
        .ptable td.ref{{font-family:'DM Mono',monospace;font-size:.78rem;color:#94a3b8;max-width:150px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}}
        .ptable td.marca-cell{{font-size:.78rem;font-weight:700;}}
        .ptable .foto-cell{{width:62px;padding:5px 10px;}}
        .no-img{{width:52px;height:52px;border-radius:6px;background:#1e2d4a;display:flex;align-items:center;justify-content:center;font-size:1.3rem;}}
        .ptable .total-row td{{border-top:2px solid #1e2d4a;font-weight:700;color:#f1f5f9;background:rgba(59,111,255,.07);}}
        .ptable .total-row td.num{{color:#f1f5f9;}}
        </style>
        <table class="ptable">
          <thead><tr>
            <th class="foto-cell">Foto</th>
            <th>Referência</th>
            <th>Marca</th>
            <th class="num">Receita Total</th>
            <th class="num">Qtde</th>
          </tr></thead>
          <tbody>{table_rows}{total_row}</tbody>
        </table>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        sh("Volume de Receita por Marca")
        seller_rec = prod_mp.groupby("marca")[["receita","qtd"]].sum().reset_index().sort_values("receita", ascending=False)
        sr1, sr2 = st.columns(2)
        with sr1:
            fig_sr = px.bar(seller_rec, x="marca", y="receita",
                            color="marca", color_discrete_map=COR_MARCA,
                            labels={"receita":"Receita (R$)","marca":""},
                            text=seller_rec["receita"].map(brl))
            fig_sr.update_traces(textposition="outside")
            fig_sr.update_layout(**L())
            st.plotly_chart(fig_sr, use_container_width=True)
        with sr2:
            fig_srp = px.pie(seller_rec, names="marca", values="receita",
                             color="marca", color_discrete_map=COR_MARCA, hole=0.55)
            fig_srp.update_traces(textinfo="percent+label", textfont_size=11)
            fig_srp.update_layout(**L(margin=dict(l=10,r=10,t=30,b=10)))
            st.plotly_chart(fig_srp, use_container_width=True)

        sh("Curva de Pareto — Top 15 Referências por Volume")
        p80 = prod_mp.sort_values("qtd", ascending=False).head(15).copy()
        total_qtd_all = prod_mp["qtd"].sum()
        if total_qtd_all > 0:
            p80["cum_pct"] = p80["qtd"].cumsum() / total_qtd_all * 100
            n80 = int((prod_mp.sort_values("qtd",ascending=False)["qtd"].cumsum() / total_qtd_all * 100 <= 80).sum()) + 1
            pct_cat = n80 / len(prod_mp) * 100 if len(prod_mp) > 0 else 0
            st.markdown(
                f"<div class='info'>📐 <strong>Pareto:</strong> "
                f"<strong>{n80} referência(s) ({pct_cat:.0f}% do mix)</strong> "
                f"representam 80% do volume faturado.</div>",
                unsafe_allow_html=True)
            fig_par = go.Figure()
            fig_par.add_trace(go.Bar(
                x=p80["referencia"].str[:30], y=p80["qtd"],
                marker_color=[COR_MARCA.get(b,"#3b6fff") for b in p80["marca"]],
                name="Unidades", opacity=0.85,
            ))
            fig_par.add_trace(go.Scatter(
                x=p80["referencia"].str[:30], y=p80["cum_pct"],
                mode="lines+markers", name="% Acumulado",
                line=dict(color="#f59e0b", width=2), yaxis="y2",
            ))
            fig_par.add_hline(y=80, line_dash="dot", line_color="#f43f5e",
                              yref="y2", annotation_text="80%",
                              annotation=dict(font_color="#f43f5e"))
            fig_par.update_layout(
                **L(), xaxis_tickangle=-30,
                yaxis2=dict(overlaying="y", side="right", range=[0,105], ticksuffix="%",
                            gridcolor="rgba(0,0,0,0)", tickcolor="#1e2d4a", linecolor="#1e2d4a"),
            )
            st.plotly_chart(fig_par, use_container_width=True)

        st.download_button("📥 Exportar itens vendidos",
                           data=prod_mp.rename(columns={
                               "referencia":"Referência","marca":"Marca",
                               "receita":"Receita Total","qtd":"Quantidade","img_url":"URL Foto",
                           }).to_csv(index=False).encode("utf-8"),
                           file_name="itens_vendidos.csv", mime="text/csv")


st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#1a2540;font-size:.7rem;font-family:DM Mono,monospace;'>"
    "⌚ Grupo Seculus · Receita via notas fiscais · "
    "Site Mondaine / Site Seculus / Site Timex / Multimarcas (E-time) → E-commerce"
    "</div>", unsafe_allow_html=True)
