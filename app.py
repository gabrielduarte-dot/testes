import unicodedata
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
def normalize_str(s):
    """Remove acentos, lowercase, strip, substitui espaços por _"""
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.lower().strip().replace(" ", "_")


def convert_gsheets_url(url: str) -> str:
    """
    Converte qualquer URL do Google Sheets para o link de exportação CSV.
    Aceita:
      - /edit, /view, /preview  → troca por /export?format=csv
      - URL já com /export       → mantém
      - Outras URLs              → retorna sem alteração
    Preserva o parâmetro gid (aba) se presente.
    """
    import re
    if "docs.google.com/spreadsheets" not in url:
        return url

    # extrai sheet id
    m = re.search(r"/spreadsheets/d/([a-zA-Z0-9_-]+)", url)
    if not m:
        return url
    sheet_id = m.group(1)

    # extrai gid (aba) se houver
    gid_match = re.search(r"[#&?]gid=(\d+)", url)
    gid = gid_match.group(1) if gid_match else "0"

    return (
        f"https://docs.google.com/spreadsheets/d/{sheet_id}"
        f"/export?format=csv&gid={gid}"
    )


@st.cache_data(ttl=300)
def load_csv(url):
    url = convert_gsheets_url(url)
    r = requests.get(url, allow_redirects=True)

    if r.status_code != 200:
        raise ValueError(f"Erro HTTP {r.status_code} ao acessar: {url}")

    # tenta detectar encoding; fallback para latin-1 (comum em CSVs BR)
    try:
        text = r.content.decode("utf-8")
    except UnicodeDecodeError:
        text = r.content.decode("latin-1")

    df = pd.read_csv(StringIO(text))

    # normaliza colunas: lowercase + sem acento + espaço → _
    df.columns = [normalize_str(c) for c in df.columns]
    return df


def get_col(df, possible_names):
    """Busca coluna pelo nome já normalizado (sem acento, com _)"""
    for name in possible_names:
        norm = normalize_str(name)
        if norm in df.columns:
            return norm
    return None


def to_numeric_br(series):
    """Converte coluna que pode ter vírgula como separador decimal"""
    if series.dtype == object:
        series = series.str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
    return pd.to_numeric(series, errors="coerce")


# ─────────────────────────────
# HEADER
# ─────────────────────────────
st.title("Dashboard de Vendas")

# ─────────────────────────────
# INPUTS
# ─────────────────────────────
c1, c2 = st.columns(2)
url_ecom   = c1.text_input("URL Ecommerce")
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
try:
    df_ecom = load_csv(url_ecom)
except Exception as e:
    st.error(f"Erro ao carregar Ecommerce: {e}")
    st.stop()

try:
    df_market = load_csv(url_market)
except Exception as e:
    st.error(f"Erro ao carregar Marketplace: {e}")
    st.stop()

# ─────────────────────────────
# DEBUG (remova quando estiver ok)
# ─────────────────────────────
with st.expander("🔍 Debug — colunas detectadas", expanded=False):
    st.write("**Ecommerce:**", list(df_ecom.columns))
    st.write("**Marketplace:**", list(df_market.columns))

# ─────────────────────────────
# ECOMMERCE — mapeamento de colunas
# ─────────────────────────────
# Aceita variações comuns de nome
col_price = get_col(df_ecom, ["sku_selling_price", "sku selling price", "selling_price", "preco_venda"])
col_qty   = get_col(df_ecom, ["quantity_sku", "quantidade_sku", "qty_sku", "quantidade"])
col_tag   = get_col(df_ecom, ["marketingtags", "marketing_tags", "tags"])
col_order = get_col(df_ecom, ["order", "pedido", "order_id", "id_pedido"])
col_utm   = get_col(df_ecom, ["utmsource", "utm_source", "utm source"])
col_brand = get_col(df_ecom, ["seller_name", "seller name", "marca", "brand"])
col_date  = get_col(df_ecom, ["creation", "created_at", "data_criacao", "data_pedido", "date"])

missing_ecom = [n for n, v in {
    "sku_selling_price": col_price,
    "quantity_sku": col_qty,
    "order": col_order,
    "creation": col_date
}.items() if v is None]

if missing_ecom:
    st.error(f"Ecommerce — colunas não encontradas: {missing_ecom}")
    st.write("Colunas disponíveis:", list(df_ecom.columns))
    st.stop()

