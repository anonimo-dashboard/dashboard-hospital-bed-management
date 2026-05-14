import streamlit as st

from src.load_data import carregar_base
from src.sidebar import aplicar_sidebar

from src.theme import (
    criar_grafico_temporal,
    obter_cor_status,
    card_kpi,
    COR_ESTAVEL,
    COR_ATENCAO,
    COR_CRITICO
)

st.set_page_config(
    page_title="Visão Executiva",
    layout="wide",
    initial_sidebar_state="expanded"
)

df_base = carregar_base()
df, data_inicio, data_fim = aplicar_sidebar(df_base)

dias_monitorados = df["data"].nunique()

ocupacao_media_total = df["taxa_ocupacao_total"].mean() * 100
ocupacao_media_uti = df["taxa_ocupacao_uti_adulto"].mean() * 100

dias_criticos_total = df[df["taxa_ocupacao_total"] >= 1].shape[0]
dias_atencao_total = df[df["taxa_ocupacao_total"] >= 0.80].shape[0]

pico_total = df["taxa_ocupacao_total"].max() * 100
pico_uti = df["taxa_ocupacao_uti_adulto"].max() * 100

if ocupacao_media_total >= 80:
    status_operacional = "CRÍTICO"
    texto_status = "Ocupação média total acima da faixa de atenção."
elif ocupacao_media_total >= 60:
    status_operacional = "ATENÇÃO"
    texto_status = "Ocupação média total em faixa intermediária de monitoramento."
else:
    status_operacional = "ESTÁVEL"
    texto_status = "Ocupação média total abaixo da faixa de atenção."

cor_status = obter_cor_status(ocupacao_media_total)

# ---------------------------------------------------
# CORES DOS KPIs
# ---------------------------------------------------

cor_ocupacao_total = (
    COR_CRITICO if ocupacao_media_total >= 80
    else COR_ATENCAO if ocupacao_media_total >= 60
    else COR_ESTAVEL
)

cor_ocupacao_uti = (
    COR_CRITICO if ocupacao_media_uti >= 80
    else COR_ATENCAO if ocupacao_media_uti >= 60
    else COR_ESTAVEL
)

cor_pico_total = (
    COR_CRITICO if pico_total >= 100
    else COR_ATENCAO if pico_total >= 80
    else COR_ESTAVEL
)

cor_pico_uti = (
    COR_CRITICO if pico_uti >= 100
    else COR_ATENCAO if pico_uti >= 80
    else COR_ESTAVEL
)

pct_dias_atencao = (
    dias_atencao_total / dias_monitorados
    if dias_monitorados > 0 else 0
)

if pct_dias_atencao > 0.30:
    cor_dias_atencao = COR_CRITICO
elif pct_dias_atencao > 0.10:
    cor_dias_atencao = COR_ATENCAO
else:
    cor_dias_atencao = COR_ESTAVEL

pct_dias_criticos = (
    dias_criticos_total / dias_monitorados
    if dias_monitorados > 0 else 0
)

if pct_dias_criticos > 0.05:
    cor_criticos = COR_CRITICO
elif pct_dias_criticos > 0:
    cor_criticos = COR_ATENCAO
else:
    cor_criticos = COR_ESTAVEL

st.title("Visão Executiva")

st.markdown(f"""
### Franco da Rocha • OpenDataSUS • 2022

Período selecionado: **{data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}**

Painel demonstrativo para leitura rápida da ocupação hospitalar, pressão operacional e comportamento temporal.
""")

if status_operacional == "CRÍTICO":
    st.error(f"🔴 Status operacional: {status_operacional} — {texto_status}")
elif status_operacional == "ATENÇÃO":
    st.warning(f"🟠 Status operacional: {status_operacional} — {texto_status}")
else:
    st.success(f"🟢 Status operacional: {status_operacional} — {texto_status}")

st.markdown("## Indicadores principais")

