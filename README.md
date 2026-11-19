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
Operating margin (%)	Operating income (EBIT) / Revenue x 100
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

Ratios were cross-checked against company annual reports. Differences are explained by definitions (for example, minority interest, lease liabilities in debt, and year-end versus average equity).

Company	Year	Ratio	App value	Annual report value	Difference and reason
to fill					
to fill					
to fill					
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
