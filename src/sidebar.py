import streamlit as st


def aplicar_sidebar(df):

    # ---------------------------------------------------
    # CABEÇALHO
    # ---------------------------------------------------

    st.sidebar.markdown("""
    # 🏥 Gestão de Leitos

    **Dashboard demonstrativo**  
    Framework visual para análise operacional de ocupação hospitalar.
    """)

    st.sidebar.markdown("---")

    # ---------------------------------------------------
    # DEFINIÇÃO DOS LIMITES
    # ---------------------------------------------------

    data_min = df["data"].min().date()
    data_max = df["data"].max().date()

    # ---------------------------------------------------
    # SESSION STATE
    # ---------------------------------------------------

    if "periodo_global" not in st.session_state:

        st.session_state.periodo_global = (
            data_min,
            data_max
        )

    # ---------------------------------------------------
    # PERÍODO DE ANÁLISE
    # ---------------------------------------------------

    st.sidebar.markdown("### 📅 Período de análise")

    data_inicio_manual = st.sidebar.date_input(
        "Data inicial",
        value=st.session_state.periodo_global[0],
        min_value=data_min,
        max_value=data_max,
        format="DD/MM/YYYY"
    )

    data_fim_manual = st.sidebar.date_input(
        "Data final",
        value=st.session_state.periodo_global[1],
        min_value=data_min,
        max_value=data_max,
        format="DD/MM/YYYY"
    )

    periodo = st.sidebar.slider(
        "Ajuste rápido",
        min_value=data_min,
        max_value=data_max,
        value=(
            data_inicio_manual,
            data_fim_manual
        ),
        format="DD/MM/YYYY"
    )

    st.session_state.periodo_global = periodo

    data_inicio, data_fim = periodo

    # ---------------------------------------------------
    # FILTRO
    # ---------------------------------------------------

    df_filtrado = df[
        (df["data"].dt.date >= data_inicio) &
        (df["data"].dt.date <= data_fim)
    ].copy()

    # ---------------------------------------------------
    # KPIs OPERACIONAIS
    # ---------------------------------------------------

    ocupacao_media = (
        df_filtrado["taxa_ocupacao_total"]
        .mean() * 100
    )

    ocupacao_uti = (
        df_filtrado["taxa_ocupacao_uti_adulto"]
        .mean() * 100
    )

    dias_criticos = df_filtrado[
        df_filtrado["taxa_ocupacao_total"] >= 1
    ].shape[0]

    # ---------------------------------------------------
    # RESUMO OPERACIONAL
    # ---------------------------------------------------

    st.sidebar.markdown("---")

    st.sidebar.markdown(
        "### 📊 Resumo operacional"
    )

    st.sidebar.metric(
        "Ocupação média",
        f"{ocupacao_media:.1f}%"
    )

    st.sidebar.metric(
        "UTI média",
        f"{ocupacao_uti:.1f}%"
    )

    st.sidebar.metric(
        "Dias críticos",
        f"{dias_criticos}"
    )

    # ---------------------------------------------------
    # STATUS OPERACIONAL
    # ---------------------------------------------------

    st.sidebar.markdown("---")

    st.sidebar.markdown(
        "### 🚦 Status operacional"
    )

    if ocupacao_media >= 80:

        st.sidebar.error(
            "🔴 CRÍTICO"
        )

        st.sidebar.caption(
            "Ocupação média acima da faixa de atenção operacional."
        )

    elif ocupacao_media >= 60:

        st.sidebar.warning(
            "🟠 ATENÇÃO"
        )

        st.sidebar.caption(
            "Ocupação média em faixa intermediária de monitoramento."
        )

    else:

        st.sidebar.success(
            "🟢 ESTÁVEL"
        )

        st.sidebar.caption(
            "Ocupação média abaixo da faixa de atenção."
        )

    # ---------------------------------------------------
    # SOBRE O DASHBOARD
    # ---------------------------------------------------

    st.sidebar.markdown("---")

    with st.sidebar.expander(
        "ℹ️ Sobre o dashboard"
    ):

        st.markdown("""
        Aplicação demonstrativa baseada em dados públicos do OpenDataSUS.

        O objetivo é apoiar a visualização do framework de gestão de leitos hospitalares, com foco em:

        - ocupação hospitalar;
        - pressão operacional;
        - leitura temporal;
        - qualidade dos dados;
        - interpretação executiva.

        **Não é auditoria hospitalar nem diagnóstico epidemiológico.**
        """)

    # ---------------------------------------------------
    # RETORNO
    # ---------------------------------------------------

    return (
        df_filtrado,
        data_inicio,
        data_fim
    )