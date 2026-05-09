import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime

# =====================================================
# CONFIG
# =====================================================

st.set_page_config(
    page_title="Sazonalidade B3",
    layout="wide"
)

# =====================================================
# LOGIN
# =====================================================

SENHA = "LUCRO6"

if "logado" not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:

    st.title("🔒 Login")

    senha_digitada = st.text_input(
        "Digite a senha",
        type="password"
    )

    if st.button("Entrar"):

        if senha_digitada == SENHA:
            st.session_state.logado = True
            st.rerun()

        else:
            st.error("Senha incorreta")

    st.stop()

# =====================================================
# TÍTULO
# =====================================================

st.title("📊 Sazonalidade Estatística B3")

# =====================================================
# MÊS ATUAL
# =====================================================

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

mes_atual = datetime.now().month

st.subheader(
    f"Mês analisado: {MESES[mes_atual]}"
)

# =====================================================
# LISTA DE ATIVOS
# =====================================================

ATIVOS = [

    # =================================================
    # FIIs
    # =================================================

    "HGLG11.SA",
    "KNRI11.SA",
    "XPLG11.SA",
    "BTLG11.SA",
    "TRXF11.SA",
    "GARE11.SA",
    "GGRC11.SA",
    "VISC11.SA",
    "XPML11.SA",
    "MALL11.SA",
    "HSML11.SA",
    "PVBI11.SA",
    "LVBI11.SA",
    "VILG11.SA",
    "HGRU11.SA",
    "ALZR11.SA",

    # =================================================
    # ENERGIA
    # =================================================

    "TAEE11.SA",
    "TAEE4.SA",
    "CMIG4.SA",
    "CPLE6.SA",
    "EGIE3.SA",
    "TRPL4.SA",
    "EQTL3.SA",
    "ALUP11.SA",
    "ENGI11.SA",
    "NEOE3.SA",
    "ENEV3.SA",
    "AURE3.SA",

    # =================================================
    # SANEAMENTO
    # =================================================

    "SBSP3.SA",
    "CSMG3.SA",
    "SAPR4.SA",
    "SAPR11.SA",
    "ORVR3.SA"
]

# =====================================================
# FUNÇÕES
# =====================================================

def classificar_confianca(amostra):

    if amostra >= 10:
        return "Excelente"

    elif amostra >= 7:
        return "Boa"

    elif amostra >= 5:
        return "Moderada"

    else:
        return "Baixa"


def calcular_score(acerto, retorno):

    score = (
        (acerto * 0.7)
        + (retorno * 0.3)
    )

    return round(score, 2)


# =====================================================
# RESULTADOS
# =====================================================

resultados_principais = []
resultados_jovens = []

# =====================================================
# PROCESSAMENTO
# =====================================================

barra = st.progress(0)

