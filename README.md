FinSight AI

Understand businesses beyond numbers.

FinSight AI is a web app for analysing listed Indian companies. Enter an NSE ticker and it pulls annual financial statements, calculates key ratios, compares companies, and generates a plain-English AI summary based only on the computed numbers.

Live app: https://finsightai-bhavy.streamlit.app/

Built by Bhavy Arora

Features
Financial Analysis: latest-year KPI cards, a revenue and net income chart, and a year-by-year ratio table for any NSE (.NS) or BSE (.BO) ticker.
Company Comparison: side-by-side ratios for up to 3 companies, with a chart for any selected ratio.
AI Analyst: a Gemini-powered summary of strengths, risks, trends and what to check next. The AI only receives the ratio table the app computes. It does not browse the web and does not use live prices or news.
Raw line items: an expandable table of the exact statement figures (in ₹ crore) that every ratio is built from, so each number can be checked against the annual report.
Home and About pages: company search, featured companies, ratio definitions, data limitations and a disclaimer.
Ratios and formulas
Ratio	Formula
Revenue growth (%)	(Revenue this year / Revenue last year - 1) x 100
Net margin (%)	Net income / Revenue x 100
Operating margin (%)	EBIT (includes other income) / Revenue x 100
ROE (%)	Net income / Year-end equity x 100
Debt / Equity (x)	Total debt / Year-end equity
Current ratio (x)	Current assets / Current liabilities
Interest coverage (x)	EBIT / Interest expense
Data and limitations
Financial data comes from Yahoo Finance through the unofficial yfinance library. It can have gaps or errors, so verify against company filings.
Equity, debt and operating profit follow the data source's definitions, which may differ from a company's own reported figures.
ROE uses year-end equity, not average equity.
Banks and financial companies have different balance-sheet structures, so debt/equity and current ratio are not meaningful for them.
The AI can make mistakes. Treat its output as a starting point for your own research.
Validation

Reliance Industries' FY25 and FY26 figures were checked against its Integrated Annual Report 2025-26 (consolidated statements). All seven ratios matched when recomputed by hand. FY26 shown below (₹ crore):

Ratio	App	Recomputed from the annual report
Revenue growth	9.59%	10,57,219 / 9,64,693 - 1
Net margin	7.64%	80,775 / 10,57,219
Operating margin	13.93%	1,47,218 / 10,57,219
ROE	8.93%	80,775 / 9,04,030
Debt / Equity	0.44	3,97,999 / 9,04,030
Current ratio	1.10	5,94,249 / 5,41,254
Interest coverage	6.12x	1,47,218 / 24,056

Definitions behind these numbers:

Revenue is revenue from operations less excise duty. It is not the headline "Value of Sales & Services" (₹11,75,919 crore), which includes GST.
Net income and equity are attributable to owners of the company and exclude non-controlling interest.
EBIT is profit before tax plus interest expense (interest and lease interest). It includes other income, so the app's operating margin is higher than a margin that excludes it (about 11.2% for FY26).
Total debt is borrowings plus lease liabilities. It excludes deferred payment liabilities of ₹99,552 crore owed to the Department of Telecommunications for spectrum. Including them, FY26 debt/equity would be about 0.55.

Only Reliance (FY25 and FY26) has been checked this way. Other companies and years have not been independently verified, and the app's "Raw line items" section lets you check the inputs yourself.

Tech stack

Python, Streamlit, pandas, Plotly, yfinance, Google Gemini API (google-genai).

Run locally
bash
git clone https://github.com/bhavyaroramba26-coder/Finsight-AI.git
cd Finsight-AI
pip install -r requirements.txt

Create .streamlit/secrets.toml with your own Gemini API key (never commit this file):

toml
GEMINI_API_KEY = "your-key-here"

Then run:

bash
streamlit run app.py

The app works without a key. Only the AI Analyst tab needs it.

Disclaimer

FinSight AI is for education and research practice only. It does not provide investment, tax or legal advice, and nothing in it is a recommendation to buy or sell any security.
