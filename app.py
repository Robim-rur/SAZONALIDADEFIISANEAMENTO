import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
from datetime import datetime

# =========================================================
# CONFIG
# =========================================================

st.set_page_config(
    page_title="Sazonalidade B3",
    layout="wide"
)

# =========================================================
# SENHA
# =========================================================

SENHA_CORRETA = "LUCRO6"

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:

    st.title("🔒 Login")

    senha = st.text_input(
        "Digite a senha:",
        type="password"
    )

    if st.button("Entrar"):

        if senha == SENHA_CORRETA:
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("Senha incorreta.")

    st.stop()

# =========================================================
# LISTA DE ATIVOS
# =========================================================

ATIVOS = [
    # FIIs
    "HGLG11.SA",
    "XPLG11.SA",
    "KNRI11.SA",
    "BTLG11.SA",
    "VISC11.SA",
    "MXRF11.SA",
    "TRXF11.SA",
    "GARE11.SA",
    "GGRC11.SA",

    # Energia
    "TAEE11.SA",
    "CPLE6.SA",
    "CMIG4.SA",
    "EGIE3.SA",
    "TRPL4.SA",

    # Saneamento
    "SBSP3.SA",
    "CSMG3.SA"
]

# =========================================================
# FUNÇÕES
# =========================================================

@st.cache_data(ttl=3600)
def baixar_dados(ticker):

    try:
        df = yf.download(
            ticker,
            period="15y",
            interval="1mo",
            auto_adjust=True,
            progress=False
        )

        if df.empty:
            return None

        df = df[["Close"]].copy()

        df["Retorno"] = df["Close"].pct_change() * 100

        df.dropna(inplace=True)

        df["Ano"] = df.index.year
        df["Mes"] = df.index.month

        return df

    except:
        return None


def calcular_estatisticas(df, ticker, mes_atual):

    df_mes = df[df["Mes"] == mes_atual].copy()

    if len(df_mes) < 5:
        return None

    positivos = df_mes[df_mes["Retorno"] > 0]
    negativos = df_mes[df_mes["Retorno"] <= 0]

    taxa_acerto = round(
        (len(positivos) / len(df_mes)) * 100,
        2
    )

    retorno_medio = round(
        df_mes["Retorno"].mean(),
        2
    )

    volatilidade = round(
        df_mes["Retorno"].std(),
        2
    )

    pior_mes = round(
        df_mes["Retorno"].min(),
        2
    )

    melhor_mes = round(
        df_mes["Retorno"].max(),
        2
    )

    gain_medio = round(
        positivos["Retorno"].mean(),
        2
    ) if len(positivos) > 0 else 0

    loss_medio = round(
        negativos["Retorno"].mean(),
        2
    ) if len(negativos) > 0 else 0

    sharpe = 0

    if volatilidade != 0:
        sharpe = round(retorno_medio / volatilidade, 2)

    score = (
        taxa_acerto * 0.4
        + retorno_medio * 0.3
        + sharpe * 20
        - abs(pior_mes) * 0.1
    )

    score = round(score, 2)

    return {
        "Ativo": ticker.replace(".SA", ""),
        "Amostra": len(df_mes),
        "Taxa de Acerto (%)": taxa_acerto,
        "Retorno Médio (%)": retorno_medio,
        "Volatilidade (%)": volatilidade,
        "Sharpe Simplificado": sharpe,
        "Gain Médio (%)": gain_medio,
        "Loss Médio (%)": loss_medio,
        "Melhor Mês (%)": melhor_mes,
        "Pior Mês (%)": pior_mes,
        "Score": score
    }


def gerar_heatmap():

    heatmap_data = []

    for ticker in ATIVOS:

        df = baixar_dados(ticker)

        if df is None:
            continue

        linha = {
            "Ativo": ticker.replace(".SA", "")
        }

        for mes in range(1, 13):

            df_mes = df[df["Mes"] == mes]

            if len(df_mes) == 0:
                valor = np.nan
            else:
                valor = round(df_mes["Retorno"].mean(), 2)

            linha[mes] = valor

        heatmap_data.append(linha)

    heatmap_df = pd.DataFrame(heatmap_data)

    return heatmap_df