for i, ticker in enumerate(ATIVOS):

    try:

        df = yf.download(
            ticker,
            period="15y",
            interval="1mo",
            progress=False
        )

        if df.empty:
            continue

        close = df["Close"]

        retorno = close.pct_change() * 100

        temp = pd.DataFrame()

        temp["Retorno"] = retorno

        temp.dropna(inplace=True)

        temp["Mes"] = temp.index.month

        filtro = temp[
            temp["Mes"] == mes_atual
        ]

        if len(filtro) < 2:
            continue

        positivos = filtro[
            filtro["Retorno"] > 0
        ]

        negativos = filtro[
            filtro["Retorno"] <= 0
        ]

        taxa_acerto = round(
            (len(positivos) / len(filtro)) * 100,
            2
        )

        retorno_medio = round(
            filtro["Retorno"].mean(),
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

        melhor_mes = round(
            filtro["Retorno"].max(),
            2
        )

        pior_mes = round(
            filtro["Retorno"].min(),
            2
        )

        score = calcular_score(
            taxa_acerto,
            retorno_medio
        )

        expectativa = round(
            (
                (taxa_acerto / 100) * gain_medio
            )
            +
            (
                ((100 - taxa_acerto) / 100)
                * loss_medio
            ),
            2
        )

        dados = {
            "Ativo": ticker.replace(".SA", ""),
            "Amostra": len(filtro),
            "Confiança": classificar_confianca(len(filtro)),
            "Taxa Acerto (%)": taxa_acerto,
            "Retorno Médio (%)": retorno_medio,
            "Gain Médio (%)": gain_medio,
            "Loss Médio (%)": loss_medio,
            "Melhor Mês (%)": melhor_mes,
            "Pior Mês (%)": pior_mes,
            "Expectativa (%)": expectativa,
            "Score": score
        }

        if len(filtro) >= 5:
            resultados_principais.append(dados)

        else:
            resultados_jovens.append(dados)

    except Exception:
        pass

    barra.progress(
        (i + 1) / len(ATIVOS)
    )

# =====================================================
# TABELA PRINCIPAL
# =====================================================

st.header("🏆 Ranking Principal")

if len(resultados_principais) > 0:

    tabela = pd.DataFrame(
        resultados_principais
    )

    tabela.sort_values(
        by="Score",
        ascending=False,
        inplace=True
    )

    tabela.reset_index(
        drop=True,
        inplace=True
    )

    st.dataframe(
        tabela.style.format({
            "Taxa Acerto (%)": "{:.2f}",
            "Retorno Médio (%)": "{:.2f}",
            "Gain Médio (%)": "{:.2f}",
            "Loss Médio (%)": "{:.2f}",
            "Melhor Mês (%)": "{:.2f}",
            "Pior Mês (%)": "{:.2f}",
            "Expectativa (%)": "{:.2f}",
            "Score": "{:.2f}"
        }),
        use_container_width=True
    )

else:

    st.warning(
        "Nenhum resultado encontrado."
    )

# =====================================================
# TABELA SECUNDÁRIA
# =====================================================

st.header("⚠️ Ativos com Baixa Amostragem")

if len(resultados_jovens) > 0:

    tabela2 = pd.DataFrame(
        resultados_jovens
    )

    tabela2.sort_values(
        by="Score",
        ascending=False,
        inplace=True
    )

    tabela2.reset_index(
        drop=True,
        inplace=True
    )

    st.dataframe(
        tabela2.style.format({
            "Taxa Acerto (%)": "{:.2f}",
            "Retorno Médio (%)": "{:.2f}",
            "Gain Médio (%)": "{:.2f}",
            "Loss Médio (%)": "{:.2f}",
            "Melhor Mês (%)": "{:.2f}",
            "Pior Mês (%)": "{:.2f}",
            "Expectativa (%)": "{:.2f}",
            "Score": "{:.2f}"
        }),
        use_container_width=True
    )

else:

    st.info(
        "Nenhum ativo com baixa amostragem."
    )

# =====================================================
# MELHOR ATIVO DO MÊS
# =====================================================

if len(resultados_principais) > 0:

    melhor = tabela.iloc[0]

    st.header("🥇 Melhor Resultado Estatístico")

    st.success(f"""
Ativo: {melhor['Ativo']}

Taxa de Acerto: {melhor['Taxa Acerto (%)']}%

Retorno Médio: {melhor['Retorno Médio (%)']}%

Score: {melhor['Score']}
""")

# =====================================================
# RODAPÉ
# =====================================================

st.markdown("---")

st.markdown("""
### 📌 Interpretação

- Taxa Acerto:
Percentual histórico de meses positivos.

- Retorno Médio:
Média histórica de retorno no mês atual.

- Gain Médio:
Média apenas dos meses positivos.

- Loss Médio:
Média apenas dos meses negativos.

- Expectativa:
Estimativa matemática histórica.

- Confiança:
Robustez baseada na quantidade de anos.

- Score:
Pontuação estatística geral.

⚠️ Aplicação puramente estatística.
Não constitui recomendação de investimento.
""")
