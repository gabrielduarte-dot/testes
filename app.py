import streamlit as st
import pandas as pd
import requests
from io import StringIO

# ─────────────────────────────
# CONFIG
# ─────────────────────────────
st.set_page_config(page_title="Dashboard", layout="wide")

# ─────────────────────────────
# STYLE
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
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────
# HELPERS
# ─────────────────────────────
@st.cache_data(ttl=300)
def load_csv(url):
    r = requests.get(url)
    df = pd.read_csv(StringIO(r.text))

    df.columns = (
        df.columns
        .str.lower()
        .str.strip()
        .str.replace(" ", "_")
    )
    return df


def get_col(df, possible_names):
    for name in possible_names:
        if name in df.columns:
            return name
    return None


# ─────────────────────────────
# HEADER
# ─────────────────────────────
st.title("Dashboard de Vendas")

# ─────────────────────────────
# INPUTS
# ─────────────────────────────
c1, c2 = st.columns(2)
url_ecom = c1.text_input("URL Ecommerce")
url_market = c2.text_input("URL Marketplace")

c3, c4 = st.columns(2)
data_ini = c3.date_input("Data início")
data_fim = c4.date_input("Data fim")

# ─────────────────────────────
# MODELO DAS PLANILHAS (AJUDA)
# ─────────────────────────────
with st.expander("📄 Modelo das planilhas esperadas", expanded=False):

    st.markdown("### 🛒 Ecommerce")

    df_model_ecom = pd.DataFrame({
        "order": ["12345"],
        "creation": ["2024-01-01"],
        "client name": ["João"],
        "uf": ["SP"],
        "status": ["Faturado"],
        "utmsource": ["google"],
        "coupon": ["DESC10"],
        "payment system name": ["credit card"],
        "installments": [1],
        "quantity_sku": [2],
        "id_sku": ["SKU123"],
        "reference code": ["REF1"],
        "sku name": ["Produto X"],
        "sku selling price": [100.0],
        "sku total price": [200.0],
        "discounts names": [""],
        "seller name": ["Marca A"],
        "marketingtags": [""]
    })

    st.dataframe(df_model_ecom, use_container_width=True)

    st.markdown("### 🏪 Marketplace")

    df_model_market = pd.DataFrame({
        "data do faturamento": ["2024-01-01"],
        "nota fiscal": ["NF123"],
        "quantidade faturada": [2],
        "valor unitário final": [150.0],
        "marketplace": ["Mercado Livre"]
    })

    st.dataframe(df_model_market, use_container_width=True)

    st.markdown("""
    ⚠️ **Regras importantes aplicadas automaticamente:**

    **Ecommerce**
    - Ignora pedidos com `marketingtags` preenchido (ex: Livelo)
    - Receita = `sku selling price × quantity_sku`
    - Agrupamento por `order`
    - UTM avaliado sem duplicidade

    **Marketplace**
    - Ignora: Site Mondaine, Site Seculus, Site Timex
    - Receita = `valor unitário final × quantidade faturada`
    - Baseado em Nota Fiscal
    """)

if not url_ecom or not url_market:
    st.stop()

# ─────────────────────────────
# LOAD
# ─────────────────────────────
df_ecom = load_csv(url_ecom)
df_market = load_csv(url_market)

# ─────────────────────────────
# ECOMMERCE
# ─────────────────────────────
col_price = get_col(df_ecom, ["sku_selling_price"])
col_qty   = get_col(df_ecom, ["quantity_sku"])
col_tag   = get_col(df_ecom, ["marketingtags"])
col_order = get_col(df_ecom, ["order"])
col_utm   = get_col(df_ecom, ["utmsource"])
col_brand = get_col(df_ecom, ["seller_name"])
col_date  = get_col(df_ecom, ["creation"])

if not col_price or not col_qty or not col_order or not col_date:
    st.error("Erro: colunas obrigatórias do Ecommerce não encontradas")
    st.stop()

# data
df_ecom[col_date] = pd.to_datetime(df_ecom[col_date], errors="coerce")
df_ecom = df_ecom[
    (df_ecom[col_date].dt.date >= data_ini) &
    (df_ecom[col_date].dt.date <= data_fim)
]

