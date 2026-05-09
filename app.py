import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
from datetime import datetime

# =========================================================
# CONFIGURAÇÃO DA PÁGINA
# =========================================================

st.set_page_config(
    page_title="Sazonalidade Estatística B3",
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

    # =====================================================
    # FIIs DE TIJOLO
    # =====================================================

    "HGLG11.SA",
    "XPLG11.SA",
    "KNRI11.SA",
    "BTLG11.SA",
    "VISC11.SA",
    "TRXF11.SA",
    "GARE11.SA",
    "GGRC11.SA",
    "LVBI11.SA",
    "PVBI11.SA",
    "VILG11.SA",
    "HGRU11.SA",
    "RBRP11.SA",
    "PATL11.SA",
    "RECT11.SA",
    "MALL11.SA",
    "HSML11.SA",
    "XPML11.SA",
    "JSRE11.SA",
    "ALZR11.SA",

    # =====================================================
    # ENERGIA
    # =====================================================

    "TAEE11.SA",
    "TAEE4.SA",
    "TAEE3.SA",
    "CMIG4.SA",
    "CMIG3.SA",
    "CPLE6.SA",
    "CPLE3.SA",
    "EGIE3.SA",
    "TRPL4.SA",
    "TRPL3.SA",
    "ALUP11.SA",
    "ALUP4.SA",
    "ALUP3.SA",
    "ENGI11.SA",
    "ENGI4.SA",
    "ENGI3.SA",
    "ENEV3.SA",
    "EQTL3.SA",
    "AURE3.SA",
    "NEOE3.SA",
    "AESB3.SA",

    # =====================================================
    # SANEAMENTO
    # =====================================================

    "SBSP3.SA",
    "CSMG3.SA",
    "SAPR11.SA",
    "SAPR4.SA",
    "SAPR3.SA",
    "ORVR3.SA"
]

# =========================================================
# MAPA DE MESES
# =========================================================

