import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from ta.trend import EMAIndicator, ADXIndicator
from ta.momentum import StochasticOscillator
from datetime import datetime

# =====================================================
# CONFIG
# =====================================================

st.set_page_config(
    page_title="Sazonalidade + Setup Técnico",
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

st.title("📊 Sazonalidade + Setup Técnico")

# =====================================================
# MÊS
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
# ATIVOS
# =====================================================

ATIVOS = [

    # FIIs
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

    # Energia
    "TAEE11.SA",
    "CMIG4.SA",
    "CPLE6.SA",
    "EGIE3.SA",
    "TRPL4.SA",
    "EQTL3.SA",
    "ALUP11.SA",
    "ENGI11.SA",

    # Saneamento
    "SBSP3.SA",
    "CSMG3.SA",
    "SAPR4.SA"
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


def analisar_sazonalidade(ticker):

    try:

        df = yf.download(
            ticker,
            period="15y",
            interval="1mo",
            progress=False,
            auto_adjust=True
        )

        if df.empty:
            return None

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
            return None

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

        score = calcular_score(
            taxa_acerto,
            retorno_medio
        )

        return {
            "Ativo": ticker,
            "Amostra": len(filtro),
            "Confiança": classificar_confianca(len(filtro)),
            "Taxa Acerto (%)": taxa_acerto,
            "Retorno Médio (%)": retorno_medio,
            "Gain Médio (%)": gain_medio,
            "Loss Médio (%)": loss_medio,
            "Score": score
        }

    except:
        return None


def analisar_tecnico(ticker):

    try:

        df = yf.download(
            ticker,
            period="1y",
            interval="1d",
            progress=False,
            auto_adjust=True
        )

        if df.empty:
            return None

        df.dropna(inplace=True)

        close = df["Close"]
        high = df["High"]
        low = df["Low"]

        # =================================================
        # EMA69
        # =================================================

        ema69 = EMAIndicator(
            close=close,
            window=69
        ).ema_indicator()

        preco_atual = close.iloc[-1]

        tendencia = preco_atual > ema69.iloc[-1]

        # =================================================
        # DMI
        # =================================================

        adx = ADXIndicator(
            high=high,
            low=low,
            close=close,
            window=14
        )

        di_plus = adx.adx_pos()
        di_minus = adx.adx_neg()

        dmi_ok = (
            di_plus.iloc[-1]
            >
            di_minus.iloc[-1]
        )

        # =================================================
        # ESTOCÁSTICO
        # =================================================

        stoch = StochasticOscillator(
            high=high,
            low=low,
            close=close,
            window=14,
            smooth_window=3
        )

        k = stoch.stoch()
        d = stoch.stoch_signal()

        estocastico_ok = (
            k.iloc[-1]
            >
            d.iloc[-1]
        )

        aprovado = (
            tendencia
            and dmi_ok
            and estocastico_ok
        )

        return {
            "Tendência": "✅" if tendencia else "❌",
            "DMI": "✅" if dmi_ok else "❌",
            "Estocástico": "✅" if estocastico_ok else "❌",
            "Status": "APROVADO" if aprovado else "REPROVADO"
        }

    except:
        return None

# =====================================================
# PROCESSAMENTO
# =====================================================

resultados = []
aprovados = []

barra = st.progress(0)

for i, ticker in enumerate(ATIVOS):

    sazonal = analisar_sazonalidade(
        ticker
    )

    if sazonal is not None:

        resultados.append(sazonal)

        if sazonal["Score"] >= 60:

            tecnico = analisar_tecnico(
                ticker
            )

            if tecnico is not None:

                linha = {
                    "Ativo": ticker.replace(".SA", ""),
                    "Score": sazonal["Score"],
                    "Taxa Acerto (%)": sazonal["Taxa Acerto (%)"],
                    "Retorno Médio (%)": sazonal["Retorno Médio (%)"],
                    "Tendência": tecnico["Tendência"],
                    "DMI": tecnico["DMI"],
                    "Estocástico": tecnico["Estocástico"],
                    "Status": tecnico["Status"]
                }

                aprovados.append(linha)

    barra.progress(
        (i + 1) / len(ATIVOS)
    )

# =====================================================
# TABELA PRINCIPAL
# =====================================================

st.header("🏆 Ranking Sazonal")

if len(resultados) > 0:

    tabela = pd.DataFrame(resultados)

    tabela["Ativo"] = tabela["Ativo"].str.replace(
        ".SA",
        "",
        regex=False
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
        tabela,
        use_container_width=True
    )

else:

    st.warning(
        "Nenhum resultado encontrado."
    )

# =====================================================
# TABELA FILTRADA
# =====================================================

st.header("✅ Sazonalidade + Setup Técnico")

if len(aprovados) > 0:

    tabela2 = pd.DataFrame(
        aprovados
    )

    tabela2 = tabela2[
        tabela2["Status"] == "APROVADO"
    ]

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
        tabela2,
        use_container_width=True
    )

else:

    st.warning(
        "Nenhum ativo aprovado."
    )

# =====================================================
# EXPLICAÇÃO
# =====================================================

st.markdown("---")

st.markdown("""
### 📌 Interpretação

## Ranking Sazonal
Mostra os ativos com melhor histórico estatístico para o mês atual.

---

## Score
Mistura:
- frequência histórica de alta;
- retorno médio.

Quanto maior:
melhor a sazonalidade histórica.

---

## Tabela "Sazonalidade + Setup Técnico"

Mostra apenas ativos que:

- possuem Score acima de 60;
- estão acima da EMA69;
- possuem DI+ acima do DI−;
- possuem estocástico alinhado.

---

## Status APROVADO
Significa:
- sazonalidade forte;
- tendência favorável;
- momentum alinhado.

⚠️ Aplicação puramente estatística/técnica.
Não constitui recomendação de investimento.
""")
