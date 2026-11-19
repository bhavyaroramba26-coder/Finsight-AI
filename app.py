import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

st.set_page_config(page_title="FinSight AI", page_icon="📊", layout="wide")

# ---------- Styling ----------
st.markdown(
    """
<style>
.block-container {padding-top: 2rem;}
h1, h2, h3 {color: #0B1F3A;}
.kpi {background:#F5F7FA; border:1px solid #E3E8EF; border-radius:10px; padding:16px;}
.kpi .label {color:#5B6B82; font-size:0.85rem;}
.kpi .value {color:#0B1F3A; font-size:1.6rem; font-weight:600;}
</style>
""",
    unsafe_allow_html=True,
)

NAVY = "#0B1F3A"
BLUE = "#2563EB"
GREY = "#94A3B8"


# ---------- Data ----------
@st.cache_data(ttl=3600, show_spinner=False)
def load_company(ticker: str):
    t = yf.Ticker(ticker)
    income = t.income_stmt
    balance = t.balance_sheet
    try:
        name = t.info.get("longName", ticker)
    except Exception:
        name = ticker
    return name, income, balance


def get_row(df, names):
    """Return the first matching row (as a Series) from a statement, else None."""
    if df is None or df.empty:
        return None
    for n in names:
        if n in df.index:
            return df.loc[n].astype(float)
    return None


def safe_div(a, b):
    if a is None or b is None:
        return None
    return a / b.where(b != 0)


# ---------- Ratios ----------
def compute_ratios(income, balance):
    income = income.sort_index(axis=1)  # oldest -> newest
    balance = balance.sort_index(axis=1)

    revenue = get_row(income, ["Total Revenue", "Operating Revenue"])
    net_income = get_row(income, ["Net Income", "Net Income Common Stockholders"])
    ebit = get_row(income, ["EBIT", "Operating Income"])
    interest = get_row(income, ["Interest Expense"])
    equity = get_row(
        balance,
        ["Stockholders Equity", "Common Stock Equity", "Total Equity Gross Minority Interest"],
    )
    debt = get_row(balance, ["Total Debt"])
    cur_assets = get_row(balance, ["Current Assets"])
    cur_liab = get_row(balance, ["Current Liabilities"])

    rows = {}
    if revenue is not None:
        rows["Revenue growth (%)"] = revenue.pct_change() * 100
    if safe_div(net_income, revenue) is not None:
        rows["Net margin (%)"] = safe_div(net_income, revenue) * 100
    if safe_div(ebit, revenue) is not None:
        rows["Operating margin (%)"] = safe_div(ebit, revenue) * 100
    if safe_div(net_income, equity) is not None:
        rows["ROE (%)"] = safe_div(net_income, equity) * 100
    if safe_div(debt, equity) is not None:
        rows["Debt / Equity (x)"] = safe_div(debt, equity)
    if safe_div(cur_assets, cur_liab) is not None:
        rows["Current ratio (x)"] = safe_div(cur_assets, cur_liab)
    if interest is not None and ebit is not None:
        rows["Interest coverage (x)"] = safe_div(ebit, interest.abs())

    ratios = pd.DataFrame(rows).T if rows else pd.DataFrame()
    if not ratios.empty:
        ratios = ratios.sort_index(axis=1).dropna(axis=1, how="all")  # drop years with no data
    return ratios, revenue, net_income


def analyze(ticker: str):
    name, income, balance = load_company(ticker)
    if income is None or income.empty or balance is None or balance.empty:
        raise ValueError(
            f"No financial statements found for {ticker}. NSE tickers end in .NS and BSE tickers in .BO."
        )
    ratios, revenue, net_income = compute_ratios(income, balance)
    if ratios.empty:
        raise ValueError(f"Statements found for {ticker}, but the line items needed for ratios are missing.")
    return name, ratios, revenue, net_income


# ---------- AI (Gemini) ----------
# The app tries these models in order. If Google renames models, only this list needs changing.
MODELS = ["gemini-flash-latest", "gemini-flash-lite-latest", "gemini-2.5-flash"]


