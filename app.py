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
    page_title="Scanner Sazonalidade B3",
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

    senha = st.text_input(
        "Digite a senha",
        type="password"
    )

    if st.button("Entrar"):

        if senha == SENHA:
            st.session_state.logado = True
            st.rerun()

        else:
            st.error("Senha incorreta")

    st.stop()

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

# =====================================================
# TÍTULO
# =====================================================

st.title("📊 Scanner Sazonalidade B3")

st.subheader(
    f"Mês analisado: {MESES[mes_atual]}"
)

# =====================================================
# LISTAS
# =====================================================

LISTAS = {

    "FIIs": [

        "GARE11.SA",
        "HGLG11.SA",
        "XPLG11.SA",
        "VILG11.SA",
        "BRCO11.SA",
        "BTLG11.SA",
        "XPML11.SA",
        "VISC11.SA",
        "HSML11.SA",
        "MALL11.SA",
        "KNRI11.SA",
        "JSRE11.SA",
        "PVBI11.SA",
        "HGRE11.SA",
        "MXRF11.SA",
        "KNCR11.SA",
        "KNIP11.SA",
        "CPTS11.SA",
        "IRDM11.SA",
        "TGAR11.SA",
        "TRXF11.SA",
        "HGRU11.SA",
        "ALZR11.SA",
        "XPCA11.SA",
        "VGIA11.SA",
        "RBRR11.SA",
        "KNSC11.SA",
        "HGCR11.SA",
        "MCCI11.SA",
        "RECR11.SA",
        "VRTA11.SA",
        "BCFF11.SA",
        "HFOF11.SA",
        "XPSF11.SA",
        "RBRP11.SA",
        "RBRF11.SA",
        "RZTR11.SA",
        "RURA11.SA",
        "VGIR11.SA",
        "CVBI11.SA",
        "UTLL11.SA",
        "GGRC11.SA",
        "AUVP11.SA",
        "IEEX11.SA"
    ],

    "Utilities": [

        "TAEE11.SA",
        "CMIG4.SA",
        "CPFE3.SA",
        "EQTL3.SA",
        "ELET3.SA",
        "ELET6.SA",
        "ALUP11.SA",
        "TRPL4.SA",
        "NEOE3.SA",
        "ENGI11.SA",
        "SBSP3.SA",
        "SAPR11.SA",
        "CSMG3.SA"
    ],

    "Bancos": [

        "BBAS3.SA",
        "ITUB4.SA",
        "ITSA4.SA",
        "BBDC4.SA",
        "BBDC3.SA",
        "SANB11.SA",
        "BPAC11.SA",
        "BRSR6.SA"
    ],

    "Blue Chips": [

        "VALE3.SA",
        "PETR4.SA",
        "PETR3.SA",
        "WEGE3.SA",
        "SUZB3.SA",
        "KLBN11.SA",
        "JBSS3.SA",
        "PRIO3.SA",
        "RECV3.SA",
        "EGIE3.SA",
        "VIVT3.SA",
        "TOTS3.SA",
        "RAIL3.SA"
    ],

    "BDRs": [

        "AAPL34.SA",
        "MSFT34.SA",
        "GOGL34.SA",
        "AMZO34.SA",
        "META34.SA",
        "NVDC34.SA",
        "JPMC34.SA",
        "DISB34.SA",
        "SBUX34.SA"
    ],

    "ETFs": [

        "BOVA11.SA",
        "SMAL11.SA",
        "IVVB11.SA",
        "DIVO11.SA"
    ]
}

# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.title("⚙️ Configurações")

categoria = st.sidebar.selectbox(
    "Escolha a categoria:",
    list(LISTAS.keys())
)

score_minimo = st.sidebar.slider(
    "Score mínimo",
    0,
    100,
    60
)

ativos = LISTAS[categoria]

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
        +
        (retorno * 0.3)
    )

    return round(score, 2)


@st.cache_data(ttl=3600)
def analisar_sazonalidade(ticker):

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
            "Ativo": ticker.replace(".SA", ""),
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


@st.cache_data(ttl=3600)
def analisar_tecnico(ticker):

    try:

        df = yf.download(
            ticker,
            period="1y",
            interval="1d",
            auto_adjust=True,
            progress=False
        )

        if df.empty:
            return None

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

        tendencia = (
            close.iloc[-1]
            >
            ema69.iloc[-1]
        )

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

for i, ticker in enumerate(ativos):

    sazonal = analisar_sazonalidade(
        ticker
    )

    if sazonal is not None:

        resultados.append(sazonal)

        if sazonal["Score"] >= score_minimo:

            tecnico = analisar_tecnico(
                ticker
            )

            if tecnico is not None:

                linha = {
                    "Ativo": ticker.replace(".SA", ""),
                    "Score": sazonal["Score"],
                    "Taxa Acerto (%)": sazonal["Taxa Acerto (%)"],
                    "Retorno Médio (%)": sazonal["Retorno Médio (%)"],
                    "Gain Médio (%)": sazonal["Gain Médio (%)"],
                    "Loss Médio (%)": sazonal["Loss Médio (%)"],
                    "Tendência": tecnico["Tendência"],
                    "DMI": tecnico["DMI"],
                    "Estocástico": tecnico["Estocástico"],
                    "Status": tecnico["Status"]
                }

                aprovados.append(linha)

    barra.progress(
        (i + 1) / len(ativos)
    )

# =====================================================
# TABELA SAZONAL
# =====================================================

st.header("🏆 Ranking Sazonal")

if len(resultados) > 0:

    tabela = pd.DataFrame(resultados)

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
# MELHOR ATIVO
# =====================================================

if len(resultados) > 0:

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

## Sazonalidade + Setup Técnico

Mostra apenas ativos que:

- possuem Score acima do filtro mínimo;
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
