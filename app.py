import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import StringIO
import requests
import re
from datetime import datetime, timedelta, date
import numpy as np
import json

try:
    from google.oauth2 import service_account
    from google.auth.transport.requests import Request as GoogleRequest
    HAS_GOOGLE_AUTH = True
except ImportError:
    HAS_GOOGLE_AUTH = False

st.set_page_config(
    page_title="Dashboard de Vendas · Grupo Seculus",
    page_icon="⌚",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700&family=DM+Mono:wght@400;500&display=swap');

/* ── DARK THEME (default) ── */
:root{
  --bg:       #080c14;
  --bg2:      #111827;
  --bg3:      #131e35;
  --border:   #1e2d4a;
  --border2:  #1a2540;
  --text:     #e2e8f0;
  --text2:    #94a3b8;
  --text3:    #64748b;
  --text4:    #475569;
  --topbar:   linear-gradient(90deg,#0d1321,#111827);
  --topbar-b: #1a2540;
  --card:     linear-gradient(135deg,#111827,#131e35);
  --card-h:   rgba(59,111,255,.05);
  --info-bg:  linear-gradient(135deg,#0f1c35,#111e38);
  --info-b:   #1e3a5f;
  --info-t:   #93c5fd;
  --warn-bg:  linear-gradient(135deg,#1a1505,#1f1a06);
  --warn-b:   #3d2e00;
  --warn-t:   #fde68a;
  --zone-bg:  linear-gradient(135deg,#0f1421,#111827);
  --tab-b:    #1a2540;
  --rc-row-b: #1a2540;
  --ptable-h: rgba(59,111,255,.04);
  --ptable-th:#1e2d4a;
  --ptable-tr:#111827;
}


html,body,[class*="css"]{font-family:'DM Sans',sans-serif;}
.stApp{background-color:var(--bg)!important;color:var(--text)!important;}
[data-testid="stSidebar"]{display:none;}

[data-testid="stMetric"]{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:20px 24px;transition:all .25s;}
[data-testid="stMetric"]:hover{border-color:#3b6fff;box-shadow:0 0 24px rgba(59,111,255,.14);}
[data-testid="stMetricLabel"]{color:var(--text3)!important;font-size:.72rem!important;font-weight:600!important;text-transform:uppercase;letter-spacing:.1em;}
[data-testid="stMetricValue"]{color:var(--text)!important;font-size:1.5rem!important;font-weight:700!important;font-family:'DM Mono',monospace!important;}
[data-testid="stMetricDelta"]{font-size:.8rem!important;}
h1,h2,h3,h4{color:var(--text)!important;}
hr{border-color:var(--border2)!important;}

.stTabs [data-baseweb="tab-list"]{background:transparent!important;border-bottom:1px solid var(--tab-b)!important;gap:0;padding:0;}
.stTabs [data-baseweb="tab"]{color:var(--text3)!important;font-weight:500!important;font-size:.88rem!important;padding:10px 22px!important;border-radius:0!important;border-bottom:2px solid transparent!important;}
.stTabs [aria-selected="true"]{color:var(--text)!important;border-bottom:2px solid #3b6fff!important;background:transparent!important;}
.stTabs [data-baseweb="tab"]:hover{color:var(--text2)!important;background:var(--card-h)!important;}
.stDataFrame{border:1px solid var(--border)!important;border-radius:12px!important;}

.topbar{background:var(--topbar);border-bottom:1px solid var(--topbar-b);padding:0 28px;display:flex;align-items:center;justify-content:space-between;height:58px;margin:-1rem -1rem 1.5rem -1rem;position:sticky;top:0;z-index:999;}
.topbar-brand{display:flex;align-items:center;gap:10px;font-size:1rem;font-weight:700;color:#f1f5f9;letter-spacing:-.02em;}
.topbar-brand span{color:#3b6fff;}
.topbar-right{display:flex;align-items:center;gap:14px;font-size:.73rem;color:#94a3b8;font-family:'DM Mono',monospace;}
.dot{width:7px;height:7px;border-radius:50%;background:#10b981;display:inline-block;animation:blink 2s infinite;}
@keyframes blink{0%,100%{opacity:1;}50%{opacity:.35;}}


.sh{display:flex;align-items:center;gap:10px;margin:22px 0 12px;}
.sh h4{margin:0!important;font-size:.78rem!important;font-weight:700!important;color:var(--text4)!important;text-transform:uppercase;letter-spacing:.1em;}
.sh .ln{flex:1;height:1px;background:linear-gradient(90deg,var(--border2),transparent);}

.info{background:var(--info-bg);border:1px solid var(--info-b);border-left:3px solid #3b6fff;border-radius:0 12px 12px 0;padding:12px 16px;margin:8px 0;font-size:.85rem;color:var(--info-t);line-height:1.6;}
.warn{background:var(--warn-bg);border:1px solid var(--warn-b);border-left:3px solid #f59e0b;border-radius:0 12px 12px 0;padding:12px 16px;margin:8px 0;font-size:.85rem;color:var(--warn-t);line-height:1.6;}
.zone{background:var(--zone-bg);border:1px dashed var(--border);border-radius:16px;padding:40px;text-align:center;}
.zone h3{color:var(--text)!important;margin-bottom:8px!important;}
.zone p{color:var(--text3);font-size:.88rem;}

.rc{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:20px 22px;}
.rc-title{font-size:.75rem;font-weight:700;text-transform:uppercase;letter-spacing:.1em;margin:0 0 14px 0;}
.rc-row{display:flex;justify-content:space-between;align-items:center;padding:5px 0;border-bottom:1px solid var(--rc-row-b);font-size:.83rem;color:var(--text2);}
.rc-row:last-child{border-bottom:none;}
.rc-val{font-family:'DM Mono',monospace;color:var(--text);font-weight:600;font-size:.88rem;}
.rc-badge{padding:2px 8px;border-radius:6px;font-size:.75rem;font-weight:700;font-family:'DM Mono',monospace;}
.rc-green{background:rgba(16,185,129,.15);color:#34d399;border:1px solid rgba(16,185,129,.25);}
.rc-red{background:rgba(244,63,94,.15);color:#fb7185;border:1px solid rgba(244,63,94,.25);}
.rc-amber{background:rgba(245,158,11,.15);color:#fbbf24;border:1px solid rgba(245,158,11,.25);}

/* ── COMPACT META CARDS ── */
.mc{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:18px 20px;transition:border-color .2s;}
.mc:hover{border-color:#3b6fff;}
.mc-icon{font-size:.9rem;margin-bottom:2px;color:var(--text3);}
.mc-label{font-size:.68rem;font-weight:600;text-transform:uppercase;letter-spacing:.1em;color:var(--text3);margin-bottom:2px;}
.mc-value{font-size:1.6rem;font-weight:700;font-family:'DM Mono',monospace;color:var(--text);line-height:1.15;}
.mc-sub{display:flex;align-items:center;gap:8px;margin-top:3px;font-size:.75rem;font-family:'DM Mono',monospace;font-weight:600;color:var(--text3);}
.mc-sub .pos{color:#10b981;}
.mc-sub .neg{color:#f43f5e;}
.mc-sub .neu{color:var(--text3);}
.mc-sub .dot-sep{color:var(--text3);}
.mc.ok{border-color:#10b981;}
.mc.warn2{border-color:#f59e0b;}
.mc.bad{border-color:#f43f5e;}
.mc.ok  .mc-value{color:#10b981;}
.mc.bad .mc-value{color:#f43f5e;}

.meta-bar-wrap{margin-top:10px;height:5px;border-radius:3px;background:#1e2d4a;overflow:hidden;}
.meta-bar-fill{height:100%;border-radius:3px;transition:width .4s;}
.mc-progress-row{display:flex;justify-content:space-between;align-items:center;margin-top:6px;}
.mc-pct{font-size:.7rem;font-family:'DM Mono',monospace;color:var(--text3);}

/* ── META SEPARATOR ── */
.meta-sep{border:none;border-top:1px solid var(--border2);margin:12px 0;}

/* ── PRODUCT TABLE ── */
.ptable{width:100%;border-collapse:collapse;font-family:'DM Sans',sans-serif;}
.ptable th{font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.1em;color:var(--text4);padding:8px 14px;border-bottom:2px solid var(--ptable-th);text-align:left;}
.ptable th.num{text-align:right;}
.ptable td{padding:10px 14px;border-bottom:1px solid var(--ptable-tr);vertical-align:middle;}
.ptable tr:hover td{background:var(--ptable-h);}
.ptable td.num{text-align:right;font-family:'DM Mono',monospace;color:var(--text);font-size:.88rem;font-weight:600;}
.ptable td.ref{font-family:'DM Mono',monospace;font-size:.78rem;color:var(--text2);max-width:150px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
.ptable td.marca-cell{font-size:.78rem;font-weight:700;}
.ptable .foto-cell{width:62px;padding:5px 10px;}
.no-img{width:52px;height:52px;border-radius:6px;background:var(--border);display:flex;align-items:center;justify-content:center;font-size:1.3rem;}
.ptable .total-row td{border-top:2px solid var(--ptable-th);font-weight:700;color:var(--text);background:var(--ptable-h);}

/* ── PRODUCT GRID CARDS ── */
.prod-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:14px;margin-top:12px;}
.prod-card{background:var(--card);border:1px solid var(--border);border-radius:14px;overflow:hidden;transition:all .25s;display:flex;flex-direction:column;}
.prod-card:hover{border-color:#3b6fff;box-shadow:0 0 20px rgba(59,111,255,.12);transform:translateY(-2px);}
.prod-img-wrap{background:var(--bg);height:160px;display:flex;align-items:center;justify-content:center;overflow:hidden;border-bottom:1px solid var(--border2);}
.prod-img-wrap img{max-height:150px;max-width:100%;object-fit:contain;transition:transform .3s;}
.prod-card:hover .prod-img-wrap img{transform:scale(1.06);}
.prod-img-placeholder{width:60px;height:60px;border-radius:50%;background:var(--border);display:flex;align-items:center;justify-content:center;font-size:1.6rem;color:#3b6fff;}
.prod-info{padding:14px 16px;flex:1;display:flex;flex-direction:column;gap:4px;}
.prod-badge{display:inline-block;padding:2px 8px;border-radius:6px;font-size:.7rem;font-weight:700;font-family:'DM Mono',monospace;margin-bottom:4px;}
.prod-name{font-size:.82rem;font-weight:600;color:var(--text);line-height:1.4;margin-bottom:6px;}
.prod-sku{font-size:.7rem;color:var(--text4);font-family:'DM Mono',monospace;}
.prod-stats{display:flex;gap:12px;margin-top:auto;padding-top:10px;border-top:1px solid var(--border2);}
.prod-stat{display:flex;flex-direction:column;gap:2px;}
.prod-stat-label{font-size:.65rem;color:var(--text4);text-transform:uppercase;letter-spacing:.08em;font-weight:600;}
.prod-stat-val{font-size:.85rem;font-weight:700;color:var(--text);font-family:'DM Mono',monospace;}
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

# GIDs das abas da planilha unificada — atualizar quando o link for confirmado
SHEET_BASE    = ""
GID_NF        = "0"
GID_EC        = "1"
GID_METAS     = "2"
GID_META_INV  = "3"   # Nova aba: Meta x Investimento
GID_ACESSOS   = "4"
GID_CAMPANHAS = "5"

COR_CLUSTER = {
    "🌳 Orgânico":        "#10b981",
    "🟢 Google Ads":      "#3b6fff",
    "🔵 Meta Ads":        "#f59e0b",
    "🔴 Livelo":          "#f43f5e",
    "🟡 Direto":          "#64748b",
    "🟡 Mais Plataforma": "#8b5cf6",
    "🔵 City Ads":        "#06b6d4",
    "⚫ CRM Bônus":       "#475569",
    "🟣 Social":          "#ec4899",
    "🟣 Livelo":          "#fb7185",
    "🍪 Perda de Cookies":"#94a3b8",
    "Outros":             "#334155",
}
COR_PLAT = {
    "meta_ads":   "#f59e0b",
    "google_ads": "#3b6fff",
}

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
    # Sniff col 6 and 7 to detect whether marketingtags column is present
    # With marketingtags: col6=tag, col7=payment → col7 is payment
    # Without marketingtags: col6=payment, col7=installments (numeric)
    try:
        rows = list(_csv.reader(text.split("\n")[:3]))
        data_row = rows[0]
        col6 = str(data_row[6]).strip().lower() if len(data_row) > 6 else ""
        col7 = str(data_row[7]).strip().lower() if len(data_row) > 7 else ""
        payment_kws = ["pix","credit","debit","boleto","card","cartao","cartão","mastercard","visa","elo","hipercard"]
        col6_is_payment = any(p in col6 for p in payment_kws)
        col7_is_payment = any(p in col7 for p in payment_kws)
        # If col6 is payment (not col7), marketingtags column is absent
        no_mktags = col6_is_payment and not col7_is_payment
    except Exception:
        no_mktags = False

    if ncols >= 19:
        return EC_COLS_18F if no_mktags else EC_COLS_19
    if ncols == 18:
        return EC_COLS_18F if no_mktags else EC_COLS_18
    if ncols == 17:
        return EC_COLS_17
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
    _ini = pd.Timestamp(ini)
    _fim = pd.Timestamp(fim) + pd.Timedelta(days=1)  # exclusive end: catches full day
    return df[(df["data"] >= _ini) & (df["data"] < _fim)].copy()

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

_MESES_BR = {"jan":1,"fev":2,"mar":3,"abr":4,"mai":5,"jun":6,
             "jul":7,"ago":8,"set":9,"out":10,"nov":11,"dez":12}

@st.cache_data(ttl=3600)
def load_meta_inv(url: str, token: str = "") -> pd.DataFrame:
    try:
        sess = requests.Session(); sess.trust_env = False
        hdrs = {"User-Agent":"Mozilla/5.0"}
        if token: hdrs["Authorization"] = f"Bearer {token}"
        r = sess.get(url, timeout=20, headers=hdrs)
        r.raise_for_status()
        try:    text = r.content.decode("utf-8")
        except: text = r.content.decode("latin-1")
        df = pd.read_csv(StringIO(text), header=None, dtype=str)

        def _p(s):
            try: return float(str(s).strip().replace("R$","").replace(" ","").replace(".","").replace(",","."))
            except: return 0.0

        rows = []
        for _, row in df.iloc[2:].iterrows():
            mes_str = str(row.iloc[0]).strip().lower()
            if mes_str in ("total","nan",""): continue
            mes_num = _MESES_BR.get(mes_str[:3], 0)
            if mes_num == 0: continue
            rows.append({
                "mes": mes_num, "mes_str": mes_str.capitalize(),
                "meta_b2c":  _p(row.iloc[1]),  "meta_sec": _p(row.iloc[2]),
                "meta_mon":  _p(row.iloc[3]),  "meta_tim": _p(row.iloc[4]),
                "meta_eti":  _p(row.iloc[5]),  "meta_inv": _p(row.iloc[6]),
                "meta_roas": _p(row.iloc[7]),
                "inv_sec":   _p(row.iloc[10]), "inv_mon":  _p(row.iloc[11]),
                "inv_tim":   _p(row.iloc[12]), "inv_eti":  _p(row.iloc[13]),
                "inv_total": _p(row.iloc[14]),
            })
        return pd.DataFrame(rows)
    except Exception:
        return pd.DataFrame()

def meta_inv_do_mes(df_mi: pd.DataFrame, mes: int) -> dict:
    _e = dict(meta_b2c=0,meta_sec=0,meta_mon=0,meta_tim=0,meta_eti=0,
              meta_inv=0,meta_roas=0,inv_sec=0,inv_mon=0,inv_tim=0,inv_eti=0,inv_total=0)
    if df_mi.empty: return _e
    row = df_mi[df_mi["mes"] == mes]
    return row.iloc[0].to_dict() if not row.empty else _e

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


def parse_brl_num(s):
    try:
        return float(str(s).strip().replace("R$ ","").replace(".","").replace(",","."))
    except Exception:
        return 0.0

def parse_sessions_num(s):
    try:
        return float(str(s).strip().replace(".","").replace(",","."))
    except Exception:
        return 0.0

def parse_mult_num(s):
    try:
        return float(str(s).strip().replace("x",""))
    except Exception:
        return 0.0

def parse_pct_num(s):
    try:
        return float(str(s).strip().replace("%","").replace(",","."))
    except Exception:
        return 0.0

def _fetch_sheet_csv(sid: str, gid: str, token: str) -> str:
    """Fetch a sheet as CSV text. Uses Sheets API v4 with token, or export URL for public sheets."""
    import csv as _csv, urllib.parse
    from io import StringIO as _SIO

    sess = requests.Session()
    sess.trust_env = False
    headers = {"User-Agent": "Mozilla/5.0"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    if token:
        # Get sheet title from metadata
        rm = sess.get(
            f"https://sheets.googleapis.com/v4/spreadsheets/{sid}?fields=sheets.properties",
            headers=headers, timeout=15)
        if rm.status_code == 403:
            raise Exception(
                "Acesso negado (403). Verifique se a SA foi adicionada como Leitor na planilha.")
        rm.raise_for_status()
        sheet_title = None
        for s in rm.json().get("sheets", []):
            p = s.get("properties", {})
            if str(p.get("sheetId","")) == str(gid):
                sheet_title = p.get("title")
                break
        if not sheet_title:
            raise Exception(f"Aba com gid={gid} não encontrada.")
        # Fetch values
        rd = sess.get(
            f"https://sheets.googleapis.com/v4/spreadsheets/{sid}"
            f"/values/{urllib.parse.quote(sheet_title)}?valueRenderOption=FORMATTED_VALUE",
            headers=headers, timeout=20)
        rd.raise_for_status()
        rows = rd.json().get("values", [])
        if not rows:
            raise Exception("A aba está vazia.")
        buf = _SIO()
        _csv.writer(buf).writerows(rows)
        return buf.getvalue()
    else:
        r = sess.get(
            f"https://docs.google.com/spreadsheets/d/{sid}/export?format=csv&gid={gid}",
            headers=headers, timeout=20, allow_redirects=False)
        if r.status_code in (301,302,303,307,308):
            raise Exception("Planilha não pública. Configure o Service Account.")
        if r.status_code == 403:
            raise Exception("Acesso negado. Configure o Service Account.")
        r.raise_for_status()
        try:    return r.content.decode("utf-8")
        except: return r.content.decode("latin-1")


@st.cache_data(ttl=270)
def load_campanhas(url: str, token: str = "") -> tuple:
    sid = url.split("/d/")[1].split("/")[0] if "/d/" in url else ""
    gid = url.split("gid=")[1].split("&")[0] if "gid=" in url else "0"
    text = _fetch_sheet_csv(sid, gid, token)
    df = pd.read_csv(StringIO(text), dtype=str)
    df.columns = list(df.columns[:-2]) + ["marca","data"]
    df["data_dt"]  = pd.to_datetime(df["data"], dayfirst=True, errors="coerce")
    df["inv"]      = df["Investimento"].apply(parse_brl_num)
    df["rec_num"]  = df["Receita"].apply(parse_brl_num)
    df["roas_num"] = df["ROAS"].apply(parse_mult_num)
    df["roas1_num"]= df["ROAS 1ª Compra"].apply(parse_mult_num)
    df["cpa_num"]  = df["CPA"].apply(parse_brl_num)
    df["trans"]    = pd.to_numeric(df["Transações"], errors="coerce").fillna(0).astype(int)
    df["trans1"]   = pd.to_numeric(df["Trans. 1ª Compra"], errors="coerce").fillna(0).astype(int)
    return df.dropna(subset=["data_dt"])

@st.cache_data(ttl=270)
def load_acessos(url: str, token: str = "") -> pd.DataFrame:
    sid = url.split("/d/")[1].split("/")[0] if "/d/" in url else ""
    gid = url.split("gid=")[1].split("&")[0] if "gid=" in url else "0"
    text = _fetch_sheet_csv(sid, gid, token)
    df = pd.read_csv(StringIO(text), dtype=str)
    cols = list(df.columns)
    if cols[-1].startswith("Unnamed"):
        cols[-1] = "data"
    df.columns = cols
    df["data_dt"]     = pd.to_datetime(df["data"], dayfirst=True, errors="coerce")
    df["sessoes_num"] = df["Sessões"].apply(parse_sessions_num)
    df["pedidos_num"] = pd.to_numeric(df["Pedidos"], errors="coerce").fillna(0).astype(int)
    df["pagos_num"]   = pd.to_numeric(df["Pedidos Pagos"], errors="coerce").fillna(0).astype(int)
    df["receita_num"] = df["Receita Paga"].apply(parse_brl_num)
    df["novos_num"]   = pd.to_numeric(df["Novos Clientes"], errors="coerce").fillna(0).astype(int)
    df["rec_novos"]   = df["Receita Novos"].apply(parse_brl_num)
    df["tx_conv"]     = df["Taxa Conv."].apply(parse_pct_num)
    df["tx_carr"]     = df["Taxa Carrinho"].apply(parse_pct_num)
    return df.dropna(subset=["data_dt"])


def gid_url(sheet_id: str, gid: str) -> str:
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"

def gid_pub_url(sheet_id: str, gid: str) -> str:
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/pub?output=csv&gid={gid}"

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

for k, v in [("df_mp_raw", None),("df_ec_raw", None),
             ("ts_mp", None),("ts_ec", None)]:
    if k not in st.session_state:
        st.session_state[k] = v

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly",
          "https://www.googleapis.com/auth/drive.readonly"]

@st.cache_resource
def _sa_credentials():
    """Load and cache SA credentials object in memory (not serialized)."""
    if not HAS_GOOGLE_AUTH:
        return None
    try:
        sa_info = dict(st.secrets["gcp_service_account"])
        return service_account.Credentials.from_service_account_info(sa_info, scopes=SCOPES)
    except Exception:
        return None

def _get_sa_token() -> str:
    """Get a fresh SA bearer token as a plain string. Returns '' if SA not configured."""
    creds = _sa_credentials()
    if creds is None:
        return ""
    try:
        creds.refresh(GoogleRequest())
        return creds.token or ""
    except Exception:
        return ""

def _sa_configured() -> bool:
    """Check whether SA secrets are present and loadable."""
    return _sa_credentials() is not None

@st.cache_data(ttl=270)
def load_url(url: str, tipo: str, token: str = "") -> tuple:
    try:
        sid = None
        gid = None
        url = url.strip()
        if "docs.google.com" in url:
            sid = url.split("/d/")[1].split("/")[0]
            gid = url.split("gid=")[1].split("&")[0].split("#")[0] if "gid=" in url else None

        sess = requests.Session()
        sess.trust_env = False
        headers = {"User-Agent": "Mozilla/5.0"}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        # With SA token: use Sheets API v4 to get sheet name then download as CSV
        # This avoids the /export redirect to googleusercontent.com
        if token and sid:
            # Step 1: get sheet metadata to find the sheet name for the given gid
            meta_url = f"https://sheets.googleapis.com/v4/spreadsheets/{sid}?fields=sheets.properties"
            rm = sess.get(meta_url, headers=headers, timeout=15)
            if rm.status_code == 403:
                raise Exception(
                    "Acesso negado (403) com Service Account. "
                    "Verifique se o e-mail da SA foi adicionado como Leitor na planilha.")
            rm.raise_for_status()
            sheets_meta = rm.json().get("sheets", [])
            sheet_title = None
            for s in sheets_meta:
                props = s.get("properties", {})
                if gid is None or str(props.get("sheetId","")) == str(gid):
                    sheet_title = props.get("title")
                    break
            if not sheet_title:
                raise Exception(f"Aba com gid={gid} não encontrada na planilha.")

            # Step 2: read all values via Sheets API v4
            import urllib.parse
            range_enc = urllib.parse.quote(f"{sheet_title}")
            data_url = (f"https://sheets.googleapis.com/v4/spreadsheets/{sid}"
                        f"/values/{range_enc}?valueRenderOption=FORMATTED_VALUE")
            rd = sess.get(data_url, headers=headers, timeout=20)
            rd.raise_for_status()
            rows = rd.json().get("values", [])
            if not rows:
                raise Exception("A aba está vazia.")
            # Convert to CSV text
            import csv as _csv
            from io import StringIO as _SIO
            buf = _SIO()
            w = _csv.writer(buf)
            w.writerows(rows)
            raw = buf.getvalue()
        else:
            # No token: try export URL directly (works only for public sheets)
            export_url = (f"https://docs.google.com/spreadsheets/d/{sid}/export?format=csv"
                          + (f"&gid={gid}" if gid else "")) if sid else url
            r = sess.get(export_url, timeout=20, headers=headers, allow_redirects=False)
            if r.status_code in (301, 302, 303, 307, 308):
                raise Exception(
                    "A planilha não está acessível publicamente. "
                    "Configure o Service Account nos Secrets do Streamlit.")
            if r.status_code == 403:
                raise Exception(
                    "Acesso negado (403). Configure o Service Account nos Secrets do Streamlit.")
            r.raise_for_status()
            try:    raw = r.content.decode("utf-8")
            except: raw = r.content.decode("latin-1")
            if "<html" in raw[:200].lower():
                raise Exception(
                    "Google retornou HTML em vez de CSV. "
                    "Configure o Service Account nos Secrets do Streamlit.")

        df = parse_csv(raw, tipo)
        return df, datetime.now().strftime("%d/%m/%Y %H:%M")
    except Exception as e:
        raise e

def parse_csv(text, tipo):
    if tipo == "ec":
        # Detect if first row is a header (contains known column names)
        try:
            import csv as _csv
            first_row = list(_csv.reader([text.split("\n")[0]]))[0]
            first_lower = [c.strip().lower() for c in first_row]
            has_header = any(h in first_lower for h in ["order","creation","status","utmsource","payment system name"])
        except Exception:
            has_header = False

        if has_header:
            df = pd.read_csv(StringIO(text), dtype=str, keep_default_na=False, na_values=[""])
            # Normalize column names to internal aliases
            col_map = {
                "creation":            "created_at",
                "client name":         "customer_name",
                "uf":                  "state",
                "coupon":              "marketingtags",
                "payment system name": "payment_method",
                "quantity_sku":        "quantity_sku",
                "id_sku":              "sku",
                "reference code":      "referencia",
                "sku name":            "product_name",
                "sku total price":     "sku_selling_price",
                "discounts names":     "discount_tags",
                "seller name":         "brand",
            }
            df.columns = [col_map.get(c.strip().lower(), c.strip().lower()) for c in df.columns]
            # Add missing columns with defaults
            for col in ["livelo_tag","sku_total_price","phone","foto_produto","installments"]:
                if col not in df.columns:
                    df[col] = ""
            return df
        else:
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

    # If columns came from headerless format, rename by position
    if "created_at" not in df.columns and len(df.columns) in (16, 17, 18, 19):
        ncols = len(df.columns)
        if ncols >= 19:   expected = EC_COLS_19
        elif ncols == 18: expected = EC_COLS_18
        else:             expected = EC_COLS_17
        if len(df.columns) == len(expected):
            df.columns = expected

    # Ensure required columns exist with defaults
    for col, default in [("livelo_tag",""), ("marketingtags",""), ("foto_produto",""),
                         ("phone",""), ("sku_total_price","0"), ("discount_tags",""),
                         ("brand",""), ("utmsource","")]:
        if col not in df.columns:
            df[col] = default

    def safe_num(s):
        return pd.to_numeric(
            s.astype(str).str.strip().str.replace(".",",",regex=False
            ).str.replace(",",".",regex=False).str.replace(r"[^\d\.]","",regex=True),
            errors="coerce"
        ).fillna(0)

    # sku_selling_price may be named differently — try both
    price_col = "sku_selling_price" if "sku_selling_price" in df.columns else "sku total price"
    if price_col not in df.columns:
        df["sku_selling_price"] = 0.0
    else:
        df["sku_selling_price"] = safe_num(df[price_col])

    df["quantity_sku"] = safe_num(df["quantity_sku"]) if "quantity_sku" in df.columns else 1.0

    suspicious = (df["sku_selling_price"] < 10) & (df["sku_selling_price"] > 0)
    df.loc[suspicious, "sku_selling_price"] = df.loc[suspicious, "sku_selling_price"] * 1000

    df["line_total"] = df["sku_selling_price"] * df["quantity_sku"]

    date_col = "created_at" if "created_at" in df.columns else "creation"
    _raw = df[date_col].astype(str).str.strip()
    # Detect format: ISO starts with 4-digit year followed by '-' (e.g. 2026-04-01)
    # BR format: DD/MM/YYYY (e.g. 01/04/2026)
    _sample = _raw.dropna().iloc[0] if not _raw.dropna().empty else ""
    _is_iso = len(_sample) >= 10 and _sample[4:5] == "-"
    if _is_iso:
        _parsed = pd.to_datetime(_raw, errors="coerce", utc=True)
        if _parsed.dt.tz is not None:
            _parsed = _parsed.dt.tz_localize(None)
    else:
        _parsed = pd.to_datetime(_raw, errors="coerce", dayfirst=True)
    df["data"] = _parsed.dt.normalize()

    df["status"]    = df["status"].astype(str).str.strip()
    df["faturado"]  = df["status"].str.lower().isin(
        ["faturado","aprovado","entregue","complete","paid","concluido","concluído"])
    df["cancelado"] = df["status"].str.lower().isin(
        ["cancelado","cancelada","canceled","cancelled","devolvido","devolvida","returned","recusado"])
    df["livelo"]    = df["livelo_tag"].astype(str).str.strip().str.lower() == "livelo"
    df["utmsource"] = df["utmsource"].replace("", np.nan).fillna("Direto").astype(str).str.strip()
    df["order"]     = df["order"].astype(str).str.strip()
    df["brand"]     = df["brand"].astype(str).str.strip()

    if "foto_produto" in df.columns and df["foto_produto"].astype(str).str.startswith("http").any():
        df["img_url"] = df["foto_produto"].apply(lambda u: u if str(u).startswith("http") else "")
    else:
        df["img_url"] = IMG_BASE_URL + "/" + df["brand"] + "/Baixa/" + df.get("sku", pd.Series([""] * len(df))).astype(str) + IMG_EXT

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


with st.expander("⚙️  Fonte de Dados", expanded=not has_mp):
    ex1, ex2 = st.columns([3, 1])
    with ex1:
        st.markdown("**📋 Planilha Unificada (Google Sheets)**")

        _sa_ok = _sa_configured()
        if _sa_ok:
            st.markdown(
                "<div style='font-size:.74rem;padding:8px 12px;margin-bottom:10px;"
                "background:rgba(16,185,129,.08);border-radius:8px;border:1px solid rgba(16,185,129,.2);color:#34d399;'>"
                "🔐 <strong>Service Account configurada</strong> — acesso autenticado e seguro. "
                "A planilha não precisa ser pública.</div>",
                unsafe_allow_html=True)
        else:
            st.markdown(
                "<div style='font-size:.74rem;padding:8px 12px;margin-bottom:10px;"
                "background:rgba(245,158,11,.08);border-radius:8px;border:1px solid rgba(245,158,11,.2);color:#fbbf24;'>"
                "⚠️ <strong>Service Account não configurada.</strong> "
                "Siga o guia abaixo para acessar planilhas privadas com segurança.</div>",
                unsafe_allow_html=True)

        st.markdown(
            "<div style='font-size:.74rem;color:#64748b;margin-bottom:8px;'>"
            "Cole o link da planilha que contém todas as abas: "
            "<strong>E-commerce · Marketplace · Metas · Acessos · Campanhas</strong></div>",
            unsafe_allow_html=True)
        sheet_url = st.text_input("URL da Planilha Google Sheets", key="sheet_url_in",
                                  placeholder="https://docs.google.com/spreadsheets/d/...")
        st.markdown(
            "<div style='font-size:.74rem;color:#64748b;margin-top:6px;'>"
            "GIDs das abas (0=Marketplace, 1=E-commerce, 2=Metas, 3=Acessos, 4=Campanhas) "
            "— ajuste se necessário:</div>", unsafe_allow_html=True)
        gcols = st.columns(6)
        gid_nf   = gcols[0].text_input("Marketplace",    value="0", key="gid_nf")
        gid_ec   = gcols[1].text_input("E-commerce",     value="1", key="gid_ec")
        gid_met  = gcols[2].text_input("Metas",          value="2", key="gid_met")
        gid_mi   = gcols[3].text_input("Meta x Inv.",    value="3", key="gid_mi")
        gid_ac   = gcols[4].text_input("Acessos",        value="4", key="gid_ac")
        gid_ca   = gcols[5].text_input("Campanhas",      value="5", key="gid_ca")

        if st.button("Carregar Planilha", use_container_width=True, key="btn_sheet"):
            url = sheet_url.strip()
            if not url:
                st.warning("Insira a URL da planilha.")
            elif "/d/" not in url:
                st.error("URL inválida. Copie o link direto da barra de endereço do Google Sheets.")
            else:
                sid   = url.split("/d/")[1].split("/")[0]
                token = _get_sa_token()
                log_msgs = []
                ok_mp = False

                # Auto-detect GIDs by listing sheet tabs
                with st.spinner("Lendo abas da planilha..."):
                    try:
                        sess = requests.Session(); sess.trust_env = False
                        hdrs = {"User-Agent":"Mozilla/5.0"}
                        if token: hdrs["Authorization"] = f"Bearer {token}"
                        rm = sess.get(
                            f"https://sheets.googleapis.com/v4/spreadsheets/{sid}?fields=sheets.properties",
                            headers=hdrs, timeout=15)
                        rm.raise_for_status()
                        abas = {str(s["properties"]["sheetId"]): s["properties"]["title"]
                                for s in rm.json().get("sheets", [])}
                        abas_inv = {v.strip().lower(): k for k, v in abas.items()}
                        st.info(f"Abas encontradas: {', '.join(abas.values())}")

                        def _resolve_gid(user_input, name_hints):
                            u = user_input.strip()
                            if u in abas: return u          # exact gid match
                            for hint in name_hints:
                                if hint in abas_inv: return abas_inv[hint]
                            return u                         # fallback to whatever user typed

                        gid_nf_r  = _resolve_gid(gid_nf,  ["base dashboard - marketplace","marketplace","nf","faturamento","base dashboard"])
                        gid_ec_r  = _resolve_gid(gid_ec,  ["base dashboard - e-commerce","e-commerce","ecommerce","ec"])
                        gid_mi_r  = _resolve_gid(gid_mi,  ["meta x investimento","meta x inv","metainv","meta inv"])
                        gid_ac_r  = _resolve_gid(gid_ac,  ["acessos","acesso"])
                        gid_ca_r  = _resolve_gid(gid_ca,  ["campanhas","campanha"])
                    except Exception as e:
                        st.error(f"Erro ao listar abas: {e}")
                        gid_nf_r = gid_nf; gid_ec_r = gid_ec
                        gid_ac_r = gid_ac; gid_ca_r = gid_ca

                with st.spinner("Carregando aba Marketplace/NF..."):
                    try:
                        raw_mp, ts_mp_ = load_url(gid_url(sid, gid_nf_r), "mp", token)
                        if raw_mp is not None and not raw_mp.empty:
                            st.session_state.df_mp_raw = raw_mp
                            st.session_state.ts_mp     = ts_mp_
                            st.session_state.sheet_id  = sid
                            st.session_state._gid_ac = gid_ac_r
                            st.session_state._gid_ca = gid_ca_r
                            st.session_state._gid_mi = gid_mi_r
                            log_msgs.append(f"✅ Marketplace/NF: {len(raw_mp)} linhas (gid={gid_nf_r})")
                            ok_mp = True
                        else:
                            log_msgs.append(f"❌ Marketplace/NF: sem dados (gid={gid_nf_r})")
                    except Exception as e:
                        log_msgs.append(f"❌ Marketplace/NF: {e}")

                with st.spinner("Carregando aba E-commerce..."):
                    try:
                        raw_ec, ts_ec_ = load_url(gid_url(sid, gid_ec_r), "ec", token)
                        if raw_ec is not None and not raw_ec.empty:
                            st.session_state.df_ec_raw = raw_ec
                            st.session_state.ts_ec     = ts_ec_
                            log_msgs.append(f"✅ E-commerce: {len(raw_ec)} linhas (gid={gid_ec_r})")
                        else:
                            log_msgs.append(f"⚪ E-commerce: sem dados (gid={gid_ec_r}, opcional)")
                    except Exception as e:
                        log_msgs.append(f"⚪ E-commerce: {e} (opcional)")

                for msg in log_msgs:
                    if msg.startswith("✅"):
                        st.success(msg)
                    elif msg.startswith("❌"):
                        st.error(msg)
                    else:
                        st.info(msg)

                if ok_mp:
                    st.rerun()

    with ex2:
        _sa_ok = _sa_configured()
        st.markdown("**Status**")
        st.markdown(
            f"{'🟢' if has_mp else '🔴'} Faturamento<br>"
            f"{'🟢' if has_ec else '⚪'} E-commerce<br>"
            f"{'🟢' if st.session_state.get('sheet_id') else '⚪'} Acessos/Campanhas<br>"
            f"{'🔐' if _sa_ok else '🔓'} Service Account",
            unsafe_allow_html=True)
        if not _sa_ok:
            with st.expander("🔐 Como configurar Service Account"):
                st.markdown("""
**1. Google Cloud Console**
- Acesse [console.cloud.google.com](https://console.cloud.google.com)
- Crie um projeto (ou use um existente)
- Ative a **Google Sheets API** e a **Google Drive API**

**2. Criar Service Account**
- IAM e Admin → Contas de serviço → Criar
- Dê um nome (ex: `dashboard-seculus`)
- Em **Chaves**, clique Adicionar chave → JSON
- Baixe o arquivo `.json`

**3. Compartilhar a planilha**
- No Google Sheets, clique em **Compartilhar**
- Adicione o e-mail da SA (`...@...iam.gserviceaccount.com`) como **Leitor**
- A planilha permanece privada

**4. Adicionar ao Streamlit**
- No Streamlit Cloud: Settings → Secrets
- Cole o conteúdo abaixo com os dados do JSON:

```toml
[gcp_service_account]
type = "service_account"
project_id = "seu-projeto"
private_key_id = "..."
private_key = "-----BEGIN RSA PRIVATE KEY-----\\n...\\n-----END RSA PRIVATE KEY-----\\n"
client_email = "dashboard@...iam.gserviceaccount.com"
client_id = "..."
token_uri = "https://oauth2.googleapis.com/token"
```
""")
        if has_mp:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔄 Limpar dados", use_container_width=True):
                for k in ["df_mp_raw","df_ec_raw","ts_mp","ts_ec","sheet_id"]:
                    st.session_state[k] = None
                load_url.clear()
                load_campanhas.clear()
                load_acessos.clear()
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
import calendar as _cal

# ── Build month options (last 24 months)
_meses_opts = []
for _i in range(23, -1, -1):
    _m = (hoje.month - _i - 1) % 12 + 1
    _y = hoje.year - ((_i + (12 - hoje.month)) // 12)
    _meses_opts.append(date(_y, _m, 1))
_meses_labels  = [d.strftime("%b/%Y") for d in _meses_opts]
_mes_atual_idx = next((i for i, d in enumerate(_meses_opts) if d == hoje.replace(day=1)),
                      len(_meses_opts) - 1)

# ── Initialise session state (first run only)
if "mes_idx"  not in st.session_state: st.session_state.mes_idx  = _mes_atual_idx
if "d_ini"    not in st.session_state: st.session_state.d_ini    = hoje.replace(day=1)
if "d_fim"    not in st.session_state: st.session_state.d_fim    = hoje
if "_prev_mes_idx" not in st.session_state: st.session_state._prev_mes_idx = _mes_atual_idx

# ── Render controls
fr = st.columns([2, 2, 2, 3])

with fr[0]:
    mes_idx = st.selectbox(
        "Mês",
        range(len(_meses_labels)),
        format_func=lambda i: _meses_labels[i],
        index=st.session_state.mes_idx,
        key="mes_idx",
    )

# When month selector changes → overwrite d_ini / d_fim BEFORE date_inputs render
if st.session_state.mes_idx != st.session_state._prev_mes_idx:
    _m = _meses_opts[st.session_state.mes_idx]
    _last = _cal.monthrange(_m.year, _m.month)[1]
    st.session_state.d_ini = _m
    st.session_state.d_fim = date(_m.year, _m.month, _last)
    st.session_state._prev_mes_idx = st.session_state.mes_idx

with fr[1]:
    data_ini = st.date_input("De",  value=st.session_state.d_ini,
                             format="DD/MM/YYYY", key="d_ini")
with fr[2]:
    data_fim = st.date_input("Até", value=st.session_state.d_fim,
                             format="DD/MM/YYYY", key="d_fim")
with fr[3]:
    comp_modo = st.selectbox(
        "Comparar com",
        ["Período anterior equivalente", "Mês anterior", "Mesmo período ano anterior"],
        key="comp",
    )

# data_ini / data_fim are now the authoritative values used by every tab
data_ini = st.session_state.d_ini
data_fim = st.session_state.d_fim

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
tab_geral, tab_metas, tab_ec_tab, tab_mp_tab, tab_prod, tab_acessos, tab_camp = st.tabs([
    "📊 Visão Geral", "🎯 Metas", "🛒 E-commerce", "🏪 Marketplace",
    "🏆 Produtos & SKUs", "📈 Acessos", "📣 Campanhas",
])

with tab_geral:
    df_meta = load_metas()
    mes_atual  = data_ini.month
    ano_atual  = data_ini.year

    if not df_meta.empty:
        m_mes = metas_do_mes(df_meta, ano_atual, mes_atual)
        m_ano = metas_ano(df_meta, ano_atual)
        m_acu = metas_acumulado(df_meta, ano_atual, mes_atual)
        mes_label_atual = date(ano_atual, mes_atual, 1).strftime('%b/%Y')

        def pct_barra(real, meta):
            if meta <= 0: return 0
            return min(real / meta * 100, 100)

        def cor_seg(real, meta):
            if meta <= 0: return "#3b6fff"
            p = real / meta * 100
            return "#10b981" if p >= 100 else ("#f59e0b" if p >= 70 else "#f43f5e")

        def mc_class(real, meta):
            if meta <= 0: return ""
            p = real / meta * 100
            return "ok" if p >= 100 else ("warn2" if p >= 70 else "bad")

        def compact_card(icon, label, meta_val, real_val, periodo, canal_cor=""):
            pct     = pct_barra(real_val, meta_val)
            cor     = cor_seg(real_val, meta_val)
            cls     = mc_class(real_val, meta_val)
            dif     = real_val - meta_val
            sinal   = "+" if dif >= 0 else ""
            dif_cls = "pos" if dif >= 0 else "neg"
            cor_style = f"style=\'color:{canal_cor};'" if canal_cor else ""
            bar = (f"<div class=\'meta-bar-wrap\'>"
                   f"<div class=\'meta-bar-fill\' style=\'width:{pct:.1f}%;background:{cor};\' ></div>"
                   f"</div>")
            return f"""
            <div class="mc {cls}">
              <div class="mc-icon" {cor_style}>{icon}</div>
              <div class="mc-label" {cor_style}>{label}</div>
              <div class="mc-value">{brl(real_val)}</div>
              <div class="mc-sub">
                <span class="{dif_cls}">{sinal}{brl(dif)}</span>
                <span class="dot-sep">·</span>
                <span class="neu">{periodo}</span>
              </div>
              {bar}
              <div class="mc-progress-row">
                <span class="mc-pct">{pct:.0f}% da meta</span>
                <span class="mc-pct">Meta: {brl(meta_val)}</span>
              </div>
            </div>"""

        sh("Painel de Metas — Mês Atual vs Meta")

        top1, top2, top3 = st.columns(3)
        with top1:
            st.markdown(compact_card("🎯", f"Total — {mes_label_atual}",
                m_mes["meta_total"], total_rec, mes_label_atual), unsafe_allow_html=True)
        with top2:
            st.markdown(compact_card("🛒", f"E-commerce — {mes_label_atual}",
                m_mes["meta_ec"], ec_m["receita"], mes_label_atual, "#3b6fff"), unsafe_allow_html=True)
        with top3:
            st.markdown(compact_card("🏪", f"Marketplace — {mes_label_atual}",
                m_mes["meta_mkt"], mp_m["receita"], mes_label_atual, "#f59e0b"), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

    sh("KPIs Consolidados do Período")
    g1, g2, g3, g4, g5 = st.columns(5)
    g1.metric("💰 Receita Total",   brl(total_rec),       delta=fv(vp(total_rec, total_rec_ant)))
    g2.metric("🛒 Receita E-com",   brl(ec_m["receita"]), delta=fv(vp(ec_m["receita"], ec_ma["receita"])))
    g3.metric("🏪 Receita Mkt",     brl(mp_m["receita"]), delta=fv(vp(mp_m["receita"], mp_ma["receita"])))
    g4.metric("📑 NFs E-com",       f"{ec_m['total']:,}", delta=fv(vp(ec_m["total"], ec_ma["total"])))
    g5.metric("📑 NFs Marketplace", f"{mp_m['total']:,}", delta=fv(vp(mp_m["total"], mp_ma["total"])))

    # ── Necessário por dia para bater a meta
    if not df_meta.empty and m_mes["meta_total"] > 0:
        import calendar as _cal2
        _hoje_kpi   = datetime.today().date()
        _dias_mes   = _cal2.monthrange(mes_atual, 0 if mes_atual == 0 else mes_atual)[1] if False else \
                      _cal2.monthrange(ano_atual, mes_atual)[1]
        _dia_atual  = min(_hoje_kpi.day, _dias_mes) if (_hoje_kpi.year == ano_atual and _hoje_kpi.month == mes_atual) else _dias_mes
        _dias_rest  = max(_dias_mes - _dia_atual, 1)
        _falta      = max(m_mes["meta_total"] - total_rec, 0)
        _por_dia    = _falta / _dias_rest
        _media_dia  = total_rec / _dia_atual if _dia_atual > 0 else 0
        _cor_ritmo  = "#10b981" if _media_dia >= _por_dia else "#f43f5e"
        st.markdown(
            f"<div class='info' style='display:flex;gap:32px;align-items:center;flex-wrap:wrap;'>"
            f"<span>📅 <strong>Dias restantes no mês:</strong> {_dias_rest}</span>"
            f"<span>🎯 <strong>Falta para meta:</strong> {brl(_falta)}</span>"
            f"<span style='color:{_cor_ritmo};'>⚡ <strong>Necessário/dia:</strong> {brl(_por_dia)}</span>"
            f"<span>📈 <strong>Média atual/dia:</strong> {brl(_media_dia)}</span>"
            f"</div>",
            unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if total_rec > 0:
        pec = ec_m["receita"]/total_rec*100; pmp = mp_m["receita"]/total_rec*100
        st.markdown(
            f"<div class='info'>📐 <strong>Mix de canal:</strong> E-commerce "
            f"<strong>{pec:.1f}%</strong> (R$ {ec_m['receita']:,.0f}) · "
            f"Marketplace <strong>{pmp:.1f}%</strong> (R$ {mp_m['receita']:,.0f})</div>",
            unsafe_allow_html=True)

    if not mp_ecom_all.empty or not mp_mkt_all.empty:
        _dias_periodo = max((data_fim - data_ini).days + 1, 1)
        sh("Resumo por Marca")
        MARCAS_ECOM = ["Seculus", "Mondaine", "Timex", "E-time"]
        cols_rc = st.columns(len(MARCAS_ECOM))
        for idx, marca in enumerate(MARCAS_ECOM):
            df_m    = ec_p[ec_p["marca"] == marca] if not ec_p.empty else pd.DataFrame()
            notas   = int(df_m["nota"].nunique())      if not df_m.empty else 0
            itens   = int(df_m["itens"].round().sum()) if not df_m.empty else 0
            receita = float(df_m["receita"].sum())     if not df_m.empty else 0
            ticket  = receita / notas if notas > 0 else 0
            media_d = receita / _dias_periodo
            cor     = COR_MARCA.get(marca, "#3b6fff")
            with cols_rc[idx]:
                st.markdown(f"""
                <div class="rc">
                  <p class="rc-title" style="color:{cor};">{marca}</p>
                  <div class="rc-row"><span>Notas fiscais</span><span class="rc-val">{notas:,}</span></div>
                  <div class="rc-row"><span>Itens faturados</span><span class="rc-val"><span class="rc-badge rc-green">{itens:,}</span></span></div>
                  <div class="rc-row"><span>Ticket médio NF</span><span class="rc-val">{brl(ticket)}</span></div>
                  <div class="rc-row"><span>Receita faturada</span><span class="rc-val">{brl(receita)}</span></div>
                  <div class="rc-row"><span>Média diária</span><span class="rc-val">{brl(media_d)}</span></div>
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

    sh("Unidades Vendidas por Marca — Evolução Diária")
    _MARCAS_PRINCIPAIS = ["Seculus", "Mondaine", "Timex", "E-time"]
    _all_nf = pd.concat([df for df in [ec_p, mp_p] if not df.empty and "marca" in df.columns],
                        ignore_index=True) if (not ec_p.empty or not mp_p.empty) else pd.DataFrame()
    if not _all_nf.empty:
        import calendar as _cal3
        _all_nf = _all_nf[_all_nf["marca"].isin(_MARCAS_PRINCIPAIS)]
        _units  = (_all_nf.groupby(["data","marca"])
                   .agg(itens=("itens","sum")).reset_index())

        _hoje_u     = datetime.today().date()
        _fim_mes_u  = date(_hoje_u.year, _hoje_u.month,
                           _cal3.monthrange(_hoje_u.year, _hoje_u.month)[1])
        # Split: actual data up to today, projection from today to end of month
        _dias_decor = max((_hoje_u - data_ini).days + 1, 1)
        _dias_proj  = max((_fim_mes_u - _hoje_u).days, 0)
        _proj_dates = [pd.Timestamp(_hoje_u + timedelta(days=i+1)) for i in range(_dias_proj)]

        fig_units = go.Figure()
        for marca in _MARCAS_PRINCIPAIS:
            _m = _units[_units["marca"] == marca].sort_values("data")
            if _m.empty:
                continue
            cor = COR_MARCA.get(marca, "#64748b")
            # Actual line
            fig_units.add_trace(go.Scatter(
                x=_m["data"], y=_m["itens"], name=marca,
                mode="lines+markers",
                line=dict(color=cor, width=2.5, shape="spline", smoothing=1.0),
                marker=dict(size=5, color=cor),
                legendgroup=marca,
            ))
            # Projection: daily avg extrapolated forward
            if _proj_dates:
                _media_u  = float(_m["itens"].sum()) / _dias_decor
                _last_val = float(_m.iloc[-1]["itens"])
                _anchor_x = _m.iloc[-1]["data"]
                proj_x = [_anchor_x] + _proj_dates
                proj_y = [_last_val] + [_media_u] * len(_proj_dates)
                fig_units.add_trace(go.Scatter(
                    x=proj_x, y=proj_y,
                    name=f"{marca} (proj.)",
                    mode="lines",
                    line=dict(color=cor, width=1.8, dash="dot"),
                    legendgroup=marca,
                    opacity=0.6,
                ))

        if _dias_proj > 0:
            fig_units.add_vline(
                x=pd.Timestamp(_hoje_u).value / 1e6,
                line_dash="dash", line_color="#475569", line_width=1,
                annotation_text="hoje",
                annotation_font_color="#94a3b8",
                annotation_position="top right",
            )
        fig_units.update_layout(**L(yaxis=dict(
            title="Unidades", gridcolor="#1a2540", zeroline=False)))
        st.plotly_chart(fig_units, use_container_width=True)

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
    hoje_meta = data_ini
    m_acu_sel = metas_acumulado(df_meta, ano_meta, data_ini.month)

    def pct_b(r, m): return min(r/m*100, 100) if m > 0 else 0
    def cor_b(r, m):
        if m <= 0: return "#3b6fff"
        p = r/m*100
        return "#10b981" if p >= 100 else ("#f59e0b" if p >= 70 else "#f43f5e")
    def cls_c(r, m):
        if m <= 0: return ""
        p = r/m*100
        return "ok" if p >= 100 else ("warn2" if p >= 70 else "bad")
    def mc_card(icon, lbl, meta, real, canal_cor=""):
        pct = pct_b(real, meta)
        cor = cor_b(real, meta)
        cls = cls_c(real, meta)
        dif = real - meta
        s = "+" if dif >= 0 else ""
        dc = "pos" if dif >= 0 else "neg"
        cs = f"style='color:{canal_cor};'" if canal_cor else ""
        bar = (f"<div class='meta-bar-wrap'>"
               f"<div class='meta-bar-fill' style='width:{pct:.1f}%;background:{cor};'></div>"
               f"</div>")
        return f"""<div class="mc {cls}">
          <div class="mc-icon" {cs}>{icon}</div>
          <div class="mc-label" {cs}>{lbl}</div>
          <div class="mc-value">{brl(real)}</div>
          <div class="mc-sub">
            <span class="{dc}">{s}{brl(dif)}</span>
            <span class="dot-sep">·</span>
            <span class="neu">{pct:.0f}% da meta</span>
          </div>
          {bar}
          <div class="mc-progress-row">
            <span class="mc-pct">Meta: {brl(meta)}</span>
          </div>
        </div>"""

    sh(f"Visão Anual — {ano_meta}")
    ya1, ya2, ya3 = st.columns(3)
    with ya1: st.markdown(mc_card("🎯","Total",          m_ano_sel["meta_total"],m_ano_sel["real_total"],""),         unsafe_allow_html=True)
    with ya2: st.markdown(mc_card("🛒","E-commerce",     m_ano_sel["meta_ec"],   m_ano_sel["real_ec"],   "#3b6fff"), unsafe_allow_html=True)
    with ya3: st.markdown(mc_card("🏪","Marketplace",    m_ano_sel["meta_mkt"],  m_ano_sel["real_mkt"],  "#f59e0b"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    sh(f"Acumulado até {data_ini.strftime('%B/%Y')} — {ano_meta}")
    aa1, aa2, aa3 = st.columns(3)
    with aa1: st.markdown(mc_card("📊","Total Acumulado",     m_acu_sel["meta_total"],m_acu_sel["real_total"],""),         unsafe_allow_html=True)
    with aa2: st.markdown(mc_card("🛒","E-commerce Acumulado",m_acu_sel["meta_ec"],   m_acu_sel["real_ec"],   "#3b6fff"), unsafe_allow_html=True)
    with aa3: st.markdown(mc_card("🏪","Marketplace Acumulado",m_acu_sel["meta_mkt"], m_acu_sel["real_mkt"],  "#f59e0b"), unsafe_allow_html=True)

    # ── Meta por Marca
    _sid_mi = st.session_state.get("sheet_id","")
    _gid_mi = st.session_state.get("_gid_mi","3")
    _tok_mi = _get_sa_token()
    df_mi   = load_meta_inv(gid_url(_sid_mi, _gid_mi), _tok_mi) if _sid_mi else pd.DataFrame()

    if not df_mi.empty:
        st.markdown("<br>", unsafe_allow_html=True)
        sh("Meta por Marca — Mês Selecionado")
        mi = meta_inv_do_mes(df_mi, data_ini.month)
        def _real_marca(marca):
            df_m = ec_p[ec_p["marca"] == marca] if not ec_p.empty else pd.DataFrame()
            return float(df_m["receita"].sum()) if not df_m.empty else 0.0
        mi_cols = st.columns(4)
        for idx, (marca, meta, cor) in enumerate([
            ("Seculus",  mi["meta_sec"], COR_MARCA.get("Seculus","#3b6fff")),
            ("Mondaine", mi["meta_mon"], COR_MARCA.get("Mondaine","#f59e0b")),
            ("Timex",    mi["meta_tim"], COR_MARCA.get("Timex","#10b981")),
            ("E-time",   mi["meta_eti"], COR_MARCA.get("E-time","#f43f5e")),
        ]):
            real  = _real_marca(marca)
            dif   = real - meta
            pct   = min(real/meta*100, 100) if meta > 0 else 0
            bar_c = "#10b981" if pct>=100 else ("#f59e0b" if pct>=70 else "#f43f5e")
            s_dif = "+" if dif >= 0 else ""
            dc    = "pos" if dif >= 0 else "neg"
            with mi_cols[idx]:
                st.markdown(f"""
                <div class="mc {'ok' if pct>=100 else ('warn2' if pct>=70 else 'bad')}">
                  <div class="mc-label" style="color:{cor};">{marca}</div>
                  <div class="mc-value">{brl(real)}</div>
                  <div class="mc-sub">
                    <span class="{dc}">{s_dif}{brl(dif)}</span>
                    <span class="dot-sep">·</span>
                    <span class="neu">{pct:.0f}% da meta</span>
                  </div>
                  <div class="meta-bar-wrap">
                    <div class="meta-bar-fill" style="width:{pct:.1f}%;background:{bar_c};"></div>
                  </div>
                  <div class="mc-progress-row">
                    <span class="mc-pct">Meta: {brl(meta)}</span>
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

        if not df_meta.empty and m_mes["meta_ec"] > 0:
            import calendar as _c2
            _hj = datetime.today().date()
            _dm = _c2.monthrange(ano_atual, mes_atual)[1]
            _da = min(_hj.day, _dm) if (_hj.year == ano_atual and _hj.month == mes_atual) else _dm
            _dr = max(_dm - _da, 1)
            _falta_ec  = max(m_mes["meta_ec"] - ec_m["receita"], 0)
            _nd_ec     = _falta_ec / _dr
            _med_ec    = ec_m["receita"] / _da if _da > 0 else 0
            _cor_ec    = "#10b981" if _med_ec >= _nd_ec else "#f43f5e"
            st.markdown(
                f"<div class='info' style='display:flex;gap:32px;align-items:center;flex-wrap:wrap;margin-top:8px;'>"
                f"<span>📅 <strong>Dias restantes:</strong> {_dr}</span>"
                f"<span>🎯 <strong>Falta para meta EC:</strong> {brl(_falta_ec)}</span>"
                f"<span style='color:{_cor_ec};'>⚡ <strong>Necessário/dia:</strong> {brl(_nd_ec)}</span>"
                f"<span>📈 <strong>Média atual/dia:</strong> {brl(_med_ec)}</span>"
                f"</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        ea1, ea2 = st.columns(2)
        with ea1:
            sh("Receita por Marca")
            import calendar as _cal_ec
            _hoje_ec    = datetime.today().date()
            _dias_decor_ec = max((_hoje_ec - data_ini).days + 1, 1)
            _dias_mes_ec   = _cal_ec.monthrange(data_ini.year, data_ini.month)[1]
            em2 = ec_p.groupby("marca")["receita"].sum().reset_index().sort_values("receita", ascending=False)
            em2["media_dia"]  = em2["receita"] / _dias_decor_ec
            em2["projecao"]   = em2["media_dia"] * _dias_mes_ec
            em2["falta_proj"] = (em2["projecao"] - em2["receita"]).clip(lower=0)

            fig_em2 = go.Figure()
            for i, row in enumerate(em2.itertuples()):
                cor = COR_MARCA.get(row.marca, "#3b6fff")
                is_first = (i == 0)
                fig_em2.add_trace(go.Bar(
                    x=[row.marca], y=[row.receita],
                    name="Realizado", marker_color=cor,
                    legendgroup="real", showlegend=is_first,
                    text=[brl(row.receita)], textposition="inside",
                    textfont=dict(size=11),
                ))
                fig_em2.add_trace(go.Bar(
                    x=[row.marca], y=[row.falta_proj],
                    name="Projeção", marker_color=cor,
                    marker_opacity=0.3,
                    marker_pattern_shape="/",
                    legendgroup="proj", showlegend=is_first,
                    text=[f"≈ {brl(row.projecao)}"] if row.falta_proj > 0 else [""],
                    textposition="outside",
                    textfont=dict(size=10, color="#94a3b8"),
                ))
            fig_em2.update_layout(barmode="stack", **L(
                legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#94a3b8", size=11))))
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
        fig_edd = px.line(ec_d, x="data", y="receita", color="marca",
                          color_discrete_map=COR_MARCA,
                          labels={"receita":"Receita (R$)","data":"","marca":"Marca"})
        fig_edd.update_traces(line=dict(width=2.5))
        fig_edd.update_layout(**L())
        st.plotly_chart(fig_edd, use_container_width=True)

        sh("Atual vs Período Anterior por Marca")
        if not ec_p.empty:
            ec_a2 = ec_p.groupby("marca")["receita"].sum().reset_index().rename(columns={"receita":"atual"})
            ec_b2 = (ec_pa.groupby("marca")["receita"].sum().reset_index().rename(columns={"receita":"anterior"})
                     if not ec_pa.empty else pd.DataFrame(columns=["marca","anterior"]))
            ec_cmp = ec_a2.merge(ec_b2, on="marca", how="outer").fillna(0)
            ec_cmp["var"] = ec_cmp.apply(
                lambda r: fv(vp(r["atual"],r["anterior"])) if r["anterior"] > 0 else "", axis=1)
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
        if df_ec.empty:
            st.markdown("<div class='warn'>⚠️ Planilha E-commerce carregada mas sem dados processados.</div>", unsafe_allow_html=True)
        elif ec_p_ec.empty:
            _ec_min = df_ec["data"].min().strftime("%d/%m/%Y")
            _ec_max = df_ec["data"].max().strftime("%d/%m/%Y")
            st.markdown(f"<div class='info'>ℹ️ A planilha E-commerce não possui pedidos no período selecionado. "
                        f"Dados disponíveis: <strong>{_ec_min} → {_ec_max}</strong>. "
                        f"Selecione um período dentro desse intervalo para ver os detalhes.</div>",
                        unsafe_allow_html=True)
        else:
            ec_dedup     = ec_p_ec.drop_duplicates("order")
            ec_fat_dedup = ec_dedup[ec_dedup["faturado"]].copy()
            n_fat_ec     = len(ec_fat_dedup)
            n_canc_ec    = int(ec_dedup["cancelado"].sum()) if "cancelado" in ec_dedup.columns else 0

            # ── Faturado vs Cancelado
            st_rows = []
            if n_fat_ec  > 0: st_rows.append({"status":"Faturado",  "qtd":n_fat_ec})
            if n_canc_ec > 0: st_rows.append({"status":"Cancelado", "qtd":n_canc_ec})
            st_cnt = pd.DataFrame(st_rows) if st_rows else pd.DataFrame(columns=["status","qtd"])

            c1, c2, c3 = st.columns(3)

            with c1:
                sh("Faturado vs Cancelado")
                if not st_cnt.empty:
                    fig_st = px.pie(st_cnt, names="status", values="qtd",
                                    color="status",
                                    color_discrete_map={"Faturado":"#10b981","Cancelado":"#f43f5e"},
                                    hole=0.58)
                    fig_st.update_traces(textinfo="percent+label", textfont_size=11)
                    fig_st.update_layout(**L(margin=dict(l=10,r=10,t=20,b=10)))
                    st.plotly_chart(fig_st, use_container_width=True)

            with c2:
                sh("Forma de Pagamento — Faturados")
                if not ec_fat_dedup.empty and "payment_method" in ec_fat_dedup.columns:
                    def _pmt_group(p):
                        p = str(p).strip().lower()
                        if "pix" in p: return "Pix"
                        if any(x in p for x in ["credit","cartão","card","crédito","mastercard","visa","elo","amex","american","hipercard"]): return "Cartão de Crédito"
                        return p.title()
                    ec_fat_dedup = ec_fat_dedup.copy()
                    ec_fat_dedup["pmt_group"] = ec_fat_dedup["payment_method"].apply(_pmt_group)
                    pmt_agg = (ec_fat_dedup.groupby("pmt_group")
                               .agg(pedidos=("order","count")).reset_index()
                               .sort_values("pedidos", ascending=False))
                    fig_pmt = px.pie(pmt_agg, names="pmt_group", values="pedidos",
                                     color="pmt_group",
                                     color_discrete_map={"Pix":"#10b981","Cartão de Crédito":"#3b6fff"},
                                     hole=0.58)
                    fig_pmt.update_traces(textinfo="percent+label", textfont_size=11)
                    fig_pmt.update_layout(**L(margin=dict(l=10,r=10,t=20,b=10)))
                    st.plotly_chart(fig_pmt, use_container_width=True)

            with c3:
                sh("Parcelamentos — Cartão")
                if not ec_fat_dedup.empty and "installments" in ec_fat_dedup.columns:
                    ec_fat_dedup["inst_num"] = pd.to_numeric(ec_fat_dedup["installments"], errors="coerce")
                    media_parc = ec_fat_dedup["inst_num"].dropna().mean()
                    dist_parc  = (ec_fat_dedup["inst_num"].dropna()
                                  .value_counts().sort_index().reset_index()
                                  .rename(columns={"inst_num":"Parcelas","count":"Pedidos"}))
                    st.metric("Média de Parcelas", f"{media_parc:.1f}x" if not pd.isna(media_parc) else "—")
                    if not dist_parc.empty:
                        fig_parc = px.bar(dist_parc, x="Parcelas", y="Pedidos",
                                          labels={"Parcelas":"Nº de Parcelas","Pedidos":"Pedidos"},
                                          text="Pedidos")
                        fig_parc.update_traces(marker_color="#3b6fff", textposition="outside")
                        fig_parc.update_layout(**L(margin=dict(l=10,r=10,t=20,b=10),
                                                   xaxis=dict(tickmode="linear", dtick=1)))
                        st.plotly_chart(fig_parc, use_container_width=True)

            # ── Cupons mais usados
            sh("Cupons Mais Utilizados")
            if "marketingtags" in ec_fat_dedup.columns:
                _cupons = (ec_fat_dedup["marketingtags"]
                           .fillna("").astype(str).str.strip()
                           .replace("", pd.NA).dropna())
                if not _cupons.empty:
                    cup_agg = (_cupons.value_counts()
                               .reset_index()
                               .rename(columns={"marketingtags":"Cupom","count":"Pedidos"})
                               .head(15))
                    cup_total = int(cup_agg["Pedidos"].sum())
                    st.markdown(f"<div class='info'>🏷️ <strong>{len(cup_agg)}</strong> cupons distintos · "
                                f"<strong>{cup_total}</strong> pedidos com cupom de <strong>{n_fat_ec}</strong> faturados</div>",
                                unsafe_allow_html=True)
                    fig_cup = px.bar(cup_agg, x="Pedidos", y="Cupom", orientation="h",
                                     text="Pedidos", labels={"Cupom":"","Pedidos":"Pedidos Faturados"})
                    fig_cup.update_traces(marker_color="#3b6fff", textposition="outside")
                    fig_cup.update_layout(**Li(height=max(260, len(cup_agg)*34)))
                    st.plotly_chart(fig_cup, use_container_width=True)
                else:
                    st.markdown("<div class='info'>ℹ️ Nenhum cupom no período.</div>", unsafe_allow_html=True)

            # ── Campanhas que geraram pedidos faturados
            sh("Campanhas com Pedidos Faturados")
            _fat_camp = ec_fat_dedup.copy()
            if "discount_tags" in _fat_camp.columns and "brand" in _fat_camp.columns:
                _fat_camp["discount_tags"] = _fat_camp["discount_tags"].fillna("").astype(str).str.strip()
                _fat_camp = _fat_camp[_fat_camp["discount_tags"] != ""]
                if not _fat_camp.empty:
                    def _norm_combo(s):
                        parts = [p.strip() for p in re.split(r",\s+", s) if p.strip()]
                        return " + ".join(sorted(parts))
                    _fat_camp = _fat_camp.copy()
                    _fat_camp["combo"] = _fat_camp["discount_tags"].apply(_norm_combo)
                    camp_agg = (_fat_camp.groupby(["combo","brand"])
                                .agg(pedidos=("order","nunique")).reset_index()
                                .sort_values("pedidos", ascending=False).head(25))
                    camp_agg = camp_agg.rename(columns={"combo":"Combo","brand":"Marca","pedidos":"Pedidos"})
                    st.markdown(f"<div class='info'>📊 <strong>{len(camp_agg)}</strong> combos · "
                                f"<strong>{camp_agg['Pedidos'].sum()}</strong> pedidos com desconto</div>",
                                unsafe_allow_html=True)
                    seller_colors = {s: list(COR_MARCA.values())[i % len(COR_MARCA)]
                                     for i, s in enumerate(camp_agg["Marca"].unique())}
                    fig_camp = px.bar(camp_agg, x="Pedidos", y="Combo", orientation="h",
                                      color="Marca", color_discrete_map=seller_colors, text="Pedidos",
                                      labels={"Combo":"","Pedidos":"Pedidos Faturados","Marca":"Marca"})
                    fig_camp.update_traces(textposition="outside")
                    fig_camp.update_layout(**Li(height=max(320, len(camp_agg)*36)))
                    st.plotly_chart(fig_camp, use_container_width=True)
                else:
                    st.markdown("<div class='info'>ℹ️ Nenhum pedido com campanha no período.</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='info'>ℹ️ Coluna <code>discount_tags</code> não encontrada.</div>", unsafe_allow_html=True)

        sh("Detalhamento de Pedidos")
        if ec_p_ec.empty:
            st.markdown("<div class='info'>ℹ️ Sem pedidos no período selecionado.</div>", unsafe_allow_html=True)
        else:
            det = (ec_p_ec.drop_duplicates("order")
                   [["order","data","status","payment_method","installments","quantity_sku","brand"]]
                   .rename(columns={"order":"Order ID","data":"Data","status":"Status",
                                    "payment_method":"Pagamento","installments":"Parcelas",
                                    "quantity_sku":"Itens","brand":"Marca"})
                   .sort_values("Data", ascending=False))
            st.dataframe(det, use_container_width=True, hide_index=True)
            st.download_button("📥 Exportar pedidos",
                               data=det.to_csv(index=False).encode("utf-8"),
                               file_name="pedidos_ecommerce.csv", mime="text/csv")
    else:
        sh("Status dos Pedidos (Planilha E-commerce)")
        st.markdown(
            "<div class='info'>ℹ️ Carregue a <strong>planilha E-commerce</strong> no painel "
            "⚙️ Fontes de Dados para visualizar status de pedidos e detalhamento.</div>",
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

        if not df_meta.empty and m_mes["meta_mkt"] > 0:
            import calendar as _c3
            _hj2 = datetime.today().date()
            _dm2 = _c3.monthrange(ano_atual, mes_atual)[1]
            _da2 = min(_hj2.day, _dm2) if (_hj2.year == ano_atual and _hj2.month == mes_atual) else _dm2
            _dr2 = max(_dm2 - _da2, 1)
            _falta_mkt = max(m_mes["meta_mkt"] - mp_m["receita"], 0)
            _nd_mkt    = _falta_mkt / _dr2
            _med_mkt   = mp_m["receita"] / _da2 if _da2 > 0 else 0
            _cor_mkt   = "#10b981" if _med_mkt >= _nd_mkt else "#f43f5e"
            st.markdown(
                f"<div class='info' style='display:flex;gap:32px;align-items:center;flex-wrap:wrap;margin-top:8px;'>"
                f"<span>📅 <strong>Dias restantes:</strong> {_dr2}</span>"
                f"<span>🎯 <strong>Falta para meta MKT:</strong> {brl(_falta_mkt)}</span>"
                f"<span style='color:{_cor_mkt};'>⚡ <strong>Necessário/dia:</strong> {brl(_nd_mkt)}</span>"
                f"<span>📈 <strong>Média atual/dia:</strong> {brl(_med_mkt)}</span>"
                f"</div>", unsafe_allow_html=True)

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
        fig_mpd = px.line(mp_d, x="data", y="receita", color="MARKETPLACE",
                          color_discrete_map=COR_MP,
                          labels={"receita":"Receita (R$)","data":"","MARKETPLACE":"Plataforma"})
        fig_mpd.update_traces(line=dict(width=2.5))
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


with tab_acessos:
    _sid   = st.session_state.get("sheet_id","")
    _gac   = st.session_state.get("_gid_ac","3")
    _tok   = _get_sa_token()
    df_ac  = pd.DataFrame()
    if _sid:
        try:
            df_ac = load_acessos(gid_url(_sid, _gac), _tok)
        except Exception as _e:
            st.error(f"Erro ao carregar Acessos (gid={_gac}): {_e}")

    if df_ac.empty:
        st.markdown("<div class='info'>ℹ️ Carregue a planilha unificada para visualizar dados de acessos.</div>", unsafe_allow_html=True)
    else:
        df_ac_f = df_ac[(df_ac["data_dt"] >= pd.Timestamp(data_ini)) &
                        (df_ac["data_dt"] < pd.Timestamp(data_fim) + pd.Timedelta(days=1))]

        marcas_ac = sorted(df_ac_f["Marca"].dropna().unique().tolist()) if not df_ac_f.empty else []
        marc_sel  = st.multiselect("Marca", marcas_ac, default=marcas_ac, key="ac_marc")
        df_ac_f   = df_ac_f[df_ac_f["Marca"].isin(marc_sel)] if marc_sel else df_ac_f

        if df_ac_f.empty:
            st.info("Sem dados no período selecionado.")
        else:
            tot_sess   = int(df_ac_f["sessoes_num"].sum())
            tot_pedidos= int(df_ac_f["pedidos_num"].sum())
            tot_pagos  = int(df_ac_f["pagos_num"].sum())
            tot_rec    = float(df_ac_f["receita_num"].sum())
            tot_novos  = int(df_ac_f["novos_num"].sum())

            sh("Resumo do Período")
            k1,k2,k3,k4,k5 = st.columns(5)
            k1.metric("👥 Sessões",       f"{tot_sess:,}")
            k2.metric("🛒 Pedidos",       f"{tot_pedidos:,}")
            k3.metric("✅ Pagos",          f"{tot_pagos:,}")
            k4.metric("💰 Receita Paga",  brl(tot_rec))
            k5.metric("🆕 Novos Clientes",f"{tot_novos:,}")

            sh("Sessões por Canal")
            ac_canal = (df_ac_f.groupby("Cluster")
                        .agg(sessoes=("sessoes_num","sum"), pedidos=("pedidos_num","sum"),
                             pagos=("pagos_num","sum"), receita=("receita_num","sum"))
                        .reset_index().sort_values("sessoes", ascending=False))
            ac_colors = [COR_CLUSTER.get(c,"#64748b") for c in ac_canal["Cluster"]]

            ac1, ac2 = st.columns(2)
            with ac1:
                fig_sess = px.bar(ac_canal, x="Cluster", y="sessoes",
                                  labels={"sessoes":"Sessões","Cluster":""},
                                  text=ac_canal["sessoes"].map(lambda x: f"{int(x):,}"))
                fig_sess.update_traces(textposition="outside", marker_color=ac_colors)
                fig_sess.update_layout(**L(title="Sessões"))
                st.plotly_chart(fig_sess, use_container_width=True)
            with ac2:
                fig_rec_ac = px.bar(ac_canal[ac_canal["receita"]>0], x="Cluster", y="receita",
                                    labels={"receita":"Receita Paga (R$)","Cluster":""},
                                    text=ac_canal[ac_canal["receita"]>0]["receita"].map(brl))
                fig_rec_ac.update_traces(textposition="outside",
                                         marker_color=[COR_CLUSTER.get(c,"#64748b")
                                                       for c in ac_canal[ac_canal["receita"]>0]["Cluster"]])
                fig_rec_ac.update_layout(**L(title="Receita por Canal"))
                st.plotly_chart(fig_rec_ac, use_container_width=True)

            sh("Evolução Diária de Sessões")
            ac_daily = (df_ac_f.groupby(["data_dt","Cluster"])
                        .agg(sessoes=("sessoes_num","sum")).reset_index())
            fig_ac_ev = px.line(ac_daily, x="data_dt", y="sessoes", color="Cluster",
                                color_discrete_map=COR_CLUSTER,
                                labels={"sessoes":"Sessões","data_dt":"","Cluster":"Canal"})
            fig_ac_ev.update_traces(line=dict(width=2))
            fig_ac_ev.update_layout(**L())
            st.plotly_chart(fig_ac_ev, use_container_width=True)

            sh("Tabela por Canal e Marca")
            ac_tab = (df_ac_f.groupby(["Marca","Cluster"])
                      .agg(sessoes=("sessoes_num","sum"), pedidos=("pedidos_num","sum"),
                           pagos=("pagos_num","sum"), receita=("receita_num","sum"),
                           novos=("novos_num","sum"))
                      .reset_index().sort_values(["Marca","receita"], ascending=[True,False]))
            ac_tab["tx_conv"] = (ac_tab["pagos"] / ac_tab["sessoes"] * 100).where(ac_tab["sessoes"]>0, 0)
            ac_tab_disp = ac_tab.copy()
            ac_tab_disp["receita"] = ac_tab_disp["receita"].map(brl)
            ac_tab_disp["tx_conv"] = ac_tab_disp["tx_conv"].map("{:.2f}%".format)
            ac_tab_disp = ac_tab_disp.rename(columns={
                "Marca":"Marca","Cluster":"Canal","sessoes":"Sessões","pedidos":"Pedidos",
                "pagos":"Pagos","receita":"Receita Paga","novos":"Novos","tx_conv":"Conv."})
            st.dataframe(ac_tab_disp, use_container_width=True, hide_index=True)


with tab_camp:
    _sid   = st.session_state.get("sheet_id","")
    _gca   = st.session_state.get("_gid_ca","4")
    _tok_c = _get_sa_token()
    df_ca  = pd.DataFrame()
    if _sid:
        try:
            df_ca = load_campanhas(gid_url(_sid, _gca), _tok_c)
        except Exception as _e:
            st.error(f"Erro ao carregar Campanhas (gid={_gca}): {_e}")

    if df_ca.empty:
        st.markdown("<div class='info'>ℹ️ Carregue a planilha unificada para visualizar dados de campanhas.</div>", unsafe_allow_html=True)
    else:
        df_ca_f = df_ca[(df_ca["data_dt"] >= pd.Timestamp(data_ini)) &
                        (df_ca["data_dt"] < pd.Timestamp(data_fim) + pd.Timedelta(days=1))]

        c_top1, c_top2 = st.columns([2,1])
        with c_top1:
            marcas_ca = sorted(df_ca_f["marca"].dropna().unique().tolist()) if not df_ca_f.empty else []
            marc_ca   = st.multiselect("Marca", marcas_ca, default=marcas_ca, key="ca_marc")
        with c_top2:
            plats_ca  = sorted(df_ca_f["Plataforma"].dropna().unique().tolist()) if not df_ca_f.empty else []
            plat_ca   = st.multiselect("Plataforma", plats_ca, default=plats_ca, key="ca_plat")

        df_ca_f = df_ca_f[df_ca_f["marca"].isin(marc_ca)] if marc_ca else df_ca_f
        df_ca_f = df_ca_f[df_ca_f["Plataforma"].isin(plat_ca)] if plat_ca else df_ca_f

        if df_ca_f.empty:
            st.info("Sem dados de campanhas no período selecionado.")
        else:
            tot_inv   = float(df_ca_f["inv"].sum())
            tot_rec_c = float(df_ca_f["rec_num"].sum())
            tot_trans = int(df_ca_f["trans"].sum())
            roas_med  = tot_rec_c / tot_inv if tot_inv > 0 else 0
            cpa_med   = tot_inv / tot_trans if tot_trans > 0 else 0

            # Load meta x investimento for ROAS meta and investment targets
            _sid_ca = st.session_state.get("sheet_id","")
            _gmi_ca = st.session_state.get("_gid_mi","3")
            _tok_ca2 = _get_sa_token()
            df_mi_ca = load_meta_inv(gid_url(_sid_ca, _gmi_ca), _tok_ca2) if _sid_ca else pd.DataFrame()
            mi_ca    = meta_inv_do_mes(df_mi_ca, data_ini.month)

            sh("Resumo de Campanhas do Período")
            tot_trans1 = int(df_ca_f["trans1"].sum()) if "trans1" in df_ca_f.columns else 0
            ck1,ck2,ck3,ck4,ck5,ck6 = st.columns(6)
            ck1.metric("💸 Investimento",    brl(tot_inv))
            ck2.metric("💰 Receita",          brl(tot_rec_c))
            ck3.metric("📦 Transações",       f"{tot_trans:,}")
            ck4.metric("🆕 1ª Compra",        f"{tot_trans1:,}")
            ck5.metric("📈 ROAS",
                       f"{roas_med:.2f}x",
                       delta=f"{(roas_med - mi_ca['meta_roas']):+.2f}x (meta {mi_ca['meta_roas']:.2f}x)" if mi_ca["meta_roas"] > 0 else None)
            ck6.metric("🎯 CPA Médio",        brl(cpa_med))

            # Investment by brand summary
            if not df_mi_ca.empty and mi_ca["meta_inv"] > 0:
                st.markdown("<br>", unsafe_allow_html=True)
                sh("Meta de Investimento por Marca")
                MARCAS_INV = [
                    ("Seculus",  mi_ca["meta_sec"] * 0,  mi_ca["inv_sec"],  COR_MARCA.get("Seculus","#3b6fff")),
                    ("Mondaine", mi_ca["meta_mon"] * 0,  mi_ca["inv_mon"],  COR_MARCA.get("Mondaine","#f59e0b")),
                    ("Timex",    mi_ca["meta_tim"] * 0,  mi_ca["inv_tim"],  COR_MARCA.get("Timex","#10b981")),
                    ("E-time",   mi_ca["meta_eti"] * 0,  mi_ca["inv_eti"],  COR_MARCA.get("E-time","#f43f5e")),
                ]
                # Compute meta inv per brand from df_ca_f
                inv_por_marca = df_ca_f.groupby("marca")["inv"].sum().to_dict() if not df_ca_f.empty else {}
                inv_cols = st.columns(4)
                inv_meta_map = {"Seculus": mi_ca["inv_sec"], "Mondaine": mi_ca["inv_mon"],
                                "Timex": mi_ca["inv_tim"],   "E-time":   mi_ca["inv_eti"]}
                for idx, marca in enumerate(["Seculus","Mondaine","Timex","E-time"]):
                    meta_i = inv_meta_map[marca]
                    real_i = inv_por_marca.get(marca, 0.0)
                    cor    = COR_MARCA.get(marca,"#3b6fff")
                    pct_i  = min(real_i/meta_i*100, 100) if meta_i > 0 else 0
                    bar_c  = "#10b981" if pct_i >= 100 else ("#f59e0b" if pct_i >= 70 else "#3b6fff")
                    with inv_cols[idx]:
                        st.markdown(f"""
                        <div class="mc">
                          <div class="mc-label" style="color:{cor};">💸 {marca}</div>
                          <div class="mc-value">{brl(real_i)}</div>
                          <div class="mc-sub">
                            <span class="neu">{pct_i:.0f}% do orçamento</span>
                          </div>
                          <div class="meta-bar-wrap">
                            <div class="meta-bar-fill" style="width:{pct_i:.1f}%;background:{bar_c};"></div>
                          </div>
                          <div class="mc-progress-row">
                            <span class="mc-pct">Orçamento: {brl(meta_i)}</span>
                          </div>
                        </div>""", unsafe_allow_html=True)

            sh("Investimento vs Receita por Campanha")
            camp_agg = (df_ca_f.groupby(["Plataforma","Campanha"])
                        .agg(inv=("inv","sum"), receita=("rec_num","sum"),
                             trans=("trans","sum"), cpa=("cpa_num","mean"),
                             roas=("roas_num","mean"))
                        .reset_index().sort_values("receita", ascending=False))
            camp_agg["roas_fmt"] = camp_agg["roas"].map("{:.2f}x".format)
            camp_colors = [COR_PLAT.get(p,"#64748b") for p in camp_agg["Plataforma"]]

            ca1, ca2 = st.columns(2)
            with ca1:
                fig_inv = go.Figure()
                fig_inv.add_trace(go.Bar(name="Investimento", x=camp_agg["Campanha"].str[:30],
                                         y=camp_agg["inv"], marker_color="rgba(100,116,139,.5)",
                                         marker_line_width=0))
                fig_inv.add_trace(go.Bar(name="Receita", x=camp_agg["Campanha"].str[:30],
                                         y=camp_agg["receita"],
                                         marker_color=camp_colors, marker_line_width=0))
                fig_inv.update_layout(barmode="group", **L(title="Investimento vs Receita"),
                                      xaxis_tickangle=-30)
                st.plotly_chart(fig_inv, use_container_width=True)
            with ca2:
                fig_roas = px.bar(camp_agg[camp_agg["roas"]>0],
                                  x="Campanha", y="roas", color="Plataforma",
                                  color_discrete_map=COR_PLAT,
                                  labels={"roas":"ROAS","Campanha":""},
                                  text=camp_agg[camp_agg["roas"]>0]["roas_fmt"],
                                  title="ROAS por Campanha")
                fig_roas.update_traces(textposition="outside")
                fig_roas.update_layout(**L(), xaxis_tickangle=-30)
                st.plotly_chart(fig_roas, use_container_width=True)

            sh("Evolução Diária — Investimento e Receita")
            ca_daily = (df_ca_f.groupby(["data_dt","Plataforma"])
                        .agg(inv=("inv","sum"), receita=("rec_num","sum")).reset_index())
            fig_ca_ev = go.Figure()
            for plat, grp in ca_daily.groupby("Plataforma"):
                cor_p = COR_PLAT.get(plat,"#64748b")
                fig_ca_ev.add_trace(go.Scatter(x=grp["data_dt"], y=grp["inv"], name=f"{plat} — Invest.",
                    mode="lines", line=dict(color=cor_p, width=1.5, dash="dot")))
                fig_ca_ev.add_trace(go.Scatter(x=grp["data_dt"], y=grp["receita"], name=f"{plat} — Receita",
                    mode="lines", fill="tozeroy",
                    line=dict(color=cor_p, width=2),
                    fillcolor=f"rgba{tuple(list(bytes.fromhex(cor_p.lstrip('#'))) + [30])}"))
            fig_ca_ev.update_layout(**L())
            st.plotly_chart(fig_ca_ev, use_container_width=True)

            sh("Tabela Detalhada de Campanhas")
            camp_tab = camp_agg.copy()
            camp_tab["inv"]     = camp_tab["inv"].map(brl)
            camp_tab["receita"] = camp_tab["receita"].map(brl)
            camp_tab["cpa"]     = camp_tab["cpa"].map(brl)
            camp_tab["roas"]    = camp_tab["roas_fmt"]
            camp_tab = camp_tab.rename(columns={
                "Plataforma":"Plataforma","Campanha":"Campanha","inv":"Investimento",
                "receita":"Receita","trans":"Transações","roas":"ROAS","cpa":"CPA Médio"})
            st.dataframe(camp_tab[["Plataforma","Campanha","Investimento","Receita",
                                   "Transações","ROAS","CPA Médio"]],
                         use_container_width=True, hide_index=True)
            st.download_button("📥 Exportar Campanhas",
                               data=df_ca_f.to_csv(index=False).encode("utf-8"),
                               file_name="campanhas.csv", mime="text/csv")


st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#1a2540;font-size:.7rem;font-family:DM Mono,monospace;'>"
    "⌚ Grupo Seculus · Receita via notas fiscais · "
    "Site Mondaine / Site Seculus / Site Timex / Multimarcas (E-time) → E-commerce"
    "</div>", unsafe_allow_html=True)
