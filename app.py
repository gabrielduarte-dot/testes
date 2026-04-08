import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import date

# ─────────────────────────────────────────────
# CONFIGURAÇÃO DA PÁGINA
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard de Vendas · Grupo Seculus",
    page_icon="🕐",
    layout="wide",
)

# ─────────────────────────────────────────────
# CORES E LAYOUT GLOBAL PLOTLY
# ─────────────────────────────────────────────
COR_MONDAINE = "#4F8EF7"
COR_SECULUS  = "#2DD4A0"
COR_DANGER   = "#F87171"
COR_SUCCESS  = "#4ADE80"
COR_WARN     = "#FBBF24"

LAYOUT_PLOTLY = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#e2e8f0", family="Inter, sans-serif", size=12),
    title_font=dict(size=14, color="#f1f5f9"),
    margin=dict(l=16, r=16, t=48, b=16),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="left",
        x=0,
        bgcolor="rgba(0,0,0,0)",
        font=dict(size=11),
    ),
    xaxis=dict(
        gridcolor="rgba(255,255,255,0.06)",
        linecolor="rgba(255,255,255,0.1)",
        tickfont=dict(size=11),
    ),
    yaxis=dict(
        gridcolor="rgba(255,255,255,0.06)",
        linecolor="rgba(255,255,255,0.1)",
        tickfont=dict(size=11),
    ),
)