# data
df_ecom[col_date] = pd.to_datetime(df_ecom[col_date], dayfirst=True, errors="coerce")
df_ecom = df_ecom[
    (df_ecom[col_date].dt.date >= data_ini) &
    (df_ecom[col_date].dt.date <= data_fim)
]

# remover Livelo / marketingtags preenchido
if col_tag:
    df_ecom = df_ecom[df_ecom[col_tag].fillna("").astype(str).str.strip() == ""]

# converter para numérico (suporte a formato BR com vírgula)
df_ecom[col_price] = to_numeric_br(df_ecom[col_price])
df_ecom[col_qty]   = to_numeric_br(df_ecom[col_qty])

# receita por linha
df_ecom["receita"] = df_ecom[col_price] * df_ecom[col_qty]

# agrupar por pedido
agg_dict = {"receita": "sum"}
if col_utm:   agg_dict[col_utm]   = "first"
if col_brand: agg_dict[col_brand] = "first"

df_ecom_group = df_ecom.groupby(col_order).agg(agg_dict).reset_index()

# ─────────────────────────────
# MARKETPLACE — mapeamento de colunas
# ─────────────────────────────
col_price_m = get_col(df_market, ["valor_unitario_final", "valor unitário final", "valor_unitario", "preco_unitario"])
col_qty_m   = get_col(df_market, ["quantidade_faturada", "quantidade faturada", "quantidade", "qty"])
col_nf      = get_col(df_market, ["nota_fiscal", "nota fiscal", "nf", "invoice"])
col_mkt     = get_col(df_market, ["marketplace", "canal", "plataforma"])
col_date_m  = get_col(df_market, ["data_do_faturamento", "data do faturamento", "data_faturamento", "data"])

missing_mkt = [n for n, v in {
    "valor_unitario_final": col_price_m,
    "quantidade_faturada": col_qty_m,
    "data_do_faturamento": col_date_m
}.items() if v is None]

if missing_mkt:
    st.error(f"Marketplace — colunas não encontradas: {missing_mkt}")
    st.write("Colunas disponíveis:", list(df_market.columns))
    st.stop()

# filtro canais internos
if col_mkt:
    df_market = df_market[~df_market[col_mkt].isin([
        "Site Mondaine", "Site Seculus", "Site Timex"
    ])]

# data
df_market[col_date_m] = pd.to_datetime(df_market[col_date_m], dayfirst=True, errors="coerce")
df_market = df_market[
    (df_market[col_date_m].dt.date >= data_ini) &
    (df_market[col_date_m].dt.date <= data_fim)
]

# converter para numérico
df_market[col_price_m] = to_numeric_br(df_market[col_price_m])
df_market[col_qty_m]   = to_numeric_br(df_market[col_qty_m])

# receita
df_market["receita"] = df_market[col_price_m] * df_market[col_qty_m]

# ─────────────────────────────
# KPIs
# ─────────────────────────────
receita_ecom   = df_ecom_group["receita"].sum()
receita_market = df_market["receita"].sum()
receita_total  = receita_ecom + receita_market

pedidos_ecom = df_ecom_group[col_order].nunique()
nf_market    = df_market[col_nf].nunique() if col_nf else 0

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

with tab1:
    df_over = pd.DataFrame({
        "Fonte": ["Ecommerce", "Marketplace"],
        "Receita": [receita_ecom, receita_market]
    })
    st.bar_chart(df_over.set_index("Fonte"))

with tab2:
    if col_utm:
        st.subheader("UTM Source")
        utm = df_ecom_group.groupby(col_utm)[col_order].nunique().reset_index()
        utm.columns = ["UTM Source", "Pedidos"]
        utm = utm.sort_values("Pedidos", ascending=False)
        st.dataframe(utm, use_container_width=True)

    if col_brand:
        st.subheader("Receita por Marca")
        marca = df_ecom_group.groupby(col_brand)["receita"].sum().reset_index()
        marca = marca.sort_values("receita", ascending=False)
        st.bar_chart(marca.set_index(col_brand))

with tab3:
    if col_mkt:
        st.subheader("Receita por Plataforma")
        plat = df_market.groupby(col_mkt)["receita"].sum().reset_index()
        plat = plat.sort_values("receita", ascending=False)
        st.bar_chart(plat.set_index(col_mkt))

    st.subheader("Detalhado")
    st.dataframe(df_market, use_container_width=True)
