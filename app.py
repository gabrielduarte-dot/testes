import streamlit as st
import pandas as pd
import requests
from io import StringIO
from datetime import datetime

# ─────────────────────────────
# CONFIG
# ─────────────────────────────
st.set_page_config(
    page_title="Dashboard",
    layout="wide"
)

# ─────────────────────────────
# STYLE (igual à imagem)
# ─────────────────────────────
st.markdown("""
<style>
body {background-color:#0f1117;color:#fff;}
.block-container {padding-top:2rem;}

.kpi {
    background:#151922;
    border:1px solid #2a2f3e;
    border-radius:14px;
    padding:20px;
}

.kpi h4 {
    color:#8896b3;
    font-size:0.8rem;
    margin-bottom:5px;
}

.kpi h2 {
    margin:0;
    font-size:1.8rem;
}

.nav {
    display:flex;
    gap:20px;
    font-size:0.9rem;
    color:#8896b3;
    margin-bottom:20px;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────
# FUNÇÃO LOAD
# ─────────────────────────────
@st.cache_data(ttl=300)
def load_csv(url):
    r = requests.get(url)
    df = pd.read_csv(StringIO(r.text))
    df.columns = df.columns.str.lower().str.strip()
    return df

# ─────────────────────────────
# HEADER
# ─────────────────────────────
st.title("Dashboard")

# ─────────────────────────────
# INPUTS
# ─────────────────────────────
col1, col2 = st.columns(2)

url_ecom = col1.text_input("URL Ecommerce")
url_market = col2.text_input("URL Marketplace")

# filtro de data
col3, col4 = st.columns(2)
data_ini = col3.date_input("Data início")
data_fim = col4.date_input("Data fim")

# ─────────────────────────────
# LOAD DATA
# ─────────────────────────────
if not url_ecom or not url_market:
    st.stop()

df_ecom = load_csv(url_ecom)
df_market = load_csv(url_market)

# ─────────────────────────────
# TRATAMENTO ECOMMERCE
# ─────────────────────────────

df_ecom = df_ecom[df_ecom["marketingtags"].fillna("") == ""]

df_ecom["creation"] = pd.to_datetime(df_ecom["creation"], errors="coerce")

df_ecom = df_ecom[
    (df_ecom["creation"].dt.date >= data_ini) &
    (df_ecom["creation"].dt.date <= data_fim)
]

df_ecom["receita"] = (
    df_ecom["sku selling price"] *
    df_ecom["quantity_sku"]
)

# agrupar por pedido
df_ecom_group = df_ecom.groupby("order").agg({
    "receita": "sum",
    "utmsource": "first",
    "seller name": "first"
}).reset_index()

# ─────────────────────────────
# TRATAMENTO MARKETPLACE
# ─────────────────────────────

df_market = df_market[~df_market["marketplace"].isin([
    "Site Mondaine",
    "Site Seculus",
    "Site Timex"
])]

df_market["data do faturamento"] = pd.to_datetime(
    df_market["data do faturamento"],
    errors="coerce"
)

df_market = df_market[
    (df_market["data do faturamento"].dt.date >= data_ini) &
    (df_market["data do faturamento"].dt.date <= data_fim)
]

df_market["receita"] = (
    df_market["valor unitário final"] *
    df_market["quantidade faturada"]
)

# ─────────────────────────────
# KPIs
# ─────────────────────────────
receita_ecom = df_ecom_group["receita"].sum()
receita_market = df_market["receita"].sum()
receita_total = receita_ecom + receita_market

pedidos_ecom = df_ecom_group["order"].nunique()
nf_market = df_market["nota fiscal"].nunique()

# ─────────────────────────────
# CARDS
# ─────────────────────────────
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="kpi">
        <h4>Receita Total</h4>
        <h2>R$ {receita_total:,.0f}</h2>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="kpi">
        <h4>Ecommerce</h4>
        <h2>R$ {receita_ecom:,.0f}</h2>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="kpi">
        <h4>Marketplace</h4>
        <h2>R$ {receita_market:,.0f}</h2>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="kpi">
        <h4>Pedidos / NF</h4>
        <h2>{pedidos_ecom} / {nf_market}</h2>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ─────────────────────────────
# TABS
# ─────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "Overview",
    "Ecommerce",
    "Marketplace"
])

# ─────────────────────────────
# OVERVIEW
# ─────────────────────────────
with tab1:
    st.subheader("Receita por origem")

    df_over = pd.DataFrame({
        "Fonte": ["Ecommerce", "Marketplace"],
        "Receita": [receita_ecom, receita_market]
    })

    st.bar_chart(df_over.set_index("Fonte"))

# ─────────────────────────────
# ECOMMERCE
# ─────────────────────────────
with tab2:
    st.subheader("UTM Source")

    utm = df_ecom_group.groupby("utmsource")["order"].nunique().reset_index()
    utm = utm.sort_values("order", ascending=False)

    st.dataframe(utm)

    st.subheader("Receita por Marca")

    marca = df_ecom_group.groupby("seller name")["receita"].sum().reset_index()
    marca = marca.sort_values("receita", ascending=False)

    st.bar_chart(marca.set_index("seller name"))

# ─────────────────────────────
# MARKETPLACE
# ─────────────────────────────
with tab3:
    st.subheader("Receita por Plataforma")

    plat = df_market.groupby("marketplace")["receita"].sum().reset_index()
    plat = plat.sort_values("receita", ascending=False)

    st.bar_chart(plat.set_index("marketplace"))

    st.subheader("Detalhado")
    st.dataframe(df_market)
