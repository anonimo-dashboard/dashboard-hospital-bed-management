import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from src.load_data import carregar_base
from src.sidebar import aplicar_sidebar

from src.theme import (
    card_kpi,
    COR_ESTAVEL,
    COR_ATENCAO,
    COR_CRITICO,
    COR_LINHA,
    COR_MM7
)

st.set_page_config(
    page_title="Previsão Exploratória",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

df_base = carregar_base()
df, data_inicio, data_fim = aplicar_sidebar(df_base)

st.title("🔮 Previsão Exploratória")

st.markdown(f"""
### Franco da Rocha • OpenDataSUS • 2022

Período base selecionado: **{data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}**

Módulo demonstrativo para projeção exploratória da taxa de ocupação hospitalar.
""")

st.warning("""
A previsão é exploratória e demonstrativa. Ela não considera fluxo hospitalar real completo,
como admissões, altas, regulação, tempo médio de permanência ou disponibilidade de equipes.
""")

col_config1, col_config2, col_config3, col_config4 = st.columns(4)

with col_config1:
    indicador = st.selectbox(
        "Indicador para previsão",
        ["Ocupação Total", "UTI Adulto"]
    )

with col_config2:
    metodo = st.selectbox(
        "Método de previsão",
        ["Média móvel", "Regressão linear"]
    )

with col_config3:
    horizonte = st.slider(
        "Horizonte de previsão (dias)",
        min_value=1,
        max_value=30,
        value=7
    )

with col_config4:
    fator_operacional = st.selectbox(
        "Cenário operacional",
        [
            "Conservador (-5%)",
            "Estável (0%)",
            "Pressão crescente (+5%)"
        ]
    )

ajuste_cenario = {
    "Conservador (-5%)": -0.05,
    "Estável (0%)": 0.00,
    "Pressão crescente (+5%)": 0.05
}[fator_operacional]

if indicador == "Ocupação Total":
    coluna_taxa = "taxa_ocupacao_total"
    titulo_indicador = "Ocupação Total"
else:
    coluna_taxa = "taxa_ocupacao_uti_adulto"
    titulo_indicador = "UTI Adulto"

df_modelo = df[["data", coluna_taxa]].dropna().copy()
df_modelo = df_modelo.sort_values("data")

if df_modelo.shape[0] < 7:
    st.error("Período selecionado insuficiente para previsão exploratória. Selecione pelo menos 7 dias.")
    st.stop()

df_modelo["taxa_percentual"] = df_modelo[coluna_taxa] * 100
df_modelo["mm7"] = df_modelo["taxa_percentual"].rolling(window=7, min_periods=1).mean()

ultima_data = df_modelo["data"].max()
ultimo_valor = df_modelo["taxa_percentual"].iloc[-1]
ultima_mm7 = df_modelo["mm7"].iloc[-1]

datas_futuras = pd.date_range(
    start=ultima_data + pd.Timedelta(days=1),
    periods=horizonte,
    freq="D"
)

if metodo == "Média móvel":
    previsao_base = np.repeat(ultima_mm7, horizonte)

else:
    df_modelo["t"] = np.arange(len(df_modelo))

    x = df_modelo["t"].values
    y = df_modelo["taxa_percentual"].values

    coef = np.polyfit(x, y, 1)
    inclinacao = coef[0]
    intercepto = coef[1]

    ultimo_t = df_modelo["t"].max()

    t_futuro = np.arange(
        ultimo_t + 1,
        ultimo_t + 1 + horizonte
    )

    previsao_base = intercepto + inclinacao * t_futuro

# Aplicação do cenário operacional
previsao = previsao_base * (1 + ajuste_cenario)
previsao = np.clip(previsao, 0, None)

df_prev = pd.DataFrame({
    "data": datas_futuras,
    "previsao_percentual": previsao
})

media_historica = df_modelo["taxa_percentual"].mean()
previsao_final = df_prev["previsao_percentual"].iloc[-1]
variacao_prevista = previsao_final - ultimo_valor

dias_prev_atencao = df_prev[df_prev["previsao_percentual"] >= 80].shape[0]
dias_prev_criticos = df_prev[df_prev["previsao_percentual"] >= 100].shape[0]

cor_previsao = (
    COR_CRITICO if previsao_final >= 100
    else COR_ATENCAO if previsao_final >= 80
    else COR_ESTAVEL
)

cor_variacao = (
    COR_CRITICO if variacao_prevista > 0
    else COR_ESTAVEL
)

cor_cenario = (
    COR_CRITICO if ajuste_cenario > 0
    else COR_ESTAVEL if ajuste_cenario < 0
    else COR_ATENCAO
)

st.markdown("## Síntese da previsão")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        card_kpi(
            "Indicador",
            titulo_indicador,
            "Série projetada.",
            "#1F4E79"
        ),
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        card_kpi(
            "Método",
            metodo,
            "Estratégia de projeção.",
            COR_ATENCAO if metodo == "Regressão linear" else COR_ESTAVEL
        ),
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        card_kpi(
            "Horizonte",
            f"{horizonte} dias",
            "Período projetado.",
            COR_ESTAVEL
        ),
        unsafe_allow_html=True
    )

with col4:
    st.markdown(
        card_kpi(
            "Cenário operacional",
            fator_operacional,
            "Ajuste demonstrativo sobre a projeção.",
            cor_cenario
        ),
        unsafe_allow_html=True
    )

col5, col6, col7, col8 = st.columns(4)

with col5:
    st.markdown(
        card_kpi(
            "Último valor observado",
            f"{ultimo_valor:.1f}%",
            "Último ponto da série filtrada.",
            COR_ESTAVEL
        ),
        unsafe_allow_html=True
    )

