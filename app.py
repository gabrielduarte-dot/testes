import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# ─────────────────────────────────────────────
# PÁGINA
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard de Vendas · Grupo Seculus",
    page_icon="⌚",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
# ESTILOS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');
html,body,[class*="css"]{font-family:'DM Sans',sans-serif;}
.stApp{background-color:#0f1117;color:#e8e8e8;}
[data-testid="stSidebar"]{background-color:#161b27;border-right:1px solid #2a2f3e;}
[data-testid="stMetric"]{background:linear-gradient(135deg,#1a2035 0%,#1e2640 100%);border:1px solid #2a3350;border-radius:12px;padding:18px 22px;transition:border-color .2s;}
[data-testid="stMetric"]:hover{border-color:#4a7cff;}
[data-testid="stMetricLabel"]{color:#8896b3!important;font-size:.78rem!important;font-weight:500!important;text-transform:uppercase;letter-spacing:.08em;}
[data-testid="stMetricValue"]{color:#fff!important;font-size:1.6rem!important;font-weight:700!important;font-family:'DM Mono',monospace!important;}
[data-testid="stMetricDelta"]{font-size:.82rem!important;}
h1,h2,h3{color:#fff!important;}
h1{font-weight:700!important;letter-spacing:-.02em;}
h3{font-size:1rem!important;font-weight:600!important;color:#a0aec0!important;text-transform:uppercase;letter-spacing:.06em;}
hr{border-color:#2a2f3e!important;}
[data-testid="stDataFrame"]{border:1px solid #2a3350;border-radius:10px;overflow:hidden;}
.insight-box{background:linear-gradient(135deg,#1a2640 0%,#1e2e50 100%);border-left:3px solid #4a7cff;border-radius:0 10px 10px 0;padding:14px 18px;margin:10px 0;font-size:.9rem;color:#c8d8f0;}
.alert-box{background:linear-gradient(135deg,#2a1020 0%,#3a1428 100%);border-left:3px solid #f43f5e;border-radius:0 10px 10px 0;padding:14px 18px;margin:6px 0;font-size:.88rem;color:#fca5a5;}
.warn-box{background:linear-gradient(135deg,#2a2010 0%,#3a2a08 100%);border-left:3px solid #f59e0b;border-radius:0 10px 10px 0;padding:14px 18px;margin:6px 0;font-size:.88rem;color:#fde68a;}
.resumo-card{background:linear-gradient(135deg,#161d30 0%,#1a2240 100%);border:1px solid #2a3350;border-radius:14px;padding:20px 24px;margin-bottom:10px;}
.resumo-card h4{font-size:1rem!important;font-weight:700!important;text-transform:uppercase!important;letter-spacing:.08em!important;margin:0 0 14px 0!important;}
.resumo-linha{display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid #1e2640;font-size:.85rem;color:#a0aec0;}
.resumo-linha:last-child{border-bottom:none;}
.resumo-valor{font-family:'DM Mono',monospace;color:#fff;font-weight:600;}
.badge-verde{background:#0d2e1e;color:#10b981;padding:2px 8px;border-radius:6px;font-size:.8rem;font-weight:600;}
.badge-vermelho{background:#2e0d14;color:#f43f5e;padding:2px 8px;border-radius:6px;font-size:.8rem;font-weight:600;}
.badge-amarelo{background:#2e200d;color:#f59e0b;padding:2px 8px;border-radius:6px;font-size:.8rem;font-weight:600;}
.bq-status{background:linear-gradient(135deg,#0d1e12 0%,#102016 100%);border:1px solid #1a4028;border-radius:10px;padding:12px 16px;margin:8px 0;font-size:.8rem;font-family:'DM Mono',monospace;}
.filtro-inline{background:#161b27;border:1px solid #2a3350;border-radius:10px;padding:12px 16px;margin-bottom:16px;}
[data-baseweb="tab-list"]{background-color:#161b27!important;border-bottom:1px solid #2a3350!important;gap:4px;}
[data-baseweb="tab"]{color:#8896b3!important;font-weight:500!important;}
[aria-selected="true"]{color:#fff!important;border-bottom:2px solid #4a7cff!important;}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CONSTANTES
# ─────────────────────────────────────────────
COR_MARCAS = {
    "Seculus":  "#4a7cff",   # azul
    "Mondaine": "#f59e0b",   # âmbar
    "Timex":    "#10b981",   # verde
    "E-time":   "#f43f5e",   # vermelho
    "Time":     "#a78bfa",   # roxo (fallback legado)
}

CORES_CANAL = {
    "Google Ads":          "#4a7cff",
    "Meta Ads":            "#f59e0b",
    "Orgânico":            "#10b981",
    "E-mail":              "#8b5cf6",
    "Influencer/Parceiro": "#f43f5e",
    "Outros":              "#6b7a99",
}

STATUS_FATURADO  = {"faturado","entregue","concluído","concluido","aprovado",
                    "complete","completed","paid","pago","invoiced"}
STATUS_CANCELADO = {"cancelado","cancelada","devolvido","devolvida",
                    "canceled","cancelled","returned"}

# ─────────────────────────────────────────────
# LAYOUT PLOTLY
# ─────────────────────────────────────────────
_BASE_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#a0aec0", family="DM Sans"),
    title_font=dict(color="#ffffff", size=14, family="DM Sans"),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#a0aec0")),
    xaxis=dict(gridcolor="#1e2640", linecolor="#2a3350", tickcolor="#2a3350"),
    margin=dict(l=20, r=20, t=50, b=20),
)
_YAXIS_BASE = dict(gridcolor="#1e2640", linecolor="#2a3350", tickcolor="#2a3350")

def layout_normal(**extra):
    d = {**_BASE_LAYOUT, "yaxis": dict(_YAXIS_BASE)}
    d.update(extra)
    return d

def layout_invertido(**extra):
    d = {**_BASE_LAYOUT, "yaxis": dict(_YAXIS_BASE, autorange="reversed")}
    d.update(extra)
    return d

# ─────────────────────────────────────────────
# BIGQUERY
# ─────────────────────────────────────────────

@st.cache_resource
def get_bq_client():
    try:
        from google.cloud import bigquery
        from google.oauth2 import service_account
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )
        return bigquery.Client(
            credentials=credentials,
            project=st.secrets["bigquery"]["project"],
        )
    except Exception as e:
        st.error(f"❌ Falha ao conectar ao BigQuery: {e}")
        return None


@st.cache_data(ttl=300, show_spinner="Consultando BigQuery...")
def carregar_dados_bq(data_inicio_str: str, data_fim_str: str) -> tuple[pd.DataFrame, str]:
    """
    Consulta a view vw_vendas_dashboard (já filtrada: sem sites próprios, sem Livelo).

    Schema da view unificada:
        id_pedido, data, marca, sku, produto, quantidade_vendida,
        valor_unitario, valor_total, status_pedido, origem_cliente,
        campanha, marketing_tags, canal_origem ('ecommerce' | 'marketplace')
    """
    from google.cloud import bigquery

    client = get_bq_client()
    if client is None:
        return pd.DataFrame(), ""

    project = st.secrets["bigquery"]["project"]
    dataset = st.secrets["bigquery"]["dataset"]
    table   = st.secrets["bigquery"]["table"]

    query = f"""
        SELECT
            CAST(id_pedido AS STRING)                AS id_pedido,
            data,
            COALESCE(marca, 'Não identificado')      AS marca,
            COALESCE(sku, '')                        AS sku,
            COALESCE(produto, '')                    AS produto,
            COALESCE(quantidade_vendida, 1)          AS quantidade_vendida,
            COALESCE(valor_unitario, 0.0)            AS valor_unitario,
            COALESCE(valor_total, 0.0)               AS valor_total,
            LOWER(TRIM(status_pedido))               AS status_pedido,
            COALESCE(origem_cliente, '')             AS origem_cliente,
            COALESCE(campanha, '')                   AS campanha,
            COALESCE(marketing_tags, '')             AS marketing_tags,
            canal_origem
        FROM `{project}.{dataset}.{table}`
        WHERE data BETWEEN @data_inicio AND @data_fim
        ORDER BY data DESC
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("data_inicio", "DATE", data_inicio_str),
            bigquery.ScalarQueryParameter("data_fim",    "DATE", data_fim_str),
        ]
    )
    try:
        df = client.query(query, job_config=job_config).to_dataframe()
        ts = datetime.now().strftime("%d/%m/%Y %H:%M")
        if df.empty:
            return df, ts
        df = preparar_df(df)
        return df, ts
    except Exception as e:
        st.error(f"❌ Erro na consulta BigQuery: {e}")
        return pd.DataFrame(), ""


# ─────────────────────────────────────────────
# PREPARAÇÃO DO DATAFRAME
# ─────────────────────────────────────────────

def classificar_tipo_canal(origem: str) -> str:
    o = str(origem).lower().strip()
    if any(w in o for w in ["google","gads","adwords","cpc","ppc","search"]):
        return "Google Ads"
    if any(w in o for w in ["meta","facebook","instagram","fb","ig"]):
        return "Meta Ads"
    if any(w in o for w in ["orgânico","organico","organic","seo","direct","direto"]):
        return "Orgânico"
    if any(w in o for w in ["email","e-mail","newsletter"]):
        return "E-mail"
    if any(w in o for w in ["influencer","influenciador","parceiro"]):
        return "Influencer/Parceiro"
    return "Outros"


def preparar_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["data"] = pd.to_datetime(df["data"], errors="coerce")
    df.dropna(subset=["data"], inplace=True)

    for col in ["valor_total","quantidade_vendida","valor_unitario"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    if "valor_unitario" in df.columns and "quantidade_vendida" in df.columns:
        mask = (df["valor_total"] == 0) & (df["valor_unitario"] > 0)
        df.loc[mask, "valor_total"] = df.loc[mask, "valor_unitario"] * df.loc[mask, "quantidade_vendida"]

    df["status_pedido"] = df["status_pedido"].astype(str).str.strip().str.lower()
    df["faturado"]  = df["status_pedido"].isin(STATUS_FATURADO)
    df["cancelado"] = df["status_pedido"].isin(STATUS_CANCELADO)
    df["pendente"]  = ~df["faturado"] & ~df["cancelado"]

    if "id_pedido" not in df.columns:
        df["id_pedido"] = df.index.astype(str)
    else:
        df["id_pedido"] = df["id_pedido"].astype(str).str.strip()

    if "origem_cliente" in df.columns:
        df["tipo_canal"] = df["origem_cliente"].apply(classificar_tipo_canal)
        df["canal"]      = df["tipo_canal"]
    else:
        df["tipo_canal"] = "Outros"
        df["canal"]      = "Outros"

    if "campanha" in df.columns:
        df["campanha"] = df["campanha"].astype(str).str.strip().str.title()
        df["campanha"] = df["campanha"].replace("", "Não informado")

    if "marca" not in df.columns:
        df["marca"] = "Não identificado"

    if "canal_origem" not in df.columns:
        df["canal_origem"] = "ecommerce"

    df["mes"] = df["data"].dt.to_period("M").astype(str)
    return df

# ─────────────────────────────────────────────
# UTILITÁRIOS
# ─────────────────────────────────────────────

def calcular_variacao(atual, anterior):
    if not anterior or anterior == 0:
        return None
    return ((atual - anterior) / anterior) * 100

def formatar_variacao(val):
    return f"{val:+.1f}%" if val is not None else None

def calcular_periodo_anterior(inicio, fim, modo: str):
    n_dias = (fim - inicio).days
    if modo == "Período anterior equivalente":
        fim_ant    = inicio - timedelta(days=1)
        inicio_ant = fim_ant - timedelta(days=n_dias)
        return inicio_ant, fim_ant
    if modo == "Mês anterior":
        primeiro_atual = inicio.replace(day=1)
        fim_ant        = primeiro_atual - timedelta(days=1)
        inicio_ant     = fim_ant.replace(day=1)
        return inicio_ant, fim_ant
    if modo == "Mesmo período ano anterior":
        try:
            return inicio.replace(year=inicio.year - 1), fim.replace(year=fim.year - 1)
        except ValueError:
            return inicio - timedelta(days=365), fim - timedelta(days=365)
    return inicio, fim

def badge_taxa(valor: float, limiar_bom: float = 5.0, limiar_medio: float = 15.0) -> str:
    if valor <= limiar_bom:
        return f"<span class='badge-verde'>{valor:.1f}%</span>"
    if valor <= limiar_medio:
        return f"<span class='badge-amarelo'>{valor:.1f}%</span>"
    return f"<span class='badge-vermelho'>{valor:.1f}%</span>"

def hex_to_rgba(hex_color: str, alpha: float = 0.1) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
    return f"rgba({r},{g},{b},{alpha})"

def cor_marca(marca: str) -> str:
    return COR_MARCAS.get(marca, "#6b7a99")

def aplicar_filtros(df: pd.DataFrame, marcas_sel, canais_sel, origens_sel) -> pd.DataFrame:
    if df.empty:
        return df
    if marcas_sel and "marca" in df.columns:
        df = df[df["marca"].isin(marcas_sel)]
    if canais_sel and "canal" in df.columns:
        df = df[df["canal"].isin(canais_sel)]
    if origens_sel and "canal_origem" in df.columns:
        df = df[df["canal_origem"].isin(origens_sel)]
    return df

# ─────────────────────────────────────────────
# MÉTRICAS DE PEDIDOS
# ─────────────────────────────────────────────

def calcular_metricas_pedidos(df: pd.DataFrame) -> dict:
    _vazio = {
        "pedidos":0,"faturados":0,"cancelados":0,"pendentes":0,
        "itens":0,"itens_fat":0,"receita":0.0,"ticket_medio":0.0,
    }
    if df.empty or "faturado" not in df.columns or "cancelado" not in df.columns:
        return _vazio

    agg = df.groupby("id_pedido", sort=False).agg(
        tem_faturado  =("faturado",  "any"),
        tem_cancelado =("cancelado", "any"),
        receita_pedido=("valor_total","sum"),
    )
    agg["status_ped"] = "pendente"
    agg.loc[agg["tem_cancelado"] & ~agg["tem_faturado"], "status_ped"] = "cancelado"
    agg.loc[agg["tem_faturado"], "status_ped"] = "faturado"

    fat_mask   = agg["status_ped"] == "faturado"
    pedidos    = len(agg)
    faturados  = int(fat_mask.sum())
    cancelados = int((agg["status_ped"] == "cancelado").sum())
    pendentes  = int((agg["status_ped"] == "pendente").sum())
    receita    = float(agg.loc[fat_mask,"receita_pedido"].sum())
    ticket     = float(agg.loc[fat_mask,"receita_pedido"].mean()) if faturados > 0 else 0.0
    qtd_col    = "quantidade_vendida" if "quantidade_vendida" in df.columns else None
    itens      = int(df[qtd_col].sum()) if qtd_col else len(df)
    itens_fat  = int(df.loc[df["faturado"], qtd_col].sum()) if qtd_col else faturados

    return {
        "pedidos":pedidos,"faturados":faturados,"cancelados":cancelados,"pendentes":pendentes,
        "itens":itens,"itens_fat":itens_fat,"receita":receita,"ticket_medio":ticket,
    }

# ─────────────────────────────────────────────
# ALERTAS
# ─────────────────────────────────────────────

def verificar_alertas(df_atual: pd.DataFrame, df_ant: pd.DataFrame, cfg: dict) -> list:
    alertas = []
    m     = calcular_metricas_pedidos(df_atual)
    m_ant = calcular_metricas_pedidos(df_ant) if not df_ant.empty else {}

    limiar_canc  = cfg.get("limiar_cancelamento", 10)
    limiar_queda = cfg.get("limiar_queda_receita", 20)

    if m["pedidos"] > 0:
        taxa_canc = m["cancelados"] / m["pedidos"] * 100
        if taxa_canc > limiar_canc:
            alertas.append(("🔴", f"Taxa de cancelamento em <strong>{taxa_canc:.1f}%</strong> — acima do limiar de {limiar_canc}%."))

    if m_ant.get("receita", 0) > 0:
        var = calcular_variacao(m["receita"], m_ant["receita"])
        if var is not None and var < -limiar_queda:
            alertas.append(("🔴", f"Receita caiu <strong>{abs(var):.1f}%</strong> vs. período anterior — abaixo do limiar de -{limiar_queda}%."))

    if m_ant.get("ticket_medio", 0) > 0:
        var_tk = calcular_variacao(m["ticket_medio"], m_ant["ticket_medio"])
        if var_tk is not None and var_tk < -15:
            alertas.append(("🟡", f"Ticket médio caiu <strong>{abs(var_tk):.1f}%</strong> vs. período anterior."))

    return alertas

# ─────────────────────────────────────────────
# EXPORTAÇÃO
# ─────────────────────────────────────────────

def gerar_resumo_texto(df: pd.DataFrame, marcas: list, d_ini, d_fim) -> str:
    m = calcular_metricas_pedidos(df)
    top_prod = "—"
    if "produto" in df.columns and "quantidade_vendida" in df.columns:
        prod_validos = df[df["produto"].str.strip() != ""]
        if not prod_validos.empty:
            top3 = prod_validos.groupby("produto")["quantidade_vendida"].sum().nlargest(3).index.tolist()
            top_prod = ", ".join(top3) if top3 else "—"
    melhor_canal = "—"
    if "canal" in df.columns and "faturado" in df.columns:
        canal_r = df[df["faturado"]].groupby("canal")["valor_total"].sum()
        if not canal_r.empty:
            melhor_canal = canal_r.idxmax()
    taxa_fat = m["faturados"] / m["pedidos"] * 100 if m["pedidos"] > 0 else 0
    return (
        f"📊 Resumo de Vendas — {d_ini.strftime('%d/%m/%Y')} a {d_fim.strftime('%d/%m/%Y')}\n"
        f"Marcas: {', '.join(marcas) if marcas else 'Todas'}\n\n"
        f"• Receita faturada:    R$ {m['receita']:>12,.2f}\n"
        f"• Pedidos realizados:  {m['pedidos']:>12,}\n"
        f"• Pedidos faturados:   {m['faturados']:>12,}  |  Cancelados: {m['cancelados']:,}\n"
        f"• Taxa de faturamento: {taxa_fat:>11.1f}%\n"
        f"• Ticket médio:        R$ {m['ticket_medio']:>12,.2f}\n"
        f"• Top produtos:        {top_prod}\n"
        f"• Canal com maior receita: {melhor_canal}"
    )

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
for k, v in {
    "cfg_alertas": {"limiar_cancelamento":10,"limiar_queda_receita":20},
    "bq_ts": "",
    "bq_n_linhas": 0,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ═══════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════
st.markdown("## ⌚ Dashboard de Vendas · Grupo Seculus")
st.markdown(
    "<p style='color:#8896b3;margin-top:-10px;font-size:.9rem;'>"
    "Análise comparativa de performance por marca e período · Fonte: BigQuery</p>",
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
# SELEÇÃO DE PERÍODO NO TOPO
# ─────────────────────────────────────────────
hoje = datetime.today().date()

c1, c2, c3, c4, c5, c_de, c_ate, c_comp, c_ref = st.columns([1,1,1,1,1,2,2,3,1.4])
with c1:
    if st.button("Hoje", use_container_width=True, key="at_hoje"):
        st.session_state["data_inicio"] = hoje
        st.session_state["data_fim"]    = hoje
with c2:
    if st.button("7d",   use_container_width=True, key="at_7d"):
        st.session_state["data_inicio"] = hoje - timedelta(days=7)
        st.session_state["data_fim"]    = hoje
with c3:
    if st.button("30d",  use_container_width=True, key="at_30d"):
        st.session_state["data_inicio"] = hoje - timedelta(days=30)
        st.session_state["data_fim"]    = hoje
with c4:
    if st.button("Mês",  use_container_width=True, key="at_mes"):
        st.session_state["data_inicio"] = hoje.replace(day=1)
        st.session_state["data_fim"]    = hoje
with c5:
    if st.button("Ano",  use_container_width=True, key="at_ano"):
        st.session_state["data_inicio"] = hoje.replace(month=1, day=1)
        st.session_state["data_fim"]    = hoje

default_ini = st.session_state.get("data_inicio", hoje - timedelta(days=30))
default_fim = st.session_state.get("data_fim",    hoje)

with c_de:
    data_inicio = st.date_input("De",  value=default_ini, key="data_inicio")
with c_ate:
    data_fim    = st.date_input("Até", value=default_fim,  key="data_fim")
with c_comp:
    comparar_periodo = st.selectbox(
        "Comparar com",
        ["Período anterior equivalente","Mês anterior","Mesmo período ano anterior"],
        index=0, key="comparar_periodo",
    )
with c_ref:
    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
    if st.button("🔄 Atualizar", use_container_width=True, key="btn_refresh"):
        carregar_dados_bq.clear()
        st.rerun()

st.markdown("---")

# ─────────────────────────────────────────────
# SIDEBAR — apenas alertas e status BQ
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Configurações")
    st.markdown("---")
    try:
        _bq_cfg = st.secrets.get("bigquery", {})
        _proj   = _bq_cfg.get("project","—")
        _ds     = _bq_cfg.get("dataset", "—")
        _tb     = _bq_cfg.get("table",   "—")
        st.markdown(
            f"<div class='bq-status'>"
            f"<span style='color:#10b981;'>●</span> BigQuery configurado<br>"
            f"<span style='color:#6b7a99;font-size:.72rem;'>{_proj} › {_ds} › {_tb}</span>"
            f"</div>", unsafe_allow_html=True,
        )
    except Exception:
        st.markdown(
            "<div class='bq-status'>"
            "<span style='color:#f43f5e;'>●</span> BigQuery não configurado<br>"
            "<span style='color:#6b7a99;font-size:.72rem;'>Adicione as credenciais em .streamlit/secrets.toml</span>"
            "</div>", unsafe_allow_html=True,
        )
    if st.session_state.bq_ts:
        st.markdown(
            f"<div style='font-size:.72rem;color:#6b7a99;text-align:center;margin-top:8px;'>"
            f"Última carga: {st.session_state.bq_ts}<br>{st.session_state.bq_n_linhas:,} linhas</div>",
            unsafe_allow_html=True,
        )
    st.markdown("---")
    st.markdown("**🔔 Limiares de Alerta**")
    st.session_state.cfg_alertas["limiar_cancelamento"] = st.slider(
        "Cancelamento (%)", 1, 50,
        value=st.session_state.cfg_alertas.get("limiar_cancelamento", 10),
        key="limiar_canc",
    )
    st.session_state.cfg_alertas["limiar_queda_receita"] = st.slider(
        "Queda de receita (%)", 1, 80,
        value=st.session_state.cfg_alertas.get("limiar_queda_receita", 20),
        key="limiar_queda",
    )

# ─────────────────────────────────────────────
# CARGA DE DADOS
# ─────────────────────────────────────────────
data_inicio_ant, data_fim_ant = calcular_periodo_anterior(data_inicio, data_fim, comparar_periodo)

df_raw_atual, ts_atual = carregar_dados_bq(
    data_inicio.strftime("%Y-%m-%d"),
    data_fim.strftime("%Y-%m-%d"),
)
df_raw_ant, _ = carregar_dados_bq(
    data_inicio_ant.strftime("%Y-%m-%d"),
    data_fim_ant.strftime("%Y-%m-%d"),
)

if ts_atual:
    st.session_state.bq_ts       = ts_atual
    st.session_state.bq_n_linhas = len(df_raw_atual)

# ─────────────────────────────────────────────
# ESTADO SEM DADOS
# ─────────────────────────────────────────────
if df_raw_atual.empty:
    st.markdown("""
    <div style='background:linear-gradient(135deg,#1a2035 0%,#161b27 100%);
    border:1px dashed #3a4560;border-radius:14px;padding:40px;text-align:center;margin:20px 0;'>
        <h2 style='color:#fff;margin:0 0 8px 0;'>Nenhum dado encontrado</h2>
        <p style='color:#8896b3;margin:0;'>
            Verifique as credenciais do BigQuery em <code>.streamlit/secrets.toml</code>
            e se há dados no período selecionado.
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ─────────────────────────────────────────────
# FILTROS GLOBAIS INLINE
# ─────────────────────────────────────────────
marcas_disponiveis  = sorted(df_raw_atual["marca"].dropna().unique().tolist()) if "marca" in df_raw_atual.columns else []
origens_disponiveis = sorted(df_raw_atual["canal_origem"].dropna().unique().tolist()) if "canal_origem" in df_raw_atual.columns else []
tipos_canal_opcoes  = ["Google Ads","Meta Ads","Orgânico","E-mail","Influencer/Parceiro","Outros"]

st.markdown("<div class='filtro-inline'>", unsafe_allow_html=True)
fc1, fc2, fc3 = st.columns([3,3,2])
with fc1:
    marcas_selecionadas = st.multiselect(
        "🏷️ Marcas", marcas_disponiveis, default=marcas_disponiveis, key="marcas_sel"
    )
with fc2:
    tipos_canal_sel = st.multiselect(
        "📡 Canal de aquisição", tipos_canal_opcoes, default=tipos_canal_opcoes, key="tipos_canal_sel"
    )
with fc3:
    origens_sel = st.multiselect(
        "🛒 Origem dos dados", origens_disponiveis, default=origens_disponiveis, key="origens_sel"
    )
st.markdown("</div>", unsafe_allow_html=True)

# Aplica filtros
df_atual = aplicar_filtros(df_raw_atual, marcas_selecionadas, tipos_canal_sel, origens_sel)
df_ant   = aplicar_filtros(df_raw_ant,   marcas_selecionadas, tipos_canal_sel, origens_sel)

# ─────────────────────────────────────────────
# ALERTAS
# ─────────────────────────────────────────────
for emoji, msg in verificar_alertas(df_atual, df_ant, st.session_state.cfg_alertas):
    st.markdown(f"<div class='alert-box'>{emoji} {msg}</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# BANNER DE PERÍODO
# ─────────────────────────────────────────────
col_p1, col_p2, col_p3 = st.columns([5,1,5])
with col_p1:
    st.markdown(
        f"<div style='background:#1a2035;border:1px solid #3a4560;border-radius:8px;"
        f"padding:10px 16px;font-size:.82rem;color:#8896b3;font-family:DM Mono,monospace;'>"
        f"📅 <strong style='color:#fff;'>Atual:</strong> "
        f"{data_inicio.strftime('%d/%m/%Y')} → {data_fim.strftime('%d/%m/%Y')}"
        f" <span style='color:#3a4560;'>({(data_fim - data_inicio).days + 1} dias)</span></div>",
        unsafe_allow_html=True,
    )
with col_p2:
    st.markdown("<div style='text-align:center;color:#6b7a99;padding-top:10px;'>vs</div>", unsafe_allow_html=True)
with col_p3:
    st.markdown(
        f"<div style='background:#1a2035;border:1px solid #3a4560;border-radius:8px;"
        f"padding:10px 16px;font-size:.82rem;color:#8896b3;font-family:DM Mono,monospace;'>"
        f"📅 <strong style='color:#fff;'>Anterior:</strong> "
        f"{data_inicio_ant.strftime('%d/%m/%Y')} → {data_fim_ant.strftime('%d/%m/%Y')}"
        f" <span style='color:#3a4560;'>({(data_fim_ant - data_inicio_ant).days + 1} dias)</span></div>",
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# RESUMO POR MARCA (cards com borda colorida por marca)
# ─────────────────────────────────────────────
marcas_com_dados = (
    [m for m in marcas_disponiveis if not df_atual[df_atual["marca"] == m].empty]
    if "marca" in df_atual.columns else []
)

if marcas_com_dados:
    st.markdown("### Resumo por Marca")
    cols_res = st.columns(len(marcas_com_dados))
    for idx, marca in enumerate(marcas_com_dados):
        df_m  = df_atual[df_atual["marca"] == marca]
        m_res = calcular_metricas_pedidos(df_m)
        taxa_canc  = (m_res["cancelados"] / m_res["pedidos"] * 100) if m_res["pedidos"] > 0 else 0
        limiar_bom = st.session_state.cfg_alertas.get("limiar_cancelamento", 10) / 2
        limiar_med = st.session_state.cfg_alertas.get("limiar_cancelamento", 10)
        cor = cor_marca(marca)
        with cols_res[idx]:
            st.markdown(f"""
            <div class="resumo-card" style="border-top:3px solid {cor};">
                <h4 style='color:{cor};'>{marca}</h4>
                <div class="resumo-linha">
                    <span>Pedidos únicos</span>
                    <span class="resumo-valor">{m_res['pedidos']:,}</span>
                </div>
                <div class="resumo-linha">
                    <span>Itens faturados</span>
                    <span class="resumo-valor"><span class='badge-verde'>{m_res['itens_fat']:,}</span></span>
                </div>
                <div class="resumo-linha">
                    <span>Cancelados</span>
                    <span class="resumo-valor"><span class='badge-vermelho'>{m_res['cancelados']:,}</span></span>
                </div>
                <div class="resumo-linha">
                    <span>Taxa cancelamento</span>
                    <span class="resumo-valor">{badge_taxa(taxa_canc, limiar_bom, limiar_med)}</span>
                </div>
                <div class="resumo-linha">
                    <span>Receita faturada</span>
                    <span class="resumo-valor">R$ {m_res['receita']:,.0f}</span>
                </div>
                <div class="resumo-linha">
                    <span>Ticket médio</span>
                    <span class="resumo-valor">R$ {m_res['ticket_medio']:,.0f}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

st.markdown("---")

# ─────────────────────────────────────────────
# ABAS
# ─────────────────────────────────────────────
tab_geral, tab_prod, tab_ped, tab_conv, tab_traf, tab_marca_aba = st.tabs([
    "📊 Visão Geral","🏆 Produtos","📦 Pedidos",
    "🎯 Conversão","📡 Tráfego & Origem","🏷️ Por Marca",
])

# ═══════════════════════════════════════════════════
# ABA 1 — VISÃO GERAL
# ═══════════════════════════════════════════════════
with tab_geral:
    if df_atual.empty:
        st.info("Nenhum dado no período selecionado para os filtros aplicados.")
    else:
        m     = calcular_metricas_pedidos(df_atual)
        m_ant = calcular_metricas_pedidos(df_ant) if not df_ant.empty else {}

        st.markdown("### KPIs do Período")
        k1,k2,k3,k4,k5,k6 = st.columns(6)
        taxa_fat_atual = m["faturados"] / m["pedidos"] * 100 if m["pedidos"] else 0
        taxa_fat_ant   = m_ant["faturados"] / m_ant["pedidos"] * 100 if m_ant.get("pedidos") else 0

        k1.metric("💰 Receita",       f"R$ {m['receita']:,.0f}",
                  delta=formatar_variacao(calcular_variacao(m["receita"],      m_ant.get("receita",0))))
        k2.metric("🛒 Pedidos",       f"{m['pedidos']:,}",
                  delta=formatar_variacao(calcular_variacao(m["pedidos"],      m_ant.get("pedidos",0))))
        k3.metric("✅ Faturados",     f"{m['faturados']:,}",
                  delta=formatar_variacao(calcular_variacao(m["faturados"],    m_ant.get("faturados",0))))
        k4.metric("❌ Cancelados",    f"{m['cancelados']:,}")
        k5.metric("📊 Taxa Fat.",     f"{taxa_fat_atual:.1f}%",
                  delta=formatar_variacao(calcular_variacao(taxa_fat_atual, taxa_fat_ant)))
        k6.metric("🎟️ Ticket Médio", f"R$ {m['ticket_medio']:,.0f}",
                  delta=formatar_variacao(calcular_variacao(m["ticket_medio"], m_ant.get("ticket_medio",0))))

        st.markdown("<br>", unsafe_allow_html=True)

        insights = []
        if m_ant.get("receita",0) > 0:
            var = calcular_variacao(m["receita"], m_ant["receita"])
            emoji   = "🟢" if var >= 0 else "🔴"
            direcao = "crescimento" if var >= 0 else "queda"
            insights.append(
                f"{emoji} <strong>Receita:</strong> {direcao} de <strong>{abs(var):.1f}%</strong> "
                f"vs. período anterior — de R$ {m_ant['receita']:,.0f} para R$ {m['receita']:,.0f}."
            )
        if "produto" in df_atual.columns:
            df_fat = df_atual[df_atual["faturado"] & (df_atual["produto"].str.strip() != "")]
            receita_prod = df_fat.groupby("produto")["valor_total"].sum().sort_values(ascending=False)
            total_r = receita_prod.sum()
            if total_r > 0:
                cumsum    = receita_prod.cumsum() / total_r
                n_prod_80 = int((cumsum <= 0.8).sum()) + 1
                pct_prod  = n_prod_80 / len(receita_prod) * 100
                insights.append(
                    f"📐 <strong>Concentração 80/20:</strong> <strong>{n_prod_80} produtos "
                    f"({pct_prod:.0f}% do catálogo)</strong> respondem por 80% da receita faturada."
                )
        if "canal" in df_atual.columns:
            canal_r = df_atual[df_atual["faturado"]].groupby("canal")["valor_total"].sum()
            if not canal_r.empty:
                top_canal = canal_r.idxmax()
                pct_canal = canal_r[top_canal] / canal_r.sum() * 100
                insights.append(
                    f"📡 <strong>Canal dominante: {top_canal}</strong> — {pct_canal:.0f}% da receita faturada."
                )
        for ins in insights:
            st.markdown(f"<div class='insight-box'>{ins}</div>", unsafe_allow_html=True)

        st.markdown("---")

        st.markdown("### Evolução de Receita Faturada por Marca")
        if "marca" in df_atual.columns:
            df_time = (df_atual[df_atual["faturado"]]
                       .groupby(["data","marca"])["valor_total"].sum().reset_index())
            fig_time = go.Figure()
            for marca in df_time["marca"].unique():
                d = df_time[df_time["marca"] == marca].sort_values("data")
                fig_time.add_trace(go.Scatter(
                    x=d["data"], y=d["valor_total"], name=marca, mode="lines",
                    line=dict(color=cor_marca(marca), width=2.5, shape="spline", smoothing=1.3),
                ))
            fig_time.update_layout(**layout_normal(title="Receita diária faturada (R$)"))
            st.plotly_chart(fig_time, use_container_width=True)

        st.markdown("---")
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.markdown("### Receita por Marca — Atual vs Anterior")
            if "marca" in df_atual.columns:
                ra = df_atual[df_atual["faturado"]].groupby("marca")["valor_total"].sum().reset_index()
                rp = (df_ant[df_ant["faturado"]].groupby("marca")["valor_total"].sum().reset_index()
                      if not df_ant.empty else pd.DataFrame(columns=["marca","valor_total"]))
                ra.columns = ["marca","atual"]
                rp.columns = ["marca","anterior"]
                comp = ra.merge(rp, on="marca", how="outer").fillna(0).sort_values("atual", ascending=False)
                fig_comp = go.Figure([
                    go.Bar(name="Anterior", x=comp["marca"], y=comp["anterior"],
                           marker_color="rgba(100,120,160,0.4)", marker_line_width=0),
                    go.Bar(name="Atual",    x=comp["marca"], y=comp["atual"],
                           marker_color=[cor_marca(m) for m in comp["marca"]], marker_line_width=0),
                ])
                fig_comp.update_layout(barmode="group", **layout_normal())
                st.plotly_chart(fig_comp, use_container_width=True)

        with col_g2:
            st.markdown("### Share de Receita Faturada por Marca")
            if "marca" in df_atual.columns:
                share = df_atual[df_atual["faturado"]].groupby("marca")["valor_total"].sum().reset_index()
                fig_pie = px.pie(share, names="marca", values="valor_total",
                                 color="marca", color_discrete_map=COR_MARCAS, hole=0.55)
                fig_pie.update_traces(textinfo="percent+label", textfont_size=12)
                fig_pie.update_layout(**layout_normal())
                st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown("### Volume Mensal de Itens Faturados por Marca")
        if "marca" in df_atual.columns and "quantidade_vendida" in df_atual.columns:
            df_men = (df_atual[df_atual["faturado"]]
                      .groupby(["mes","marca"])["quantidade_vendida"].sum().reset_index())
            fig_men = px.bar(df_men, x="mes", y="quantidade_vendida", color="marca",
                             barmode="group", color_discrete_map=COR_MARCAS,
                             labels={"quantidade_vendida":"Itens","mes":"","marca":"Marca"})
            fig_men.update_layout(**layout_normal())
            st.plotly_chart(fig_men, use_container_width=True)

        st.markdown("---")
        st.markdown("### Exportar")
        c_exp1, c_exp2 = st.columns(2)
        with c_exp1:
            st.download_button("📋 Baixar resumo em texto",
                               data=gerar_resumo_texto(df_atual, marcas_selecionadas, data_inicio, data_fim),
                               file_name="resumo_vendas.txt", mime="text/plain",
                               use_container_width=True)
        with c_exp2:
            st.download_button("📥 Exportar dados filtrados (CSV)",
                               data=df_atual.to_csv(index=False).encode("utf-8"),
                               file_name="dados_filtrados.csv", mime="text/csv",
                               use_container_width=True)


# ═══════════════════════════════════════════════════
# ABA 2 — PRODUTOS
# ═══════════════════════════════════════════════════
with tab_prod:
    st.markdown("### 🏆 Produtos")

    if df_atual.empty:
        st.info("Nenhum dado no período.")
    else:
        # Filtro de marca e top N inline
        cf1, cf2, _ = st.columns([3,1,4])
        with cf1:
            marcas_prod = st.multiselect(
                "🏷️ Marca", marcas_selecionadas, default=marcas_selecionadas, key="prod_marcas"
            )
        with cf2:
            top_n = st.selectbox("Top N", [5,10,15,20], index=1, key="top_n")

        df_prod = (df_atual[df_atual["marca"].isin(marcas_prod)]
                   if "marca" in df_atual.columns else df_atual)
        df_prod_fat = df_prod[df_prod["faturado"]]

        # Produtos só existem no ecommerce
        tem_produto = (
            "produto" in df_prod_fat.columns
            and df_prod_fat["produto"].str.strip().ne("").any()
        )

        if not tem_produto:
            st.markdown(
                "<div class='warn-box'>⚠️ Os dados de <strong>produto</strong> vêm exclusivamente "
                "do canal <strong>ecommerce</strong>. Verifique se a coluna <code>produto</code> está "
                "preenchida na tabela e se a origem <em>ecommerce</em> está selecionada nos filtros globais.</div>",
                unsafe_allow_html=True,
            )
        else:
            df_prod_fat_p = df_prod_fat[df_prod_fat["produto"].str.strip() != ""]

            col_p1, col_p2 = st.columns(2)
            with col_p1:
                st.markdown("**Por quantidade faturada**")
                if "quantidade_vendida" in df_prod_fat_p.columns:
                    top_qtd = (df_prod_fat_p.groupby(["marca","produto"])["quantidade_vendida"]
                               .sum().reset_index()
                               .sort_values("quantidade_vendida", ascending=False).head(top_n))
                    fig_qtd = px.bar(top_qtd, x="quantidade_vendida", y="produto", color="marca",
                                     orientation="h", color_discrete_map=COR_MARCAS,
                                     labels={"quantidade_vendida":"Unidades","produto":""})
                    fig_qtd.update_layout(**layout_invertido())
                    st.plotly_chart(fig_qtd, use_container_width=True)

            with col_p2:
                st.markdown("**Por receita faturada**")
                top_rec = (df_prod_fat_p.groupby(["marca","produto"])["valor_total"]
                           .sum().reset_index()
                           .sort_values("valor_total", ascending=False).head(top_n))
                fig_rec = px.bar(top_rec, x="valor_total", y="produto", color="marca",
                                 orientation="h", color_discrete_map=COR_MARCAS,
                                 labels={"valor_total":"Receita (R$)","produto":""})
                fig_rec.update_layout(**layout_invertido())
                st.plotly_chart(fig_rec, use_container_width=True)

            st.markdown("### Detalhamento por Produto")
            group_cols = ["marca","produto"] + (
                ["sku"] if "sku" in df_prod_fat_p.columns
                and df_prod_fat_p["sku"].str.strip().ne("").any() else []
            )
            resumo_prod = (
                df_prod_fat_p.groupby(group_cols)
                .agg(qtd_vendida=("quantidade_vendida","sum"),
                     receita_total=("valor_total","sum"),
                     pedidos=("id_pedido","nunique"))
                .reset_index()
                .sort_values("receita_total", ascending=False)
            )
            resumo_prod["ticket_medio"] = (
                resumo_prod["receita_total"] / resumo_prod["pedidos"].replace(0, np.nan)
            )
            resumo_prod["receita_total"] = resumo_prod["receita_total"].map("R$ {:,.2f}".format)
            resumo_prod["ticket_medio"]  = resumo_prod["ticket_medio"].map(
                lambda x: f"R$ {x:,.2f}" if pd.notna(x) else "—"
            )
            st.dataframe(resumo_prod, use_container_width=True, hide_index=True)
            st.download_button("📥 Exportar tabela",
                               data=resumo_prod.to_csv(index=False).encode("utf-8"),
                               file_name="produtos.csv", mime="text/csv")


# ═══════════════════════════════════════════════════
# ABA 3 — PEDIDOS
# ═══════════════════════════════════════════════════
with tab_ped:
    st.markdown("### 📦 Pedidos")

    if df_atual.empty or "faturado" not in df_atual.columns:
        st.info("Nenhum dado de pedidos no período.")
    else:
        m     = calcular_metricas_pedidos(df_atual)
        m_ant = calcular_metricas_pedidos(df_ant) if not df_ant.empty else {}

        taxa_fat_ped = m["faturados"] / m["pedidos"] * 100 if m["pedidos"] else 0
        taxa_ant_ped = m_ant["faturados"] / m_ant["pedidos"] * 100 if m_ant.get("pedidos") else 0

        kp1,kp2,kp3,kp4,kp5 = st.columns(5)
        kp1.metric("📥 Realizados", f"{m['pedidos']:,}",
                   delta=formatar_variacao(calcular_variacao(m["pedidos"],   m_ant.get("pedidos",0))))
        kp2.metric("✅ Faturados",  f"{m['faturados']:,}",
                   delta=formatar_variacao(calcular_variacao(m["faturados"], m_ant.get("faturados",0))))
        kp3.metric("⏳ Pendentes",  f"{m['pendentes']:,}")
        kp4.metric("❌ Cancelados", f"{m['cancelados']:,}")
        kp5.metric("📈 Taxa Fat.",  f"{taxa_fat_ped:.1f}%",
                   delta=formatar_variacao(calcular_variacao(taxa_fat_ped, taxa_ant_ped)))

        st.markdown("<br>", unsafe_allow_html=True)

        ped_agg = (df_atual.groupby("id_pedido", sort=False)
                   .agg(tem_faturado=("faturado","any"), tem_cancelado=("cancelado","any"))
                   .reset_index())
        ped_agg["status"] = "Pendente"
        ped_agg.loc[ped_agg["tem_cancelado"] & ~ped_agg["tem_faturado"], "status"] = "Cancelado"
        ped_agg.loc[ped_agg["tem_faturado"], "status"] = "Faturado"

        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.markdown("### Status dos Pedidos")
            sc = ped_agg["status"].value_counts().reset_index()
            sc.columns = ["status","qtd"]
            CORES_STATUS = {"Faturado":"#10b981","Pendente":"#f59e0b","Cancelado":"#f43f5e"}
            fig_st = px.pie(sc, names="status", values="qtd",
                            color="status", color_discrete_map=CORES_STATUS, hole=0.55)
            fig_st.update_traces(textinfo="percent+label")
            fig_st.update_layout(**layout_normal())
            st.plotly_chart(fig_st, use_container_width=True)

        with col_s2:
            st.markdown("### Pedidos por Marca")
            if "marca" in df_atual.columns:
                pm = (df_atual.groupby(["id_pedido","marca"])
                      .agg(faturado=("faturado","any")).reset_index()
                      .groupby("marca")
                      .agg(realizados=("id_pedido","nunique"), faturados=("faturado","sum"))
                      .reset_index())
                fig_pm = go.Figure([
                    go.Bar(name="Realizados", x=pm["marca"], y=pm["realizados"],
                           marker_color="rgba(100,120,200,0.4)"),
                    go.Bar(name="Faturados",  x=pm["marca"], y=pm["faturados"],
                           marker_color=[cor_marca(m) for m in pm["marca"]]),
                ])
                fig_pm.update_layout(barmode="group", **layout_normal())
                st.plotly_chart(fig_pm, use_container_width=True)

        st.markdown("### Funil de Conversão")
        fig_funil = go.Figure(go.Funnel(
            y=["Realizados","Faturados","Cancelados"],
            x=[m["pedidos"],m["faturados"],m["cancelados"]],
            marker={"color":["#4a7cff","#10b981","#f43f5e"]},
            textinfo="value+percent initial",
        ))
        fig_funil.update_layout(**layout_normal())
        st.plotly_chart(fig_funil, use_container_width=True)

        st.markdown("### Volume de Pedidos por Dia")
        if "marca" in df_atual.columns:
            ped_dia = (df_atual.groupby(["data","marca"])["id_pedido"]
                       .nunique().reset_index().rename(columns={"id_pedido":"pedidos"}))
            fig_pd = px.area(ped_dia, x="data", y="pedidos", color="marca",
                             color_discrete_map=COR_MARCAS,
                             labels={"pedidos":"Pedidos","data":""})
            fig_pd.update_layout(**layout_normal())
            st.plotly_chart(fig_pd, use_container_width=True)

        st.markdown("### Registro de Pedidos")
        cols_ex = [c for c in ["data","marca","id_pedido","produto","sku",
                                "quantidade_vendida","valor_total","status_pedido","canal","canal_origem"]
                   if c in df_atual.columns]
        df_tab = df_atual[cols_ex].sort_values("data", ascending=False)
        st.dataframe(df_tab, use_container_width=True, hide_index=True)
        st.download_button("📥 Exportar pedidos",
                           data=df_tab.to_csv(index=False).encode("utf-8"),
                           file_name="pedidos.csv", mime="text/csv")


# ═══════════════════════════════════════════════════
# ABA 4 — CONVERSÃO
# ═══════════════════════════════════════════════════
with tab_conv:
    st.markdown("### 🎯 Conversão")

    if df_atual.empty or "faturado" not in df_atual.columns:
        st.info("Sem dados de conversão.")
    else:
        def taxa_conv_por_pedido(df: pd.DataFrame) -> pd.DataFrame:
            if df.empty or "marca" not in df.columns:
                return pd.DataFrame(columns=["marca","taxa"])
            g = (df.groupby(["id_pedido","marca"])
                 .agg(faturado=("faturado","any")).reset_index())
            return (g.groupby("marca")
                    .apply(lambda x: x["faturado"].mean() * 100)
                    .reset_index().rename(columns={0:"taxa"}))

        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.markdown("**Taxa de Conversão por Marca — Atual vs Anterior**")
            if "marca" in df_atual.columns:
                ca = taxa_conv_por_pedido(df_atual)
                cp = (taxa_conv_por_pedido(df_ant).rename(columns={"taxa":"taxa_ant"})
                      if not df_ant.empty else pd.DataFrame(columns=["marca","taxa_ant"]))
                cm = ca.merge(cp, on="marca", how="left").fillna(0)
                fig_cv = go.Figure([
                    go.Bar(name="Anterior", x=cm["marca"], y=cm["taxa_ant"],
                           marker_color="rgba(100,120,160,0.4)"),
                    go.Bar(name="Atual",    x=cm["marca"], y=cm["taxa"],
                           marker_color=[cor_marca(m) for m in cm["marca"]]),
                ])
                fig_cv.update_layout(barmode="group", yaxis_ticksuffix="%", **layout_normal())
                st.plotly_chart(fig_cv, use_container_width=True)

        with col_c2:
            st.markdown("**Evolução da Taxa de Conversão**")
            if "marca" in df_atual.columns:
                ct = (df_atual.groupby(["data","id_pedido","marca"])
                      .agg(faturado=("faturado","any")).reset_index()
                      .groupby(["data","marca"])
                      .apply(lambda x: x["faturado"].mean() * 100)
                      .reset_index().rename(columns={0:"conv"}))
                fig_cvt = go.Figure()
                for marca in ct["marca"].unique():
                    d = ct[ct["marca"] == marca].sort_values("data")
                    fig_cvt.add_trace(go.Scatter(
                        x=d["data"], y=d["conv"], name=marca, mode="lines",
                        line=dict(color=cor_marca(marca), width=2.5, shape="spline", smoothing=1.3),
                    ))
                fig_cvt.update_layout(**layout_normal(), yaxis_ticksuffix="%")
                st.plotly_chart(fig_cvt, use_container_width=True)

        if "canal" in df_atual.columns:
            tick_canal = (df_atual[df_atual["faturado"]]
                          .groupby(["id_pedido","canal"])["valor_total"]
                          .sum().reset_index()
                          .groupby("canal")["valor_total"].mean())
            if not tick_canal.empty:
                melhor_tk = tick_canal.idxmax()
                st.markdown(
                    f"<div class='insight-box'>🎟️ <strong>Canal com maior ticket médio: {melhor_tk}</strong> — "
                    f"R$ {tick_canal[melhor_tk]:,.0f} por pedido faturado.</div>",
                    unsafe_allow_html=True,
                )

        st.markdown("### Taxa de Conversão por Canal")
        if "canal" in df_atual.columns:
            conv_c = (df_atual.groupby(["id_pedido","canal"])
                      .agg(faturado=("faturado","any")).reset_index()
                      .groupby("canal")
                      .agg(pedidos=("id_pedido","nunique"), faturados=("faturado","sum"))
                      .reset_index())
            conv_c["taxa"] = conv_c["faturados"] / conv_c["pedidos"].replace(0,np.nan) * 100
            conv_c = conv_c.sort_values("taxa", ascending=True)
            fig_cc = px.bar(conv_c, x="taxa", y="canal", orientation="h",
                            color="canal", color_discrete_map=CORES_CANAL,
                            labels={"taxa":"Taxa (%)","canal":""},
                            text=conv_c["taxa"].map("{:.1f}%".format))
            fig_cc.update_traces(textposition="outside")
            fig_cc.update_layout(**layout_invertido())
            st.plotly_chart(fig_cc, use_container_width=True)


# ═══════════════════════════════════════════════════
# ABA 5 — TRÁFEGO & ORIGEM
# ═══════════════════════════════════════════════════
with tab_traf:
    st.markdown("### 📡 Tráfego & Origem")

    if df_atual.empty or "canal" not in df_atual.columns:
        st.info("Coluna `origem_cliente` não encontrada nos dados.")
    else:
        ped_canal = (df_atual.groupby(["id_pedido","canal"])
                     .agg(faturado=("faturado","any"), receita=("valor_total","sum"))
                     .reset_index())
        ca_agg = (ped_canal.groupby("canal")
                  .agg(pedidos=("id_pedido","nunique"), faturados=("faturado","sum"),
                       receita=("receita","sum"))
                  .reset_index())

        col_t1, col_t2 = st.columns(2)
        with col_t1:
            st.markdown("**Distribuição de Pedidos por Canal**")
            fig_cc2 = px.pie(ca_agg, names="canal", values="pedidos",
                             color="canal", color_discrete_map=CORES_CANAL, hole=0.55)
            fig_cc2.update_traces(textinfo="percent+label")
            fig_cc2.update_layout(**layout_normal())
            st.plotly_chart(fig_cc2, use_container_width=True)

        with col_t2:
            st.markdown("**Receita Faturada por Canal**")
            cr = ca_agg.sort_values("receita", ascending=True)
            fig_cr = px.bar(cr, x="receita", y="canal", orientation="h",
                            color="canal", color_discrete_map=CORES_CANAL,
                            labels={"receita":"Receita (R$)","canal":""})
            fig_cr.update_layout(**layout_invertido())
            st.plotly_chart(fig_cr, use_container_width=True)

        st.markdown("### Canal: Atual vs Período Anterior")
        if not df_ant.empty and "canal" in df_ant.columns:
            ped_canal_ant = (df_ant.groupby(["id_pedido","canal"])
                             .agg(receita=("valor_total","sum")).reset_index())
            cp_agg = (ped_canal_ant.groupby("canal")
                      .agg(ped_ant=("id_pedido","nunique"), rec_ant=("receita","sum"))
                      .reset_index())
            ccomp = ca_agg.merge(cp_agg, on="canal", how="left").fillna(0)
            ccomp["var"] = ccomp.apply(
                lambda r: formatar_variacao(calcular_variacao(r["receita"],r["rec_ant"])) or "—", axis=1
            )
            fig_ccp = go.Figure([
                go.Bar(name="Anterior", x=ccomp["canal"], y=ccomp["rec_ant"],
                       marker_color="rgba(100,120,160,0.4)"),
                go.Bar(name="Atual", x=ccomp["canal"], y=ccomp["receita"],
                       marker_color=[CORES_CANAL.get(c,"#4a7cff") for c in ccomp["canal"]],
                       text=ccomp["var"], textposition="outside"),
            ])
            fig_ccp.update_layout(barmode="group", **layout_normal())
            st.plotly_chart(fig_ccp, use_container_width=True)

        st.markdown("### Canal por Marca")
        if "marca" in df_atual.columns:
            cm2 = (df_atual[df_atual["faturado"]]
                   .groupby(["marca","canal"])["valor_total"].sum().reset_index())
            fig_cm2 = px.bar(cm2, x="marca", y="valor_total", color="canal",
                             color_discrete_map=CORES_CANAL, barmode="stack",
                             labels={"valor_total":"Receita Faturada (R$)","marca":"","canal":"Canal"})
            fig_cm2.update_layout(**layout_normal())
            st.plotly_chart(fig_cm2, use_container_width=True)

        st.markdown("### Resumo por Canal")
        canal_tab = ca_agg.copy()
        canal_tab["taxa_conv"]   = (canal_tab["faturados"] / canal_tab["pedidos"].replace(0,np.nan) * 100).map("{:.1f}%".format)
        canal_tab["receita_fmt"] = canal_tab["receita"].map("R$ {:,.0f}".format)
        canal_tab = canal_tab.rename(columns={
            "canal":"Canal","pedidos":"Pedidos","faturados":"Faturados",
            "taxa_conv":"Taxa Conv.","receita_fmt":"Receita",
        })
        st.dataframe(canal_tab[["Canal","Pedidos","Faturados","Taxa Conv.","Receita"]],
                     use_container_width=True, hide_index=True)
        st.download_button("📥 Exportar",
                           data=canal_tab.to_csv(index=False).encode("utf-8"),
                           file_name="canais.csv", mime="text/csv")

        st.markdown("### Detalhamento por Campanha")
        if "campanha" in df_atual.columns and "tipo_canal" in df_atual.columns:
            camp_a = (df_atual.groupby(["tipo_canal","campanha"])
                      .agg(pedidos=("id_pedido","nunique"),
                           faturados=("faturado","sum"),
                           receita=("valor_total","sum"))
                      .reset_index())
            if not df_ant.empty and "campanha" in df_ant.columns:
                camp_p = df_ant.groupby("campanha").agg(rec_ant=("valor_total","sum")).reset_index()
                camp_a = camp_a.merge(camp_p, on="campanha", how="left").fillna(0)
                camp_a["var"] = camp_a.apply(
                    lambda r: formatar_variacao(calcular_variacao(r["receita"],r["rec_ant"])) or "—", axis=1
                )
            else:
                camp_a["var"] = "—"
            camp_a["taxa_conv"] = (
                camp_a["faturados"] / camp_a["pedidos"].replace(0,np.nan) * 100
            ).map("{:.1f}%".format)
            camp_a = camp_a.sort_values("receita", ascending=False)

            fig_camp = px.bar(camp_a.head(20), x="receita", y="campanha", color="tipo_canal",
                              orientation="h", color_discrete_map=CORES_CANAL,
                              labels={"receita":"Receita (R$)","campanha":"","tipo_canal":"Canal"})
            fig_camp.update_layout(**layout_invertido())
            st.plotly_chart(fig_camp, use_container_width=True)

            camp_exib = camp_a.copy()
            camp_exib["receita"] = camp_exib["receita"].map("R$ {:,.0f}".format)
            camp_exib = camp_exib.rename(columns={
                "tipo_canal":"Tipo de Canal","campanha":"Campanha","pedidos":"Pedidos",
                "faturados":"Faturados","taxa_conv":"Taxa Conv.","receita":"Receita","var":"Var. vs Ant.",
            })
            cols_c = [c for c in ["Tipo de Canal","Campanha","Pedidos","Faturados","Taxa Conv.","Receita","Var. vs Ant."]
                      if c in camp_exib.columns]
            st.dataframe(camp_exib[cols_c], use_container_width=True, hide_index=True)
            st.download_button("📥 Exportar campanhas",
                               data=camp_exib[cols_c].to_csv(index=False).encode("utf-8"),
                               file_name="campanhas.csv", mime="text/csv")


# ═══════════════════════════════════════════════════
# ABA 6 — POR MARCA
# ═══════════════════════════════════════════════════
with tab_marca_aba:
    st.markdown("### 🏷️ Análise por Marca")

    if not marcas_selecionadas:
        st.info("Nenhuma marca selecionada nos filtros globais.")
    else:
        marca_sel = st.selectbox("Marca", marcas_selecionadas, key="marca_ind")

        df_ma = df_atual[df_atual["marca"] == marca_sel] if "marca" in df_atual.columns else df_atual
        df_mp = df_ant[df_ant["marca"]   == marca_sel] if "marca" in df_ant.columns  else df_ant

        if df_ma.empty:
            st.info(f"Sem dados para {marca_sel} no período selecionado.")
        else:
            m_a = calcular_metricas_pedidos(df_ma)
            m_p = calcular_metricas_pedidos(df_mp) if not df_mp.empty else {}

            km1,km2,km3,km4,km5 = st.columns(5)
            km1.metric("Receita",      f"R$ {m_a['receita']:,.0f}",
                       delta=formatar_variacao(calcular_variacao(m_a["receita"],      m_p.get("receita",0))))
            km2.metric("Pedidos",      f"{m_a['pedidos']:,}",
                       delta=formatar_variacao(calcular_variacao(m_a["pedidos"],      m_p.get("pedidos",0))))
            km3.metric("Faturados",    f"{m_a['faturados']:,}",
                       delta=formatar_variacao(calcular_variacao(m_a["faturados"],    m_p.get("faturados",0))))
            km4.metric("Cancelados",   f"{m_a['cancelados']:,}")
            km5.metric("Ticket Médio", f"R$ {m_a['ticket_medio']:,.0f}",
                       delta=formatar_variacao(calcular_variacao(m_a["ticket_medio"], m_p.get("ticket_medio",0))))

            st.markdown("<br>", unsafe_allow_html=True)
            col_m1, col_m2 = st.columns(2)

            with col_m1:
                st.markdown(f"**Top 10 Produtos — {marca_sel}**")
                if "produto" in df_ma.columns and "quantidade_vendida" in df_ma.columns:
                    df_ma_p = df_ma[df_ma["faturado"] & (df_ma["produto"].str.strip() != "")]
                    if df_ma_p.empty:
                        st.info("Dados de produto disponíveis apenas no canal ecommerce.")
                    else:
                        top_m = df_ma_p.groupby("produto")["quantidade_vendida"].sum().nlargest(10).reset_index()
                        fig_tm = px.bar(top_m, x="quantidade_vendida", y="produto", orientation="h",
                                        color_discrete_sequence=[cor_marca(marca_sel)],
                                        labels={"quantidade_vendida":"Unidades","produto":""})
                        fig_tm.update_layout(**layout_invertido())
                        st.plotly_chart(fig_tm, use_container_width=True)

            with col_m2:
                st.markdown(f"**Origem dos Clientes — {marca_sel}**")
                if "canal" in df_ma.columns:
                    canal_ped = (df_ma.groupby(["id_pedido","canal"])
                                 .size().reset_index(name="_")
                                 .groupby("canal").size().reset_index(name="qtd"))
                    fig_cm3 = px.pie(canal_ped, names="canal", values="qtd",
                                     color="canal", color_discrete_map=CORES_CANAL, hole=0.55)
                    fig_cm3.update_traces(textinfo="percent+label")
                    fig_cm3.update_layout(**layout_normal())
                    st.plotly_chart(fig_cm3, use_container_width=True)

            st.markdown(f"**Receita Diária Faturada — {marca_sel}**")
            rd = df_ma[df_ma["faturado"]].groupby("data")["valor_total"].sum().reset_index()
            cor_m = cor_marca(marca_sel)
            fig_rd = go.Figure()
            fig_rd.add_trace(go.Scatter(
                x=rd["data"], y=rd["valor_total"], mode="lines", fill="tozeroy",
                line=dict(color=cor_m, width=2.5, shape="spline", smoothing=1.3),
                fillcolor=hex_to_rgba(cor_m, 0.1),
                name="Receita faturada",
            ))
            fig_rd.update_layout(**layout_normal())
            st.plotly_chart(fig_rd, use_container_width=True)

            st.markdown(f"**Receita Mensal Faturada — {marca_sel}**")
            men_m = df_ma[df_ma["faturado"]].groupby("mes")["valor_total"].sum().reset_index()
            fig_mm = go.Figure([go.Bar(
                x=men_m["mes"], y=men_m["valor_total"],
                marker_color=cor_marca(marca_sel),
            )])
            fig_mm.update_layout(**layout_normal())
            st.plotly_chart(fig_mm, use_container_width=True)

            st.download_button(f"📥 Exportar dados {marca_sel}",
                               data=df_ma.to_csv(index=False).encode("utf-8"),
                               file_name=f"{marca_sel.lower()}_periodo.csv", mime="text/csv")

# ─────────────────────────────────────────────
# RODAPÉ
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#3a4560;font-size:.75rem;font-family:DM Mono,monospace;'>"
    "⌚ Dashboard de Vendas · Grupo Seculus · Fonte: BigQuery · Cache: 5 min"
    "</div>",
    unsafe_allow_html=True,
)