def get_api_key():
    try:
        return st.secrets["GEMINI_API_KEY"]
    except Exception:
        return None


def ask_gemini(prompt: str) -> str:
    key = get_api_key()
    if not key:
        raise RuntimeError("NO_KEY")
    from google import genai

    client = genai.Client(api_key=key)
    last_error = None
    for model in MODELS:
        try:
            response = client.models.generate_content(model=model, contents=prompt)
            return response.text
        except Exception as e:
            last_error = e
    raise last_error


def build_prompt(name: str, ticker: str, ratios: pd.DataFrame) -> str:
    table = ratios.copy()
    table.columns = label_dates(table.columns)
    table_text = table.round(2).to_string()
    return (
        "You are a financial research assistant helping finance students understand listed Indian companies.\n"
        f"Company: {name} ({ticker}). Figures come from annual statements; columns are financial year-ends.\n\n"
        "Computed ratios (revenue growth, margins and ROE are in %, the rest are multiples):\n"
        f"{table_text}\n\n"
        "Write a concise analysis using ONLY the numbers above. Do not mention stock prices, news, "
        "valuation multiples or any figure that is not in the table. If something cannot be concluded "
        "from the data, say so. Use these sections with short bullet points:\n"
        "1. Overview (2 sentences)\n"
        "2. Strengths\n"
        "3. Risks and watch points\n"
        "4. Trends over the years shown\n"
        "5. What to check next in the annual report\n"
        "If the company looks like a bank or financial company, note that ratios such as debt/equity "
        "and current ratio are not meaningful for it. End with one line saying this is educational "
        "analysis and not investment advice."
    )


# ---------- Helpers ----------
def label_dates(cols):
    return [pd.to_datetime(c).strftime("%b %Y") for c in cols]


def kpi(col, label, value):
    shown = "n/a" if value is None or pd.isna(value) else f"{value:,.2f}"
    col.markdown(
        f'<div class="kpi"><div class="label">{label}</div><div class="value">{shown}</div></div>',
        unsafe_allow_html=True,
    )


def style_fig(fig):
    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(orientation="h"),
        font=dict(color=NAVY),
    )
    fig.update_yaxes(gridcolor="#E3E8EF")
    return fig


# ---------- UI ----------
st.title("FinSight AI")
st.caption("Understand businesses beyond numbers.")

tab1, tab2, tab3 = st.tabs(["Company analysis", "Compare companies", "AI Analyst"])

# ===== Tab 1: single company =====
with tab1:
    ticker = st.text_input(
        "Enter an NSE ticker (examples: RELIANCE.NS, ITC.NS, HINDUNILVR.NS)",
        value="RELIANCE.NS",
        key="single_ticker",
    ).strip().upper()

    if ticker:
        try:
            with st.spinner("Fetching financial statements..."):
                name, ratios, revenue, net_income = analyze(ticker)
        except Exception as e:
            st.error(f"Could not analyse {ticker}. {e}")
        else:
            st.header(name)
            latest = ratios.columns[-1]

            def latest_val(row_name):
                if row_name in ratios.index:
                    return ratios.loc[row_name, latest]
                return None

            st.subheader(f"Latest year KPIs ({pd.to_datetime(latest).strftime('%b %Y')})")
            c1, c2, c3, c4 = st.columns(4)
            kpi(c1, "Net margin (%)", latest_val("Net margin (%)"))
            kpi(c2, "ROE (%)", latest_val("ROE (%)"))
            kpi(c3, "Debt / Equity (x)", latest_val("Debt / Equity (x)"))
            kpi(c4, "Current ratio (x)", latest_val("Current ratio (x)"))

            if revenue is not None and net_income is not None:
                st.subheader("Revenue and net income (₹ crore)")
                rev = revenue.dropna()
                labels = label_dates(rev.index)
                fig = go.Figure()
                fig.add_bar(x=labels, y=(rev / 1e7).values, name="Revenue", marker_color=NAVY)
                fig.add_bar(
                    x=labels,
                    y=(net_income.reindex(rev.index) / 1e7).values,
                    name="Net income",
                    marker_color=BLUE,
                )
                fig.update_layout(barmode="group")
                fig.update_yaxes(tickformat=",", title_text="₹ crore")
                st.plotly_chart(style_fig(fig), use_container_width=True)

            st.subheader("Ratio table")
            table = ratios.copy()
            table.columns = label_dates(table.columns)
            st.dataframe(table.round(2), use_container_width=True)

