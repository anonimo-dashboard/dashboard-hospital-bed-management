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
    page_title="Metodologia",
    layout="wide",
    initial_sidebar_state="expanded"
)

df_base = carregar_base()
df, data_inicio, data_fim = aplicar_sidebar(df_base)

st.title("Metodologia do Dashboard")

st.markdown(f"""
### Dashboard Demonstrativo — Gestão de Leitos Hospitalares

Período selecionado: **{data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}**

Síntese metodológica da aplicação desenvolvida para apoiar a camada visual do framework.
""")

st.info("""
Este dashboard é um artefato demonstrativo. Ele não substitui o artigo original, não altera o framework dos autores e não deve ser usado como diagnóstico sanitário, auditoria hospitalar ou ranking municipal.
""")

st.markdown("## Identificação do artefato")

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
            "Ano-base",
            "2022",
            "Recorte temporal da base.",
            COR_ESTAVEL
        ),
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        card_kpi(
            "Fonte",
            "OpenDataSUS",
            "Dados públicos hospitalares.",
            COR_ESTAVEL
        ),
        unsafe_allow_html=True
    )

with col4:
    st.markdown(
        card_kpi(
            "Finalidade",
            "Demonstrativa",
            "Apoio visual ao framework.",
            COR_ATENCAO
        ),
        unsafe_allow_html=True
    )

st.markdown("---")

col_escopo, col_premissas = st.columns(2)

with col_escopo:
    st.markdown("## Escopo")

    st.markdown("""
    A aplicação foi construída para demonstrar como dados públicos hospitalares podem apoiar:

    - visualização da ocupação hospitalar;
    - leitura operacional de pressão;
    - identificação de faixas de atenção;
    - avaliação da qualidade dos registros;
    - interpretação temporal;
    - comunicação executiva.
    """)

with col_premissas:
    st.markdown("## Premissas")

    st.markdown("""
    1. A capacidade hospitalar mensal foi tratada como constante nos dias do mês.
    2. A ocupação diária foi integrada à capacidade mensal com finalidade exploratória.
    3. A UTI adulto é tratada como proxy operacional de leito crítico.
    4. As faixas operacionais são referências visuais exploratórias.
    5. Franco da Rocha é caso demonstrativo, não ranking sanitário.
    """)

st.markdown("---")

st.markdown("## Relação com o artigo-base")

st.markdown("""
O artigo **A Data-Driven Simulation Framework for Hospital Bed Management Using Synthetic Data**
propõe um framework orientado à simulação e apoio à decisão na gestão de leitos hospitalares.

A contribuição deste dashboard está na **camada visual e demonstrativa**:

- aproxima o framework de dados públicos observáveis;
- organiza indicadores operacionais;
- traduz séries temporais em leitura executiva;
- explicita limites de interpretação;
- adiciona leitura exploratória de estabilidade;
- prepara a estrutura para futura publicação pública.
""")

st.markdown("---")

col_ind, col_estat = st.columns(2)

with col_ind:
    st.markdown("## Indicadores utilizados")

    st.markdown("""
    - Taxa de ocupação total;
    - Taxa de ocupação UTI adulto;
    - Média móvel de 7 dias;
    - Status operacional;
    - Qualidade dos dados;
    - Leitos existentes;
    - UTI adulto existente;
    - Dias em atenção;
    - Dias críticos.
    """)

with col_estat:
    st.markdown("## Leitura estatística exploratória")

    st.markdown("""
    A leitura estatística incorporada ao dashboard utiliza:

    - distribuição por faixas operacionais;
    - média e mediana;
    - percentil 90;
    - picos de ocupação;
    - média móvel de 7 dias;
    - limites exploratórios tipo Shewhart;
    - identificação de pontos fora dos limites.

    A carta Shewhart é usada apenas como **leitura exploratória de estabilidade**, não como controle estatístico formal do processo.
    """)

st.markdown("---")

col_lim, col_qualidade = st.columns(2)

with col_lim:
    st.markdown("## Limitações")

    st.warning("""
    A aplicação não deve ser interpretada como:

    - auditoria hospitalar;
    - avaliação epidemiológica;
    - diagnóstico sanitário;
    - ranking municipal;
    - sistema oficial de monitoramento;
    - controle estatístico formal do processo.
    """)

with col_qualidade:
    st.markdown("## Qualidade dos dados")

    st.markdown("""
    A qualidade dos dados é tratada como dimensão de governança do dashboard.

    A base de disponibilidade hospitalar possui estrutura predominantemente mensal, enquanto a ocupação hospitalar possui estrutura diária. Por isso, a integração deve ser lida com cautela.

    A página **Qualidade dos Dados** torna visível o grau de segurança interpretativa dos indicadores.
    """)

st.markdown("---")

st.markdown("## Transparência e rastreabilidade")

st.markdown("""
A construção do dashboard segue lógica incremental e rastreável:

1. preparação analítica em RMarkdown;
2. exportação da base demonstrativa;
3. construção local em Streamlit;
4. separação modular do código;
5. validação visual e metodológica;
6. futura publicação pública no Streamlit Community Cloud.

Essa abordagem preserva supervisão humana, documentação, reprodutibilidade e rastreabilidade do artefato.
""")

with st.expander("Próximos passos planejados"):
    st.markdown("""
    - Refinar identidade visual executiva;
    - Criar relatório automático;
    - Preparar versionamento no GitHub;
    - Criar README técnico;
    - Publicar no Streamlit Community Cloud;
    - Compartilhar link público com os professores.
    """)