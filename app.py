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
    return ratios, revenue, net_income


def label_dates(cols):
    return [pd.to_datetime(c).strftime("%b %Y") for c in cols]


def kpi(col, label, value):
    shown = "n/a" if value is None or pd.isna(value) else f"{value:,.2f}"
    col.markdown(
        f'<div class="kpi"><div class="label">{label}</div><div class="value">{shown}</div></div>',
        unsafe_allow_html=True,
    )


# ---------- UI ----------
st.title("FinSight AI")
st.caption("Understand businesses beyond numbers.")

ticker = st.text_input(
    "Enter an NSE ticker (examples: RELIANCE.NS, ITC.NS, HINDUNILVR.NS)",
    value="RELIANCE.NS",
).strip().upper()

if ticker:
    try:
        with st.spinner("Fetching financial statements..."):
            name, income, balance = load_company(ticker)
    except Exception as e:
        st.error(f"Could not fetch data for {ticker}. Details: {e}")
        st.stop()

    if income is None or income.empty or balance is None or balance.empty:
        st.error(
            f"No financial statements found for {ticker}. "
            "Check the ticker (NSE tickers end in .NS, BSE in .BO)."
        )
        st.stop()

    st.header(name)
    ratios, revenue, net_income = compute_ratios(income, balance)

    if ratios.empty:
        st.warning("Statements were found, but the line items needed for ratios are missing.")
        st.stop()

    latest = ratios.columns[-1]
    st.subheader(f"Latest year KPIs ({pd.to_datetime(latest).strftime('%b %Y')})")
    c1, c2, c3, c4 = st.columns(4)
    def latest_val(row_name):
        if row_name in ratios.index:
            return ratios.loc[row_name, latest]
        return None

    kpi(c1, "Net margin (%)", latest_val("Net margin (%)"))
    kpi(c2, "ROE (%)", latest_val("ROE (%)"))
    kpi(c3, "Debt / Equity (x)", latest_val("Debt / Equity (x)"))
    kpi(c4, "Current ratio (x)", latest_val("Current ratio (x)"))

    st.subheader("Revenue and net income (₹ crore)")
    if revenue is not None and net_income is not None:
        labels = label_dates(revenue.index)
        fig = go.Figure()
        fig.add_bar(x=labels, y=(revenue / 1e7).values, name="Revenue", marker_color="#0B1F3A")
        fig.add_bar(x=labels, y=(net_income.reindex(revenue.index) / 1e7).values, name="Net income", marker_color="#2563EB")
        fig.update_layout(
            barmode="group",
            plot_bgcolor="white",
            paper_bgcolor="white",
            margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(orientation="h"),
        )
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Ratio table")
    table = ratios.copy()
    table.columns = label_dates(table.columns)
    st.dataframe(table.round(2), use_container_width=True)

    st.caption(
        "Source: Yahoo Finance via the yfinance library (unofficial). Data may have gaps or errors, "
        "so verify against company filings. For education only, not investment advice."
    )
