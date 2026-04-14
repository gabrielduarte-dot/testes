import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import StringIO
import requests
from datetime import datetime, timedelta
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
.dot-live{width:7px;height:7px;border-radius:50%;background:#10b981;display:inline-block;animation:blink 2s infinite;}
@keyframes blink{0%,100%{opacity:1;}50%{opacity:.35;}}
.sec-head{display:flex;align-items:center;gap:10px;margin:24px 0 14px;}
.sec-head h4{margin:0!important;font-size:.8rem!important;font-weight:700!important;color:#475569!important;text-transform:uppercase;letter-spacing:.1em;}
.sec-head .line{flex:1;height:1px;background:linear-gradient(90deg,#1e2d4a,transparent);}
.insight{background:linear-gradient(135deg,#0f1c35,#111e38);border:1px solid #1e3a5f;border-left:3px solid #3b6fff;border-radius:0 12px 12px 0;padding:13px 17px;margin:8px 0;font-size:.86rem;color:#93c5fd;line-height:1.65;}
.warn{background:linear-gradient(135deg,#1a1505,#1f1a06);border:1px solid #3d2e00;border-left:3px solid #f59e0b;border-radius:0 12px 12px 0;padding:13px 17px;margin:8px 0;font-size:.86rem;color:#fde68a;line-height:1.65;}
.upload-zone{background:linear-gradient(135deg,#0f1421,#111827);border:1px dashed #2a3a5a;border-radius:16px;padding:40px;text-align:center;}
.upload-zone h3{color:#f1f5f9!important;margin-bottom:8px!important;}
.upload-zone p{color:#64748b;font-size:.88rem;}
</style>
""", unsafe_allow_html=True)

ECOM_CANAIS = ["Site Mondaine", "Site Seculus", "Site Timex", "Multimarcas"]
MARCA_MAP   = {
    "Site Mondaine": "Mondaine",
    "Site Seculus":  "Seculus",
    "Site Timex":    "Timex",
    "Multimarcas":   "E-time",
}

COR_CANAL_EC = {
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
COR_MP_PLAT = {
    "Livelo":        "#fbbf24",
    "Shopee":        "#f97316",
    "Mercado Livre": "#facc15",
    "Amazon":        "#fb923c",
    "Outros":        "#64748b",
}

EC_COLS = [
    "order", "created_at", "customer_name", "state", "status",
    "utmsource", "marketingtags", "payment_method", "installments",
    "quantity_sku", "phone", "sku", "product_name",
    "sku_selling_price", "sku_total_price", "discount_tags", "brand", "livelo_tag",
]

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

def L_inv(**kw):
    d = dict(_BL)
    d["yaxis"] = dict(_BL["yaxis"], autorange="reversed")
    d.update(kw); return d

def fmt_brl(v):
    try:
        return f"R$ {float(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "R$ 0,00"

def var_pct(a, b):
    if not b or b == 0: return None
    return (a - b) / b * 100

def fmt_var(v):
    if v is None: return None
    return f"{v:+.1f}%"

def filter_dt(df, ini, fim):
    if df.empty or "data" not in df.columns: return df
    return df[(df["data"] >= pd.Timestamp(ini)) & (df["data"] <= pd.Timestamp(fim))]

def prev_period(ini, fim, modo):
    if modo == "Período anterior equivalente":
        d = fim - ini
        return ini - d - timedelta(days=1), ini - timedelta(days=1)
    if modo == "Mês anterior":
        p = ini.replace(day=1)
        fe = p - timedelta(days=1)
        return fe.replace(day=1), fe
    if modo == "Mesmo período ano anterior":
        try: return ini.replace(year=ini.year-1), fim.replace(year=fim.year-1)
        except ValueError: return ini - timedelta(days=365), fim - timedelta(days=365)
    return ini, fim

for k, v in [("df_mp_raw", None), ("df_ec_raw", None),
             ("ts_mp", None), ("ts_ec", None)]:
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
        r = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        try:    text = r.content.decode("utf-8")
        except: text = r.content.decode("latin-1")
        if tipo == "ec":
            df = pd.read_csv(StringIO(text), header=None, names=EC_COLS)
        else:
            df = pd.read_csv(StringIO(text))
        return df, datetime.now().strftime("%d/%m/%Y %H:%M")
    except Exception as e:
        st.error(f"Erro: {e}")
        return None, None

def read_bytes(f, tipo):
    try:    text = f.read().decode("utf-8")
    except: f.seek(0); text = f.read().decode("latin-1")
    if tipo == "ec":
        return pd.read_csv(StringIO(text), header=None, names=EC_COLS)
    return pd.read_csv(StringIO(text))

def prep_mp(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw.copy()
    df.columns = [c.strip().upper() for c in df.columns]
    col_map = {}
    for tgt, alts in [
        ("DATA",        ["DATA","DATE"]),
        ("NOTA",        ["NOTA","NF","INVOICE","ORDER_ID"]),
        ("QUANTIDADE",  ["QUANTIDADE","QTY","QUANTITY","QTD"]),
        ("VALOR",       ["VALOR","PRICE","UNIT_PRICE","VALOR_UNITARIO"]),
        ("MARKETPLACE", ["MARKETPLACE","CANAL","PLATAFORMA","SOURCE","CHANNEL"]),
    ]:
        for c in df.columns:
            if c in alts:
                col_map[c] = tgt; break
    df = df.rename(columns=col_map)
    for req in ["DATA", "NOTA", "QUANTIDADE", "VALOR", "MARKETPLACE"]:
        if req not in df.columns:
            df[req] = np.nan
    df["valor_num"] = (
        df["VALOR"].astype(str)
        .str.replace(r"\.", "", regex=True)
        .str.replace(",", ".", regex=False)
        .pipe(pd.to_numeric, errors="coerce").fillna(0)
    )
    df["qty_num"]    = pd.to_numeric(df["QUANTIDADE"], errors="coerce").fillna(1)
    df["line_total"] = df["valor_num"] * df["qty_num"]
    df["nota"]       = df["NOTA"].astype(str).str.strip()
    df["data"]       = pd.to_datetime(df["DATA"], dayfirst=True, errors="coerce")
    df["canal_tipo"] = df["MARKETPLACE"].apply(
        lambda x: "ecommerce" if x in ECOM_CANAIS else "marketplace"
    )
    df["marca"] = df["MARKETPLACE"].map(MARCA_MAP).fillna(df["MARKETPLACE"])
    return df

def prep_ec(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw.copy()
    df["sku_selling_price"] = pd.to_numeric(
        df["sku_selling_price"].astype(str).str.replace(",", ".", regex=False),
        errors="coerce"
    ).fillna(0)
    df["quantity_sku"] = pd.to_numeric(df["quantity_sku"], errors="coerce").fillna(0)
    suspicious = (df["sku_selling_price"] < 10) & (df["sku_selling_price"] > 0)
    df.loc[suspicious, "sku_selling_price"] = df.loc[suspicious, "sku_selling_price"] * 1000
    df["line_total"] = df["sku_selling_price"] * df["quantity_sku"]
    df["data"]       = pd.to_datetime(df["created_at"], errors="coerce", utc=True)
    df["data"]       = df["data"].dt.tz_localize(None).dt.normalize()
    df["status"]     = df["status"].astype(str).str.strip()
    df["faturado"]   = df["status"].isin(["Faturado", "faturado", "Aprovado", "Entregue"])
    df["utmsource"]  = df["utmsource"].fillna("Direto").astype(str).str.strip()
    df["livelo"]     = df["livelo_tag"].astype(str).str.strip().str.lower() == "livelo"
    df["order"]      = df["order"].astype(str).str.strip()
    return df

def mp_agg_notas(df_mp: pd.DataFrame, canal_tipo: str) -> pd.DataFrame:
    sub = df_mp[df_mp["canal_tipo"] == canal_tipo]
    if sub.empty:
        return pd.DataFrame()
    return (
        sub.groupby(["nota", "MARKETPLACE", "marca", "data"])
        .agg(receita=("line_total", "sum"), itens=("qty_num", "sum"))
        .reset_index()
    )

def kpis(df_notas: pd.DataFrame):
    if df_notas.empty:
        return dict(total=0, receita=0, ticket=0, itens=0)
    total   = df_notas["nota"].nunique()
    receita = float(df_notas["receita"].sum())
    itens   = int(df_notas["itens"].sum())
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
    <span class="dot-live"></span>
    <span>NF/Faturamento: {ts_mp}</span>
    <span style="color:#1a2540">|</span>
    <span>E-com Enriq.: {ts_ec}</span>
  </div>
</div>
""", unsafe_allow_html=True)

with st.expander("⚙️  Fontes de Dados", expanded=not has_mp):
    c1, c2, c3 = st.columns([2, 2, 1])

    with c1:
        st.markdown("**📋 Planilha de Faturamento (Notas Fiscais)**")
        st.markdown(
            "<div style='font-size:.75rem;color:#64748b;margin-bottom:8px;'>"
            "Fonte principal de receita. Colunas: <code>DATA · NOTA · QUANTIDADE · VALOR · MARKETPLACE</code><br>"
            "<code>Site Mondaine / Site Seculus / Site Timex / Multimarcas</code> → classificados como E-commerce<br>"
            "Demais canais (Livelo, Shopee, etc.) → classificados como Marketplace</div>",
            unsafe_allow_html=True,
        )
        mp_url  = st.text_input("URL Google Sheets / CSV", key="mp_url",
                                placeholder="https://docs.google.com/spreadsheets/d/...")
        mp_file = st.file_uploader("ou upload CSV", type="csv", key="mp_up")
        if st.button("Carregar Faturamento", use_container_width=True):
            raw = None
            if mp_file:
                raw = read_bytes(mp_file, "mp")
                ts  = datetime.now().strftime("%d/%m/%Y %H:%M")
            elif mp_url.strip():
                with st.spinner("Carregando..."):
                    raw, ts = load_url(mp_url.strip(), "mp")
            if raw is not None:
                st.session_state.df_mp_raw = raw
                st.session_state.ts_mp = ts
                st.success(f"✅ {len(raw)} linhas carregadas")
                st.rerun()

    with c2:
        st.markdown("**🛒 Planilha E-commerce (Enriquecimento)**")
        st.markdown(
            "<div style='font-size:.75rem;color:#64748b;margin-bottom:8px;'>"
            "Usada para: status dos pedidos, UTM Source (deduplicado por order ID), "
            "quantidade por SKU e ranking de produtos.<br>"
            "Pedidos com <code>livelo_tag = Livelo</code> são ignorados automaticamente.</div>",
            unsafe_allow_html=True,
        )
        ec_url  = st.text_input("URL Google Sheets / CSV", key="ec_url",
                                placeholder="https://docs.google.com/spreadsheets/d/...")
        ec_file = st.file_uploader("ou upload CSV", type="csv", key="ec_up")
        if st.button("Carregar E-commerce", use_container_width=True):
            raw = None
            if ec_file:
                raw = read_bytes(ec_file, "ec")
                ts  = datetime.now().strftime("%d/%m/%Y %H:%M")
            elif ec_url.strip():
                with st.spinner("Carregando..."):
                    raw, ts = load_url(ec_url.strip(), "ec")
            if raw is not None:
                st.session_state.df_ec_raw = raw
                st.session_state.ts_ec = ts
                st.success(f"✅ {len(raw)} linhas carregadas")
                st.rerun()

    with c3:
        st.markdown("**📥 Templates**")
        tpl_mp = "DATA,NOTA,QUANTIDADE,VALOR,MARKETPLACE\n01/04/2026,NF001,1,\"269,10\",Livelo\n01/04/2026,NF002,2,\"350,00\",Site Seculus\n01/04/2026,NF003,1,\"180,00\",Multimarcas"
        tpl_ec = ",".join(EC_COLS) + "\nPED001,2026-04-01 10:00:00Z,Cliente,SP,Faturado,google-shopping,PRIMEIRACOMPRA,Pix,1,1,,SKU001,Relógio Slim,350.00,350.00,,Seculus,"
        st.download_button("⬇️ Template NF", data=tpl_mp,
                           file_name="template_nf.csv", mime="text/csv", use_container_width=True)
        st.download_button("⬇️ Template EC", data=tpl_ec,
                           file_name="template_ec.csv", mime="text/csv", use_container_width=True)
        st.markdown("**Status:**")
        st.markdown(
            f"{'🟢' if has_mp else '🔴'} Faturamento &nbsp; {'🟢' if has_ec else '⚪'} E-com (opcional)",
            unsafe_allow_html=True,
        )

if not has_mp:
    st.markdown("""
    <div class="upload-zone">
        <h3>Nenhum dado carregado</h3>
        <p>Carregue a planilha de faturamento (notas fiscais) para começar.<br>
        A planilha de E-commerce é opcional e enriquece com status, UTM e produtos.</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

df_mp = prep_mp(st.session_state.df_mp_raw)
df_ec = prep_ec(st.session_state.df_ec_raw) if has_ec else pd.DataFrame()

mp_ecom_all = mp_agg_notas(df_mp, "ecommerce")
mp_mkt_all  = mp_agg_notas(df_mp, "marketplace")

st.markdown("---")
fr = st.columns([2, 2, 2, 1, 1, 1, 1, 1])
hoje = datetime.today().date()
with fr[0]: data_ini = st.date_input("De",  value=hoje - timedelta(days=30), key="fi")
with fr[1]: data_fim = st.date_input("Até", value=hoje, key="ff")
with fr[2]: comp_modo = st.selectbox("Comparar com",
    ["Período anterior equivalente", "Mês anterior", "Mesmo período ano anterior"])
atalhos = [("7d", hoje-timedelta(days=7), hoje), ("30d", hoje-timedelta(days=30), hoje),
           ("Mês", hoje.replace(day=1), hoje), ("Ano", hoje.replace(month=1,day=1), hoje),
           ("Hoje", hoje, hoje)]
for i, (lbl, d, f) in enumerate(atalhos, start=3):
    with fr[i]:
        if st.button(lbl):
            st.session_state.fi = d; st.session_state.ff = f; st.rerun()

ini_ant, fim_ant = prev_period(data_ini, data_fim, comp_modo)

ec_p  = filter_dt(mp_ecom_all, data_ini, data_fim)
mp_p  = filter_dt(mp_mkt_all,  data_ini, data_fim)
ec_pa = filter_dt(mp_ecom_all, ini_ant,  fim_ant)
mp_pa = filter_dt(mp_mkt_all,  ini_ant,  fim_ant)

ec_m  = kpis(ec_p)
mp_m  = kpis(mp_p)
ec_ma = kpis(ec_pa)
mp_ma = kpis(mp_pa)

total_rec     = ec_m["receita"] + mp_m["receita"]
total_rec_ant = ec_ma["receita"] + mp_ma["receita"]

ec_p_ec     = filter_dt(df_ec, data_ini, data_fim) if has_ec else pd.DataFrame()
ec_fat_df   = ec_p_ec[ec_p_ec["faturado"] & ~ec_p_ec["livelo"]] if not ec_p_ec.empty else pd.DataFrame()
n_fat       = int(ec_fat_df["order"].nunique()) if not ec_fat_df.empty else 0
n_tot       = int(ec_p_ec[~ec_p_ec["livelo"]]["order"].nunique()) if not ec_p_ec.empty else 0
n_pend      = n_tot - n_fat
ec_pa_ec    = filter_dt(df_ec, ini_ant, fim_ant) if has_ec else pd.DataFrame()
ec_fat_ant  = ec_pa_ec[ec_pa_ec["faturado"] & ~ec_pa_ec["livelo"]] if not ec_pa_ec.empty else pd.DataFrame()
n_fat_ant   = int(ec_fat_ant["order"].nunique()) if not ec_fat_ant.empty else 0

st.markdown("---")

tab_geral, tab_ec_tab, tab_mp_tab, tab_prod = st.tabs([
    "📊 Visão Geral", "🛒 E-commerce", "🏪 Marketplace", "🏆 Produtos & SKUs",
])

with tab_geral:
    st.markdown('<div class="sec-head"><h4>KPIs Consolidados do Período</h4><div class="line"></div></div>',
                unsafe_allow_html=True)

    g1, g2, g3, g4, g5, g6 = st.columns(6)
    g1.metric("💰 Receita Total",   fmt_brl(total_rec),
              delta=fmt_var(var_pct(total_rec, total_rec_ant)))
    g2.metric("🛒 Receita E-com",   fmt_brl(ec_m["receita"]),
              delta=fmt_var(var_pct(ec_m["receita"], ec_ma["receita"])))
    g3.metric("🏪 Receita Mkt",     fmt_brl(mp_m["receita"]),
              delta=fmt_var(var_pct(mp_m["receita"], mp_ma["receita"])))
    g4.metric("📑 NFs E-com",       f"{ec_m['total']:,}",
              delta=fmt_var(var_pct(ec_m["total"], ec_ma["total"])))
    g5.metric("📑 NFs Marketplace", f"{mp_m['total']:,}",
              delta=fmt_var(var_pct(mp_m["total"], mp_ma["total"])))
    g6.metric("📦 Pedidos Fat.",
              f"{n_fat:,}" if has_ec else "—",
              delta=fmt_var(var_pct(n_fat, n_fat_ant)) if has_ec else None,
              help="Pedidos com status Faturado na planilha E-commerce, deduplicados por order ID, Livelo excluído")

    st.markdown("<br>", unsafe_allow_html=True)

    if total_rec > 0:
        pec = ec_m["receita"] / total_rec * 100
        pmp = mp_m["receita"] / total_rec * 100
        st.markdown(
            f"<div class='insight'>📐 <strong>Mix de canal:</strong> E-commerce representa "
            f"<strong>{pec:.1f}%</strong> da receita (R$ {ec_m['receita']:,.0f}) e Marketplace "
            f"<strong>{pmp:.1f}%</strong> (R$ {mp_m['receita']:,.0f}) no período.</div>",
            unsafe_allow_html=True,
        )
    if has_ec and n_tot > 0:
        taxa_fat = n_fat / n_tot * 100
        if taxa_fat < 70:
            st.markdown(
                f"<div class='warn'>⚠️ Taxa de faturamento E-commerce em "
                f"<strong>{taxa_fat:.1f}%</strong> — {n_pend} pedido(s) ainda pendente(s).</div>",
                unsafe_allow_html=True,
            )

    col_ev, col_sh = st.columns([3, 1])
    with col_ev:
        st.markdown('<div class="sec-head"><h4>Evolução de Receita</h4><div class="line"></div></div>',
                    unsafe_allow_html=True)
        fig_ev = go.Figure()
        if not ec_p.empty:
            ts1 = ec_p.groupby("data")["receita"].sum().reset_index()
            fig_ev.add_trace(go.Scatter(
                x=ts1["data"], y=ts1["receita"], name="E-commerce",
                mode="lines", fill="tozeroy",
                line=dict(color="#3b6fff", width=2.5, shape="spline", smoothing=1.2),
                fillcolor="rgba(59,111,255,0.07)",
            ))
        if not mp_p.empty:
            ts2 = mp_p.groupby("data")["receita"].sum().reset_index()
            fig_ev.add_trace(go.Scatter(
                x=ts2["data"], y=ts2["receita"], name="Marketplace",
                mode="lines", fill="tozeroy",
                line=dict(color="#f59e0b", width=2.5, shape="spline", smoothing=1.2),
                fillcolor="rgba(245,158,11,0.06)",
            ))
        fig_ev.update_layout(**L())
        st.plotly_chart(fig_ev, use_container_width=True)

    with col_sh:
        st.markdown('<div class="sec-head"><h4>Share por Canal</h4><div class="line"></div></div>',
                    unsafe_allow_html=True)
        rows = []
        if ec_m["receita"] > 0: rows.append({"Canal": "E-commerce", "Receita": ec_m["receita"]})
        if mp_m["receita"] > 0: rows.append({"Canal": "Marketplace","Receita": mp_m["receita"]})
        if rows:
            fig_sh = px.pie(pd.DataFrame(rows), names="Canal", values="Receita",
                            color="Canal",
                            color_discrete_map={"E-commerce":"#3b6fff","Marketplace":"#f59e0b"},
                            hole=0.6)
            fig_sh.update_traces(textinfo="percent+label", textfont_size=11)
            fig_sh.update_layout(**L(margin=dict(l=10,r=10,t=30,b=10)))
            st.plotly_chart(fig_sh, use_container_width=True)

    cb1, cb2 = st.columns(2)
    with cb1:
        st.markdown('<div class="sec-head"><h4>E-commerce por Marca</h4><div class="line"></div></div>',
                    unsafe_allow_html=True)
        if not ec_p.empty and "marca" in ec_p.columns:
            em = (ec_p.groupby("marca")["receita"].sum().reset_index()
                  .sort_values("receita", ascending=True))
            fig_em = px.bar(em, x="receita", y="marca", orientation="h",
                            color="marca", color_discrete_map=COR_MARCA,
                            labels={"receita":"Receita (R$)","marca":""})
            fig_em.update_layout(**L_inv())
            st.plotly_chart(fig_em, use_container_width=True)

    with cb2:
        st.markdown('<div class="sec-head"><h4>Marketplace por Plataforma</h4><div class="line"></div></div>',
                    unsafe_allow_html=True)
        if not mp_p.empty:
            mm = (mp_p.groupby("MARKETPLACE")["receita"].sum().reset_index()
                  .sort_values("receita", ascending=True))
            fig_mm = px.bar(mm, x="receita", y="MARKETPLACE", orientation="h",
                            color="MARKETPLACE", color_discrete_map=COR_MP_PLAT,
                            labels={"receita":"Receita (R$)","MARKETPLACE":""})
            fig_mm.update_layout(**L_inv())
            st.plotly_chart(fig_mm, use_container_width=True)

    if has_ec and not ec_fat_df.empty:
        st.markdown('<div class="sec-head"><h4>UTM Source — Pedidos Faturados E-commerce</h4><div class="line"></div></div>',
                    unsafe_allow_html=True)
        utm_g = (ec_fat_df.drop_duplicates("order")
                 .groupby("utmsource")
                 .agg(pedidos=("order", "count"))
                 .reset_index()
                 .sort_values("pedidos", ascending=False))
        utm_g["pct"] = utm_g["pedidos"] / utm_g["pedidos"].sum() * 100
        ug1, ug2 = st.columns([2, 1])
        with ug1:
            fig_utm = px.bar(utm_g, x="utmsource", y="pedidos",
                             color="utmsource", color_discrete_map=COR_CANAL_EC,
                             labels={"pedidos":"Pedidos Faturados","utmsource":"UTM Source"},
                             text=utm_g["pedidos"].astype(str) + " (" + utm_g["pct"].map("{:.0f}%".format) + ")")
            fig_utm.update_traces(textposition="outside")
            fig_utm.update_layout(**L())
            st.plotly_chart(fig_utm, use_container_width=True)
        with ug2:
            fig_utmp = px.pie(utm_g, names="utmsource", values="pedidos",
                              color="utmsource", color_discrete_map=COR_CANAL_EC, hole=0.58)
            fig_utmp.update_traces(textinfo="percent+label", textfont_size=11)
            fig_utmp.update_layout(**L(margin=dict(l=5,r=5,t=30,b=5)))
            st.plotly_chart(fig_utmp, use_container_width=True)


with tab_ec_tab:
    st.markdown('<div class="sec-head"><h4>E-commerce — Receita por Notas Fiscais</h4><div class="line"></div></div>',
                unsafe_allow_html=True)

    if ec_p.empty:
        st.info("Nenhuma nota fiscal classificada como E-commerce no período.")
    else:
        e1, e2, e3, e4, e5 = st.columns(5)
        e1.metric("💰 Receita",      fmt_brl(ec_m["receita"]),
                  delta=fmt_var(var_pct(ec_m["receita"], ec_ma["receita"])))
        e2.metric("📑 NFs",          f"{ec_m['total']:,}",
                  delta=fmt_var(var_pct(ec_m["total"], ec_ma["total"])))
        e3.metric("📦 Itens",        f"{ec_m['itens']:,}",
                  delta=fmt_var(var_pct(ec_m["itens"], ec_ma["itens"])))
        e4.metric("🎟️ Ticket NF",   fmt_brl(ec_m["ticket"]),
                  delta=fmt_var(var_pct(ec_m["ticket"], ec_ma["ticket"])))
        e5.metric("📊 Pedidos Fat.", f"{n_fat:,}" if has_ec else "—",
                  delta=fmt_var(var_pct(n_fat, n_fat_ant)) if has_ec else None,
                  help="Da planilha E-commerce, deduplicado por order ID")

        st.markdown("<br>", unsafe_allow_html=True)

        ea1, ea2 = st.columns(2)
        with ea1:
            st.markdown('<div class="sec-head"><h4>Receita por Marca</h4><div class="line"></div></div>',
                        unsafe_allow_html=True)
            em2 = (ec_p.groupby("marca")["receita"].sum().reset_index()
                   .sort_values("receita", ascending=False))
            fig_em2 = px.bar(em2, x="marca", y="receita",
                             color="marca", color_discrete_map=COR_MARCA,
                             labels={"receita":"Receita (R$)","marca":""},
                             text=em2["receita"].map(lambda x: f"R$ {x:,.0f}"))
            fig_em2.update_traces(textposition="outside")
            fig_em2.update_layout(**L())
            st.plotly_chart(fig_em2, use_container_width=True)

        with ea2:
            st.markdown('<div class="sec-head"><h4>Share por Marca</h4><div class="line"></div></div>',
                        unsafe_allow_html=True)
            fig_em2p = px.pie(em2, names="marca", values="receita",
                              color="marca", color_discrete_map=COR_MARCA, hole=0.58)
            fig_em2p.update_traces(textinfo="percent+label", textfont_size=11)
            fig_em2p.update_layout(**L(margin=dict(l=10,r=10,t=30,b=10)))
            st.plotly_chart(fig_em2p, use_container_width=True)

        st.markdown('<div class="sec-head"><h4>Evolução Diária</h4><div class="line"></div></div>',
                    unsafe_allow_html=True)
        ec_d = ec_p.groupby(["data","marca"]).agg(receita=("receita","sum")).reset_index()
        fig_edd = px.area(ec_d, x="data", y="receita", color="marca",
                          color_discrete_map=COR_MARCA,
                          labels={"receita":"Receita (R$)","data":"","marca":"Marca"})
        fig_edd.update_layout(**L())
        st.plotly_chart(fig_edd, use_container_width=True)

        st.markdown('<div class="sec-head"><h4>Atual vs Período Anterior por Marca</h4><div class="line"></div></div>',
                    unsafe_allow_html=True)
        ec_a2 = ec_p.groupby("marca")["receita"].sum().reset_index().rename(columns={"receita":"atual"})
        ec_b2 = (ec_pa.groupby("marca")["receita"].sum().reset_index().rename(columns={"receita":"anterior"})
                 if not ec_pa.empty else pd.DataFrame(columns=["marca","anterior"]))
        ec_cmp = ec_a2.merge(ec_b2, on="marca", how="outer").fillna(0)
        ec_cmp["var"] = ec_cmp.apply(
            lambda r: fmt_var(var_pct(r["atual"], r["anterior"])) or "—", axis=1)
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
        st.markdown('<div class="sec-head"><h4>Status dos Pedidos (Planilha E-commerce)</h4><div class="line"></div></div>',
                    unsafe_allow_html=True)
        if not ec_p_ec.empty:
            ec_dedup = ec_p_ec[~ec_p_ec["livelo"]].drop_duplicates("order")
            st_cnt   = ec_dedup["faturado"].map({True:"Faturado",False:"Pendente"}).value_counts().reset_index()
            st_cnt.columns = ["status","qtd"]

            sv1, sv2 = st.columns(2)
            with sv1:
                fig_st = px.pie(st_cnt, names="status", values="qtd",
                                color="status",
                                color_discrete_map={"Faturado":"#10b981","Pendente":"#f59e0b"},
                                hole=0.58)
                fig_st.update_traces(textinfo="percent+label", textfont_size=11)
                fig_st.update_layout(**L(margin=dict(l=10,r=10,t=30,b=10)))
                st.plotly_chart(fig_st, use_container_width=True)

            with sv2:
                st.markdown('<div class="sec-head"><h4>UTM Source — Pedidos Faturados</h4><div class="line"></div></div>',
                            unsafe_allow_html=True)
                if not ec_fat_df.empty:
                    utm_t = (ec_fat_df.drop_duplicates("order")
                             .groupby("utmsource")
                             .agg(pedidos=("order","count"))
                             .reset_index()
                             .sort_values("pedidos", ascending=False))
                    utm_t["pct"]   = utm_t["pedidos"] / utm_t["pedidos"].sum() * 100
                    utm_t["share"] = utm_t["pct"].map("{:.1f}%".format)
                    utm_t = utm_t.rename(columns={"utmsource":"UTM Source","pedidos":"Pedidos Fat.","share":"Share"})
                    st.dataframe(utm_t[["UTM Source","Pedidos Fat.","Share"]], use_container_width=True, hide_index=True)

        st.markdown('<div class="sec-head"><h4>Detalhamento de Pedidos</h4><div class="line"></div></div>',
                    unsafe_allow_html=True)
        if not ec_p_ec.empty:
            det = (ec_p_ec[~ec_p_ec["livelo"]].drop_duplicates("order")
                   [["order","data","status","utmsource","quantity_sku"]]
                   .rename(columns={"order":"Order ID","data":"Data","status":"Status",
                                    "utmsource":"UTM Source","quantity_sku":"Itens"})
                   .sort_values("Data", ascending=False))
            st.dataframe(det, use_container_width=True, hide_index=True)
            st.download_button("📥 Exportar pedidos",
                               data=det.to_csv(index=False).encode("utf-8"),
                               file_name="pedidos_ecommerce.csv", mime="text/csv")

    st.markdown('<div class="sec-head"><h4>Notas Fiscais E-commerce</h4><div class="line"></div></div>',
                unsafe_allow_html=True)
    if not ec_p.empty:
        nf = ec_p[["nota","data","MARKETPLACE","marca","receita","itens"]].copy()
        nf["receita"] = nf["receita"].map(fmt_brl)
        nf = nf.sort_values("data", ascending=False).rename(columns={
            "nota":"Nota Fiscal","data":"Data","MARKETPLACE":"Canal","marca":"Marca",
            "receita":"Receita","itens":"Itens"})
        st.dataframe(nf, use_container_width=True, hide_index=True)
        st.download_button("📥 Exportar NFs",
                           data=ec_p.to_csv(index=False).encode("utf-8"),
                           file_name="nf_ecommerce.csv", mime="text/csv")


with tab_mp_tab:
    st.markdown('<div class="sec-head"><h4>Marketplace — Receita por Notas Fiscais</h4><div class="line"></div></div>',
                unsafe_allow_html=True)

    if mp_p.empty:
        st.info("Nenhuma nota fiscal de Marketplace no período.")
    else:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("💰 Receita",      fmt_brl(mp_m["receita"]),
                  delta=fmt_var(var_pct(mp_m["receita"], mp_ma["receita"])))
        m2.metric("📑 NFs",          f"{mp_m['total']:,}",
                  delta=fmt_var(var_pct(mp_m["total"], mp_ma["total"])))
        m3.metric("📦 Itens",        f"{mp_m['itens']:,}",
                  delta=fmt_var(var_pct(mp_m["itens"], mp_ma["itens"])))
        m4.metric("🎟️ Ticket Médio", fmt_brl(mp_m["ticket"]),
                  delta=fmt_var(var_pct(mp_m["ticket"], mp_ma["ticket"])))

        st.markdown("<br>", unsafe_allow_html=True)

        mp1, mp2 = st.columns(2)
        with mp1:
            st.markdown('<div class="sec-head"><h4>Receita por Plataforma</h4><div class="line"></div></div>',
                        unsafe_allow_html=True)
            mpp = (mp_p.groupby("MARKETPLACE")["receita"].sum().reset_index()
                   .sort_values("receita", ascending=False))
            fig_mpp = px.bar(mpp, x="MARKETPLACE", y="receita",
                             color="MARKETPLACE", color_discrete_map=COR_MP_PLAT,
                             labels={"receita":"Receita (R$)","MARKETPLACE":""},
                             text=mpp["receita"].map(lambda x: f"R$ {x:,.0f}"))
            fig_mpp.update_traces(textposition="outside")
            fig_mpp.update_layout(**L())
            st.plotly_chart(fig_mpp, use_container_width=True)

        with mp2:
            st.markdown('<div class="sec-head"><h4>Share por Plataforma</h4><div class="line"></div></div>',
                        unsafe_allow_html=True)
            fig_mpp2 = px.pie(mpp, names="MARKETPLACE", values="receita",
                              color="MARKETPLACE", color_discrete_map=COR_MP_PLAT, hole=0.58)
            fig_mpp2.update_traces(textinfo="percent+label", textfont_size=11)
            fig_mpp2.update_layout(**L(margin=dict(l=10,r=10,t=30,b=10)))
            st.plotly_chart(fig_mpp2, use_container_width=True)

        st.markdown('<div class="sec-head"><h4>Evolução Diária</h4><div class="line"></div></div>',
                    unsafe_allow_html=True)
        mp_d = mp_p.groupby(["data","MARKETPLACE"])["receita"].sum().reset_index()
        fig_mpd = px.area(mp_d, x="data", y="receita", color="MARKETPLACE",
                          color_discrete_map=COR_MP_PLAT,
                          labels={"receita":"Receita (R$)","data":"","MARKETPLACE":"Plataforma"})
        fig_mpd.update_layout(**L())
        st.plotly_chart(fig_mpd, use_container_width=True)

        st.markdown('<div class="sec-head"><h4>Atual vs Período Anterior</h4><div class="line"></div></div>',
                    unsafe_allow_html=True)
        mp_a2 = mp_p.groupby("MARKETPLACE")["receita"].sum().reset_index().rename(columns={"receita":"atual"})
        mp_b2 = (mp_pa.groupby("MARKETPLACE")["receita"].sum().reset_index().rename(columns={"receita":"anterior"})
                 if not mp_pa.empty else pd.DataFrame(columns=["MARKETPLACE","anterior"]))
        mp_cmp = mp_a2.merge(mp_b2, on="MARKETPLACE", how="outer").fillna(0)
        mp_cmp["var"] = mp_cmp.apply(
            lambda r: fmt_var(var_pct(r["atual"], r["anterior"])) or "—", axis=1)
        fig_mpcp = go.Figure([
            go.Bar(name="Anterior", x=mp_cmp["MARKETPLACE"], y=mp_cmp["anterior"],
                   marker_color="rgba(100,116,139,.35)", marker_line_width=0),
            go.Bar(name="Atual",    x=mp_cmp["MARKETPLACE"], y=mp_cmp["atual"],
                   marker_color=[COR_MP_PLAT.get(c,"#f59e0b") for c in mp_cmp["MARKETPLACE"]],
                   marker_line_width=0, text=mp_cmp["var"], textposition="outside"),
        ])
        fig_mpcp.update_layout(barmode="group", **L())
        st.plotly_chart(fig_mpcp, use_container_width=True)

        st.markdown('<div class="sec-head"><h4>Notas Fiscais Marketplace</h4><div class="line"></div></div>',
                    unsafe_allow_html=True)
        nf_mp = mp_p[["nota","data","MARKETPLACE","receita","itens"]].copy()
        nf_mp["receita"] = nf_mp["receita"].map(fmt_brl)
        nf_mp = nf_mp.sort_values("data", ascending=False).rename(columns={
            "nota":"Nota Fiscal","data":"Data","MARKETPLACE":"Plataforma",
            "receita":"Receita","itens":"Itens"})
        st.dataframe(nf_mp, use_container_width=True, hide_index=True)
        st.download_button("📥 Exportar NFs",
                           data=mp_p.to_csv(index=False).encode("utf-8"),
                           file_name="nf_marketplace.csv", mime="text/csv")


with tab_prod:
    if not has_ec or df_ec.empty:
        st.info("Carregue a planilha E-commerce para visualizar o ranking de produtos.")
        st.stop()

    df_fp  = filter_dt(df_ec, data_ini, data_fim)
    df_fp  = df_fp[~df_fp["livelo"]] if not df_fp.empty else df_fp
    df_fat = df_fp[df_fp["faturado"]] if not df_fp.empty else pd.DataFrame()

    if df_fat.empty:
        st.info("Sem dados de produtos faturados no período.")
        st.stop()

    st.markdown(
        "<div class='insight'>ℹ️ Ranking calculado a partir de <code>sku_selling_price × quantity_sku</code> "
        "da planilha E-commerce. A receita oficial do negócio está nas abas E-commerce e Marketplace (notas fiscais).</div>",
        unsafe_allow_html=True,
    )

    pf1, pf2 = st.columns([3, 1])
    with pf1:
        marcas_d = sorted(df_fat["brand"].dropna().unique().tolist())
        marcas_s = st.multiselect("Filtrar por marca", marcas_d, default=marcas_d, key="pm")
    with pf2:
        top_n = st.selectbox("Top N", [5, 10, 15, 20], index=1, key="tn")

    df_fat2 = df_fat[df_fat["brand"].isin(marcas_s)] if marcas_s else df_fat
    prod = (
        df_fat2.groupby(["sku","product_name","brand"])
        .agg(qty=("quantity_sku","sum"), orders=("order","nunique"), receita=("line_total","sum"))
        .reset_index()
        .sort_values("qty", ascending=False)
    )

    pc1, pc2 = st.columns(2)
    with pc1:
        st.markdown('<div class="sec-head"><h4>Top por Quantidade Vendida</h4><div class="line"></div></div>',
                    unsafe_allow_html=True)
        fig_pq = px.bar(prod.head(top_n), x="qty", y="product_name", color="brand",
                        orientation="h", color_discrete_map=COR_MARCA,
                        labels={"qty":"Unidades","product_name":"","brand":"Marca"})
        fig_pq.update_layout(**L_inv())
        st.plotly_chart(fig_pq, use_container_width=True)

    with pc2:
        st.markdown('<div class="sec-head"><h4>Top por Receita Estimada</h4><div class="line"></div></div>',
                    unsafe_allow_html=True)
        fig_pr = px.bar(prod.sort_values("receita",ascending=False).head(top_n),
                        x="receita", y="product_name", color="brand",
                        orientation="h", color_discrete_map=COR_MARCA,
                        labels={"receita":"Receita Est. (R$)","product_name":"","brand":"Marca"})
        fig_pr.update_layout(**L_inv())
        st.plotly_chart(fig_pr, use_container_width=True)

    st.markdown('<div class="sec-head"><h4>Curva de Pareto — Volume de Unidades</h4><div class="line"></div></div>',
                unsafe_allow_html=True)
    p80 = prod.sort_values("qty", ascending=False).copy()
    p80["cum_pct"] = p80["qty"].cumsum() / p80["qty"].sum() * 100
    n80 = int((p80["cum_pct"] <= 80).sum()) + 1
    pct_cat = n80 / len(p80) * 100 if len(p80) > 0 else 0
    st.markdown(
        f"<div class='insight'>📐 <strong>Pareto:</strong> "
        f"<strong>{n80} produto(s) ({pct_cat:.0f}% do catálogo)</strong> "
        f"representam 80% do volume de unidades vendidas no período.</div>",
        unsafe_allow_html=True,
    )
    fig_par = go.Figure()
    fig_par.add_trace(go.Bar(
        x=p80["product_name"].str[:45], y=p80["qty"],
        marker_color="#3b6fff", name="Unidades", opacity=0.85,
    ))
    fig_par.add_trace(go.Scatter(
        x=p80["product_name"].str[:45], y=p80["cum_pct"],
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

    st.markdown('<div class="sec-head"><h4>Tabela Detalhada por SKU</h4><div class="line"></div></div>',
                unsafe_allow_html=True)
    df_ant_fp  = filter_dt(df_ec, ini_ant, fim_ant)
    df_ant_fp  = df_ant_fp[~df_ant_fp["livelo"]] if not df_ant_fp.empty else pd.DataFrame()
    df_ant_fat = df_ant_fp[df_ant_fp["faturado"]] if not df_ant_fp.empty else pd.DataFrame()

    if not df_ant_fat.empty:
        ant_s = (df_ant_fat.groupby("sku")["quantity_sku"].sum()
                 .reset_index().rename(columns={"quantity_sku":"qty_ant"}))
        prod = prod.merge(ant_s, on="sku", how="left").fillna(0)
        prod["var_qty"] = prod.apply(
            lambda r: fmt_var(var_pct(r["qty"], r["qty_ant"])) or "—", axis=1)
    else:
        prod["var_qty"] = "—"

    prod_disp = prod.copy()
    prod_disp["receita"] = prod_disp["receita"].map(fmt_brl)
    prod_disp = prod_disp.rename(columns={
        "brand":"Marca","sku":"SKU","product_name":"Produto",
        "qty":"Qtd Vendida","orders":"Pedidos","receita":"Receita Est.",
        "var_qty":"Var. Qtd vs Ant.",
    })
    cols = [c for c in ["Marca","SKU","Produto","Qtd Vendida","Pedidos","Receita Est.","Var. Qtd vs Ant."]
            if c in prod_disp.columns]
    st.dataframe(prod_disp[cols], use_container_width=True, hide_index=True)
    st.download_button("📥 Exportar SKUs",
                       data=prod.to_csv(index=False).encode("utf-8"),
                       file_name="skus.csv", mime="text/csv")

st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#1a2540;font-size:.7rem;font-family:DM Mono,monospace;'>"
    "⌚ Grupo Seculus · Receita calculada via notas fiscais · "
    "Site Mondaine / Site Seculus / Site Timex / Multimarcas → E-commerce (Multimarcas = E-time) · "
    "Livelo excluído automaticamente"
    "</div>",
    unsafe_allow_html=True,
)
