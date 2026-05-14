import streamlit as st
import pandas as pd
import plotly.express as px

from src.load_data import carregar_base
from src.sidebar import aplicar_sidebar
from src.theme import (
    card_kpi,
    COR_ESTAVEL,
    COR_ATENCAO,
    COR_CRITICO
)

st.set_page_config(
    page_title="Qualidade dos Dados",
    layout="wide",
    initial_sidebar_state="expanded"
)

df_base = carregar_base()
df, data_inicio, data_fim = aplicar_sidebar(df_base)

df["confiabilidade_total_pad"] = (
    df["confiabilidade_total"]
    .astype(str)
    .str.strip()
    .str.upper()
)

df["confiabilidade_uti_pad"] = (
    df["confiabilidade_uti"]
    .astype(str)
    .str.strip()
    .str.upper()
)

total_registros = df.shape[0]

alta_total = df[df["confiabilidade_total_pad"] == "ALTA"].shape[0]
media_total = df[df["confiabilidade_total_pad"] == "MÉDIA"].shape[0]
baixa_total = df[df["confiabilidade_total_pad"] == "BAIXA"].shape[0]

alta_uti = df[df["confiabilidade_uti_pad"] == "ALTA"].shape[0]
media_uti = df[df["confiabilidade_uti_pad"] == "MÉDIA"].shape[0]
baixa_uti = df[df["confiabilidade_uti_pad"] == "BAIXA"].shape[0]

pct_alta_total = (alta_total / total_registros) * 100 if total_registros > 0 else 0
pct_alta_uti = (alta_uti / total_registros) * 100 if total_registros > 0 else 0

registros_revisao = df[
    (df["confiabilidade_total_pad"] == "BAIXA") |
    (df["confiabilidade_uti_pad"] == "BAIXA")
].copy()

qtd_revisao = registros_revisao.shape[0]
pct_revisao = (qtd_revisao / total_registros) * 100 if total_registros > 0 else 0

if pct_revisao == 0:
    status_conf = "ADEQUADA"
    msg_status = "Não há registros classificados como baixa qualidade."
elif pct_revisao <= 5:
    status_conf = "ATENÇÃO"
    msg_status = "Há poucos registros para revisão metodológica."
else:
    status_conf = "REVISÃO NECESSÁRIA"
    msg_status = "Há volume relevante de registros com baixa qualidade."

cor_revisao = (
    COR_CRITICO if pct_revisao > 5
    else COR_ATENCAO if pct_revisao > 0
    else COR_ESTAVEL
)

st.title("Qualidade dos Dados")

st.markdown(f"""
### Franco da Rocha • OpenDataSUS • 2022

Período selecionado: **{data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}**

Leitura da qualidade dos registros utilizados na construção dos indicadores do dashboard.
""")

if status_conf == "ADEQUADA":
    st.success(f"🟢 Status da qualidade dos dados: {status_conf} — {msg_status}")
elif status_conf == "ATENÇÃO":
    st.warning(f"🟠 Status da qualidade dos dados: {status_conf} — {msg_status}")
else:
    st.error(f"🔴 Status da qualidade dos dados: {status_conf} — {msg_status}")

st.markdown("## Indicadores de qualidade")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        card_kpi("Registros analisados", f"{total_registros}", "Registros após aplicação do filtro.", COR_ESTAVEL),
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        card_kpi("Alta qualidade — Total", f"{pct_alta_total:.1f}%", "Registros consistentes da ocupação total.", COR_ESTAVEL),
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        card_kpi("Alta qualidade — UTI", f"{pct_alta_uti:.1f}%", "Registros consistentes da UTI adulto.", COR_ESTAVEL),
        unsafe_allow_html=True
    )

with col4:
    st.markdown(
        card_kpi("Registros para revisão", f"{qtd_revisao}", f"{pct_revisao:.1f}% da base filtrada.", cor_revisao),
        unsafe_allow_html=True
    )

col5, col6, col7, col8 = st.columns(4)

with col5:
    st.markdown(
        card_kpi("Baixa qualidade — Total", f"{baixa_total}", "Ocupação total.", COR_CRITICO if baixa_total > 0 else COR_ESTAVEL),
        unsafe_allow_html=True
    )