# =========================================================
# APP
# =========================================================

mes_atual = datetime.now().month

meses_nome = {
    1: "Janeiro",
    2: "Fevereiro",
    3: "Março",
    4: "Abril",
    5: "Maio",
    6: "Junho",
    7: "Julho",
    8: "Agosto",
    9: "Setembro",
    10: "Outubro",
    11: "Novembro",
    12: "Dezembro"
}

nome_mes_atual = meses_nome[mes_atual]

st.title("📊 Sazonalidade Estatística B3")

st.markdown(f"""
### Mês analisado:
# {nome_mes_atual}
""")

st.markdown("""
Este app analisa:
- FIIs de tijolo
- ações perenes
- utilities da B3

Com base em:
- frequência histórica de alta
- retorno médio
- volatilidade
- expectativa estatística
""")

# =========================================================
# RANKING
# =========================================================

st.header("🏆 Ranking Estatístico do Mês Atual")

resultado = []

barra = st.progress(0)

for i, ticker in enumerate(ATIVOS):

    df = baixar_dados(ticker)

    if df is not None:

        stats = calcular_estatisticas(
            df,
            ticker,
            mes_atual
        )

        if stats is not None:
            resultado.append(stats)

    barra.progress((i + 1) / len(ATIVOS))

ranking = pd.DataFrame(resultado)

ranking.sort_values(
    by="Score",
    ascending=False,
    inplace=True
)

ranking.reset_index(drop=True, inplace=True)

st.dataframe(
    ranking,
    use_container_width=True
)

# =========================================================
# TOP 5
# =========================================================

st.header("🔥 Top 5 Melhores Ativos")

top5 = ranking.head(5)

fig = px.bar(
    top5,
    x="Ativo",
    y="Score",
    text="Score"
)

fig.update_layout(
    height=500
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# =========================================================
# HEATMAP
# =========================================================

st.header("🌡️ Heatmap de Retorno Médio Mensal")

heatmap_df = gerar_heatmap()

heatmap_plot = heatmap_df.set_index("Ativo")

heatmap_plot.columns = [
    "Jan",
    "Fev",
    "Mar",
    "Abr",
    "Mai",
    "Jun",
    "Jul",
    "Ago",
    "Set",
    "Out",
    "Nov",
    "Dez"
]

fig2 = px.imshow(
    heatmap_plot,
    text_auto=True,
    aspect="auto"
)

fig2.update_layout(
    height=700
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

# =========================================================
# DETALHAMENTO
# =========================================================

st.header("🔎 Detalhamento por Ativo")

ativo_escolhido = st.selectbox(
    "Escolha um ativo:",
    ranking["Ativo"].tolist()
)

ticker_detalhe = ativo_escolhido + ".SA"

df_detalhe = baixar_dados(ticker_detalhe)

if df_detalhe is not None:

    df_mes = df_detalhe[
        df_detalhe["Mes"] == mes_atual
    ].copy()

    st.subheader(
        f"Retornos Históricos de {ativo_escolhido} em {nome_mes_atual}"
    )

    tabela = df_mes[[
        "Ano",
        "Retorno"
    ]].copy()

    tabela["Retorno"] = tabela["Retorno"].round(2)

    st.dataframe(
        tabela,
        use_container_width=True
    )

    fig3 = px.bar(
        tabela,
        x="Ano",
        y="Retorno",
        text="Retorno"
    )

    fig3.update_layout(
        height=500
    )

    st.plotly_chart(
        fig3,
        use_container_width=True
    )

# =========================================================
# RODAPÉ
# =========================================================

st.markdown("---")

st.markdown("""
### 📌 Interpretação

- Taxa de Acerto:
Percentual histórico de meses positivos.

- Retorno Médio:
Média histórica de retorno naquele mês.

- Sharpe Simplificado:
Relação retorno/risco.

- Gain Médio:
Média dos meses positivos.

- Loss Médio:
Média dos meses negativos.

- Score:
Ranking estatístico geral.

⚠️ Este app é puramente estatístico e não constitui recomendação de investimento.
""")
