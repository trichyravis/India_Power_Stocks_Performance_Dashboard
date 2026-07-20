
from __future__ import annotations

from datetime import date, timedelta
import io
import math

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf


st.set_page_config(
    page_title="India Power Stocks Analytics | Mountain Path Academy",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

STOCKS = {
    "NTPC": "NTPC.NS",
    "Power Grid": "POWERGRID.NS",
    "Tata Power": "TATAPOWER.NS",
    "Adani Power": "ADANIPOWER.NS",
    "JSW Energy": "JSWENERGY.NS",
}
COLORS = {
    "NTPC": "#0B5CAD", "Power Grid": "#13A89E", "Tata Power": "#F59E0B",
    "Adani Power": "#E45756", "JSW Energy": "#7C3AED"
}
TRADING_DAYS = 252
RISK_FREE_RATE = 0.065

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
html, body, [class*="css"] {font-family: 'Inter', sans-serif;}
.stApp {background: linear-gradient(180deg,#F7F9FC 0%,#EEF3F8 100%);}
[data-testid="stSidebar"] {background: linear-gradient(180deg,#0B2545,#153F69);}
[data-testid="stSidebar"] * {color:#F4F8FC!important;}
.hero {background:linear-gradient(115deg,#081F3A 0%,#124A78 70%,#A97908 150%); padding:30px 34px;
 border-radius:20px; color:white; box-shadow:0 12px 32px rgba(6,27,52,.18); margin-bottom:18px;}
.hero h1 {font-size:2.15rem; margin:0 0 8px; color:white}.hero p {margin:0;color:#D6E9F5;font-size:1.02rem}
.eyebrow {color:#F3C84B;text-transform:uppercase;letter-spacing:.12em;font-weight:800;font-size:.75rem;margin-bottom:.55rem}
.section-title {font-size:1.35rem;font-weight:800;color:#0B2545;margin:16px 0 8px}
[data-testid="stMetric"] {background:#FFF;border:1px solid #DFE9F1;padding:14px;border-radius:14px;
 box-shadow:0 5px 16px rgba(18,54,84,.06)}
.note {background:#FFF7DD;border-left:5px solid #D4A017;padding:12px 15px;border-radius:9px;color:#4A3A0A}
.stTabs [data-baseweb="tab-list"] {gap:8px;flex-wrap:wrap;background:#D7E1EC;padding:.5rem;border-radius:13px}
.stTabs [data-baseweb="tab"] {background:#0B2545!important;border:2px solid #0B2545!important;border-radius:9px!important;padding:9px 16px;color:#F3C84B!important;font-weight:850!important;box-shadow:0 3px 8px rgba(11,37,69,.14)}
.stTabs [data-baseweb="tab"] p {color:#F3C84B!important;font-weight:850!important}
.stTabs [data-baseweb="tab"]:hover {background:#123F69!important;border-color:#F3C84B!important}
.stTabs [aria-selected="true"] {background:#123F69!important;color:#FFD85A!important;border:2px solid #F3C84B!important;box-shadow:0 0 0 2px rgba(243,200,75,.18)}
.stTabs [aria-selected="true"] p {color:#FFD85A!important}
.stButton button,.stDownloadButton button {background:#0B3B67!important;color:white!important;border:1px solid #0B3B67!important;border-radius:9px!important;font-weight:750!important}
.stButton button:hover,.stDownloadButton button:hover {background:#D4A017!important;color:#071A2F!important;border-color:#D4A017!important}
div[data-testid="stSelectbox"] [data-baseweb="select"]>div {min-height:46px!important;background:#FFF!important;border:2px solid #0B3B67!important;border-radius:10px!important}
div[data-testid="stSelectbox"] [data-baseweb="select"] * {color:#0B2545!important;-webkit-text-fill-color:#0B2545!important;font-weight:700!important}
[data-baseweb="popover"] [role="listbox"] {background:#FFF!important;border:2px solid #0B3B67!important}
[data-baseweb="popover"] [role="option"] {color:#0B2545!important;-webkit-text-fill-color:#0B2545!important;background:#FFF!important}
[data-baseweb="popover"] [role="option"]:hover,[data-baseweb="popover"] [aria-selected="true"] {background:#0B3B67!important;color:#FFF!important;-webkit-text-fill-color:#FFF!important}
/* Sidebar controls: gold labels, white fields and high-contrast navy values */
section[data-testid="stSidebar"] label p {color:#F3C84B!important;-webkit-text-fill-color:#F3C84B!important;font-weight:800!important}
section[data-testid="stSidebar"] div[data-testid="stSelectbox"] [data-baseweb="select"]>div {background:#FFF!important;border:2px solid #F3C84B!important}
section[data-testid="stSidebar"] div[data-testid="stSelectbox"] [data-baseweb="select"] span,
section[data-testid="stSidebar"] div[data-testid="stSelectbox"] [data-baseweb="select"] svg {color:#0B2545!important;-webkit-text-fill-color:#0B2545!important;fill:#0B2545!important;opacity:1!important}
/* Keep the selected company visible across Streamlit/BaseWeb versions.
   The displayed value may be rendered as a div, p, or span. */
section[data-testid="stSidebar"] div[data-testid="stSelectbox"] [data-baseweb="select"] > div,
section[data-testid="stSidebar"] div[data-testid="stSelectbox"] [data-baseweb="select"] > div * {
 color:#071A2F!important;
 -webkit-text-fill-color:#071A2F!important;
 font-weight:800!important;
 opacity:1!important;
}
section[data-testid="stSidebar"] div[data-testid="stSelectbox"] [data-baseweb="select"] svg {
 color:#071A2F!important;fill:#071A2F!important;
}
section[data-testid="stSidebar"] div[data-testid="stSelectbox"] input,
section[data-testid="stSidebar"] div[data-testid="stSelectbox"] input::placeholder,
section[data-testid="stSidebar"] div[data-testid="stSelectbox"] [data-baseweb="select"] p,
section[data-testid="stSidebar"] div[data-testid="stSelectbox"] [data-baseweb="select"] div[role="button"] {
 color:#071A2F!important;
 -webkit-text-fill-color:#071A2F!important;
 caret-color:#071A2F!important;
 font-weight:800!important;
 opacity:1!important;
}
.selected-company-confirmation {
 margin:-4px 0 10px;
 padding:7px 10px;
 background:#F3C84B;
 border:1px solid #D4A017;
 border-radius:8px;
 color:#071A2F!important;
 -webkit-text-fill-color:#071A2F!important;
 font-size:.84rem;
 font-weight:800;
}
.selected-company-confirmation * {color:#071A2F!important;-webkit-text-fill-color:#071A2F!important}
section[data-testid="stSidebar"] div[data-testid="stNumberInput"]>div {background:#FFF!important;border:2px solid #F3C84B!important;border-radius:10px!important;overflow:hidden}
section[data-testid="stSidebar"] div[data-testid="stNumberInput"] input {background:#FFF!important;color:#0B2545!important;-webkit-text-fill-color:#0B2545!important;font-weight:800!important;opacity:1!important}
section[data-testid="stSidebar"] div[data-testid="stNumberInput"] button {background:#E8EEF5!important;color:#0B2545!important;border-color:#CBD8E5!important}
section[data-testid="stSidebar"] div[data-testid="stNumberInput"] button svg {fill:#0B2545!important;color:#0B2545!important;opacity:1!important}
section[data-testid="stSidebar"] div[data-testid="stMultiSelect"] [data-baseweb="select"]>div {background:#FFF!important;border:2px solid #F3C84B!important;border-radius:10px!important}
section[data-testid="stSidebar"] div[data-testid="stMultiSelect"] [data-baseweb="tag"] {background:#D4A017!important}
section[data-testid="stSidebar"] div[data-testid="stMultiSelect"] [data-baseweb="tag"] span {color:#071A2F!important;-webkit-text-fill-color:#071A2F!important;font-weight:800!important}
section[data-testid="stSidebar"] div[data-testid="stMultiSelect"] [data-baseweb="tag"] svg {fill:#071A2F!important;color:#071A2F!important}
.profile-card {background:linear-gradient(135deg,#071A2F,#123B65);border:1px solid rgba(243,200,75,.42);border-radius:14px;padding:17px;margin:15px 0 8px;box-shadow:0 7px 20px rgba(0,0,0,.18)}
.profile-card .name {color:#F3C84B!important;font-weight:850;font-size:1rem;margin:0 0 5px}
.profile-card .title {color:#D7E9FA!important;font-size:.81rem;line-height:1.4;margin:0 0 8px}
.profile-card .stats {color:#AFC7DE!important;font-size:.76rem;line-height:1.45;margin:4px 0}
.profile-card .links {margin-top:11px;display:flex;gap:11px;flex-wrap:wrap}
.profile-card .links a {color:#F3C84B!important;text-decoration:none;font-size:.78rem;font-weight:750}
.profile-card .links a:hover {color:#FFF!important;text-decoration:underline}
.about-section {background:linear-gradient(125deg,#0B2545,#123F69);color:#EAF3FC;border:1px solid rgba(212,160,23,.45);border-radius:17px;padding:26px 30px;margin:24px 0 12px;box-shadow:0 10px 27px rgba(11,37,69,.16)}
.about-section h3 {color:#F3C84B!important;margin:0 0 11px}.about-section p {color:#EAF3FC;line-height:1.62;margin:7px 0}.about-section .highlight {color:#F3C84B;font-weight:800}
.academy-link {display:inline-block;margin-top:13px;padding:8px 16px;background:#D4A017;color:#071A2F!important;border-radius:8px;text-decoration:none;font-weight:850}
.mp-footer {text-align:center;padding:23px 0 8px;margin-top:25px;border-top:1px solid rgba(212,160,23,.4);color:#64778B;font-size:.84rem}
.mp-footer .footer-brand {color:#0B2545;font-size:1.12rem;font-weight:850}.mp-footer .footer-profile {color:#38556F;margin:5px 0 8px}.mp-footer a {color:#0B4F86;text-decoration:none;font-weight:750;margin:0 7px}.mp-footer a:hover {color:#A97908;text-decoration:underline}
</style>
""", unsafe_allow_html=True)


def first_row(df: pd.DataFrame, names: list[str]) -> pd.Series:
    for name in names:
        if name in df.index:
            return pd.to_numeric(df.loc[name], errors="coerce")
    return pd.Series(index=df.columns, dtype=float)


def safe_div(a, b):
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where((pd.notna(b)) & (b != 0), a / b, np.nan)


def fmt_num(v, prefix="₹", suffix=""):
    if pd.isna(v): return "—"
    av = abs(v)
    if av >= 1e12: return f"{prefix}{v/1e12:,.2f}T{suffix}"
    if av >= 1e9: return f"{prefix}{v/1e9:,.2f}B{suffix}"
    if av >= 1e7: return f"{prefix}{v/1e7:,.2f} Cr{suffix}"
    return f"{prefix}{v:,.2f}{suffix}"


def pct(v):
    return "—" if pd.isna(v) else f"{v:.2%}"


@st.cache_data(ttl=3600, show_spinner=False)
def load_prices(tickers: tuple[str, ...], start: str, end: str):
    raw = yf.download(list(tickers), start=start, end=end, auto_adjust=True,
                      progress=False, group_by="column", threads=True)
    close = raw["Close"] if isinstance(raw.columns, pd.MultiIndex) else raw[["Close"]]
    if isinstance(close, pd.Series): close = close.to_frame(tickers[0])
    close = close.rename(columns={v: k for k, v in STOCKS.items()})
    return close.dropna(how="all")


@st.cache_data(ttl=21600, show_spinner=False)
def load_company(ticker: str):
    t = yf.Ticker(ticker)
    try: info = t.info or {}
    except Exception: info = {}
    try: income = t.financials.copy()
    except Exception: income = pd.DataFrame()
    try: balance = t.balance_sheet.copy()
    except Exception: balance = pd.DataFrame()
    try: cashflow = t.cashflow.copy()
    except Exception: cashflow = pd.DataFrame()
    return info, income, balance, cashflow


def annual_financials(income, balance, cashflow):
    cols = sorted(set(income.columns) | set(balance.columns) | set(cashflow.columns))
    out = pd.DataFrame(index=cols)
    out["Revenue"] = first_row(income, ["Total Revenue", "Operating Revenue"])
    out["EBITDA"] = first_row(income, ["EBITDA", "Normalized EBITDA"])
    out["EBIT"] = first_row(income, ["EBIT", "Operating Income"])
    out["Net Income"] = first_row(income, ["Net Income", "Net Income Common Stockholders"])
    out["Interest Expense"] = abs(first_row(income, ["Interest Expense", "Interest Expense Non Operating"]))
    out["Total Assets"] = first_row(balance, ["Total Assets"])
    out["Equity"] = first_row(balance, ["Stockholders Equity", "Total Equity Gross Minority Interest"])
    out["Debt"] = first_row(balance, ["Total Debt"])
    out["Current Assets"] = first_row(balance, ["Current Assets", "Total Current Assets"])
    out["Current Liabilities"] = first_row(balance, ["Current Liabilities", "Total Current Liabilities"])
    out["Cash"] = first_row(balance, ["Cash Cash Equivalents And Short Term Investments", "Cash And Cash Equivalents"])
    out["Inventory"] = first_row(balance, ["Inventory"])
    out["Receivables"] = first_row(balance, ["Accounts Receivable", "Receivables"])
    out["Payables"] = first_row(balance, ["Payables And Accrued Expenses", "Accounts Payable", "Payables"])
    out["Operating Cash Flow"] = first_row(cashflow, ["Operating Cash Flow", "Total Cash From Operating Activities"])
    out["Capital Expenditure"] = abs(first_row(cashflow, ["Capital Expenditure", "Capital Expenditures"]))
    out["Free Cash Flow"] = out["Operating Cash Flow"] - out["Capital Expenditure"]
    avg_assets = out["Total Assets"].rolling(2).mean()
    avg_equity = out["Equity"].rolling(2).mean()
    out["Net Margin"] = safe_div(out["Net Income"], out["Revenue"])
    out["EBITDA Margin"] = safe_div(out["EBITDA"], out["Revenue"])
    out["ROA"] = safe_div(out["Net Income"], avg_assets)
    out["ROE"] = safe_div(out["Net Income"], avg_equity)
    out["Current Ratio"] = safe_div(out["Current Assets"], out["Current Liabilities"])
    out["Quick Ratio"] = safe_div(out["Current Assets"] - out["Inventory"], out["Current Liabilities"])
    out["Debt / Equity"] = safe_div(out["Debt"], out["Equity"])
    out["Interest Coverage"] = safe_div(out["EBIT"], out["Interest Expense"])
    out["Asset Turnover"] = safe_div(out["Revenue"], avg_assets)
    out["Receivable Days"] = safe_div(out["Receivables"], out["Revenue"]) * 365
    out["Inventory Days"] = safe_div(out["Inventory"], out["Revenue"]) * 365
    out["Payable Days"] = safe_div(out["Payables"], out["Revenue"]) * 365
    out["Cash Conversion Cycle"] = out["Receivable Days"] + out["Inventory Days"] - out["Payable Days"]
    out.index = pd.to_datetime(out.index).year
    return out.sort_index().tail(5)


def price_metrics(prices: pd.DataFrame, benchmark: pd.Series | None = None):
    ret = prices.pct_change().dropna(how="all")
    rows = []
    for c in prices:
        s, r = prices[c].dropna(), ret[c].dropna()
        if len(s) < 2: continue
        years = max((s.index[-1] - s.index[0]).days / 365.25, 1/365)
        wealth = (1 + r).cumprod()
        dd = wealth / wealth.cummax() - 1
        beta = np.nan
        if benchmark is not None:
            joined = pd.concat([r, benchmark.pct_change()], axis=1).dropna()
            if len(joined) > 2 and joined.iloc[:,1].var() != 0:
                beta = joined.cov().iloc[0,1] / joined.iloc[:,1].var()
        rows.append({"Company":c, "Last Price":s.iloc[-1], "5Y CAGR":(s.iloc[-1]/s.iloc[0])**(1/years)-1,
                     "Annual Return":r.mean()*TRADING_DAYS, "Volatility":r.std()*math.sqrt(TRADING_DAYS),
                     "Sharpe Ratio":(r.mean()*TRADING_DAYS-RISK_FREE_RATE)/(r.std()*math.sqrt(TRADING_DAYS)) if r.std() else np.nan,
                     "Max Drawdown":dd.min(), "Beta":beta})
    return pd.DataFrame(rows).set_index("Company"), ret


end = date.today() + timedelta(days=1)
start = end - timedelta(days=365*5 + 10)

with st.sidebar:
    st.markdown("## ⚡ Analysis Controls")
    selected = st.multiselect("Companies", list(STOCKS), default=list(STOCKS))
    primary = st.selectbox("Detailed company", selected if selected else list(STOCKS))
    st.markdown(
        f'<div class="selected-company-confirmation">Selected: {primary}</div>',
        unsafe_allow_html=True,
    )
    base = st.number_input("Investment simulation (₹)", 10_000, 10_000_000, 100_000, 10_000)
    normalize = st.toggle("Normalize price chart", value=True)
    st.markdown("---")
    st.caption("Prices: Yahoo Finance · Financial statements: company filings aggregated by Yahoo Finance. Values may differ by reporting convention.")
    if st.button("Refresh cached data", use_container_width=True):
        st.cache_data.clear(); st.rerun()
    st.markdown(
        """<div class='profile-card'>
        <p class='name'>Prof. V. Ravichandran</p>
        <p class='title'>Visiting Professor &amp; Professor of Practice at Leading Business Schools<br>
        Founder — The Mountain Path Academy</p>
        <p class='stats'>28+ years of industry experience<br>12+ years teaching Finance &amp; Financial Analytics</p>
        <div class='links'>
          <a href='https://themountainpathacademy.com' target='_blank'>🏔️ Academy</a>
          <a href='https://www.linkedin.com/in/trichyravis' target='_blank'>💼 LinkedIn</a>
          <a href='https://github.com/trichyravis' target='_blank'>💻 GitHub</a>
        </div></div>""", unsafe_allow_html=True)

if not selected:
    st.warning("Select at least one company from the sidebar."); st.stop()

st.markdown("""<div class="hero"><div class="eyebrow">The Mountain Path Academy · Equity Analytics</div><h1>India Power Stocks — Five-Year Analytics</h1>
<p>Market performance, risk, financial strength, profitability, valuation and working-capital intelligence in one classroom-ready dashboard.</p></div>""", unsafe_allow_html=True)

try:
    prices = load_prices(tuple(STOCKS[n] for n in selected), start.isoformat(), end.isoformat())
except Exception as e:
    st.error(f"Market data could not be loaded. Please check the internet connection or try again. Details: {e}"); st.stop()
if prices.empty:
    st.error("No market-price data was returned."); st.stop()

try:
    nifty = yf.download("^NSEI", start=start.isoformat(), end=end.isoformat(), auto_adjust=True, progress=False)["Close"]
    if isinstance(nifty, pd.DataFrame): nifty = nifty.iloc[:,0]
except Exception: nifty = None

pm, returns = price_metrics(prices, nifty)
infos, financials = {}, {}
with st.spinner("Loading reported financial statements…"):
    for name in selected:
        info, inc, bal, cf = load_company(STOCKS[name])
        infos[name] = info
        financials[name] = annual_financials(inc, bal, cf)

latest = pm.loc[primary]
c1,c2,c3,c4,c5 = st.columns(5)
c1.metric(f"{primary} price", fmt_num(latest["Last Price"], "₹"))
c2.metric("5Y CAGR", pct(latest["5Y CAGR"]))
c3.metric("Annual volatility", pct(latest["Volatility"]))
c4.metric("Sharpe ratio", "—" if pd.isna(latest["Sharpe Ratio"]) else f"{latest['Sharpe Ratio']:.2f}")
c5.metric("Maximum drawdown", pct(latest["Max Drawdown"]))

tabs = st.tabs(["Executive Dashboard","Market Performance","Financial Performance","Ratio Analysis","Working Capital","Valuation & Ranking","Statements & Downloads"])

with tabs[0]:
    st.markdown('<div class="section-title">Peer Snapshot</div>', unsafe_allow_html=True)
    peer=[]
    for n in selected:
        i=infos[n]; f=financials[n]; last=f.iloc[-1] if not f.empty else pd.Series(dtype=float)
        peer.append({"Company":n,"Market Cap (₹ Cr)":i.get("marketCap",np.nan)/1e7,"Price (₹)":pm.loc[n,"Last Price"],
                     "5Y CAGR":pm.loc[n,"5Y CAGR"],"ROE":i.get("returnOnEquity",last.get("ROE",np.nan)),
                     "Net Margin":i.get("profitMargins",last.get("Net Margin",np.nan)),"Debt/Equity":last.get("Debt / Equity",np.nan),
                     "P/E":i.get("trailingPE",np.nan)})
    peer_df=pd.DataFrame(peer).set_index("Company")
    # Keep table styling dependency-free for reliable cloud deployment.
    peer_styler = peer_df.style.format({
        "Market Cap (₹ Cr)":"{:,.0f}", "Price (₹)":"{:,.2f}",
        "5Y CAGR":"{:.2%}", "ROE":"{:.2%}", "Net Margin":"{:.2%}",
        "Debt/Equity":"{:.2f}", "P/E":"{:.2f}"
    }).set_properties(
        subset=["5Y CAGR", "ROE", "Net Margin"],
        **{"background-color":"#EAF4E2", "color":"#173B2A", "font-weight":"700"}
    )
    st.dataframe(peer_styler, use_container_width=True)
    a,b=st.columns(2)
    with a:
        fig=px.bar(peer_df.reset_index(),x="Company",y="Market Cap (₹ Cr)",color="Company",color_discrete_map=COLORS,title="Market Capitalisation (₹ crore)")
        fig.update_layout(showlegend=False); st.plotly_chart(fig,use_container_width=True)
    with b:
        risk=pm.reset_index()
        fig=px.scatter(risk,x="Volatility",y="Annual Return",size=[max(infos[n].get("marketCap",1),1) for n in risk.Company],text="Company",color="Company",color_discrete_map=COLORS,title="Risk–Return Map")
        fig.update_traces(textposition="top center"); fig.update_xaxes(tickformat=".0%");fig.update_yaxes(tickformat=".0%");st.plotly_chart(fig,use_container_width=True)
    st.markdown('<div class="note"><b>Teaching note:</b> A larger company is not automatically a better investment. Read market performance together with profitability, leverage, cash generation and valuation.</div>',unsafe_allow_html=True)

with tabs[1]:
    plot=(prices/prices.ffill().iloc[0]*100) if normalize else prices
    label="Growth of ₹100" if normalize else "Adjusted share price (₹)"
    fig=px.line(plot,title=f"Five-Year Price Trend — {label}",color_discrete_map=COLORS)
    fig.update_layout(yaxis_title=label,xaxis_title="",legend_title="Company",hovermode="x unified");st.plotly_chart(fig,use_container_width=True)
    invested=(prices/prices.ffill().iloc[0])*base
    st.plotly_chart(px.line(invested,title=f"Growth of ₹{base:,.0f} Invested",color_discrete_map=COLORS),use_container_width=True)
    show=pm.copy(); st.dataframe(show.style.format({"Last Price":"₹{:,.2f}","5Y CAGR":"{:.2%}","Annual Return":"{:.2%}","Volatility":"{:.2%}","Sharpe Ratio":"{:.2f}","Max Drawdown":"{:.2%}","Beta":"{:.2f}"}),use_container_width=True)
    corr=returns.corr(); fig=px.imshow(corr,text_auto=".2f",zmin=-1,zmax=1,color_continuous_scale="RdBu_r",title="Daily Return Correlation");st.plotly_chart(fig,use_container_width=True)

with tabs[2]:
    f=financials[primary]
    if f.empty: st.warning("Annual financial statements are unavailable for this company from the current data source.")
    else:
        units=1e7
        long=f[["Revenue","EBITDA","Net Income","Operating Cash Flow","Free Cash Flow"]].div(units).reset_index(names="Year").melt("Year",var_name="Metric",value_name="₹ crore")
        fig=px.bar(long,x="Year",y="₹ crore",color="Metric",barmode="group",title=f"{primary}: Revenue, Profit and Cash Flow (₹ crore)");st.plotly_chart(fig,use_container_width=True)
        margins=f[["EBITDA Margin","Net Margin","ROA","ROE"]].reset_index(names="Year").melt("Year",var_name="Metric",value_name="Ratio")
        fig=px.line(margins,x="Year",y="Ratio",color="Metric",markers=True,title="Profitability and Return Ratios");fig.update_yaxes(tickformat=".1%");st.plotly_chart(fig,use_container_width=True)

with tabs[3]:
    metric=st.selectbox("Compare ratio",["Net Margin","EBITDA Margin","ROA","ROE","Current Ratio","Quick Ratio","Debt / Equity","Interest Coverage","Asset Turnover"])
    comp=pd.DataFrame({n:financials[n][metric] for n in selected if metric in financials[n]}).sort_index()
    fig=px.line(comp,markers=True,title=f"Peer Comparison — {metric}",color_discrete_map=COLORS)
    if metric in ["Net Margin","EBITDA Margin","ROA","ROE"]: fig.update_yaxes(tickformat=".1%")
    st.plotly_chart(fig,use_container_width=True)
    f=financials[primary]
    cols=["Net Margin","EBITDA Margin","ROA","ROE","Current Ratio","Quick Ratio","Debt / Equity","Interest Coverage","Asset Turnover"]
    st.dataframe(f[cols].style.format({c:"{:.2%}" for c in cols[:4]}|{c:"{:.2f}" for c in cols[4:]}),use_container_width=True)

with tabs[4]:
    f=financials[primary]
    wc=["Current Assets","Current Liabilities","Inventory","Receivables","Payables"]
    long=f[wc].div(1e7).reset_index(names="Year").melt("Year",var_name="Component",value_name="₹ crore")
    st.plotly_chart(px.bar(long,x="Year",y="₹ crore",color="Component",barmode="group",title=f"{primary}: Working-Capital Components"),use_container_width=True)
    days=["Receivable Days","Inventory Days","Payable Days","Cash Conversion Cycle"]
    st.plotly_chart(px.line(f[days],markers=True,title="Working-Capital Efficiency (days)"),use_container_width=True)
    st.dataframe(f[["Current Ratio","Quick Ratio"]+days].style.format("{:.2f}"),use_container_width=True)
    st.caption("For power utilities, negative or unusual cash-conversion cycles may reflect billing cycles, regulated receivables, fuel arrangements and customer advances; interpret with business-model context.")

with tabs[5]:
    val=[]
    for n in selected:
        i=infos[n]
        val.append({"Company":n,"P/E":i.get("trailingPE",np.nan),"Forward P/E":i.get("forwardPE",np.nan),"P/B":i.get("priceToBook",np.nan),"EV/EBITDA":i.get("enterpriseToEbitda",np.nan),"Dividend Yield":i.get("dividendYield",np.nan),"Market Cap (₹ Cr)":i.get("marketCap",np.nan)/1e7})
    val_df=pd.DataFrame(val).set_index("Company")
    st.dataframe(val_df.style.format({"P/E":"{:.2f}","Forward P/E":"{:.2f}","P/B":"{:.2f}","EV/EBITDA":"{:.2f}","Dividend Yield":"{:.2%}","Market Cap (₹ Cr)":"{:,.0f}"}),use_container_width=True)
    score=pd.DataFrame(index=selected)
    score["Return score"]=pm["5Y CAGR"].rank(pct=True)
    score["Risk score"]=(-pm["Volatility"]).rank(pct=True)
    score["ROE score"]=peer_df["ROE"].rank(pct=True)
    score["Leverage score"]=(-peer_df["Debt/Equity"]).rank(pct=True)
    score["Valuation score"]=(-val_df["P/E"]).rank(pct=True)
    score["Composite / 100"]=score.mean(axis=1,skipna=True)*100
    score=score.sort_values("Composite / 100",ascending=False)
    st.plotly_chart(px.bar(score.reset_index(names="Company"),x="Company",y="Composite / 100",color="Company",color_discrete_map=COLORS,title="Educational Peer Scorecard"),use_container_width=True)
    st.dataframe(score.style.format("{:.1f}"),use_container_width=True)
    st.info("The scorecard uses equal weights and cross-sectional percentile ranks. It is a learning tool—not a buy/sell recommendation.")

with tabs[6]:
    f=financials[primary]
    statement=st.radio("View",["Income & cash flow","Balance sheet","Calculated ratios"],horizontal=True)
    mapping={"Income & cash flow":["Revenue","EBITDA","EBIT","Net Income","Interest Expense","Operating Cash Flow","Capital Expenditure","Free Cash Flow"],"Balance sheet":["Total Assets","Equity","Debt","Current Assets","Current Liabilities","Cash","Inventory","Receivables","Payables"],"Calculated ratios":["Net Margin","EBITDA Margin","ROA","ROE","Current Ratio","Quick Ratio","Debt / Equity","Interest Coverage","Asset Turnover","Receivable Days","Inventory Days","Payable Days","Cash Conversion Cycle"]}
    st.dataframe(f[mapping[statement]].T,use_container_width=True)
    buffer=io.BytesIO()
    with pd.ExcelWriter(buffer,engine="xlsxwriter") as writer:
        prices.to_excel(writer,sheet_name="5Y Prices")
        pm.to_excel(writer,sheet_name="Market Metrics")
        peer_df.to_excel(writer,sheet_name="Peer Snapshot")
        val_df.to_excel(writer,sheet_name="Valuation")
        for n in selected: financials[n].to_excel(writer,sheet_name=n[:31])
    st.download_button("⬇ Download complete analysis (Excel)",buffer.getvalue(),"India_Power_Stocks_Analysis.xlsx","application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",use_container_width=True)
    st.download_button("⬇ Download adjusted prices (CSV)",prices.to_csv().encode(),"India_Power_Stocks_5Y_Prices.csv","text/csv",use_container_width=True)
    st.caption(f"Data window: {prices.index.min():%d %b %Y} to {prices.index.max():%d %b %Y}. Financials are annual and depend on source availability. Refresh after results announcements.")

st.markdown("""<div class='about-section'>
<h3>About This Project</h3>
<p>Developed by <span class='highlight'>Prof. V. Ravichandran</span>, Visiting Professor &amp;
Professor of Practice at Leading Business Schools and founder of
<span class='highlight'>The Mountain Path Academy</span>.</p>
<p>Drawing on <span class='highlight'>28+ years of industry experience</span> and
<span class='highlight'>12+ years of teaching</span>, this dashboard combines financial-statement analysis,
equity analytics and risk measurement in a practical, classroom-ready application.</p>
<a class='academy-link' href='https://themountainpathacademy.com' target='_blank'>🏔️ Visit The Mountain Path Academy</a>
</div>
<div class='mp-footer'>
  <div class='footer-brand'>🏔️ The Mountain Path Academy</div>
  <div class='footer-profile'>Prof. V. Ravichandran · Visiting Professor &amp; Professor of Practice at Leading Business Schools</div>
  <div><a href='https://themountainpathacademy.com' target='_blank'>themountainpathacademy.com</a></div>
  <div style='margin-top:8px'><a href='https://www.linkedin.com/in/trichyravis' target='_blank'>LinkedIn</a><a href='https://github.com/trichyravis' target='_blank'>GitHub</a></div>
  <div style='margin-top:10px;font-size:.77rem'>Educational analytics project · Not investment advice · © 2026 The Mountain Path Academy</div>
</div>""",unsafe_allow_html=True)