with col6:
    st.markdown(
        card_kpi("Baixa qualidade — UTI", f"{baixa_uti}", "UTI adulto.", COR_CRITICO if baixa_uti > 0 else COR_ESTAVEL),
        unsafe_allow_html=True
    )

with col7:
    st.markdown(
        card_kpi("Média qualidade — Total", f"{media_total}", "Ocupação total.", COR_ATENCAO if media_total > 0 else COR_ESTAVEL),
        unsafe_allow_html=True
    )

with col8:
    st.markdown(
        card_kpi("Média qualidade — UTI", f"{media_uti}", "UTI adulto.", COR_ATENCAO if media_uti > 0 else COR_ESTAVEL),
        unsafe_allow_html=True
    )

st.markdown("---")
st.markdown("## Distribuição da qualidade")

conf_total = df["confiabilidade_total_pad"].value_counts().reset_index()
conf_total.columns = ["Qualidade", "Quantidade"]
conf_total["Indicador"] = "Ocupação Total"

conf_uti = df["confiabilidade_uti_pad"].value_counts().reset_index()
conf_uti.columns = ["Qualidade", "Quantidade"]
conf_uti["Indicador"] = "UTI Adulto"

conf = pd.concat([conf_total, conf_uti], ignore_index=True)

fig = px.bar(
    conf,
    x="Qualidade",
    y="Quantidade",
    color="Indicador",
    barmode="group",
    title="Qualidade por indicador",
    text="Quantidade"
)

fig.update_layout(
    template="plotly_white",
    height=420,
    xaxis_title="Nível de qualidade",
    yaxis_title="Quantidade de registros",
    margin=dict(l=20, r=20, t=50, b=30)
)

fig.update_traces(textposition="outside")

st.plotly_chart(fig, use_container_width=True)

st.markdown("## Registros para revisão")

registros_revisao_tabela = registros_revisao[
    [
        "data",
        "taxa_ocupacao_total",
        "taxa_ocupacao_uti_adulto",
        "confiabilidade_total",
        "confiabilidade_uti",
        "status_total",
        "status_uti"
    ]
].copy()

if registros_revisao_tabela.empty:
    st.success("Não foram identificados registros classificados como baixa qualidade.")
else:
    registros_revisao_tabela["data"] = registros_revisao_tabela["data"].dt.strftime("%d/%m/%Y")
    registros_revisao_tabela["taxa_ocupacao_total"] = (
        registros_revisao_tabela["taxa_ocupacao_total"] * 100
    ).round(1)
    registros_revisao_tabela["taxa_ocupacao_uti_adulto"] = (
        registros_revisao_tabela["taxa_ocupacao_uti_adulto"] * 100
    ).round(1)

    registros_revisao_tabela = registros_revisao_tabela.rename(
        columns={
            "data": "Data",
            "taxa_ocupacao_total": "Taxa Total (%)",
            "taxa_ocupacao_uti_adulto": "Taxa UTI (%)",
            "confiabilidade_total": "Qualidade Total",
            "confiabilidade_uti": "Qualidade UTI",
            "status_total": "Status Total",
            "status_uti": "Status UTI"
        }
    )

    st.dataframe(registros_revisao_tabela, use_container_width=True, height=320)

st.markdown("---")
st.markdown("## Leitura metodológica")

st.info(
    f"Foram analisados {total_registros} registros no período selecionado. "
    f"A ocupação total apresentou {pct_alta_total:.1f}% de registros classificados como alta qualidade, "
    f"enquanto a UTI adulto apresentou {pct_alta_uti:.1f}%. "
    f"O total de registros sinalizados para revisão foi {qtd_revisao}, equivalente a {pct_revisao:.1f}% da base filtrada."
)

with st.expander("Nota metodológica"):
    st.markdown("""
    A qualidade dos dados é tratada como dimensão essencial do dashboard.

    A base de disponibilidade hospitalar possui estrutura predominantemente mensal,
    enquanto a base de ocupação possui estrutura diária. Essa diferença exige cautela interpretativa.

    Esta página não possui objetivo de exclusão automática de registros,
    mas tornar explícito o grau de segurança interpretativa dos indicadores.

    A abordagem reforça rastreabilidade, supervisão humana e redução de risco de interpretação indevida.
    """)