MESES = {
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

# =========================================================
# FUNÇÕES
# =========================================================

@st.cache_data(ttl=3600)
def baixar_dados(ticker):

    try:

        df = yf.download(
            ticker,
            period="20y",
            interval="1mo",
            auto_adjust=True,
            progress=False
        )

        if df.empty:
            return None

        df.reset_index(inplace=True)

        if "Close" not in df.columns:
            return None

        df = df[["Date", "Close"]].copy()

        df["Close"] = pd.to_numeric(
            df["Close"],
            errors="coerce"
        )

        df.dropna(inplace=True)

        df["Retorno"] = (
            df["Close"].pct_change() * 100
        )

        df.dropna(inplace=True)

        df["Ano"] = pd.to_datetime(
            df["Date"]
        ).dt.year

        df["Mes"] = pd.to_datetime(
            df["Date"]
        ).dt.month

        return df

    except:
        return None


def classificar_confianca(amostra):

    if amostra >= 10:
        return "Excelente"

    elif amostra >= 7:
        return "Forte"

    elif amostra >= 5:
        return "Boa"

    elif amostra >= 3:
        return "Moderada"

    else:
        return "Fraca"


def multiplicador_confianca(amostra):

    if amostra >= 10:
        return 1.00

    elif amostra >= 7:
        return 0.90

    elif amostra >= 5:
        return 0.80

    elif amostra >= 3:
        return 0.65

    else:
        return 0.50


def calcular_estatisticas(df, ticker, mes_atual):

    try:

        df_mes = df[
            df["Mes"] == mes_atual
        ].copy()

        if len(df_mes) < 2:
            return None

        positivos = df_mes[
            df_mes["Retorno"] > 0
        ]

        negativos = df_mes[
            df_mes["Retorno"] <= 0
        ]

        amostra = len(df_mes)

        taxa_acerto = round(
            (len(positivos) / amostra) * 100,
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

        melhor_mes = round(
            df_mes["Retorno"].max(),
            2
        )

        pior_mes = round(
            df_mes["Retorno"].min(),
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
            sharpe = round(
                retorno_medio / volatilidade,
                2
            )

        score_base = (
            taxa_acerto * 0.4
            + retorno_medio * 0.3
            + sharpe * 20
            - abs(pior_mes) * 0.1
        )

        score_final = (
            score_base
            * multiplicador_confianca(amostra)
        )

        score_final = round(score_final, 2)

        return {
            "Ativo": ticker.replace(".SA", ""),
            "Amostra": amostra,
            "Confiança": classificar_confianca(amostra),
            "Taxa Acerto (%)": taxa_acerto,
            "Retorno Médio (%)": retorno_medio,
            "Volatilidade (%)": volatilidade,
            "Sharpe": sharpe,
            "Gain Médio (%)": gain_medio,
            "Loss Médio (%)": loss_medio,
            "Melhor Mês (%)": melhor_mes,
            "Pior Mês (%)": pior_mes,
            "Score": score_final
        }

    except:
        return None


@st.cache_data(ttl=3600)
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

            try:

                df_mes = df[
                    df["Mes"] == mes
                ]

                if len(df_mes) == 0:
                    valor = np.nan

                else:
                    valor = round(
                        df_mes["Retorno"].mean(),
                        2
                    )

                linha[mes] = valor

            except:
                linha[mes] = np.nan

        heatmap_data.append(linha)

    return pd.DataFrame(heatmap_data)

# =========================================================
# APP
# =========================================================

mes_atual = datetime.now().month

nome_mes = MESES[mes_atual]

st.title("📊 Sazonalidade Estatística B3")

st.markdown(f"""
# {nome_mes}

Análise estatística histórica mensal de:
- FIIs de tijolo
- Empresas de energia
- Empresas de saneamento

Baseado em:
- frequência histórica de alta
- retorno médio
- volatilidade
- expectativa matemática
- robustez estatística
""")

# =========================================================
# PROCESSAMENTO
# =========================================================

resultado_robusto = []
resultado_jovem = []

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

            if stats["Amostra"] >= 5:
                resultado_robusto.append(stats)

            else:
                resultado_jovem.append(stats)

    barra.progress(
        (i + 1) / len(ATIVOS)
    )

# =========================================================
# RANKING PRINCIPAL
# =========================================================

st.header("🏆 Ranking Principal")

ranking = pd.DataFrame(resultado_robusto)

if not ranking.empty:

    ranking.sort_values(
        by="Score",
        ascending=False,
        inplace=True
    )

    ranking.reset_index(
        drop=True,
        inplace=True
    )

    st.dataframe(
        ranking,
        use_container_width=True
    )

else:

    st.warning(
        "Nenhum ativo encontrado."
    )

# =========================================================
# RANKING SECUNDÁRIO
# =========================================================

st.header("⚠️ Ativos com Baixa Amostragem")

ranking_jovem = pd.DataFrame(
    resultado_jovem
)

if not ranking_jovem.empty:

    ranking_jovem.sort_values(
        by="Score",
        ascending=False,
        inplace=True
    )

    ranking_jovem.reset_index(
        drop=True,
        inplace=True
    )

    st.dataframe(
        ranking_jovem,
        use_container_width=True
    )

else:

    st.info(
        "Nenhum ativo jovem encontrado."
    )

# =========================================================
# TOP 10
# =========================================================

if not ranking.empty:

    st.header("🔥 Top 10 Scores")

    top10 = ranking.head(10).copy()

    top10["Score"] = pd.to_numeric(
        top10["Score"],
        errors="coerce"
    )

    top10.dropna(inplace=True)

    if not top10.empty:

        fig = px.bar(
            top10,
            x="Ativo",
            y="Score",
            text="Score"
        )

        fig.update_layout(
            height=600
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

# =========================================================
# HEATMAP
# =========================================================

st.header("🌡️ Heatmap de Retornos Médios")

heatmap_df = gerar_heatmap()

if not heatmap_df.empty:

    try:

        heatmap_plot = heatmap_df.set_index(
            "Ativo"
        )

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
            height=1000
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

    except:

        st.warning(
            "Não foi possível gerar o heatmap."
        )

# =========================================================
# DETALHAMENTO
# =========================================================

if not ranking.empty:

    st.header("🔎 Detalhamento por Ativo")

    ativo_escolhido = st.selectbox(
        "Escolha um ativo:",
        ranking["Ativo"].tolist()
    )

    ticker_detalhe = (
        ativo_escolhido + ".SA"
    )

    df_detalhe = baixar_dados(
        ticker_detalhe
    )

    if df_detalhe is not None:

        df_mes = df_detalhe[
            df_detalhe["Mes"] == mes_atual
        ].copy()

        if not df_mes.empty:

            st.subheader(
                f"""
                Retornos Históricos de
                {ativo_escolhido}
                em {nome_mes}
                """
            )

            tabela = df_mes[[
                "Ano",
                "Retorno"
            ]].copy()

            tabela["Ano"] = tabela[
                "Ano"
            ].astype(str)

            tabela["Retorno"] = pd.to_numeric(
                tabela["Retorno"],
                errors="coerce"
            )

            tabela.dropna(inplace=True)

            tabela["Retorno"] = (
                tabela["Retorno"]
                .round(2)
            )

            st.dataframe(
                tabela,
                use_container_width=True
            )

            grafico_df = pd.DataFrame({
                "Ano": tabela["Ano"].tolist(),
                "Retorno": tabela["Retorno"].tolist()
            })

            grafico_df.dropna(inplace=True)

            if not grafico_df.empty:

                fig3 = px.bar(
                    grafico_df,
                    x="Ano",
                    y="Retorno",
                    text="Retorno"
                )

                fig3.update_traces(
                    texttemplate='%{text:.2f}',
                    textposition='outside'
                )

                fig3.update_layout(
                    height=600,
                    xaxis_title="Ano",
                    yaxis_title="Retorno (%)"
                )

                st.plotly_chart(
                    fig3,
                    use_container_width=True
                )

            else:

                st.warning(
                    "Não foi possível gerar o gráfico."
                )

# =========================================================
# RODAPÉ
# =========================================================

st.markdown("---")

st.markdown("""
## 📌 Interpretação

### Taxa Acerto
Percentual histórico de meses positivos.

### Retorno Médio
Média histórica de retorno do mês.

### Gain Médio
Média apenas dos meses positivos.

### Loss Médio
Média apenas dos meses negativos.

### Sharpe
Retorno ajustado pela volatilidade.

### Confiança
Robustez estatística baseada no tamanho da amostra.

### Score
Pontuação quantitativa final do ativo.

⚠️ Aplicação puramente estatística.
Não constitui recomendação de investimento.
""")