# remover Livelo
if col_tag:
    df_ecom = df_ecom[df_ecom[col_tag].fillna("") == ""]

# receita
df_ecom["receita"] = df_ecom[col_price] * df_ecom[col_qty]

# agrupar por pedido
agg_dict = {"receita": "sum"}
if col_utm: agg_dict[col_utm] = "first"
if col_brand: agg_dict[col_brand] = "first"

df_ecom_group = df_ecom.groupby(col_order).agg(agg_dict).reset_index()

# ─────────────────────────────
# MARKETPLACE
# ─────────────────────────────
col_price_m = get_col(df_market, ["valor_unitario_final"])
col_qty_m   = get_col(df_market, ["quantidade_faturada"])
col_nf      = get_col(df_market, ["nota_fiscal"])
col_mkt     = get_col(df_market, ["marketplace"])
col_date_m  = get_col(df_market, ["data_do_faturamento"])

if not col_price_m or not col_qty_m or not col_date_m:
    st.error("Erro: colunas obrigatórias do Marketplace não encontradas")
    st.stop()

# filtro canais
if col_mkt:
    df_market = df_market[~df_market[col_mkt].isin([
        "Site Mondaine",
        "Site Seculus",
        "Site Timex"
    ])]

# data
df_market[col_date_m] = pd.to_datetime(df_market[col_date_m], errors="coerce")
df_market = df_market[
    (df_market[col_date_m].dt.date >= data_ini) &
    (df_market[col_date_m].dt.date <= data_fim)
]

# receita
df_market["receita"] = df_market[col_price_m] * df_market[col_qty_m]

# ─────────────────────────────
# KPIs
# ─────────────────────────────
receita_ecom = df_ecom_group["receita"].sum()
receita_market = df_market["receita"].sum()
receita_total = receita_ecom + receita_market

pedidos_ecom = df_ecom_group[col_order].nunique()
nf_market = df_market[col_nf].nunique() if col_nf else 0

# ─────────────────────────────
# CARDS
# ─────────────────────────────
k1, k2, k3, k4 = st.columns(4)

k1.markdown(f"<div class='kpi'><h4>Receita Total</h4><h2>R$ {receita_total:,.0f}</h2></div>", unsafe_allow_html=True)
k2.markdown(f"<div class='kpi'><h4>Ecommerce</h4><h2>R$ {receita_ecom:,.0f}</h2></div>", unsafe_allow_html=True)
k3.markdown(f"<div class='kpi'><h4>Marketplace</h4><h2>R$ {receita_market:,.0f}</h2></div>", unsafe_allow_html=True)
k4.markdown(f"<div class='kpi'><h4>Pedidos / NF</h4><h2>{pedidos_ecom} / {nf_market}</h2></div>", unsafe_allow_html=True)

st.markdown("---")

# ─────────────────────────────
# TABS
# ─────────────────────────────
tab1, tab2, tab3 = st.tabs(["Overview", "Ecommerce", "Marketplace"])

# ─────────────────────────────
# OVERVIEW
# ─────────────────────────────
with tab1:
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

    if col_utm:
        utm = df_ecom_group.groupby(col_utm)[col_order].nunique().reset_index()
        utm = utm.sort_values(col_order, ascending=False)
        st.dataframe(utm)

    if col_brand:
        st.subheader("Receita por Marca")
        marca = df_ecom_group.groupby(col_brand)["receita"].sum().reset_index()
        marca = marca.sort_values("receita", ascending=False)
        st.bar_chart(marca.set_index(col_brand))

# ─────────────────────────────
# MARKETPLACE
# ─────────────────────────────
with tab3:
    if col_mkt:
        st.subheader("Receita por Plataforma")
        plat = df_market.groupby(col_mkt)["receita"].sum().reset_index()
        plat = plat.sort_values("receita", ascending=False)
        st.bar_chart(plat.set_index(col_mkt))

    st.subheader("Detalhado")
    st.dataframe(df_market)
