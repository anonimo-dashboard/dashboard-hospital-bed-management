import streamlit as st

from src.load_data import carregar_base
from src.sidebar import aplicar_sidebar
from src.theme import (
    criar_grafico_temporal,
    criar_grafico_faixas,
    criar_grafico_shewhart,
    card_kpi,
    COR_ESTAVEL,
    COR_ATENCAO,
    COR_CRITICO
)

st.set_page_config(
    page_title="UTI Adulto",
    layout="wide",
    initial_sidebar_state="expanded"
)

df_base = carregar_base()
df, data_inicio, data_fim = aplicar_sidebar(df_base)

media_uti = df["taxa_ocupacao_uti_adulto"].mean() * 100
mediana_uti = df["taxa_ocupacao_uti_adulto"].median() * 100
max_uti = df["taxa_ocupacao_uti_adulto"].max() * 100
p90_uti = df["taxa_ocupacao_uti_adulto"].quantile(0.90) * 100

dias_acima_80 = df[df["taxa_ocupacao_uti_adulto"] >= 0.80].shape[0]
dias_acima_100 = df[df["taxa_ocupacao_uti_adulto"] >= 1].shape[0]
total_dias = df["data"].nunique()

pct_dias_atencao = (dias_acima_80 / total_dias) * 100 if total_dias > 0 else 0
pct_dias_criticos = (dias_acima_100 / total_dias) * 100 if total_dias > 0 else 0

cor_media = (
    COR_CRITICO if media_uti >= 80
    else COR_ATENCAO if media_uti >= 60
    else COR_ESTAVEL
)

cor_p90 = (
    COR_CRITICO if p90_uti >= 100
    else COR_ATENCAO if p90_uti >= 80
    else COR_ESTAVEL
)

cor_max = (
    COR_CRITICO if max_uti >= 100
    else COR_ATENCAO if max_uti >= 80
    else COR_ESTAVEL
)

cor_dias_atencao = (
    COR_CRITICO if pct_dias_atencao > 30
    else COR_ATENCAO if pct_dias_atencao > 10
    else COR_ESTAVEL
)

cor_dias_criticos = (
    COR_CRITICO if pct_dias_criticos > 5
    else COR_ATENCAO if pct_dias_criticos > 0
    else COR_ESTAVEL
)

if media_uti >= 80:
    status_uti = "CRÍTICO"
    msg_status = "A média de ocupação da UTI adulto está acima da faixa de atenção."
elif media_uti >= 60:
    status_uti = "ATENÇÃO"
    msg_status = "A média de ocupação da UTI adulto exige monitoramento operacional."
else:
    status_uti = "ESTÁVEL"
    msg_status = "A média de ocupação da UTI adulto permanece abaixo da faixa de atenção."

st.title("UTI Adulto")

st.markdown(f"""
### Franco da Rocha • OpenDataSUS • 2022

Período selecionado: **{data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}**

Análise operacional da ocupação de leitos de UTI adulto.
""")

if status_uti == "CRÍTICO":
    st.error(f"🔴 Status da UTI adulto: {status_uti} — {msg_status}")
elif status_uti == "ATENÇÃO":
    st.warning(f"🟠 Status da UTI adulto: {status_uti} — {msg_status}")
else:
    st.success(f"🟢 Status da UTI adulto: {status_uti} — {msg_status}")

st.markdown("## Indicadores da UTI adulto")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        card_kpi("Média", f"{media_uti:.1f}%", "Taxa média no período.", cor_media),
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        card_kpi("Mediana", f"{mediana_uti:.1f}%", "Ponto central da distribuição.", COR_ESTAVEL),
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        card_kpi("Percentil 90", f"{p90_uti:.1f}%", "90% dos dias ficaram abaixo.", cor_p90),
        unsafe_allow_html=True
    )

with col4:
    st.markdown(
        card_kpi("Máximo", f"{max_uti:.1f}%", "Maior taxa observada.", cor_max),
        unsafe_allow_html=True
    )

col5, col6, col7, col8 = st.columns(4)

with col5:
    st.markdown(
        card_kpi("Dias monitorados", f"{total_dias}", "Dias presentes no período filtrado.", COR_ESTAVEL),
        unsafe_allow_html=True
    )

with col6:
    st.markdown(
        card_kpi("Dias ≥ 80%", f"{dias_acima_80}", f"{pct_dias_atencao:.1f}% do período.", cor_dias_atencao),
        unsafe_allow_html=True
    )

with col7:
    st.markdown(
        card_kpi("Dias ≥ 100%", f"{dias_acima_100}", f"{pct_dias_criticos:.1f}% do período.", cor_dias_criticos),
        unsafe_allow_html=True
    )

with col8:
    st.markdown(
        card_kpi("Indicador", "UTI adulto", "Monitoramento de leitos críticos.", "#1F4E79"),
        unsafe_allow_html=True
    )

