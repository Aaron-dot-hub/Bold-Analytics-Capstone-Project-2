import streamlit as st
import sqlite3
import pandas as pd
import os

DB_PATH = "nifty100_intelligence.db"

st.set_page_config(page_title="Nifty 100 Financial Intelligence Platform", layout="wide")

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("🚀 B100 Intelligence")
st.sidebar.markdown("---")
page = st.sidebar.radio("Go to Page:", ["🏆 Health Leaderboard", "🎯 Investment Screener"])

if not os.path.exists(DB_PATH):
    st.error(f"❌ Database file not found at `{DB_PATH}`. Please run your engine scripts first!")
else:
    # --- PAGE 1: HEALTH LEADERBOARD ---
    if page == "🏆 Health Leaderboard":
        st.title("🏆 Nifty 100 Financial Health Leaderboard")
        st.markdown("Real-time corporate evaluation scores computed via our **Sprint 3 & 4 Engines**.")
        
        try:
            conn = sqlite3.connect(DB_PATH)
            
            # Pull scores and join with ratios, growth, peer rankings, AND cash flows
            query_scores = """
            SELECT h.company_id, c.company_name, h.composite_health_score, 
                   r.roe_percentage, r.npm_percentage,
                   g.revenue_cagr_3y,
                   p.roe_percentile,
                   cf.free_cash_flow, cf.cash_conversion_ratio
            FROM fact_financial_health_scores h
            JOIN dim_companies c ON h.company_id = c.id
            JOIN fact_financial_ratios r ON h.company_id = r.company_id AND h.year_clean = r.year_clean
            LEFT JOIN fact_growth_analytics g ON h.company_id = g.company_id
            LEFT JOIN fact_peer_rankings p ON h.company_id = p.company_id
            LEFT JOIN fact_cashflow_intelligence cf ON h.company_id = cf.company_id
            ORDER BY h.composite_health_score DESC;
            """
            df = pd.read_sql_query(query_scores, conn)
            df_baseline = pd.read_sql_query("SELECT * FROM fact_sector_benchmarks", conn)
            conn.close()
            
            col1, col2, col3 = st.columns(3)
            if not df.empty:
                col1.metric("Top Rated Company", f"{df.iloc[0]['company_id']} ({df.iloc[0]['composite_health_score']})")
            col2.metric("Universe Size", f"{len(df)} Companies")
            if not df_baseline.empty:
                col3.metric("Market Median ROE", f"{df_baseline.iloc[0]['median_roe']}%")
            
            st.markdown("### 📊 Full Universe Rankings (Comprehensive Analytical Suite)")
            st.dataframe(df, use_container_width=True, hide_index=True)
                
        except Exception as e:
            st.error(f"💥 Live Analytics Database Error: {e}")

    # --- PAGE 2: INVESTMENT SCREENER ---
    elif page == "🎯 Investment Screener":
        st.title("🎯 Institutional Investment Screener")
        st.markdown("Filter the universe instantly using advanced capital allocation, structural growth, and liquidity metrics.")
        
        # Sidebar Filter Controls
        st.sidebar.subheader("Core Ratios Filters")
        min_roe = st.sidebar.slider("Minimum ROE (%)", 0.0, 50.0, 15.0)
        min_npm = st.sidebar.slider("Minimum Net Margin (%)", 0.0, 40.0, 10.0)
        max_debt = st.sidebar.slider("Maximum Debt/Equity", 0.0, 3.0, 0.5)
        
        st.sidebar.subheader("Growth Filters")
        min_growth = st.sidebar.slider("Minimum 3Y Revenue CAGR (%)", -10.0, 50.0, 10.0)

        st.sidebar.subheader("Relative Peer Ranks")
        min_roe_pct = st.sidebar.slider("Minimum ROE Percentile Rank", 0, 100, 50)

        st.sidebar.subheader("Cash Liquidity Filters")
        min_fcf = st.sidebar.number_input("Minimum Free Cash Flow (Cr)", value=0.0)
        
        try:
            conn = sqlite3.connect(DB_PATH)
            query_screen = """
            SELECT r.company_id, c.company_name, r.roe_percentage, r.debt_to_equity, r.npm_percentage,
                   g.revenue_cagr_3y, p.roe_percentile, cf.free_cash_flow, cf.cash_conversion_ratio
            FROM fact_financial_ratios r
            JOIN dim_companies c ON r.company_id = c.id
            LEFT JOIN fact_growth_analytics g ON r.company_id = g.company_id
            LEFT JOIN fact_peer_rankings p ON r.company_id = p.company_id
            LEFT JOIN fact_cashflow_intelligence cf ON r.company_id = cf.company_id
            WHERE r.year_clean = (SELECT MAX(year_clean) FROM fact_financial_ratios WHERE company_id = r.company_id)
              AND r.roe_percentage >= ?
              AND r.npm_percentage >= ?
              AND r.debt_to_equity <= ?
              AND COALESCE(g.revenue_cagr_3y, 0) >= ?
              AND COALESCE(p.roe_percentile, 0) >= ?
              AND COALESCE(cf.free_cash_flow, 0) >= ?
            ORDER BY cf.free_cash_flow DESC;
            """
            df_screen = pd.read_sql_query(query_screen, conn, params=(min_roe, min_npm, max_debt, min_growth, min_roe_pct, min_fcf))
            conn.close()
            
            st.subheader(f"Found {len(df_screen)} High-Liquidity Alpha Compounders")
            st.dataframe(df_screen, use_container_width=True, hide_index=True)
            
        except Exception as e:
            st.error(f"Screener Engine Query Error: {e}")