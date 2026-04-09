import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import StringIO
import requests
from datetime import datetime, timedelta
import numpy as np
import json

# ─────────────────────────────────────────────
# PÁGINA
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard de Vendas · Grupo Seculus",
    page_icon="⌚",
    layout="wide",
    initial_sidebar_state="expanded",
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
.upload-section{background:linear-gradient(135deg,#1a2035 0%,#161b27 100%);border:1px dashed #3a4560;border-radius:14px;padding:30px;text-align:center;margin:20px 0;}
.source-status{display:inline-flex;align-items:center;gap:6px;font-size:.75rem;font-family:'DM Mono',monospace;color:#6b7a99;}
[data-baseweb="tab-list"]{background-color:#161b27!important;border-bottom:1px solid #2a3350!important;gap:4px;}
[data-baseweb="tab"]{color:#8896b3!important;font-weight:500!important;}
[aria-selected="true"]{color:#fff!important;border-bottom:2px solid #4a7cff!important;}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CONSTANTES
# ─────────────────────────────────────────────
MARCAS = ["Seculus", "Mondaine", "Time", "E-time"]

COR_MARCAS = {
    "Seculus":  "#4a7cff",
    "Mondaine": "#f59e0b",
    "Time":     "#10b981",
    "E-time":   "#f43f5e",
}

CORES_CANAL = {
    "Google Ads":          "#4a7cff",
    "Meta Ads":            "#f59e0b",
    "Orgânico":            "#10b981",
    "E-mail":              "#8b5cf6",
    "Influencer/Parceiro": "#f43f5e",
    "Outros":              "#6b7a99",
}

# Campos internos esperados → sinônimos comuns nas planilhas
CAMPOS_SINONIMOS = {
    "data":               ["data", "dt", "dt_venda", "data_pedido", "date", "order_date", "created_at", "data_criacao"],
    "marca":              ["marca", "brand", "loja", "store"],
    "produto":            ["produto", "product", "item", "descricao", "description", "nome_produto", "product_name"],
    "sku":                ["sku", "id_sku", "sku_id", "cod_produto", "codigo_produto", "product_id", "item_sku"],
    "quantidade_vendida": ["quantidade_vendida", "qtd", "qty", "quantidade", "units", "itens", "quantity", "quantity_sku", "qtd_vendida"],
    "valor_unitario":     ["valor_unitario", "preco", "preco_unitario", "price", "unit_price", "sku_selling_price", "selling_price", "preco_venda"],
    "valor_total":        ["valor_total", "total", "vlr_total", "receita", "revenue", "gmv", "preco_total", "sku_total_price", "total_price", "item_total"],
    "status_pedido":      ["status_pedido", "status", "situacao", "order_status", "payment_status", "estado"],
    "origem_cliente":     ["origem_cliente", "origem", "canal", "source", "utm_source", "midia", "traffic_source", "channel"],
    "id_pedido":          ["id_pedido", "pedido", "order_id", "num_pedido", "codigo", "id_order", "numero_pedido", "order_number"],
}

CAMPOS_OBRIGATORIOS = ["data", "valor_total", "status_pedido"]

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
    d = dict(_BASE_LAYOUT); d["yaxis"] = dict(_YAXIS_BASE); d.update(extra); return d

def layout_invertido(**extra):
    d = dict(_BASE_LAYOUT); d["yaxis"] = dict(_YAXIS_BASE, autorange="reversed"); d.update(extra); return d

# ─────────────────────────────────────────────
# UTILITÁRIOS GERAIS
# ─────────────────────────────────────────────

def calcular_variacao(atual, anterior):
    if not anterior or anterior == 0:
        return None
    return ((atual - anterior) / anterior) * 100

def formatar_variacao(val):
    return f"{val:+.1f}%" if val is not None else None

def filtrar_periodo(df, d_ini, d_fim):
    if df.empty:
        return df
    return df[(df["data"] >= pd.Timestamp(d_ini)) & (df["data"] <= pd.Timestamp(d_fim))]

def calcular_periodo_anterior(inicio, fim, modo):
    if modo == "Período anterior equivalente":
        delta = fim - inicio
        return inicio - delta - timedelta(days=1), inicio - timedelta(days=1)
    elif modo == "Mês anterior":
        p = inicio.replace(day=1)
        fim_ant = p - timedelta(days=1)
        return fim_ant.replace(day=1), fim_ant
    elif modo == "Mesmo período ano anterior":
        try:
            return inicio.replace(year=inicio.year-1), fim.replace(year=fim.year-1)
        except ValueError:
            return inicio - timedelta(days=365), fim - timedelta(days=365)
    return inicio, fim

def badge_taxa(valor, limiar_bom=10.0):
    if valor <= limiar_bom:
        return f"<span class='badge-verde'>{valor:.1f}%</span>"
    elif valor <= 20:
        return f"<span class='badge-amarelo'>{valor:.1f}%</span>"
    else:
        return f"<span class='badge-vermelho'>{valor:.1f}%</span>"

def hex_to_rgba(hex_color, alpha=0.1):
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
    return f"rgba({r},{g},{b},{alpha})"

def classificar_tipo_canal(origem):
    o = str(origem).lower().strip()
    if any(w in o for w in ["google","gads","adwords","cpc","ppc","search"]):
        return "Google Ads"
    elif any(w in o for w in ["meta","facebook","instagram","fb","ig"]):
        return "Meta Ads"
    elif any(w in o for w in ["orgânico","organico","organic","seo","direct","direto"]):
        return "Orgânico"
    elif any(w in o for w in ["email","e-mail","newsletter"]):
        return "E-mail"
    elif any(w in o for w in ["influencer","influenciador","parceiro"]):
        return "Influencer/Parceiro"
    return "Outros"

# ─────────────────────────────────────────────
# MAPEAMENTO DE COLUNAS
# ─────────────────────────────────────────────

def detectar_mapeamento_auto(colunas):
    """Tenta mapear automaticamente colunas da planilha para campos internos."""
    mapeamento = {}
    cols_lower = {c: c.lower().strip() for c in colunas}
    for campo, sinonimos in CAMPOS_SINONIMOS.items():
        for col_orig, col_low in cols_lower.items():
            if any(s == col_low or s in col_low for s in sinonimos):
                if campo not in mapeamento:
                    mapeamento[campo] = col_orig
    return mapeamento

def aplicar_mapeamento(df, mapeamento):
    """Renomeia colunas do df conforme mapeamento {campo_interno: col_original}."""
    rename = {v: k for k, v in mapeamento.items() if v in df.columns}
    return df.rename(columns=rename)

# ─────────────────────────────────────────────
# CARREGAMENTO DE URL
# ─────────────────────────────────────────────

@st.cache_data(ttl=300)
def carregar_csv_url(url: str):
    """Carrega CSV de URL pública ou Google Sheets. Retorna (df, timestamp_carga)."""
    try:
        url = url.strip()
        if "docs.google.com" in url:
            if "/edit" in url or "/view" in url or "/pub" in url:
                sheet_id = url.split("/d/")[1].split("/")[0]
                gid = url.split("gid=")[1].split("&")[0].split("#")[0] if "gid=" in url else None
                url = (f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
                       + (f"&gid={gid}" if gid else ""))
        headers = {"User-Agent": "Mozilla/5.0", "Accept": "text/csv,text/plain,*/*"}
        r = requests.get(url, timeout=20, headers=headers)
        r.raise_for_status()
        try:
            text = r.content.decode("utf-8")
        except UnicodeDecodeError:
            text = r.content.decode("latin-1")
        df = pd.read_csv(StringIO(text))
        df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
        ts = datetime.now().strftime("%d/%m/%Y %H:%M")
        return df, ts
    except requests.exceptions.HTTPError as e:
        st.error(f"❌ Erro HTTP: {e}. Confirme que a planilha está compartilhada publicamente.")
        return pd.DataFrame(), None
    except Exception as e:
        st.error(f"❌ Erro ao carregar: {e}")
        return pd.DataFrame(), None

# ─────────────────────────────────────────────
# PREPARAÇÃO DO DATAFRAME
# ─────────────────────────────────────────────

def limpar_numero(series):
    """Converte coluna de texto/número para float, tratando R$, pontos e vírgulas."""
    return (
        series.astype(str)
        .str.replace(r"[R$\s]", "", regex=True)
        .str.replace(r"\.(?=\d{3})", "", regex=True)   # remove ponto de milhar
        .str.replace(",", ".", regex=False)
        .pipe(pd.to_numeric, errors="coerce")
        .fillna(0)
    )

def preparar_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Data
    df["data"] = pd.to_datetime(df["data"], dayfirst=True, errors="coerce")
    df.dropna(subset=["data"], inplace=True)

    # Numéricos
    for col in ["valor_total", "quantidade_vendida", "valor_unitario"]:
        if col in df.columns:
            df[col] = limpar_numero(df[col])

    # ── Lógica de pedidos desmembrados por SKU ──────────────────────────────
    # Um mesmo id_pedido pode aparecer em N linhas (uma por SKU).
    # Regras:
    #   • quantidade_vendida = qtd daquele SKU na linha
    #   • valor_unitario     = preço unitário do SKU
    #   • valor_total        = valor_unitario × quantidade_vendida  (por linha)
    #   • O pedido (id_pedido) é contado UMA única vez para KPIs de pedidos
    #   • status_pedido é herdado do pedido — se qualquer linha estiver
    #     "faturado", o pedido inteiro é faturado (usa o status mais recente/
    #     mais avançado da hierarquia)
    #
    # Se valor_total estiver zerado mas valor_unitario e quantidade_vendida
    # existirem, recalcula automaticamente.
    if "valor_unitario" in df.columns and "quantidade_vendida" in df.columns:
        mask_recalc = (df["valor_total"] == 0) & (df["valor_unitario"] > 0)
        df.loc[mask_recalc, "valor_total"] = (
            df.loc[mask_recalc, "valor_unitario"] * df.loc[mask_recalc, "quantidade_vendida"]
        )

    # Status
    if "status_pedido" in df.columns:
        df["status_pedido"] = df["status_pedido"].astype(str).str.strip().str.lower()
        df["faturado"]  = df["status_pedido"].isin(
            ["faturado","entregue","concluído","concluido","aprovado","complete","completed","paid","pago"]
        )
        df["cancelado"] = df["status_pedido"].isin(
            ["cancelado","cancelada","devolvido","devolvida","canceled","cancelled","returned"]
        )
        df["pendente"] = ~df["faturado"] & ~df["cancelado"]

    # Garantir id_pedido
    if "id_pedido" not in df.columns:
        df["id_pedido"] = df.index.astype(str)
    else:
        df["id_pedido"] = df["id_pedido"].astype(str).str.strip()

    # Origem / canal
    if "origem_cliente" in df.columns:
        df["campanha"]   = df["origem_cliente"].astype(str).str.strip().str.title()
        df["tipo_canal"] = df["origem_cliente"].apply(classificar_tipo_canal)
        df["canal"]      = df["tipo_canal"]

    # Mês
    df["mes"] = df["data"].dt.to_period("M").astype(str)

    return df

# ─────────────────────────────────────────────
# MÉTRICAS DE PEDIDOS (considera linhas desmembradas)
# ─────────────────────────────────────────────

def calcular_metricas_pedidos(df: pd.DataFrame) -> dict:
    """
    Calcula métricas corretas para pedidos que podem ter múltiplas linhas de SKU.

    Pedidos únicos = id_pedido.nunique()
    Status do pedido = status MAIS AVANÇADO entre as linhas do mesmo id_pedido
      Hierarquia: faturado > pendente > cancelado
      (se ao menos 1 linha estiver faturada, o pedido é faturado)
    Receita = soma de valor_total de TODAS as linhas (faturadas)
    Itens   = soma de quantidade_vendida de TODAS as linhas
    """
    if df.empty:
        return {"pedidos":0,"faturados":0,"cancelados":0,"pendentes":0,
                "itens":0,"itens_fat":0,"receita":0,"ticket_medio":0}

    # Agrega por pedido para definir status do pedido inteiro
    agg = df.groupby("id_pedido").agg(
        tem_faturado  =("faturado",  "any"),
        tem_cancelado =("cancelado", "any") if "cancelado" in df.columns else ("faturado", "count"),
        receita_pedido=("valor_total","sum"),
        itens_pedido  =("quantidade_vendida","sum") if "quantidade_vendida" in df.columns else ("valor_total","count"),
    ).reset_index()

    agg["status_ped"] = "pendente"
    agg.loc[agg["tem_cancelado"] & ~agg["tem_faturado"], "status_ped"] = "cancelado"
    agg.loc[agg["tem_faturado"], "status_ped"] = "faturado"

    pedidos   = len(agg)
    faturados = int((agg["status_ped"] == "faturado").sum())
    cancelados= int((agg["status_ped"] == "cancelado").sum())
    pendentes = int((agg["status_ped"] == "pendente").sum())
    receita   = float(agg.loc[agg["status_ped"] == "faturado", "receita_pedido"].sum())
    itens     = int(df["quantidade_vendida"].sum()) if "quantidade_vendida" in df.columns else len(df)
    itens_fat = int(df.loc[df["faturado"], "quantidade_vendida"].sum()) if "quantidade_vendida" in df.columns else faturados
    ticket    = float(agg.loc[agg["status_ped"]=="faturado","receita_pedido"].mean()) if faturados > 0 else 0

    return {
        "pedidos": pedidos, "faturados": faturados,
        "cancelados": cancelados, "pendentes": pendentes,
        "itens": itens, "itens_fat": itens_fat,
        "receita": receita, "ticket_medio": ticket,
    }

# ─────────────────────────────────────────────
# ALERTAS PROATIVOS
# ─────────────────────────────────────────────

def verificar_alertas(df_atual, df_ant, cfg_alertas):
    """Retorna lista de alertas com base nos limiares configurados."""
    alertas = []
    m = calcular_metricas_pedidos(df_atual)
    m_ant = calcular_metricas_pedidos(df_ant) if not df_ant.empty else {}

    # Cancelamento
    limiar_canc = cfg_alertas.get("limiar_cancelamento", 15)
    if m["pedidos"] > 0:
        taxa_canc = m["cancelados"] / m["pedidos"] * 100
        if taxa_canc > limiar_canc:
            alertas.append(("🔴", f"Taxa de cancelamento em <strong>{taxa_canc:.1f}%</strong> — acima do limiar de {limiar_canc}%."))

    # Queda de receita
    limiar_queda = cfg_alertas.get("limiar_queda_receita", 20)
    if m_ant.get("receita", 0) > 0:
        var = calcular_variacao(m["receita"], m_ant["receita"])
        if var is not None and var < -limiar_queda:
            alertas.append(("🔴", f"Receita caiu <strong>{abs(var):.1f}%</strong> vs. período anterior — abaixo do limiar de -{limiar_queda}%."))

    return alertas

# ─────────────────────────────────────────────
# CONSOLIDAÇÃO
# ─────────────────────────────────────────────

def consolidar(marcas_sel, canais_sel, campanhas_sel, d_ini, d_fim):
    frames = []
    for m in marcas_sel:
        if m not in st.session_state.dfs:
            continue
        df_m = filtrar_periodo(st.session_state.dfs[m], d_ini, d_fim)
        if df_m.empty:
            continue
        if "canal" in df_m.columns and canais_sel:
            df_m = df_m[df_m["canal"].isin(canais_sel)]
        if "campanha" in df_m.columns and campanhas_sel:
            df_m = df_m[df_m["campanha"].isin(campanhas_sel)]
        frames.append(df_m)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

# ─────────────────────────────────────────────
# EXPORTAÇÃO
# ─────────────────────────────────────────────

def gerar_resumo_texto(df, marcas, d_ini, d_fim):
    m = calcular_metricas_pedidos(df)
    top_prod = ""
    if "produto" in df.columns and "quantidade_vendida" in df.columns:
        top3 = (df.groupby("produto")["quantidade_vendida"].sum()
                .nlargest(3).index.tolist())
        top_prod = ", ".join(top3)
    melhor_canal = ""
    if "canal" in df.columns:
        mc = (df.groupby("canal")["valor_total"].sum().idxmax()
              if not df.groupby("canal")["valor_total"].sum().empty else "—")
        melhor_canal = mc

    return (
        f"📊 Resumo de Vendas — {d_ini.strftime('%d/%m/%Y')} a {d_fim.strftime('%d/%m/%Y')}\n"
        f"Marcas: {', '.join(marcas)}\n\n"
        f"• Receita faturada: R$ {m['receita']:,.0f}\n"
        f"• Pedidos realizados: {m['pedidos']:,}\n"
        f"• Pedidos faturados: {m['faturados']:,}  |  Cancelados: {m['cancelados']:,}\n"
        f"• Ticket médio: R$ {m['ticket_medio']:,.0f}\n"
        f"• Top produtos: {top_prod or '—'}\n"
        f"• Canal com maior receita: {melhor_canal or '—'}"
    )

# ─────────────────────────────────────────────
# TEMPLATE CSV
# ─────────────────────────────────────────────
TEMPLATE_CSV = """id_pedido,data,marca,produto,sku,quantidade_vendida,valor_unitario,valor_total,status_pedido,origem_cliente
PED001,01/01/2025,Seculus,Relógio Seculus Slim,SKU001,1,350.00,350.00,faturado,google ads
PED001,01/01/2025,Seculus,Pulseira Extra Slim,SKU002,2,80.00,160.00,faturado,google ads
PED002,02/01/2025,Seculus,Relógio Seculus Sport,SKU003,1,420.00,420.00,pendente,meta ads
PED003,03/01/2025,Mondaine,Relógio Mondaine Digital,SKU010,3,280.00,840.00,faturado,organico
PED004,04/01/2025,Time,Relógio Time Classic,SKU020,2,190.00,380.00,faturado,instagram
PED005,05/01/2025,E-time,Relógio E-time Sport,SKU030,1,250.00,250.00,cancelado,direto
"""
# Nota: PED001 aparece em 2 linhas (2 SKUs diferentes) — exemplo de pedido desmembrado.

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
for key, default in [
    ("dfs", {}),
    ("timestamps", {}),
    ("mapeamentos", {}),
    ("aguardando_mapeamento", {}),
    ("dfs_raw", {}),
    ("cfg_alertas", {"limiar_cancelamento": 15, "limiar_queda_receita": 20}),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
_, col_title, _ = st.columns([1, 6, 1])
with col_title:
    st.markdown("## ⌚ Dashboard de Vendas · Grupo Seculus")
    st.markdown(
        "<p style='color:#8896b3;margin-top:-10px;font-size:.9rem;'>"
        "Análise comparativa de performance por marca e período</p>",
        unsafe_allow_html=True,
    )
st.markdown("---")

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Configurações")
    st.markdown("---")

    # ── Template ──
    st.markdown("**📄 Template de Planilha**")
    st.download_button("⬇️ Baixar template CSV", data=TEMPLATE_CSV,
                       file_name="template_vendas.csv", mime="text/csv",
                       use_container_width=True)
    st.markdown(
        "<div style='font-size:.72rem;color:#6b7a99;margin-top:4px;'>"
        "Colunas obrigatórias: <code>data · valor_total · status_pedido</code><br>"
        "Colunas recomendadas: <code>id_pedido · marca · produto · sku · "
        "quantidade_vendida · valor_unitario · origem_cliente</code></div>",
        unsafe_allow_html=True,
    )
    st.markdown("---")

    # ── Fontes por marca ──
    st.markdown("**🔗 Fontes de Dados por Marca**")
    st.markdown(
        "<div style='font-size:.75rem;color:#6b7a99;margin-bottom:10px;'>"
        "Cole o link do Google Sheets (compartilhado) ou URL de um CSV público</div>",
        unsafe_allow_html=True,
    )

    for marca in MARCAS:
        carregado = marca in st.session_state.dfs
        ts = st.session_state.timestamps.get(marca, "")
        cor_dot = "#10b981" if carregado else "#374151"
        label_ts = f" · {ts}" if ts else ""

        with st.expander(f"⌚ {marca}", expanded=(marca == "Seculus" and not carregado)):
            if carregado:
                st.markdown(
                    f"<div class='source-status'>"
                    f"<span style='color:{cor_dot};font-size:1rem;'>●</span>"
                    f" Conectado{label_ts}</div>",
                    unsafe_allow_html=True,
                )

            url_input = st.text_input(
                f"URL — {marca}", key=f"url_{marca}",
                placeholder="https://docs.google.com/spreadsheets/d/...",
                label_visibility="collapsed",
            )

            c1, c2 = st.columns([3, 1])
            with c1:
                if st.button(f"Carregar {marca}", key=f"btn_{marca}", use_container_width=True):
                    if url_input.strip():
                        with st.spinner("Buscando dados..."):
                            df_raw, ts_carga = carregar_csv_url(url_input.strip())
                        if not df_raw.empty:
                            st.session_state.dfs_raw[marca] = df_raw
                            st.session_state.timestamps[marca] = ts_carga
                            # Detecta mapeamento automático
                            mapa_auto = detectar_mapeamento_auto(list(df_raw.columns))
                            st.session_state.mapeamentos[marca] = mapa_auto
                            # Verifica se precisa de mapeamento manual
                            faltando = [c for c in CAMPOS_OBRIGATORIOS if c not in mapa_auto]
                            if faltando:
                                st.session_state.aguardando_mapeamento[marca] = True
                                st.warning(f"Mapeamento necessário para: {', '.join(faltando)}")
                            else:
                                df_mapeado = aplicar_mapeamento(df_raw, mapa_auto)
                                st.session_state.dfs[marca] = preparar_df(df_mapeado)
                                n = len(st.session_state.dfs[marca])
                                pedidos_u = st.session_state.dfs[marca]["id_pedido"].nunique()
                                st.success(f"✅ {n} linhas · {pedidos_u} pedidos únicos")
                    else:
                        st.warning("Insira uma URL válida.")

            with c2:
                if carregado:
                    if st.button("🔄", key=f"reload_{marca}", help="Recarregar dados"):
                        # Limpa cache e recarrega
                        carregar_csv_url.clear()
                        st.session_state.pop(marca, None)
                        st.rerun()

            # ── Interface de mapeamento manual ──
            if st.session_state.aguardando_mapeamento.get(marca) and marca in st.session_state.dfs_raw:
                st.markdown("**⚙️ Configure o mapeamento de colunas:**")
                df_raw_m = st.session_state.dfs_raw[marca]
                colunas_disp = ["— não usar —"] + list(df_raw_m.columns)
                mapa_atual = st.session_state.mapeamentos.get(marca, {})

                novo_mapa = {}
                for campo, sinonimos in CAMPOS_SINONIMOS.items():
                    obrig = "* " if campo in CAMPOS_OBRIGATORIOS else ""
                    sugestao = mapa_atual.get(campo, "— não usar —")
                    idx_sug = colunas_disp.index(sugestao) if sugestao in colunas_disp else 0
                    escolha = st.selectbox(
                        f"{obrig}{campo}",
                        colunas_disp,
                        index=idx_sug,
                        key=f"map_{marca}_{campo}",
                        help=f"Sinônimos detectados: {', '.join(sinonimos[:4])}...",
                    )
                    if escolha != "— não usar —":
                        novo_mapa[campo] = escolha

                # Preview dos dados
                with st.expander("👁️ Preview (primeiras 3 linhas)"):
                    st.dataframe(df_raw_m.head(3), use_container_width=True)

                faltando_conf = [c for c in CAMPOS_OBRIGATORIOS if c not in novo_mapa]
                if faltando_conf:
                    st.error(f"Obrigatórios sem mapeamento: {', '.join(faltando_conf)}")
                else:
                    if st.button(f"✅ Confirmar mapeamento — {marca}", key=f"conf_{marca}"):
                        df_mapeado = aplicar_mapeamento(df_raw_m, novo_mapa)
                        st.session_state.dfs[marca] = preparar_df(df_mapeado)
                        st.session_state.mapeamentos[marca] = novo_mapa
                        st.session_state.aguardando_mapeamento[marca] = False
                        n = len(st.session_state.dfs[marca])
                        pu = st.session_state.dfs[marca]["id_pedido"].nunique()
                        st.success(f"✅ {n} linhas · {pu} pedidos únicos")
                        st.rerun()

    st.markdown("---")

    # ── Exportar / importar configuração de mapeamentos ──
    if st.session_state.mapeamentos:
        cfg_json = json.dumps(st.session_state.mapeamentos, ensure_ascii=False, indent=2)
        st.download_button(
            "💾 Exportar configuração de colunas", data=cfg_json,
            file_name="mapeamento_colunas.json", mime="application/json",
            use_container_width=True,
        )

    cfg_upload = st.file_uploader("📂 Importar configuração", type="json",
                                   key="cfg_import", label_visibility="collapsed")
    if cfg_upload:
        try:
            imported = json.load(cfg_upload)
            st.session_state.mapeamentos.update(imported)
            st.success("Configuração importada.")
        except Exception:
            st.error("Arquivo inválido.")

    st.markdown("---")

    # ── Período ──
    st.markdown("**📅 Período de Análise**")
    hoje = datetime.today().date()

    # Atalhos de período
    col_a1, col_a2, col_a3 = st.columns(3)
    with col_a1:
        if st.button("7d", use_container_width=True, key="atalho_7d"):
            st.session_state["data_inicio"] = hoje - timedelta(days=7)
            st.session_state["data_fim"]    = hoje
    with col_a2:
        if st.button("30d", use_container_width=True, key="atalho_30d"):
            st.session_state["data_inicio"] = hoje - timedelta(days=30)
            st.session_state["data_fim"]    = hoje
    with col_a3:
        if st.button("Mês", use_container_width=True, key="atalho_mes"):
            st.session_state["data_inicio"] = hoje.replace(day=1)
            st.session_state["data_fim"]    = hoje

    col_b1, col_b2 = st.columns(2)
    with col_b1:
        if st.button("Ano", use_container_width=True, key="atalho_ano"):
            st.session_state["data_inicio"] = hoje.replace(month=1, day=1)
            st.session_state["data_fim"]    = hoje
    with col_b2:
        if st.button("Hoje", use_container_width=True, key="atalho_hoje"):
            st.session_state["data_inicio"] = hoje
            st.session_state["data_fim"]    = hoje

    default_ini = st.session_state.get("data_inicio", hoje - timedelta(days=30))
    default_fim = st.session_state.get("data_fim", hoje)

    data_inicio = st.date_input("De",  value=default_ini, key="data_inicio")
    data_fim    = st.date_input("Até", value=default_fim, key="data_fim")

    comparar_periodo = st.selectbox(
        "Comparar com",
        ["Período anterior equivalente", "Mês anterior", "Mesmo período ano anterior"],
        index=0,
    )

    st.markdown("---")

    # ── Filtros ──
    st.markdown("**🔍 Filtros**")
    marcas_disponiveis = [m for m in MARCAS if m in st.session_state.dfs]
    marcas_selecionadas = st.multiselect(
        "Marcas", marcas_disponiveis, default=marcas_disponiveis, key="marcas_sel"
    )

    tipos_canal_opcoes = ["Google Ads", "Meta Ads", "Orgânico", "E-mail", "Influencer/Parceiro", "Outros"]
    tipos_canal_sel = st.multiselect(
        "Tipo de canal", tipos_canal_opcoes, default=tipos_canal_opcoes, key="tipos_canal_sel"
    )

    campanhas_disp = sorted(set(
        c for df_m in st.session_state.dfs.values()
        if "campanha" in df_m.columns
        for c in df_m["campanha"].dropna().unique()
    ))
    campanhas_sel = (
        st.multiselect("Campanhas", campanhas_disp, default=campanhas_disp, key="camp_sel")
        if campanhas_disp else []
    )

    st.markdown("---")

    # ── Alertas ──
    st.markdown("**🔔 Limiares de Alerta**")
    st.session_state.cfg_alertas["limiar_cancelamento"] = st.slider(
        "Cancelamento (%)", 1, 50,
        value=st.session_state.cfg_alertas.get("limiar_cancelamento", 15),
        key="limiar_canc",
    )
    st.session_state.cfg_alertas["limiar_queda_receita"] = st.slider(
        "Queda de receita (%)", 1, 80,
        value=st.session_state.cfg_alertas.get("limiar_queda_receita", 20),
        key="limiar_queda",
    )

# ─────────────────────────────────────────────
# PERÍODOS E DADOS CONSOLIDADOS
# ─────────────────────────────────────────────
data_inicio_ant, data_fim_ant = calcular_periodo_anterior(data_inicio, data_fim, comparar_periodo)

df_atual = consolidar(marcas_selecionadas, tipos_canal_sel, campanhas_sel, data_inicio, data_fim)
df_ant   = consolidar(marcas_selecionadas, tipos_canal_sel, campanhas_sel, data_inicio_ant, data_fim_ant)

# ─────────────────────────────────────────────
# ESTADO SEM DADOS
# ─────────────────────────────────────────────
if not st.session_state.dfs:
    st.markdown("""
    <div class="upload-section">
        <h2 style='color:#fff;margin:0 0 8px 0;'>Nenhum dado carregado</h2>
        <p style='color:#8896b3;margin:0 0 20px 0;'>
            Carregue os dados de cada marca na barra lateral.<br>
            O dashboard aceita qualquer estrutura de planilha — você mapeia as colunas uma única vez.
        </p>
        <p style='color:#4a7cff;font-size:.85rem;font-family:monospace;'>← Use a barra lateral para inserir os links</p>
    </div>
    """, unsafe_allow_html=True)
    with st.expander("📋 Estrutura de planilha sugerida"):
        st.markdown("""
| Coluna | Obrigatória | Descrição | Exemplo |
|---|:---:|---|---|
| `id_pedido` | — | ID do pedido (repete se multi-SKU) | `PED-001` |
| `data` | ✅ | Data do pedido | `15/01/2025` |
| `marca` | — | Nome da marca | `Seculus` |
| `produto` | — | Nome do produto | `Relógio Slim` |
| `sku` | — | Código do SKU | `SKU001` |
| `quantidade_vendida` | — | Qtd do SKU na linha | `2` |
| `valor_unitario` | — | Preço unitário do SKU | `350.00` |
| `valor_total` | ✅ | Valor total da linha (qty × unit) | `700.00` |
| `status_pedido` | ✅ | Status | `faturado` / `pendente` / `cancelado` |
| `origem_cliente` | — | Canal de aquisição | `google ads` |

**Pedidos desmembrados:** o mesmo `id_pedido` pode aparecer em múltiplas linhas, uma por SKU.
O dashboard consolida automaticamente, contando o pedido uma única vez e somando os valores de todas as linhas.
        """)
    st.stop()

# ─────────────────────────────────────────────
# ALERTAS PROATIVOS — topo da página
# ─────────────────────────────────────────────
alertas = verificar_alertas(df_atual, df_ant, st.session_state.cfg_alertas)
for emoji, msg in alertas:
    st.markdown(f"<div class='alert-box'>{emoji} {msg}</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SELETOR DE PERÍODO inline
# ─────────────────────────────────────────────
col_p1, col_p2, col_p3 = st.columns([5, 1, 5])
with col_p1:
    st.markdown(
        f"<div style='background:#1a2035;border:1px solid #3a4560;border-radius:8px;"
        f"padding:10px 16px;font-size:.82rem;color:#8896b3;font-family:DM Mono,monospace;'>"
        f"📅 <strong style='color:#fff;'>Atual:</strong> "
        f"{data_inicio.strftime('%d/%m/%Y')} → {data_fim.strftime('%d/%m/%Y')}</div>",
        unsafe_allow_html=True,
    )
with col_p2:
    st.markdown("<div style='text-align:center;color:#6b7a99;padding-top:10px;'>vs</div>",
                unsafe_allow_html=True)
with col_p3:
    st.markdown(
        f"<div style='background:#1a2035;border:1px solid #3a4560;border-radius:8px;"
        f"padding:10px 16px;font-size:.82rem;color:#8896b3;font-family:DM Mono,monospace;'>"
        f"📅 <strong style='color:#fff;'>Anterior:</strong> "
        f"{data_inicio_ant.strftime('%d/%m/%Y')} → {data_fim_ant.strftime('%d/%m/%Y')}</div>",
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# RESUMO POR MARCA (cards lado a lado)
# ─────────────────────────────────────────────
marcas_carregadas = [m for m in MARCAS if m in st.session_state.dfs]
if marcas_carregadas:
    st.markdown("### Resumo por Marca")
    cols_res = st.columns(len(marcas_carregadas))
    for idx, marca in enumerate(marcas_carregadas):
        df_full = st.session_state.dfs[marca]
        m = calcular_metricas_pedidos(df_full)
        taxa_canc = (m["cancelados"] / m["pedidos"] * 100) if m["pedidos"] > 0 else 0
        cor = COR_MARCAS.get(marca, "#4a7cff")
        ts_label = st.session_state.timestamps.get(marca, "")
        with cols_res[idx]:
            st.markdown(f"""
            <div class="resumo-card">
                <h4 style='color:{cor};'>{marca}</h4>
                <div class="resumo-linha">
                    <span>Pedidos únicos</span>
                    <span class="resumo-valor">{m['pedidos']:,}</span>
                </div>
                <div class="resumo-linha">
                    <span>Total de itens</span>
                    <span class="resumo-valor">{m['itens']:,}</span>
                </div>
                <div class="resumo-linha">
                    <span>Itens faturados</span>
                    <span class="resumo-valor"><span class='badge-verde'>{m['itens_fat']:,}</span></span>
                </div>
                <div class="resumo-linha">
                    <span>Cancelados</span>
                    <span class="resumo-valor"><span class='badge-vermelho'>{m['cancelados']:,}</span></span>
                </div>
                <div class="resumo-linha">
                    <span>Taxa cancelamento</span>
                    <span class="resumo-valor">{badge_taxa(taxa_canc)}</span>
                </div>
                <div class="resumo-linha">
                    <span>Receita faturada</span>
                    <span class="resumo-valor">R$ {m['receita']:,.0f}</span>
                </div>
                <div class="resumo-linha">
                    <span>Ticket médio</span>
                    <span class="resumo-valor">R$ {m['ticket_medio']:,.0f}</span>
                </div>
                <div style='font-size:.68rem;color:#3a4560;margin-top:8px;font-family:DM Mono,monospace;'>
                    atualizado: {ts_label or "—"}
                </div>
            </div>
            """, unsafe_allow_html=True)

st.markdown("---")

# ─────────────────────────────────────────────
# ABAS
# ─────────────────────────────────────────────
tab_geral, tab_prod, tab_ped, tab_conv, tab_traf, tab_marca_aba = st.tabs([
    "📊 Visão Geral", "🏆 Produtos", "📦 Pedidos",
    "🎯 Conversão", "📡 Tráfego & Origem", "🏷️ Por Marca",
])

# ═══════════════════════════════════════════════════
# ABA 1 — VISÃO GERAL
# ═══════════════════════════════════════════════════
with tab_geral:
    if df_atual.empty:
        st.info("Nenhum dado no período selecionado para as marcas carregadas.")
        st.stop()

    m     = calcular_metricas_pedidos(df_atual)
    m_ant = calcular_metricas_pedidos(df_ant) if not df_ant.empty else {}

    st.markdown("### KPIs do Período")
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("💰 Receita",        f"R$ {m['receita']:,.0f}",
              delta=formatar_variacao(calcular_variacao(m['receita'],      m_ant.get('receita',0))))
    k2.metric("🛒 Pedidos",        f"{m['pedidos']:,}",
              delta=formatar_variacao(calcular_variacao(m['pedidos'],      m_ant.get('pedidos',0))))
    k3.metric("✅ Faturados",      f"{m['faturados']:,}",
              delta=formatar_variacao(calcular_variacao(m['faturados'],    m_ant.get('faturados',0))))
    k4.metric("❌ Cancelados",     f"{m['cancelados']:,}")
    k5.metric("📊 Taxa Fat.",      f"{(m['faturados']/m['pedidos']*100 if m['pedidos'] else 0):.1f}%",
              delta=formatar_variacao(calcular_variacao(
                  m['faturados']/m['pedidos']*100 if m['pedidos'] else 0,
                  m_ant['faturados']/m_ant['pedidos']*100 if m_ant.get('pedidos') else 0)))
    k6.metric("🎟️ Ticket Médio",  f"R$ {m['ticket_medio']:,.0f}",
              delta=formatar_variacao(calcular_variacao(m['ticket_medio'], m_ant.get('ticket_medio',0))))

    st.markdown("<br>", unsafe_allow_html=True)

    # Insight
    if m_ant.get("receita", 0) > 0:
        var = calcular_variacao(m["receita"], m_ant["receita"])
        emoji   = "🟢" if var >= 0 else "🔴"
        direcao = "crescimento" if var >= 0 else "queda"
        st.markdown(
            f"<div class='insight-box'>{emoji} <strong>Insight:</strong> Receita com "
            f"<strong>{direcao} de {abs(var):.1f}%</strong> vs. período anterior — "
            f"de R$ {m_ant['receita']:,.0f} para R$ {m['receita']:,.0f}.</div>",
            unsafe_allow_html=True,
        )

    # Análise 80/20
    if "produto" in df_atual.columns and "valor_total" in df_atual.columns:
        receita_prod = df_atual.groupby("produto")["valor_total"].sum().sort_values(ascending=False)
        total_r = receita_prod.sum()
        if total_r > 0:
            cumsum  = receita_prod.cumsum() / total_r
            n_prod_80 = int((cumsum <= 0.8).sum()) + 1
            pct_prod  = n_prod_80 / len(receita_prod) * 100
            st.markdown(
                f"<div class='insight-box'>📐 <strong>Concentração de receita:</strong> "
                f"Os <strong>{n_prod_80} produtos mais vendidos ({pct_prod:.0f}% do catálogo)</strong> "
                f"respondem por 80% da receita no período.</div>",
                unsafe_allow_html=True,
            )

    st.markdown("---")

    # Evolução receita — linhas spline
    st.markdown("### Evolução de Receita por Marca")
    if "marca" in df_atual.columns:
        df_time = (df_atual[df_atual.get("faturado", pd.Series(True, index=df_atual.index))]
                   .groupby(["data","marca"])["valor_total"].sum().reset_index())
        fig_time = go.Figure()
        for marca in df_time["marca"].unique():
            d = df_time[df_time["marca"]==marca].sort_values("data")
            fig_time.add_trace(go.Scatter(
                x=d["data"], y=d["valor_total"], name=marca, mode="lines",
                line=dict(color=COR_MARCAS.get(marca,"#4a7cff"), width=2.5, shape="spline", smoothing=1.3),
            ))
        fig_time.update_layout(**layout_normal())
        st.plotly_chart(fig_time, use_container_width=True)

    st.markdown("---")
    col_g1, col_g2 = st.columns(2)

    with col_g1:
        st.markdown("### Receita por Marca — Atual vs Anterior")
        if "marca" in df_atual.columns:
            ra = df_atual.groupby("marca")["valor_total"].sum().reset_index()
            rp = df_ant.groupby("marca")["valor_total"].sum().reset_index() if not df_ant.empty else pd.DataFrame(columns=["marca","valor_total"])
            ra.columns = ["marca","atual"]; rp.columns = ["marca","anterior"]
            comp = ra.merge(rp, on="marca", how="left").fillna(0)
            fig_comp = go.Figure([
                go.Bar(name="Anterior", x=comp["marca"], y=comp["anterior"],
                       marker_color="rgba(100,120,160,0.4)", marker_line_width=0),
                go.Bar(name="Atual", x=comp["marca"], y=comp["atual"],
                       marker_color=[COR_MARCAS.get(m,"#4a7cff") for m in comp["marca"]],
                       marker_line_width=0),
            ])
            fig_comp.update_layout(barmode="group", **layout_normal())
            st.plotly_chart(fig_comp, use_container_width=True)

    with col_g2:
        st.markdown("### Share de Receita por Marca")
        if "marca" in df_atual.columns:
            share = df_atual.groupby("marca")["valor_total"].sum().reset_index()
            fig_pie = px.pie(share, names="marca", values="valor_total",
                             color="marca", color_discrete_map=COR_MARCAS, hole=0.55)
            fig_pie.update_traces(textinfo="percent+label", textfont_size=12)
            fig_pie.update_layout(**layout_normal())
            st.plotly_chart(fig_pie, use_container_width=True)

    # Volume mensal por marca
    st.markdown("### Volume Mensal de Itens por Marca")
    if "marca" in df_atual.columns and "quantidade_vendida" in df_atual.columns:
        df_men = df_atual.groupby(["mes","marca"])["quantidade_vendida"].sum().reset_index()
        fig_men = px.bar(df_men, x="mes", y="quantidade_vendida", color="marca",
                         barmode="group", color_discrete_map=COR_MARCAS,
                         labels={"quantidade_vendida":"Itens","mes":"","marca":"Marca"})
        fig_men.update_layout(**layout_normal())
        st.plotly_chart(fig_men, use_container_width=True)

    # Exportação — resumo em texto
    st.markdown("---")
    st.markdown("### Exportar Resumo")
    c_exp1, c_exp2 = st.columns(2)
    with c_exp1:
        resumo_txt = gerar_resumo_texto(df_atual, marcas_selecionadas, data_inicio, data_fim)
        st.download_button("📋 Baixar resumo em texto", data=resumo_txt,
                           file_name="resumo_vendas.txt", mime="text/plain",
                           use_container_width=True)
    with c_exp2:
        csv_export = df_atual.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Exportar dados filtrados (CSV)", data=csv_export,
                           file_name="dados_filtrados.csv", mime="text/csv",
                           use_container_width=True)


# ═══════════════════════════════════════════════════
# ABA 2 — PRODUTOS
# ═══════════════════════════════════════════════════
with tab_prod:
    st.markdown("### 🏆 Produtos")

    if df_atual.empty or "produto" not in df_atual.columns:
        st.info("Nenhum dado de produto disponível no período."); st.stop()

    c_fm, c_fn = st.columns([3,1])
    with c_fm:
        marcas_prod = st.multiselect("Marca", marcas_selecionadas,
                                     default=marcas_selecionadas, key="prod_marcas")
    with c_fn:
        top_n = st.selectbox("Top N", [5,10,15,20], index=1, key="top_n")

    df_prod = df_atual[df_atual["marca"].isin(marcas_prod)] if "marca" in df_atual.columns else df_atual

    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.markdown("**Por quantidade vendida**")
        top_qtd = (df_prod.groupby(["marca","produto"])["quantidade_vendida"]
                   .sum().reset_index()
                   .sort_values("quantidade_vendida", ascending=False).head(top_n))
        fig_qtd = px.bar(top_qtd, x="quantidade_vendida", y="produto", color="marca",
                         orientation="h", color_discrete_map=COR_MARCAS,
                         labels={"quantidade_vendida":"Unidades","produto":""})
        fig_qtd.update_layout(**layout_invertido())
        st.plotly_chart(fig_qtd, use_container_width=True)

    with col_p2:
        st.markdown("**Por receita gerada**")
        top_rec = (df_prod.groupby(["marca","produto"])["valor_total"]
                   .sum().reset_index()
                   .sort_values("valor_total", ascending=False).head(top_n))
        fig_rec = px.bar(top_rec, x="valor_total", y="produto", color="marca",
                         orientation="h", color_discrete_map=COR_MARCAS,
                         labels={"valor_total":"Receita (R$)","produto":""})
        fig_rec.update_layout(**layout_invertido())
        st.plotly_chart(fig_rec, use_container_width=True)

    # Produtos sem venda no período vs. catálogo total
    if st.session_state.dfs and "produto" in df_prod.columns:
        todos_prod = set()
        for m_name in marcas_prod:
            if m_name in st.session_state.dfs and "produto" in st.session_state.dfs[m_name].columns:
                todos_prod.update(st.session_state.dfs[m_name]["produto"].dropna().unique())
        prod_com_venda = set(df_prod["produto"].unique())
        sem_venda = todos_prod - prod_com_venda
        if sem_venda:
            st.markdown(
                f"<div class='warn-box'>⚠️ <strong>{len(sem_venda)} produto(s) sem venda</strong> "
                f"no período selecionado (presentes no histórico total).</div>",
                unsafe_allow_html=True,
            )
            with st.expander(f"Ver {len(sem_venda)} produtos sem venda"):
                st.dataframe(pd.DataFrame(sorted(sem_venda), columns=["Produto"]),
                             use_container_width=True, hide_index=True)

    # Tabela detalhada
    st.markdown("### Detalhamento por Produto")
    group_cols = ["marca","produto"] + (["sku"] if "sku" in df_prod.columns else [])
    resumo_prod = (
        df_prod.groupby(group_cols)
        .agg(
            qtd_vendida  =("quantidade_vendida","sum"),
            receita_total=("valor_total","sum"),
            pedidos      =("id_pedido","nunique"),
        )
        .reset_index()
        .sort_values("receita_total", ascending=False)
    )
    resumo_prod["ticket_medio"] = (resumo_prod["receita_total"] /
                                   resumo_prod["pedidos"].replace(0, np.nan))
    resumo_prod["receita_total"]= resumo_prod["receita_total"].map("R$ {:,.0f}".format)
    resumo_prod["ticket_medio"] = resumo_prod["ticket_medio"].map(
        lambda x: f"R$ {x:,.0f}" if pd.notna(x) else "—")

    st.dataframe(resumo_prod, use_container_width=True, hide_index=True)
    csv_prod = resumo_prod.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Exportar tabela", data=csv_prod,
                       file_name="produtos.csv", mime="text/csv")


# ═══════════════════════════════════════════════════
# ABA 3 — PEDIDOS
# ═══════════════════════════════════════════════════
with tab_ped:
    st.markdown("### 📦 Pedidos")

    if df_atual.empty or "status_pedido" not in df_atual.columns:
        st.info("Nenhum dado de pedidos no período."); st.stop()

    m     = calcular_metricas_pedidos(df_atual)
    m_ant = calcular_metricas_pedidos(df_ant) if not df_ant.empty else {}

    kp1,kp2,kp3,kp4,kp5 = st.columns(5)
    kp1.metric("📥 Realizados", f"{m['pedidos']:,}",
               delta=formatar_variacao(calcular_variacao(m['pedidos'],   m_ant.get('pedidos',0))))
    kp2.metric("✅ Faturados",  f"{m['faturados']:,}",
               delta=formatar_variacao(calcular_variacao(m['faturados'], m_ant.get('faturados',0))))
    kp3.metric("⏳ Pendentes",  f"{m['pendentes']:,}")
    kp4.metric("❌ Cancelados", f"{m['cancelados']:,}")
    taxa_fat_ped = m['faturados']/m['pedidos']*100 if m['pedidos'] else 0
    taxa_ant_ped = m_ant['faturados']/m_ant['pedidos']*100 if m_ant.get('pedidos') else 0
    kp5.metric("📈 Taxa Fat.", f"{taxa_fat_ped:.1f}%",
               delta=formatar_variacao(calcular_variacao(taxa_fat_ped, taxa_ant_ped)))

    st.markdown("<br>", unsafe_allow_html=True)
    col_s1, col_s2 = st.columns(2)

    with col_s1:
        st.markdown("### Status dos Pedidos")
        # Agrega por pedido (não por linha)
        ped_status = (df_atual.groupby("id_pedido")
                      .agg(faturado=("faturado","any"),
                           cancelado=("cancelado","any") if "cancelado" in df_atual.columns else ("faturado","count"))
                      .reset_index())
        ped_status["status"] = "Pendente"
        ped_status.loc[ped_status["cancelado"] & ~ped_status["faturado"], "status"] = "Cancelado"
        ped_status.loc[ped_status["faturado"], "status"] = "Faturado"
        sc = ped_status["status"].value_counts().reset_index()
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
                       marker_color=[COR_MARCAS.get(m,"#4a7cff") for m in pm["marca"]]),
            ])
            fig_pm.update_layout(barmode="group", **layout_normal())
            st.plotly_chart(fig_pm, use_container_width=True)

    # Funil
    st.markdown("### Funil de Conversão")
    fig_funil = go.Figure(go.Funnel(
        y=["Realizados","Faturados","Cancelados"],
        x=[m['pedidos'], m['faturados'], m['cancelados']],
        marker={"color":["#4a7cff","#10b981","#f43f5e"]},
        textinfo="value+percent initial",
    ))
    fig_funil.update_layout(**layout_normal())
    st.plotly_chart(fig_funil, use_container_width=True)

    # Volume diário
    st.markdown("### Volume de Pedidos por Dia")
    if "marca" in df_atual.columns:
        ped_dia = (df_atual.groupby(["data","marca"])["id_pedido"]
                   .nunique().reset_index().rename(columns={"id_pedido":"pedidos"}))
        fig_pd = px.area(ped_dia, x="data", y="pedidos", color="marca",
                         color_discrete_map=COR_MARCAS,
                         labels={"pedidos":"Pedidos","data":""})
        fig_pd.update_layout(**layout_normal())
        st.plotly_chart(fig_pd, use_container_width=True)

    # Tabela
    st.markdown("### Registro de Pedidos")
    cols_ex = [c for c in ["data","marca","id_pedido","produto","sku",
                            "quantidade_vendida","valor_total","status_pedido","canal"]
               if c in df_atual.columns]
    df_tab = df_atual[cols_ex].sort_values("data", ascending=False)
    st.dataframe(df_tab, use_container_width=True, hide_index=True)
    st.download_button("📥 Exportar pedidos", data=df_tab.to_csv(index=False).encode("utf-8"),
                       file_name="pedidos.csv", mime="text/csv")


# ═══════════════════════════════════════════════════
# ABA 4 — CONVERSÃO
# ═══════════════════════════════════════════════════
with tab_conv:
    st.markdown("### 🎯 Conversão")

    if df_atual.empty or "faturado" not in df_atual.columns:
        st.info("Sem dados de conversão."); st.stop()

    col_c1, col_c2 = st.columns(2)

    with col_c1:
        st.markdown("**Taxa de Conversão por Marca — Atual vs Anterior**")
        if "marca" in df_atual.columns:
            # Converte por pedido (não por linha)
            def taxa_por_pedido(df):
                if df.empty: return pd.DataFrame(columns=["marca","taxa"])
                g = (df.groupby(["id_pedido","marca"])
                     .agg(faturado=("faturado","any")).reset_index())
                return (g.groupby("marca")
                        .apply(lambda x: x["faturado"].mean()*100)
                        .reset_index().rename(columns={0:"taxa"}))
            ca = taxa_por_pedido(df_atual)
            cp = taxa_por_pedido(df_ant).rename(columns={"taxa":"taxa_ant"}) if not df_ant.empty else pd.DataFrame(columns=["marca","taxa_ant"])
            cm = ca.merge(cp, on="marca", how="left").fillna(0)
            fig_cv = go.Figure([
                go.Bar(name="Anterior", x=cm["marca"], y=cm["taxa_ant"],
                       marker_color="rgba(100,120,160,0.4)"),
                go.Bar(name="Atual",    x=cm["marca"], y=cm["taxa"],
                       marker_color=[COR_MARCAS.get(m,"#4a7cff") for m in cm["marca"]]),
            ])
            fig_cv.update_layout(barmode="group", yaxis_ticksuffix="%", **layout_normal())
            st.plotly_chart(fig_cv, use_container_width=True)

    with col_c2:
        st.markdown("**Evolução da Taxa de Conversão**")
        if "marca" in df_atual.columns:
            # Agrupa por dia e marca, usando pedidos únicos
            ct = (df_atual.groupby(["data","id_pedido","marca"])
                  .agg(faturado=("faturado","any")).reset_index()
                  .groupby(["data","marca"])
                  .apply(lambda x: x["faturado"].mean()*100)
                  .reset_index().rename(columns={0:"conv"}))
            fig_cvt = go.Figure()
            for marca in ct["marca"].unique():
                d = ct[ct["marca"]==marca].sort_values("data")
                fig_cvt.add_trace(go.Scatter(
                    x=d["data"], y=d["conv"], name=marca, mode="lines",
                    line=dict(color=COR_MARCAS.get(marca,"#4a7cff"), width=2.5, shape="spline", smoothing=1.3),
                ))
            fig_cvt.update_layout(**layout_normal(), yaxis_ticksuffix="%")
            st.plotly_chart(fig_cvt, use_container_width=True)

    # Insight canal com maior ticket
    if "canal" in df_atual.columns:
        tick_canal = (df_atual[df_atual["faturado"]]
                      .groupby(["id_pedido","canal"])["valor_total"].sum().reset_index()
                      .groupby("canal")["valor_total"].mean())
        if not tick_canal.empty:
            melhor_tk = tick_canal.idxmax()
            st.markdown(
                f"<div class='insight-box'>🎟️ <strong>Canal com maior ticket médio: {melhor_tk}</strong> — "
                f"R$ {tick_canal[melhor_tk]:,.0f} por pedido faturado.</div>",
                unsafe_allow_html=True,
            )

    # Conversão por canal
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
        st.info("Coluna `origem_cliente` não encontrada — adicione-a à planilha."); st.stop()

    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.markdown("**Distribuição por Canal**")
        cc = df_atual["canal"].value_counts().reset_index()
        cc.columns = ["canal","pedidos"]
        fig_cc2 = px.pie(cc, names="canal", values="pedidos",
                         color="canal", color_discrete_map=CORES_CANAL, hole=0.55)
        fig_cc2.update_traces(textinfo="percent+label")
        fig_cc2.update_layout(**layout_normal())
        st.plotly_chart(fig_cc2, use_container_width=True)

    with col_t2:
        st.markdown("**Receita por Canal**")
        cr = (df_atual.groupby("canal")["valor_total"].sum()
              .reset_index().sort_values("valor_total", ascending=True))
        fig_cr = px.bar(cr, x="valor_total", y="canal", orientation="h",
                        color="canal", color_discrete_map=CORES_CANAL,
                        labels={"valor_total":"Receita (R$)","canal":""})
        fig_cr.update_layout(**layout_invertido())
        st.plotly_chart(fig_cr, use_container_width=True)

    # Atual vs anterior por canal
    st.markdown("### Canal: Atual vs Período Anterior")
    ca_agg = df_atual.groupby("canal").agg(
        pedidos=("id_pedido","nunique"), receita=("valor_total","sum"),
        faturados=("faturado","sum")).reset_index()

    if not df_ant.empty and "canal" in df_ant.columns:
        cp_agg = (df_ant.groupby("canal")
                  .agg(ped_ant=("id_pedido","nunique"), rec_ant=("valor_total","sum"))
                  .reset_index())
        ccomp = ca_agg.merge(cp_agg, on="canal", how="left").fillna(0)
        ccomp["var"] = ccomp.apply(lambda r: formatar_variacao(
            calcular_variacao(r["receita"], r["rec_ant"])) or "—", axis=1)
        fig_ccp = go.Figure([
            go.Bar(name="Anterior", x=ccomp["canal"], y=ccomp["rec_ant"],
                   marker_color="rgba(100,120,160,0.4)"),
            go.Bar(name="Atual", x=ccomp["canal"], y=ccomp["receita"],
                   marker_color=[CORES_CANAL.get(c,"#4a7cff") for c in ccomp["canal"]],
                   text=ccomp["var"], textposition="outside"),
        ])
        fig_ccp.update_layout(barmode="group", **layout_normal())
        st.plotly_chart(fig_ccp, use_container_width=True)

    # Canal x Marca
    st.markdown("### Canal por Marca")
    if "marca" in df_atual.columns:
        cm2 = df_atual.groupby(["marca","canal"])["valor_total"].sum().reset_index()
        fig_cm2 = px.bar(cm2, x="marca", y="valor_total", color="canal",
                         color_discrete_map=CORES_CANAL, barmode="stack",
                         labels={"valor_total":"Receita (R$)","marca":"","canal":"Canal"})
        fig_cm2.update_layout(**layout_normal())
        st.plotly_chart(fig_cm2, use_container_width=True)

    # Resumo por canal
    st.markdown("### Resumo por Canal")
    canal_tab = ca_agg.copy()
    canal_tab["taxa_conv"] = (canal_tab["faturados"] /
                              canal_tab["pedidos"].replace(0,np.nan) * 100).map("{:.1f}%".format)
    canal_tab["receita_fmt"] = canal_tab["receita"].map("R$ {:,.0f}".format)
    canal_tab = canal_tab.rename(columns={
        "canal":"Canal","pedidos":"Pedidos","faturados":"Faturados",
        "taxa_conv":"Taxa Conv.","receita_fmt":"Receita"})
    st.dataframe(canal_tab[["Canal","Pedidos","Faturados","Taxa Conv.","Receita"]],
                 use_container_width=True, hide_index=True)
    st.download_button("📥 Exportar", data=canal_tab.to_csv(index=False).encode("utf-8"),
                       file_name="canais.csv", mime="text/csv")

    # Detalhamento por campanha
    st.markdown("### Detalhamento por Campanha")
    if "campanha" in df_atual.columns and "tipo_canal" in df_atual.columns:
        camp_a = df_atual.groupby(["tipo_canal","campanha"]).agg(
            pedidos=("id_pedido","nunique"),
            faturados=("faturado","sum"),
            receita=("valor_total","sum"),
        ).reset_index()
        if not df_ant.empty and "campanha" in df_ant.columns:
            camp_p = df_ant.groupby("campanha").agg(
                rec_ant=("valor_total","sum")).reset_index()
            camp_a = camp_a.merge(camp_p, on="campanha", how="left").fillna(0)
            camp_a["var"] = camp_a.apply(
                lambda r: formatar_variacao(calcular_variacao(r["receita"],r["rec_ant"])) or "—", axis=1)
        else:
            camp_a["var"] = "—"
        camp_a["taxa_conv"] = (camp_a["faturados"] /
                               camp_a["pedidos"].replace(0,np.nan) * 100).map("{:.1f}%".format)
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
            "faturados":"Faturados","taxa_conv":"Taxa Conv.","receita":"Receita","var":"Var. vs Ant."})
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
        st.info("Nenhuma marca selecionada."); st.stop()

    marca_sel = st.selectbox("Marca", marcas_selecionadas, key="marca_ind")

    if marca_sel and marca_sel in st.session_state.dfs:
        df_ma = filtrar_periodo(st.session_state.dfs[marca_sel], data_inicio, data_fim)
        df_mp = filtrar_periodo(st.session_state.dfs[marca_sel], data_inicio_ant, data_fim_ant)

        if df_ma.empty:
            st.info(f"Sem dados para {marca_sel} no período."); st.stop()

        m_a = calcular_metricas_pedidos(df_ma)
        m_p = calcular_metricas_pedidos(df_mp) if not df_mp.empty else {}

        km1,km2,km3,km4,km5 = st.columns(5)
        km1.metric("Receita", f"R$ {m_a['receita']:,.0f}",
                   delta=formatar_variacao(calcular_variacao(m_a['receita'],   m_p.get('receita',0))))
        km2.metric("Pedidos", f"{m_a['pedidos']:,}",
                   delta=formatar_variacao(calcular_variacao(m_a['pedidos'],   m_p.get('pedidos',0))))
        km3.metric("Faturados", f"{m_a['faturados']:,}",
                   delta=formatar_variacao(calcular_variacao(m_a['faturados'], m_p.get('faturados',0))))
        km4.metric("Cancelados", f"{m_a['cancelados']:,}")
        km5.metric("Ticket Médio", f"R$ {m_a['ticket_medio']:,.0f}",
                   delta=formatar_variacao(calcular_variacao(m_a['ticket_medio'], m_p.get('ticket_medio',0))))

        st.markdown("<br>", unsafe_allow_html=True)
        col_m1, col_m2 = st.columns(2)

        with col_m1:
            st.markdown(f"**Top 10 Produtos — {marca_sel}**")
            if "produto" in df_ma.columns and "quantidade_vendida" in df_ma.columns:
                top_m = (df_ma.groupby("produto")["quantidade_vendida"]
                         .sum().nlargest(10).reset_index())
                fig_tm = px.bar(top_m, x="quantidade_vendida", y="produto", orientation="h",
                                color_discrete_sequence=[COR_MARCAS.get(marca_sel,"#4a7cff")],
                                labels={"quantidade_vendida":"Unidades","produto":""})
                fig_tm.update_layout(**layout_invertido())
                st.plotly_chart(fig_tm, use_container_width=True)

        with col_m2:
            st.markdown(f"**Origem dos Clientes — {marca_sel}**")
            if "canal" in df_ma.columns:
                cm3 = df_ma["canal"].value_counts().reset_index()
                cm3.columns = ["canal","qtd"]
                fig_cm3 = px.pie(cm3, names="canal", values="qtd",
                                 color="canal", color_discrete_map=CORES_CANAL, hole=0.55)
                fig_cm3.update_traces(textinfo="percent+label")
                fig_cm3.update_layout(**layout_normal())
                st.plotly_chart(fig_cm3, use_container_width=True)

        # Receita diária — spline
        st.markdown(f"**Receita Diária — {marca_sel}**")
        rd = df_ma.groupby("data")["valor_total"].sum().reset_index()
        cor_m = COR_MARCAS.get(marca_sel,"#4a7cff")
        fig_rd = go.Figure()
        fig_rd.add_trace(go.Scatter(
            x=rd["data"], y=rd["valor_total"], mode="lines", fill="tozeroy",
            line=dict(color=cor_m, width=2.5, shape="spline", smoothing=1.3),
            fillcolor=hex_to_rgba(cor_m, 0.1),
        ))
        fig_rd.update_layout(**layout_normal())
        st.plotly_chart(fig_rd, use_container_width=True)

        # Receita mensal
        st.markdown(f"**Receita Mensal — {marca_sel}**")
        men_m = df_ma.groupby("mes")["valor_total"].sum().reset_index()
        fig_mm = go.Figure([go.Bar(
            x=men_m["mes"], y=men_m["valor_total"],
            marker_color=COR_MARCAS.get(marca_sel,"#4a7cff"),
        )])
        fig_mm.update_layout(**layout_normal())
        st.plotly_chart(fig_mm, use_container_width=True)

        # Exportar dados da marca
        csv_marca = df_ma.to_csv(index=False).encode("utf-8")
        st.download_button(f"📥 Exportar dados {marca_sel}", data=csv_marca,
                           file_name=f"{marca_sel.lower()}_periodo.csv", mime="text/csv")
    else:
        st.info("Selecione uma marca carregada.")

# ─────────────────────────────────────────────
# RODAPÉ
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#3a4560;font-size:.75rem;font-family:DM Mono,monospace;'>"
    "⌚ Dashboard de Vendas · Grupo Seculus · Cache: 5 min"
    "</div>",
    unsafe_allow_html=True,
)
