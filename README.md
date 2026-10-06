# 🚀 Nifty 100 Financial Intelligence Platform (v1.0)

A production-grade, self-contained fundamental analysis data architecture that ingests raw corporate financials, computes over 50 institutional key performance indicators, establishes cross-sector relative percentile benchmarks, and visualizes market insights through a unified analytical terminal.

---

## Platform Architecture

```text
D:\B100 Intelligence Fundamental Analysis Project\
│
├── nifty100_intelligence.db        # Core SQLite Analytical Data Warehouse
│
├── app.py                         # Streamlit Interactive Analytics Terminal
├── peer_comparison.py              # Sprint 4 Percentile Engine
├── cashflow_analytics.py           # Sprint 4 Liquidity Engine
├── report_generator.py             # Sprint 5 Multi-Tab Excel Export Utility
├── pdf_generator.py                # Sprint 5 Executive PDF Dossier Compiler
└── test_suite.py                  # Sprint 6 Pytest Unit Testing Matrix


⚡ Quickstart Deployment Guide
1. Environment Initialization
Clone or open the workspace folder and install the mandatory platform dependencies via your terminal console:

pip install pandas openpyxl streamlit reportlab pytest

2. Analytical Processing Pipeline Run Order
Execute the analytics scripts sequentially to compute downstream matrices and seed your database warehouse layers:

# Calculate universe relative ranks and percentile distribution brackets
python peer_comparison.py

# Extract cash flow statements, compute FCF metrics, and map conversion ratios
python cashflow_analytics.py

3. Reporting & Export Utilities
Generate executive reporting sheets directly out of your structured relational tables:

# Build multi-tab institutional Excel workbooks
python report_generator.py

# Compile individual presentation-ready PDF corporate dossier sheets (default: BEL)
python pdf_generator.py

4. Booting the Analytics UI Terminal
Launch your interactive web platform locally:

streamlit run app.py

Open http://localhost:8501/ in your web browser to browse your custom financial health leaderboard and institutional investment screener tabs.

5. Running the Automated Testing Matrix
Execute the verification test suite to ensure engine mathematical stability:

pytest test_suite.py -v

🛡️ Core Verification Safeguards
Zero-Leverage Protections: Debt metrics auto-filter structural anomalies gracefully.

Capital Protection Triggers: Financial ratios prevent division-by-zero layout breaks by applying zero fallback conditions for negative equity or zero-base CAGR intervals.

## 🏆 Project Completion & Sign-off

With data tables populated, Streamlit app running cleanly, Excel and PDF report sheets exporting correctly, and test coverage baseline verified, we have officially met every single mandatory exit gate in your project roadmap.

