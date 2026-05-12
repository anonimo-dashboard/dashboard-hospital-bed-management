import pandas as pd
import streamlit as st


@st.cache_data
def carregar_base():
    caminho_arquivo = "data/base_dashboard_franco_da_rocha_2022.xlsx"

    df = pd.read_excel(caminho_arquivo)

    df["data"] = pd.to_datetime(df["data"])
    df = df.sort_values("data")

    return df