# ─────────────────────────────────────────────
# CSS GLOBAL
# ─────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background-color: #0f1117; }
[data-testid="stHeader"]           { background-color: #0f1117; }
[data-testid="stSidebar"]          { background-color: #161b27; }

.kpi-card {
    background: #1e2535; border-radius: 12px;
    padding: 18px 20px 14px; border: 1px solid #2a3448;
}
.kpi-icon  { font-size: 14px; color: #94a3b8; margin-bottom: 6px; }
.kpi-label { font-size: 11px; color: #94a3b8; text-transform: uppercase;
             letter-spacing: .08em; margin-bottom: 4px; }
.kpi-value { font-size: 30px; font-weight: 700; color: #f1f5f9;
             line-height: 1.1; margin-bottom: 6px; }
.kpi-delta-up   { font-size: 12px; color: #4ade80; font-weight: 600; }
.kpi-delta-down { font-size: 12px; color: #f87171; font-weight: 600; }
.kpi-delta-neu  { font-size: 12px; color: #94a3b8; font-weight: 600; }

.brand-card {
    background: #1e2535; border-radius: 12px;
    padding: 20px 22px; border: 1px solid #2a3448;
}
.brand-title-m { font-size: 16px; font-weight: 700; color: #4F8EF7; margin-bottom: 14px; }
.brand-title-s { font-size: 16px; font-weight: 700; color: #2DD4A0; margin-bottom: 14px; }
.brand-row {
    display: flex; justify-content: space-between; align-items: center;
    font-size: 13px; padding: 6px 0; border-bottom: 1px solid #2a3448;
}
.brand-row:last-child { border-bottom: none; }
.brand-row-label { color: #94a3b8; }
.brand-row-val   { font-weight: 600; color: #f1f5f9; }
.badge-green { background:#14532d; color:#4ade80; border-radius:5px; padding:2px 8px; font-size:12px; }
.badge-red   { background:#450a0a; color:#f87171; border-radius:5px; padding:2px 8px; font-size:12px; }
.badge-amber { background:#451a03; color:#fbbf24; border-radius:5px; padding:2px 8px; font-size:12px; }

.section-title {
    font-size: 11px; font-weight: 600; color: #64748b;
    text-transform: uppercase; letter-spacing: .1em;
    margin: 0 0 14px; padding-bottom: 8px;
    border-bottom: 1px solid #2a3448;
}

[data-testid="stTabs"] [role="tablist"] { border-bottom: 1px solid #2a3448 !important; }
[data-testid="stTabs"] [role="tab"]     { color: #64748b !important; font-size: 13px !important; }
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    color: #f1f5f9 !important;
    border-bottom: 2px solid #4F8EF7 !important;
}
/* inputs de data no tema escuro */
[data-testid="stDateInput"] input {
    background: #1e2535 !important; color: #f1f5f9 !important;
    border: 1px solid #2a3448 !important; border-radius: 8px !important;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def fmt_brl(v):
    if pd.isna(v) or v == 0:
        return "R$ 0"
    return "R$ {:,.0f}".format(v).replace(",", "X").replace(".", ",").replace("X", ".")

def delta_html(val, ref):
    if ref == 0:
        return '<span class="kpi-delta-neu">—</span>'
    pct = (val - ref) / ref * 100
    cls   = "kpi-delta-up" if pct >= 0 else "kpi-delta-down"
    arrow = "↑" if pct >= 0 else "↓"
    return f'<span class="{cls}">{arrow} {abs(pct):.1f}%</span>'

def kpi_card(icon, label, value, dlt=""):
    return f"""
    <div class="kpi-card">
      <div class="kpi-icon">{icon}</div>
      <div class="kpi-label">{label}</div>
      <div class="kpi-value">{value}</div>
      {dlt}
    </div>"""

def brand_card(host, d):
    tcls  = "brand-title-m" if host == "mondaine" else "brand-title-s"
    nome  = "Mondaine" if host == "mondaine" else "Seculus"
    cbadge = "badge-green" if d["tx"] < 7 else ("badge-amber" if d["tx"] < 10 else "badge-red")
    return f"""
    <div class="brand-card">
      <div class="{tcls}">{nome}</div>
      <div class="brand-row"><span class="brand-row-label">Clientes únicos</span>
        <span class="brand-row-val">{d['cli']:,}</span></div>
      <div class="brand-row"><span class="brand-row-label">Total de itens</span>
        <span class="brand-row-val">{d['total']:,}</span></div>
      <div class="brand-row"><span class="brand-row-label">Itens faturados</span>
        <span class="brand-row-val"><span class="badge-green">{d['fat']:,}</span></span></div>
      <div class="brand-row"><span class="brand-row-label">Itens cancelados</span>
        <span class="brand-row-val"><span class="badge-red">{d['can']:,}</span></span></div>
      <div class="brand-row"><span class="brand-row-label">Taxa de cancelamento</span>
        <span class="brand-row-val"><span class="{cbadge}">{d['tx']:.1f}%</span></span></div>
      <div class="brand-row"><span class="brand-row-label">Receita faturada</span>
        <span class="brand-row-val">{fmt_brl(d['rec'])}</span></div>
    </div>"""


# ─────────────────────────────────────────────
# CARREGAMENTO DOS DADOS
# ─────────────────────────────────────────────
@st.cache_data
def load_data():
    import os

    def clean_money(s):
        if pd.isna(s): return np.nan
        s = str(s).replace("R$","").replace(" ","").replace(".","").replace(",",".")
        try: return float(s)
        except: return np.nan

    # Busca os arquivos em locais comuns (local e Streamlit Cloud)
    base_paths = [".", "/mount/src/testes", "/app"]
    dfN = dfO = None
    for bp in base_paths:
        pN = os.path.join(bp, "Mondaine_X_Seculus_-_Agosto_a_Março_-_Report.csv")
        pO = os.path.join(bp, "Report_-_2.csv")
        if os.path.exists(pN): dfN = pd.read_csv(pN)
        if os.path.exists(pO): dfO = pd.read_csv(pO)
        if dfN is not None and dfO is not None:
            break

    if dfN is None or dfO is None:
        st.error("Arquivos CSV não encontrados. Coloque os dois CSVs na raiz do repositório.")
        st.stop()

    dfN["Host"] = dfN["Host"].str.lower()
    for df in [dfN, dfO]:
        df["Creation Date"] = pd.to_datetime(df["Creation Date"], utc=True)
        df["valor_pago_num"] = df["Valor pago"].apply(clean_money)
        df["mes"] = df["Creation Date"].dt.to_period("M")

    meses_rec = ["2026-01","2026-02","2026-03"]

    aug_dec   = dfN[~dfN["mes"].astype(str).isin(meses_rec)].copy()
    aug_dec   = aug_dec.rename(columns={"Muriele": "Client Name"})

    jan_mar_m = dfO[dfO["mes"].astype(str).isin(meses_rec) & (dfO["Host"]=="mondaine")].copy()

    jan_mar_s = dfN[dfN["mes"].astype(str).isin(meses_rec) & (dfN["Host"]=="seculus")].copy()
    jan_mar_s = jan_mar_s.rename(columns={"Muriele": "Client Name"})

    df = pd.concat([aug_dec, jan_mar_m, jan_mar_s], ignore_index=True)
    df["Creation Date"] = df["Creation Date"].dt.tz_localize(None)
    df["data"]          = df["Creation Date"].dt.date
    df["parcelas_num"]  = pd.to_numeric(df["Parcelamento"], errors="coerce")
    return df

df_all = load_data()


# ─────────────────────────────────────────────
# CABEÇALHO
# ─────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:20px 0 6px">
  <span style="font-size:34px">🕐</span>
  <h1 style="color:#f1f5f9;font-size:30px;font-weight:700;margin:4px 0 2px">
    Dashboard de Vendas · Grupo Seculus
  </h1>
  <p style="color:#64748b;font-size:13px;margin:0">
    Análise comparativa de performance por marca e período
  </p>
</div>
<hr style="border-color:#2a3448;margin:14px 0 20px">
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SELEÇÃO DE PERÍODO — date_input interativo
# ─────────────────────────────────────────────
data_min = df_all["data"].min()
data_max = df_all["data"].max()

col_p1, col_vs, col_p2 = st.columns([5, 1, 5])

with col_p1:
    st.markdown('<p style="color:#64748b;font-size:12px;margin-bottom:2px">📅 Período atual</p>',
                unsafe_allow_html=True)
    ca, cb = st.columns(2)
    with ca:
        ini_atual = st.date_input("De",  value=date(2026, 3, 8),
                                  min_value=data_min, max_value=data_max,
                                  key="ini_a", label_visibility="collapsed")
    with cb:
        fim_atual = st.date_input("Até", value=data_max,
                                  min_value=data_min, max_value=data_max,
                                  key="fim_a", label_visibility="collapsed")

with col_vs:
    st.markdown('<p style="font-size:12px;margin-bottom:2px">&nbsp;</p>', unsafe_allow_html=True)
    st.markdown('<div style="text-align:center;padding:7px 0;font-size:13px;'
                'color:#64748b;font-weight:600">vs</div>', unsafe_allow_html=True)

with col_p2:
    st.markdown('<p style="color:#64748b;font-size:12px;margin-bottom:2px">📅 Período anterior</p>',
                unsafe_allow_html=True)
    pa, pb = st.columns(2)
    with pa:
        ini_ant = st.date_input("De ",  value=date(2026, 2, 5),
                                min_value=data_min, max_value=data_max,
                                key="ini_p", label_visibility="collapsed")
    with pb:
        fim_ant = st.date_input("Até ", value=date(2026, 3, 7),
                                min_value=data_min, max_value=data_max,
                                key="fim_p", label_visibility="collapsed")

st.markdown("<div style='margin-bottom:20px'></div>", unsafe_allow_html=True)

# Filtros de período
df_at   = df_all[(df_all["data"] >= ini_atual) & (df_all["data"] <= fim_atual)]
df_ant  = df_all[(df_all["data"] >= ini_ant)   & (df_all["data"] <= fim_ant)]
fat_at  = df_at[df_at["Status"]  == "Faturado"]
fat_ant = df_ant[df_ant["Status"] == "Faturado"]


# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab_visao, tab_marcas, tab_produtos, tab_pedidos = st.tabs([
    "📊 Visão Geral", "🏷️ Por Marca", "🏆 Produtos", "📦 Pedidos"
])


# ══════════════════════════════════════════════
# TAB 1 — VISÃO GERAL
# ══════════════════════════════════════════════
with tab_visao:

    # KPIs
    st.markdown('<div class="section-title">KPIs do Período</div>', unsafe_allow_html=True)

    rec_at  = fat_at["valor_pago_num"].sum()
    rec_ant = fat_ant["valor_pago_num"].sum()
    ped_at  = len(df_at)
    ped_ant = len(df_ant)
    nfat_at  = len(fat_at)
    nfat_ant = len(fat_ant)
    tx_at   = nfat_at  / ped_at  * 100 if ped_at  > 0 else 0
    tx_ant  = nfat_ant / ped_ant * 100 if ped_ant > 0 else 0
    tick_at  = fat_at["valor_pago_num"].mean()  if nfat_at  > 0 else 0
    tick_ant = fat_ant["valor_pago_num"].mean() if nfat_ant > 0 else 0

    k1, k2, k3, k4, k5 = st.columns(5)
    dados_kpi = [
        (k1, "💰", "Receita Total",        fmt_brl(rec_at),      delta_html(rec_at,   rec_ant)),
        (k2, "🧾", "Pedidos Realizados",   f"{ped_at:,}",         delta_html(ped_at,   ped_ant)),
        (k3, "✅", "Pedidos Faturados",    f"{nfat_at:,}",        delta_html(nfat_at,  nfat_ant)),
        (k4, "📈", "Taxa de Faturamento",  f"{tx_at:.1f}%",       delta_html(tx_at,    tx_ant)),
        (k5, "🎯", "Ticket Médio",         fmt_brl(tick_at),      delta_html(tick_at,  tick_ant)),
    ]
    for col, icon, lbl, val, dlt in dados_kpi:
        with col:
            st.markdown(kpi_card(icon, lbl, val, dlt), unsafe_allow_html=True)

    st.markdown("<div style='margin:24px 0 8px'></div>", unsafe_allow_html=True)

    # Resumo por marca (histórico completo)
    st.markdown('<div class="section-title">Resumo Geral — Ago/2025 a Mar/2026</div>',
                unsafe_allow_html=True)

    def stats(host, src):
        s = src[src["Host"] == host]
        f = s[s["Status"] == "Faturado"]
        c = s[s["Status"] == "Cancelado"]
        return dict(cli=s["Client Name"].nunique(), total=len(s),
                    fat=len(f), can=len(c),
                    tx=len(c)/len(s)*100 if len(s) > 0 else 0,
                    rec=f["valor_pago_num"].sum())

    bm = stats("mondaine", df_all)
    bs = stats("seculus",  df_all)

    bc1, bc2 = st.columns(2)
    with bc1: st.markdown(brand_card("mondaine", bm), unsafe_allow_html=True)
    with bc2: st.markdown(brand_card("seculus",  bs), unsafe_allow_html=True)

    st.markdown("<div style='margin:24px 0 8px'></div>", unsafe_allow_html=True)

    # Gráfico de linhas — receita mensal (curvas suaves)
    st.markdown('<div class="section-title">Receita Faturada Mensal — Mondaine vs Seculus</div>',
                unsafe_allow_html=True)

    monthly = (
        df_all[df_all["Status"] == "Faturado"]
        .groupby(["mes","Host"])["valor_pago_num"].sum()
        .reset_index()
    )
    monthly["mes_str"]   = monthly["mes"].astype(str)
    monthly["mes_label"] = pd.to_datetime(monthly["mes_str"]).dt.strftime("%b/%y")
    monthly = monthly.sort_values("mes_str")

    fig_line = go.Figure()
    for host, cor, nome in [
        ("mondaine", COR_MONDAINE, "Mondaine"),
        ("seculus",  COR_SECULUS,  "Seculus"),
    ]:
        d = monthly[monthly["Host"] == host]
        r, g, b = int(cor[1:3],16), int(cor[3:5],16), int(cor[5:7],16)
        fig_line.add_trace(go.Scatter(
            x=d["mes_label"], y=d["valor_pago_num"],
            name=nome, mode="lines+markers",
            line=dict(color=cor, width=2.5, shape="spline", smoothing=1.3),
            marker=dict(size=6, color=cor),
            fill="tozeroy",
            fillcolor=f"rgba({r},{g},{b},0.07)",
            hovertemplate=f"<b>{nome}</b><br>%{{x}}<br>R$ %{{y:,.0f}}<extra></extra>",
        ))

    fig_line.update_layout(
        **LAYOUT_PLOTLY, height=300,
        yaxis=dict(tickformat=",.0f",
                   gridcolor="rgba(255,255,255,0.06)",
                   linecolor="rgba(255,255,255,0.1)"),
    )
    st.plotly_chart(fig_line, use_container_width=True)

    # Gráfico de barras — volume mensal
    st.markdown('<div class="section-title">Volume de Itens Faturados por Mês</div>',
                unsafe_allow_html=True)

    monthly_v = (
        df_all[df_all["Status"] == "Faturado"]
        .groupby(["mes","Host"]).size()
        .reset_index(name="itens")
    )
    monthly_v["mes_str"]   = monthly_v["mes"].astype(str)
    monthly_v["mes_label"] = pd.to_datetime(monthly_v["mes_str"]).dt.strftime("%b/%y")
    monthly_v = monthly_v.sort_values("mes_str")

    fig_vol = go.Figure()
    for host, cor, nome in [
        ("mondaine", COR_MONDAINE, "Mondaine"),
        ("seculus",  COR_SECULUS,  "Seculus"),
    ]:
        d = monthly_v[monthly_v["Host"] == host]
        fig_vol.add_trace(go.Bar(
            x=d["mes_label"], y=d["itens"], name=nome,
            marker_color=cor,
            hovertemplate=f"<b>{nome}</b><br>%{{x}}<br>%{{y}} itens<extra></extra>",
        ))

    fig_vol.update_layout(
        **LAYOUT_PLOTLY, barmode="group", height=280,
        bargap=0.2, bargroupgap=0.05,
    )
    st.plotly_chart(fig_vol, use_container_width=True)

    # Comparativo período atual vs anterior
    st.markdown('<div class="section-title">Comparativo — Período Atual vs Anterior</div>',
                unsafe_allow_html=True)

    gc1, gc2 = st.columns(2)

    def receita_host(df_src, host):
        return df_src[df_src["Host"] == host]["valor_pago_num"].sum()

    def volume_host(df_src, host):
        return len(df_src[df_src["Host"] == host])

    with gc1:
        fig_cr = go.Figure()
        for label, src, opac in [("Atual", fat_at, 1.0), ("Anterior", fat_ant, 0.45)]:
            fig_cr.add_trace(go.Bar(
                x=["Mondaine", "Seculus"],
                y=[receita_host(src,"mondaine"), receita_host(src,"seculus")],
                name=label,
                marker_color=[COR_MONDAINE, COR_SECULUS],
                opacity=opac,
                hovertemplate="<b>%{x}</b> — " + label + "<br>R$ %{y:,.0f}<extra></extra>",
            ))
        fig_cr.update_layout(
            **LAYOUT_PLOTLY, barmode="group", height=260,
            title=dict(text="Receita faturada", font=dict(size=13)),
            yaxis=dict(tickformat=",.0f", gridcolor="rgba(255,255,255,0.06)"),
        )
        st.plotly_chart(fig_cr, use_container_width=True)

    with gc2:
        fig_cv = go.Figure()
        for label, src, opac in [("Atual", fat_at, 1.0), ("Anterior", fat_ant, 0.45)]:
            fig_cv.add_trace(go.Bar(
                x=["Mondaine", "Seculus"],
                y=[volume_host(src,"mondaine"), volume_host(src,"seculus")],
                name=label,
                marker_color=[COR_MONDAINE, COR_SECULUS],
                opacity=opac,
                hovertemplate="<b>%{x}</b> — " + label + "<br>%{y} itens<extra></extra>",
            ))
        fig_cv.update_layout(
            **LAYOUT_PLOTLY, barmode="group", height=260,
            title=dict(text="Volume de itens faturados", font=dict(size=13)),
            yaxis=dict(gridcolor="rgba(255,255,255,0.06)"),
        )
        st.plotly_chart(fig_cv, use_container_width=True)


# ══════════════════════════════════════════════
# TAB 2 — POR MARCA
# ══════════════════════════════════════════════
with tab_marcas:

    st.markdown('<div class="section-title">Desempenho por Marca — Período Atual</div>',
                unsafe_allow_html=True)

    for host, cor, nome in [("mondaine", COR_MONDAINE, "Mondaine"),
                             ("seculus",  COR_SECULUS,  "Seculus")]:
        st.markdown(
            f'<p style="color:{cor};font-weight:700;font-size:15px;margin:18px 0 8px">{nome}</p>',
            unsafe_allow_html=True)

        sub_at  = fat_at[fat_at["Host"]  == host]
        sub_ant = fat_ant[fat_ant["Host"] == host]

        rec  = sub_at["valor_pago_num"].sum()
        rec_a= sub_ant["valor_pago_num"].sum()
        vol  = len(sub_at)
        vol_a= len(sub_ant)
        tick = sub_at["valor_pago_num"].mean()  if vol   > 0 else 0
        tick_a=sub_ant["valor_pago_num"].mean() if vol_a > 0 else 0
        cli  = sub_at["Client Name"].nunique()

        m1,m2,m3,m4 = st.columns(4)
        with m1: st.markdown(kpi_card("💰","Receita",        fmt_brl(rec),  delta_html(rec,  rec_a)), unsafe_allow_html=True)
        with m2: st.markdown(kpi_card("📦","Volume",         f"{vol:,}",    delta_html(vol,  vol_a)), unsafe_allow_html=True)
        with m3: st.markdown(kpi_card("🎯","Ticket médio",   fmt_brl(tick), delta_html(tick, tick_a)), unsafe_allow_html=True)
        with m4: st.markdown(kpi_card("👤","Clientes únicos",f"{cli:,}",    ""),               unsafe_allow_html=True)

        st.markdown("<div style='margin-bottom:18px'></div>", unsafe_allow_html=True)

    # UF
    st.markdown('<div class="section-title">Receita por UF — Período Atual</div>',
                unsafe_allow_html=True)
    u1, u2 = st.columns(2)
    for col, host, cor, nome in [(u1,"mondaine",COR_MONDAINE,"Mondaine"),
                                  (u2,"seculus", COR_SECULUS, "Seculus")]:
        with col:
            d = (fat_at[fat_at["Host"]==host]
                 .groupby("UF")["valor_pago_num"].sum()
                 .nlargest(8).reset_index().sort_values("valor_pago_num"))
            fig = go.Figure(go.Bar(
                x=d["valor_pago_num"], y=d["UF"], orientation="h",
                marker_color=cor,
                hovertemplate="<b>%{y}</b><br>R$ %{x:,.0f}<extra></extra>",
            ))
            fig.update_layout(**LAYOUT_PLOTLY, height=300,
                title=dict(text=f"{nome} — Top UFs", font=dict(size=13)),
                xaxis=dict(tickformat=",.0f"),
                margin=dict(l=8, r=16, t=48, b=8))
            st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════
# TAB 3 — PRODUTOS
# ══════════════════════════════════════════════
with tab_produtos:

    st.markdown('<div class="section-title">Top 10 Produtos por Quantidade — Período Atual</div>',
                unsafe_allow_html=True)
    p1, p2 = st.columns(2)
    for col, host, cor, nome in [(p1,"mondaine",COR_MONDAINE,"Mondaine"),
                                  (p2,"seculus", COR_SECULUS, "Seculus")]:
        with col:
            d = (fat_at[fat_at["Host"]==host]
                 .groupby("SKU Name")
                 .agg(qtd=("SKU Name","count"), receita=("valor_pago_num","sum"))
                 .nlargest(10,"qtd").reset_index().sort_values("qtd"))
            d["label"] = d["SKU Name"].str[:38].str.strip()
            fig = go.Figure(go.Bar(
                x=d["qtd"], y=d["label"], orientation="h",
                marker_color=cor,
                text=d["qtd"], textposition="outside",
                customdata=d["receita"],
                hovertemplate="<b>%{y}</b><br>%{x} pedidos<br>R$ %{customdata:,.0f}<extra></extra>",
            ))
            fig.update_layout(**LAYOUT_PLOTLY, height=380,
                title=dict(text=f"{nome}", font=dict(size=13)),
                margin=dict(l=8, r=40, t=48, b=8))
            st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-title">Top 10 Produtos por Receita — Período Atual</div>',
                unsafe_allow_html=True)
    p3, p4 = st.columns(2)
    for col, host, cor, nome in [(p3,"mondaine",COR_MONDAINE,"Mondaine"),
                                  (p4,"seculus", COR_SECULUS, "Seculus")]:
        with col:
            d = (fat_at[fat_at["Host"]==host]
                 .groupby("SKU Name")
                 .agg(qtd=("SKU Name","count"), receita=("valor_pago_num","sum"))
                 .nlargest(10,"receita").reset_index().sort_values("receita"))
            d["label"] = d["SKU Name"].str[:38].str.strip()
            fig = go.Figure(go.Bar(
                x=d["receita"], y=d["label"], orientation="h",
                marker_color=cor,
                hovertemplate="<b>%{y}</b><br>R$ %{x:,.0f}<extra></extra>",
            ))
            fig.update_layout(**LAYOUT_PLOTLY, height=380,
                title=dict(text=f"{nome}", font=dict(size=13)),
                xaxis=dict(tickformat=",.0f"),
                margin=dict(l=8, r=16, t=48, b=8))
            st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════
# TAB 4 — PEDIDOS
# ══════════════════════════════════════════════
with tab_pedidos:

    st.markdown('<div class="section-title">Status dos Pedidos — Período Atual</div>',
                unsafe_allow_html=True)
    s1, s2 = st.columns(2)
    cores_status = {
        "Faturado": COR_SUCCESS, "Cancelado": COR_DANGER,
        "Preparando Entrega": COR_WARN, "Pronto para o manuseio": COR_MONDAINE,
    }
    for col, host, nome in [(s1,"mondaine","Mondaine"),(s2,"seculus","Seculus")]:
        with col:
            d = df_at[df_at["Host"]==host]["Status"].value_counts().reset_index()
            d.columns = ["Status","Qtd"]
            fig = go.Figure(go.Pie(
                labels=d["Status"], values=d["Qtd"], hole=0.55,
                marker_colors=[cores_status.get(s,"#94a3b8") for s in d["Status"]],
                textinfo="percent+label",
                hovertemplate="<b>%{label}</b><br>%{value}<br>%{percent}<extra></extra>",
            ))
            fig.update_layout(**LAYOUT_PLOTLY, height=280,
                title=dict(text=nome, font=dict(size=13)),
                showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-title">Forma de Pagamento — Período Atual</div>',
                unsafe_allow_html=True)
    f1, f2 = st.columns(2)
    for col, host, cor, nome in [(f1,"mondaine",COR_MONDAINE,"Mondaine"),
                                  (f2,"seculus", COR_SECULUS, "Seculus")]:
        with col:
            d = (fat_at[fat_at["Host"]==host]["Forma de pagamento"]
                 .str.split(",").explode().str.strip()
                 .value_counts().head(6).reset_index())
            d.columns = ["Pagamento","Qtd"]
            fig = go.Figure(go.Bar(
                x=d["Qtd"], y=d["Pagamento"], orientation="h",
                marker_color=cor,
                hovertemplate="<b>%{y}</b><br>%{x} transações<extra></extra>",
            ))
            fig.update_layout(**LAYOUT_PLOTLY, height=250,
                title=dict(text=f"{nome}", font=dict(size=13)),
                margin=dict(l=8, r=16, t=48, b=8))
            st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-title">Distribuição de Parcelamento — Período Atual</div>',
                unsafe_allow_html=True)
    pa1, pa2 = st.columns(2)
    for col, host, cor, nome in [(pa1,"mondaine",COR_MONDAINE,"Mondaine"),
                                  (pa2,"seculus", COR_SECULUS, "Seculus")]:
        with col:
            sub = fat_at[fat_at["Host"]==host]
            avg = sub["parcelas_num"].mean()
            d   = (sub["parcelas_num"].dropna().astype(int)
                   .value_counts().sort_index().reset_index())
            d.columns = ["Parcelas","Qtd"]
            fig = go.Figure(go.Bar(
                x=d["Parcelas"], y=d["Qtd"],
                marker_color=cor,
                hovertemplate="<b>%{x}x</b><br>%{y} compras<extra></extra>",
            ))
            fig.update_layout(**LAYOUT_PLOTLY, height=240,
                title=dict(text=f"{nome} — média {avg:.1f}x", font=dict(size=13)),
                xaxis=dict(tickmode="linear"))
            st.plotly_chart(fig, use_container_width=True)