# ===== Tab 2: comparison =====
with tab2:
    st.subheader("Compare companies")
    raw = st.text_input(
        "Enter 2 or 3 tickers separated by commas",
        value="RELIANCE.NS, ITC.NS, HINDUNILVR.NS",
        key="compare_tickers",
    )
    tickers = [t.strip().upper() for t in raw.split(",") if t.strip()][:3]

    if len(tickers) < 2:
        st.info("Enter at least two tickers to compare.")
    else:
        results = {}
        for t in tickers:
            try:
                with st.spinner(f"Fetching {t}..."):
                    name, ratios, _, _ = analyze(t)
                results[t] = (name, ratios)
            except Exception as e:
                st.warning(f"{t}: {e}")

        if len(results) >= 2:
            table = pd.DataFrame({t: r.iloc[:, -1] for t, (n, r) in results.items()})
            st.markdown("**Latest available year**")
            st.dataframe(table.round(2), use_container_width=True)

            st.caption(
                " | ".join(
                    f"{t}: {pd.to_datetime(r.columns[-1]).strftime('%b %Y')}"
                    for t, (n, r) in results.items()
                )
            )

            metric = st.selectbox("Chart a ratio", list(table.index))
            colors = [NAVY, BLUE, GREY]
            fig = go.Figure()
            for i, t in enumerate(table.columns):
                fig.add_bar(x=[t], y=[table.loc[metric, t]], name=t, marker_color=colors[i % 3])
            st.plotly_chart(style_fig(fig), use_container_width=True)

            st.caption(
                "Banks and financial companies (for example HDFCBANK.NS) have different balance-sheet "
                "structures, so ratios like debt/equity and current ratio are not meaningful for them."
            )

# ===== Tab 3: AI Analyst =====
with tab3:
    st.subheader("AI Analyst")
    st.caption(
        "The AI explains the ratios computed by this app. It does not browse the internet "
        "and does not use live prices or news."
    )
    ai_ticker = st.text_input(
        "Enter an NSE ticker", value="RELIANCE.NS", key="ai_ticker"
    ).strip().upper()

    if st.button("Generate analysis") and ai_ticker:
        try:
            with st.spinner("Computing ratios..."):
                name, ratios, _, _ = analyze(ai_ticker)
        except Exception as e:
            st.error(f"Could not analyse {ai_ticker}. {e}")
        else:
            try:
                with st.spinner("Writing analysis..."):
                    text = ask_gemini(build_prompt(name, ai_ticker, ratios))
                st.session_state["ai_result"] = (ai_ticker, name, ratios, text)
            except RuntimeError:
                st.info(
                    "The AI key is not set up yet. Add GEMINI_API_KEY in the app's Secrets "
                    "(Manage app, then Settings, then Secrets)."
                )
            except Exception as e:
                st.error(
                    "The AI service returned an error. This can happen if the free quota is "
                    "used up or the model name has changed. Try again in a minute."
                )
                st.caption(str(e)[:300])

    result = st.session_state.get("ai_result")
    if result:
        r_ticker, r_name, r_ratios, r_text = result
        st.header(r_name)
        st.markdown(r_text)
        st.caption("AI-generated from the computed ratios. It can make mistakes, so verify against filings.")
        with st.expander("Data given to the AI"):
            shown = r_ratios.copy()
            shown.columns = label_dates(shown.columns)
            st.dataframe(shown.round(2), use_container_width=True)

st.caption(
    "Source: Yahoo Finance via the yfinance library (unofficial). Data may have gaps or errors, "
    "so verify against company filings. For education only, not investment advice."
)
