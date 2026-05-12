import plotly.graph_objects as go
import plotly.express as px

COR_ESTAVEL = "#2E8B57"
COR_ATENCAO = "#E6A700"
COR_CRITICO = "#C0392B"

COR_LINHA = "#1F4E79"
COR_MM7 = "#0B84F3"
COR_FUNDO = "white"


def obter_cor_status(valor):
    if valor >= 80:
        return COR_CRITICO
    elif valor >= 60:
        return COR_ATENCAO
    else:
        return COR_ESTAVEL


def card_kpi(titulo, valor, subtitulo="", cor_borda="#D9E2EC"):
    return f"""
<div style="border-left: 6px solid {cor_borda}; background-color: white; padding: 14px 16px; border-radius: 10px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); min-height: 112px; margin-bottom: 8px;">
  <div style="font-size: 0.78rem; color: #5F6C72; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: 6px;">
    {titulo}
  </div>
  <div style="font-size: 1.8rem; color: #1F2D3D; font-weight: 700; line-height: 1.1; margin-bottom: 8px;">
    {valor}
  </div>
  <div style="font-size: 0.82rem; color: #6B7280; line-height: 1.3;">
    {subtitulo}
  </div>
</div>
"""


def criar_grafico_temporal(df, coluna_taxa, coluna_mm7, titulo):
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df["data"],
            y=df[coluna_taxa] * 100,
            mode="lines",
            name="Taxa diária",
            line=dict(width=1.5, color=COR_LINHA)
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df["data"],
            y=df[coluna_mm7] * 100,
            mode="lines",
            name="Média móvel 7 dias",
            line=dict(width=3, color=COR_MM7)
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
        title=titulo,
        template="plotly_white",
        height=420,
        paper_bgcolor=COR_FUNDO,
        plot_bgcolor=COR_FUNDO,
        xaxis_title="Data",
        yaxis_title="Taxa de ocupação (%)",
        margin=dict(l=20, r=20, t=60, b=30),
        legend_title_text=""
    )

    fig.update_yaxes(ticksuffix="%")

    return fig


def classificar_faixa_ocupacao(valor):
    if valor >= 1:
        return "Crítico (≥100%)"
    elif valor >= 0.80:
        return "Atenção (80–99%)"
    elif valor >= 0.60:
        return "Monitoramento (60–79%)"
    else:
        return "Estável (<60%)"


def criar_grafico_faixas(df, coluna_taxa, titulo):
    df_temp = df.copy()

    df_temp["faixa_operacional"] = (
        df_temp[coluna_taxa]
        .apply(classificar_faixa_ocupacao)
    )

    ordem = [
        "Estável (<60%)",
        "Monitoramento (60–79%)",
        "Atenção (80–99%)",
        "Crítico (≥100%)"
    ]

    cores = {
        "Estável (<60%)": COR_ESTAVEL,
        "Monitoramento (60–79%)": "#7F8C8D",
        "Atenção (80–99%)": COR_ATENCAO,
        "Crítico (≥100%)": COR_CRITICO
    }

    contagem = (
        df_temp["faixa_operacional"]
        .value_counts()
        .reindex(ordem, fill_value=0)
        .reset_index()
    )

    contagem.columns = ["Faixa operacional", "Quantidade de dias"]

    fig = px.bar(
        contagem,
        x="Faixa operacional",
        y="Quantidade de dias",
        color="Faixa operacional",
        color_discrete_map=cores,
        title=titulo,
        text="Quantidade de dias"
    )

    fig.update_layout(
        template="plotly_white",
        height=360,
        xaxis_title="Faixa operacional",
        yaxis_title="Quantidade de dias",
        margin=dict(l=20, r=20, t=50, b=30),
        showlegend=False
    )

    fig.update_traces(textposition="outside")

    return fig


def calcular_limites_shewhart(df, coluna_taxa):
    serie = df[coluna_taxa].dropna() * 100

    media = serie.mean()
    desvio = serie.std()

    lsc = media + 3 * desvio
    lic = media - 3 * desvio

    if lic < 0:
        lic = 0

    return media, desvio, lsc, lic


def criar_grafico_shewhart(df, coluna_taxa, titulo):
    media, desvio, lsc, lic = calcular_limites_shewhart(df, coluna_taxa)

    df_temp = df.copy()
    df_temp["taxa_percentual"] = df_temp[coluna_taxa] * 100

    df_temp["fora_limite"] = (
        (df_temp["taxa_percentual"] > lsc) |
        (df_temp["taxa_percentual"] < lic)
    )

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df_temp["data"],
            y=df_temp["taxa_percentual"],
            mode="lines",
            name="Taxa diária",
            line=dict(width=1.5, color=COR_LINHA)
        )
    )

    pontos_fora = df_temp[df_temp["fora_limite"]]

    if not pontos_fora.empty:
        fig.add_trace(
            go.Scatter(
                x=pontos_fora["data"],
                y=pontos_fora["taxa_percentual"],
                mode="markers",
                name="Ponto fora dos limites",
                marker=dict(size=9, color=COR_CRITICO)
            )
        )

    fig.add_hline(
        y=media,
        line_color=COR_ESTAVEL,
        line_width=2,
        annotation_text="Linha central",
        annotation_position="top left"
    )

    fig.add_hline(
        y=lsc,
        line_dash="dash",
        line_color=COR_CRITICO,
        annotation_text="LSC (+3σ)",
        annotation_position="top left"
    )

    fig.add_hline(
        y=lic,
        line_dash="dash",
        line_color=COR_ATENCAO,
        annotation_text="LIC (-3σ)",
        annotation_position="bottom left"
    )

    fig.update_layout(
        title=titulo,
        template="plotly_white",
        height=420,
        xaxis_title="Data",
        yaxis_title="Taxa de ocupação (%)",
        margin=dict(l=20, r=20, t=60, b=30),
        legend_title_text=""
    )

    fig.update_yaxes(ticksuffix="%")

    return fig, media, desvio, lsc, lic, df_temp["fora_limite"].sum()