# Linha 1 — Percentuais
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        card_kpi(
            "Ocupação média total",
            f"{ocupacao_media_total:.1f}%",
            "Leitura sistêmica da ocupação.",
            cor_ocupacao_total
        ),
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        card_kpi(
            "Ocupação média UTI",
            f"{ocupacao_media_uti:.1f}%",
            "Pressão sobre leitos críticos.",
            cor_ocupacao_uti
        ),
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        card_kpi(
            "Pico ocupação total",
            f"{pico_total:.1f}%",
            "Maior taxa observada.",
            cor_pico_total
        ),
        unsafe_allow_html=True
    )

with col4:
    st.markdown(
        card_kpi(
            "Pico UTI adulto",
            f"{pico_uti:.1f}%",
            "Maior pressão em UTI.",
            cor_pico_uti
        ),
        unsafe_allow_html=True
    )

# Linha 2 — Dias e contexto
col5, col6, col7, col8 = st.columns(4)

with col5:
    st.markdown(
        card_kpi(
            "Dias monitorados",
            f"{dias_monitorados}",
            "Registros no período filtrado.",
            COR_ESTAVEL
        ),
        unsafe_allow_html=True
    )

with col6:
    st.markdown(
        card_kpi(
            "Dias ≥ 80%",
            f"{dias_atencao_total}",
            f"{pct_dias_atencao * 100:.1f}% do período filtrado.",
            cor_dias_atencao
        ),
        unsafe_allow_html=True
    )

with col7:
    st.markdown(
        card_kpi(
            "Dias críticos ≥ 100%",
            f"{dias_criticos_total}",
            f"{pct_dias_criticos * 100:.1f}% do período filtrado.",
            cor_criticos
        ),
        unsafe_allow_html=True
    )

with col8:
    st.markdown(
        card_kpi(
            "Município",
            "Franco da Rocha",
            "Caso demonstrativo.",
            "#1F4E79"
        ),
        unsafe_allow_html=True
    )

st.markdown("---")

st.markdown("## Leitura executiva")

st.info(
    f"A base filtrada contempla {dias_monitorados} dias monitorados. "
    f"A ocupação média total foi de {ocupacao_media_total:.1f}%, "
    f"com pico de {pico_total:.1f}%. "
    f"A UTI adulto apresentou média de {ocupacao_media_uti:.1f}% "
    f"e pico de {pico_uti:.1f}%. "
    f"Foram observados {dias_atencao_total} dias em faixa de atenção operacional "
    f"({pct_dias_atencao * 100:.1f}% do período) e {dias_criticos_total} dias "
    f"com ocupação total igual ou superior a 100% "
    f"({pct_dias_criticos * 100:.1f}% do período)."
)

st.markdown("---")

st.markdown("## Monitoramento temporal")

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    fig_total = criar_grafico_temporal(
        df=df,
        coluna_taxa="taxa_ocupacao_total",
        coluna_mm7="mm7_total",
        titulo="Ocupação Total"
    )

    st.plotly_chart(
        fig_total,
        use_container_width=True
    )

with col_graf2:
    fig_uti = criar_grafico_temporal(
        df=df,
        coluna_taxa="taxa_ocupacao_uti_adulto",
        coluna_mm7="mm7_uti",
        titulo="UTI Adulto"
    )

    st.plotly_chart(
        fig_uti,
        use_container_width=True
    )

st.markdown("---")

with st.expander("Nota metodológica resumida"):
    st.markdown("""
    Este dashboard possui finalidade demonstrativa e exploratória, sendo utilizado como apoio visual ao framework proposto no artigo
    **A Data-Driven Simulation Framework for Hospital Bed Management Using Synthetic Data**.

    Os dados utilizados são públicos, provenientes do OpenDataSUS, restritos ao município de Franco da Rocha no ano de 2022.

    A seleção de Franco da Rocha tem função instrumental para prototipagem do dashboard.
    A análise não deve ser interpretada como auditoria hospitalar, ranking sanitário ou avaliação epidemiológica definitiva.

    As cores dos cards seguem lógica operacional: verde para estabilidade, amarelo para atenção e vermelho para pressão crítica ou recorrente.
    """)