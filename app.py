import streamlit as st
import pandas as pd
import yfinance as yf
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

if "logado" not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:

    st.title("🔒 Login")

    senha = st.text_input(
        "Digite a senha:",
        type="password"
    )

    if st.button("Entrar"):

        if senha == SENHA_CORRETA:
            st.session_state.logado = True
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
# MESES
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

mes_atual = datetime.now().month
nome_mes = MESES[mes_atual]

# =========================================================
# TÍTULO
# =========================================================

st.title("📊 Sazonalidade Estatística B3")

st.markdown(f"""
## Mês analisado: {nome_mes}

Análise histórica simples de:
- FIIs
- Energia
- Saneamento
""")

# =========================================================
# FUNÇÃO
# =========================================================

@st.cache_data(ttl=3600)
def analisar_ativo(ticker):

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

        df["Retorno"] = (
            df["Close"].pct_change() * 100
        )

        df.dropna(inplace=True)

        df["Mes"] = df.index.month

        df_mes = df[
            df["Mes"] == mes_atual
        ]

        if len(df_mes) < 2:
            return None

        positivos = df_mes[
            df_mes["Retorno"] > 0
        ]

        taxa_acerto = round(
            (len(positivos) / len(df_mes)) * 100,
            2
        )

        retorno_medio = round(
            df_mes["Retorno"].mean(),
            2
        )

        return {
            "Ativo": ticker.replace(".SA", ""),
            "Amostra": len(df_mes),
            "Taxa Acerto (%)": taxa_acerto,
            "Retorno Médio (%)": retorno_medio
        }

    except:
        return None

# =========================================================
# PROCESSAMENTO
# =========================================================

resultado = []

barra = st.progress(0)

for i, ticker in enumerate(ATIVOS):

    dados = analisar_ativo(ticker)

    if dados is not None:
        resultado.append(dados)

    barra.progress(
        (i + 1) / len(ATIVOS)
    )

# =========================================================
# RESULTADO
# =========================================================

if len(resultado) > 0:

    tabela = pd.DataFrame(resultado)

    tabela.sort_values(
        by="Taxa Acerto (%)",
        ascending=False,
        inplace=True
    )

    tabela.reset_index(
        drop=True,
        inplace=True
    )

    st.subheader("🏆 Ranking Histórico")

    st.dataframe(
        tabela,
        use_container_width=True
    )

else:

    st.warning(
        "Nenhum resultado encontrado."
    )

# =========================================================
# RODAPÉ
# =========================================================

st.markdown("---")

st.markdown("""
### 📌 Interpretação

- Taxa Acerto:
Percentual histórico de meses positivos.

- Retorno Médio:
Média histórica de retorno no mês atual.

- Amostra:
Quantidade de anos analisados.

⚠️ Aplicação puramente estatística.
""")
