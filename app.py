import streamlit as st

from src.load_data import carregar_base
from src.sidebar import aplicar_sidebar

from src.theme import (
    card_kpi,
    COR_ESTAVEL,
    COR_ATENCAO,
    COR_CRITICO
)

st.set_page_config(
    page_title="Gestão de Leitos Hospitalares",
    layout="wide",
    initial_sidebar_state="expanded"
)

df_base = carregar_base()
df_filtrado, data_inicio, data_fim = aplicar_sidebar(df_base)

dias_monitorados = df_filtrado["data"].nunique()
ocupacao_media_total = df_filtrado["taxa_ocupacao_total"].mean() * 100
dias_criticos = df_filtrado[df_filtrado["taxa_ocupacao_total"] >= 1].shape[0]

pct_dias_criticos = (
    dias_criticos / dias_monitorados * 100
    if dias_monitorados > 0 else 0
)

cor_ocupacao = (
    COR_CRITICO if ocupacao_media_total >= 80
    else COR_ATENCAO if ocupacao_media_total >= 60
    else COR_ESTAVEL
)

cor_critico = (
    COR_CRITICO if pct_dias_criticos > 5
    else COR_ATENCAO if pct_dias_criticos > 0
    else COR_ESTAVEL
)

st.title("Gestão de Leitos Hospitalares")
st.caption("Página Inicial")

st.markdown("""
### Dashboard demonstrativo para apoio visual ao framework de simulação e gestão de leitos

Aplicação orientada à comunicação executiva de ocupação hospitalar, pressão operacional,
qualidade dos dados e leitura exploratória de estabilidade.
""")

st.info("""
Artefato demonstrativo vinculado ao artigo **A Data-Driven Simulation Framework for Hospital Bed Management Using Synthetic Data**.
Não substitui auditoria hospitalar, diagnóstico epidemiológico ou sistema oficial de monitoramento.
""")

st.markdown("## Recorte atual")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        card_kpi(
            "Município",
            "Franco da Rocha/SP",
            "Caso demonstrativo.",
            "#1F4E79"
        ),
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        card_kpi(
            "Período",
            data_inicio.strftime("%d/%m/%Y"),
            f"até {data_fim.strftime('%d/%m/%Y')}",
            COR_ESTAVEL
        ),
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        card_kpi(
            "Ocupação média",
            f"{ocupacao_media_total:.1f}%",
            "Taxa média total.",
            cor_ocupacao
        ),
        unsafe_allow_html=True
    )

with col4:
    st.markdown(
        card_kpi(
            "Dias críticos",
            f"{dias_criticos}",
            f"{pct_dias_criticos:.1f}% do período.",
            cor_critico
        ),
        unsafe_allow_html=True
    )

st.markdown("---")

col_objetivo, col_navegacao = st.columns([1.15, 0.85])

with col_objetivo:
    st.markdown("## Objetivo")

    st.markdown("""
    Este dashboard organiza dados públicos hospitalares em uma camada visual para apoiar
    a demonstração do framework de gestão de leitos.

    O foco está em transformar séries de ocupação em uma leitura operacional simples,
    rastreável e adequada para apresentação.
    """)

    st.markdown("""
    **O que a aplicação demonstra:**

    - ocupação hospitalar total;
    - ocupação de UTI adulto;
    - alertas por faixas operacionais;
    - qualidade dos registros;
    - estabilidade exploratória;
    - previsão exploratória.
    """)

with col_navegacao:
    st.markdown("## Navegação")

    st.markdown("""
    **1. Visão Executiva**  
    Síntese dos principais indicadores.

    **2. Ocupação Total**  
    Pressão geral sobre a capacidade.

    **3. UTI Adulto**  
    Monitoramento de leitos críticos.

    **4. Qualidade dos Dados**  
    Segurança interpretativa.

    **5. Previsão Exploratória**  
    Simulação visual de tendência.

    **6. Metodologia**  
    Premissas, limites e rastreabilidade.
    """)

st.markdown("---")

with st.expander("Camadas analíticas incorporadas"):
    st.markdown("""
    **Operacional:** indicadores de ocupação, dias em atenção, dias críticos e faixas operacionais.

    **Estatística:** média, mediana, percentil 90, média móvel de 7 dias e leitura exploratória tipo Shewhart.

    **Metodológica:** qualidade dos dados, premissas explícitas, limitações e rastreabilidade.
    """)

with st.expander("Ressalva metodológica"):
    st.markdown("""
    A aplicação possui finalidade demonstrativa e exploratória.

    Os resultados dependem da qualidade, completude e estrutura dos dados públicos utilizados.
    O dashboard não deve ser interpretado como auditoria hospitalar, avaliação epidemiológica,
    ranking sanitário, decisão assistencial automatizada ou controle estatístico formal do processo.
    """)