st.markdown("---")
st.markdown("## Monitoramento temporal")

fig = criar_grafico_temporal(
    df=df,
    coluna_taxa="taxa_ocupacao_uti_adulto",
    coluna_mm7="mm7_uti",
    titulo="UTI Adulto"
)

st.plotly_chart(fig, use_container_width=True)

col_dist, col_tab = st.columns([1, 1])

with col_dist:
    st.markdown("## Faixas operacionais")

    fig_faixas = criar_grafico_faixas(
        df=df,
        coluna_taxa="taxa_ocupacao_uti_adulto",
        titulo="Distribuição por faixa operacional"
    )

    st.plotly_chart(fig_faixas, use_container_width=True)

with col_tab:
    st.markdown("## Dias críticos")

    dias_criticos = df[
        df["taxa_ocupacao_uti_adulto"] >= 1
    ][[
        "data",
        "taxa_ocupacao_uti_adulto",
        "ocupacao_uti",
        "uti_adulto_exist"
    ]].copy()

    if dias_criticos.empty:
        st.success("Não há dias críticos no período selecionado.")
    else:
        dias_criticos["data"] = dias_criticos["data"].dt.strftime("%d/%m/%Y")
        dias_criticos["taxa_ocupacao_uti_adulto"] = (
            dias_criticos["taxa_ocupacao_uti_adulto"] * 100
        ).round(1)

        dias_criticos = dias_criticos.rename(
            columns={
                "data": "Data",
                "taxa_ocupacao_uti_adulto": "Taxa (%)",
                "ocupacao_uti": "Ocupação UTI",
                "uti_adulto_exist": "Leitos UTI adulto"
            }
        )

        st.dataframe(dias_criticos, use_container_width=True, height=360)

st.markdown("---")
st.markdown("## Leitura exploratória de estabilidade")

fig_shewhart, media_sh, desvio_sh, lsc_sh, lic_sh, pontos_fora = criar_grafico_shewhart(
    df=df,
    coluna_taxa="taxa_ocupacao_uti_adulto",
    titulo="Carta exploratória — UTI Adulto"
)

cor_pontos_fora = COR_CRITICO if pontos_fora > 0 else COR_ESTAVEL

col_sh1, col_sh2, col_sh3, col_sh4 = st.columns(4)

with col_sh1:
    st.markdown(
        card_kpi("Linha central", f"{media_sh:.1f}%", "Média da taxa no período.", COR_ESTAVEL),
        unsafe_allow_html=True
    )

with col_sh2:
    st.markdown(
        card_kpi("Desvio-padrão", f"{desvio_sh:.1f} p.p.", "Variabilidade observada.", COR_ATENCAO),
        unsafe_allow_html=True
    )

with col_sh3:
    st.markdown(
        card_kpi("LSC", f"{lsc_sh:.1f}%", "Limite superior exploratório.", COR_CRITICO),
        unsafe_allow_html=True
    )

with col_sh4:
    st.markdown(
        card_kpi("Pontos fora", f"{pontos_fora}", "Sinais de comportamento atípico.", cor_pontos_fora),
        unsafe_allow_html=True
    )

st.plotly_chart(fig_shewhart, use_container_width=True)

st.info(
    f"A carta exploratória apresenta linha central de {media_sh:.1f}% e limite superior de {lsc_sh:.1f}%. "
    f"Foram identificados {pontos_fora} ponto(s) fora dos limites exploratórios no período selecionado. "
    "Essa leitura auxilia na identificação de instabilidade operacional, mas não deve ser interpretada como controle estatístico formal do processo."
)

st.markdown("---")
st.markdown("## Leitura operacional")

st.info(
    f"A ocupação de UTI adulto apresentou média de {media_uti:.1f}% e mediana de {mediana_uti:.1f}%. "
    f"O percentil 90 foi de {p90_uti:.1f}%, indicando que 90% dos dias ficaram abaixo desse patamar. "
    f"Foram registrados {dias_acima_80} dias acima de 80% e {dias_acima_100} dias com ocupação igual ou superior a 100%. "
    f"O pico observado foi de {max_uti:.1f}%."
)

with st.expander("Nota metodológica"):
    st.markdown("""
    A taxa de ocupação de UTI adulto é tratada como proxy operacional de pressão sobre leitos críticos.

    A média móvel de 7 dias é utilizada para suavizar oscilações diárias e apoiar a leitura de tendência.

    As faixas operacionais são referências exploratórias para comunicação visual de estabilidade, monitoramento, atenção e pressão crítica.

    A carta Shewhart apresentada possui finalidade exploratória. Ela usa média e limites de ±3 desvios-padrão para indicar possíveis sinais atípicos no comportamento da série.

    A análise possui finalidade demonstrativa e não substitui auditoria hospitalar, avaliação epidemiológica ou controle estatístico formal do processo.
    """)