with col6:
    st.markdown(
        card_kpi(
            "MM7 final",
            f"{ultima_mm7:.1f}%",
            "Média móvel final do período.",
            COR_ESTAVEL
        ),
        unsafe_allow_html=True
    )

with col7:
    st.markdown(
        card_kpi(
            "Previsão final",
            f"{previsao_final:.1f}%",
            "Valor estimado no último dia previsto.",
            cor_previsao
        ),
        unsafe_allow_html=True
    )

with col8:
    st.markdown(
        card_kpi(
            "Variação prevista",
            f"{variacao_prevista:+.1f} p.p.",
            "Diferença frente ao último valor observado.",
            cor_variacao
        ),
        unsafe_allow_html=True
    )

col9, col10 = st.columns(2)

with col9:
    st.markdown(
        card_kpi(
            "Dias previstos ≥ 80%",
            f"{dias_prev_atencao}",
            "Dias em faixa de atenção no horizonte.",
            COR_ATENCAO if dias_prev_atencao > 0 else COR_ESTAVEL
        ),
        unsafe_allow_html=True
    )

with col10:
    st.markdown(
        card_kpi(
            "Dias previstos ≥ 100%",
            f"{dias_prev_criticos}",
            "Dias em faixa crítica no horizonte.",
            COR_CRITICO if dias_prev_criticos > 0 else COR_ESTAVEL
        ),
        unsafe_allow_html=True
    )

st.markdown("---")
st.markdown("## Histórico e previsão")

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=df_modelo["data"],
        y=df_modelo["taxa_percentual"],
        mode="lines",
        name="Histórico",
        line=dict(color=COR_LINHA, width=2)
    )
)

fig.add_trace(
    go.Scatter(
        x=df_modelo["data"],
        y=df_modelo["mm7"],
        mode="lines",
        name="Média móvel 7 dias",
        line=dict(color=COR_MM7, width=2)
    )
)

fig.add_trace(
    go.Scatter(
        x=df_prev["data"],
        y=df_prev["previsao_percentual"],
        mode="lines+markers",
        name=f"Previsão — {metodo} | {fator_operacional}",
        line=dict(
            color=COR_CRITICO if ajuste_cenario > 0 else COR_ATENCAO,
            width=3,
            dash="dash"
        ),
        marker=dict(size=7)
    )
)

fig.add_hline(
    y=80,
    line_dash="dash",
    line_color=COR_ATENCAO,
    annotation_text="Atenção (80%)",
    annotation_position="top left"
)

fig.add_hline(
    y=100,
    line_dash="dash",
    line_color=COR_CRITICO,
    annotation_text="Crítico (100%)",
    annotation_position="top left"
)

fig.update_layout(
    template="plotly_white",
    height=480,
    xaxis_title="Data",
    yaxis_title="Taxa de ocupação (%)",
    legend_title_text="",
    margin=dict(l=20, r=20, t=50, b=30)
)

fig.update_yaxes(ticksuffix="%")

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.markdown("## Tabela da previsão")

df_prev_tabela = df_prev.copy()
df_prev_tabela["data"] = df_prev_tabela["data"].dt.strftime("%d/%m/%Y")
df_prev_tabela["previsao_percentual"] = df_prev_tabela["previsao_percentual"].round(1)

df_prev_tabela = df_prev_tabela.rename(
    columns={
        "data": "Data prevista",
        "previsao_percentual": "Taxa prevista (%)"
    }
)

st.dataframe(
    df_prev_tabela,
    use_container_width=True,
    height=320
)

st.markdown("---")
st.markdown("## Leitura interpretativa")

direcao = (
    "aumento" if variacao_prevista > 0
    else "redução" if variacao_prevista < 0
    else "estabilidade"
)

st.info(
    f"Com base no período selecionado, usando o método **{metodo}** e o cenário **{fator_operacional}**, "
    f"a projeção exploratória indica tendência de {direcao} para {titulo_indicador}. "
    f"O último valor observado foi de {ultimo_valor:.1f}% e a previsão ao final de "
    f"{horizonte} dias é de {previsao_final:.1f}%. "
    f"No horizonte projetado, há {dias_prev_atencao} dia(s) em faixa de atenção "
    f"e {dias_prev_criticos} dia(s) em faixa crítica."
)

with st.expander("Nota metodológica"):
    st.markdown("""
    Esta previsão possui finalidade demonstrativa e exploratória.

    **Média móvel:** projeta para o horizonte selecionado o valor da média móvel final de 7 dias.  
    É um método simples, conservador e útil para demonstrar continuidade operacional.

    **Regressão linear:** ajusta uma tendência linear simples sobre a série filtrada e projeta os próximos dias.  
    É útil para demonstrar direção de tendência, mas pode exagerar movimentos quando há picos ou quedas recentes.

    **Cenário operacional:** aplica um ajuste simples sobre a previsão para simular hipóteses operacionais:
    - Conservador (-5%): representa maior alívio operacional ou maior saída implícita de pacientes;
    - Estável (0%): mantém a projeção sem ajuste;
    - Pressão crescente (+5%): representa maior pressão operacional ou entrada implícita superior à saída.

    O modelo não incorpora variáveis hospitalares reais, como admissões, altas efetivas, tempo médio de permanência,
    regulação de leitos, equipes, sazonalidade epidemiológica ou mudanças operacionais.

    Portanto, a previsão não deve ser interpretada como modelo hospitalar validado.
    O objetivo é demonstrar visualmente cenários de tendência dentro do framework de gestão de leitos.
    """)