import sqlite3
import pandas as pd
import os

DB_PATH = "nifty100_intelligence.db"
OUTPUT_XLSX = "Nifty100_Intelligence_Executive_Report.xlsx"

def generate_excel_report():
    print("\nLaunching Sprint 5 Reporting & Export Engine...")
    if not os.path.exists(DB_PATH):
        print(f"Error: Database file not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    
    # 1. Gather Sheet 1: Master Health Leaderboard Dataset
    print("Extracting Health Leaderboard records...")
    query_leaderboard = """
    SELECT h.company_id, c.company_name, h.composite_health_score, 
           r.roe_percentage, r.npm_percentage, g.revenue_cagr_3y,
           p.roe_percentile, cf.free_cash_flow, cf.cash_conversion_ratio
    FROM fact_financial_health_scores h
    JOIN dim_companies c ON h.company_id = c.id
    JOIN fact_financial_ratios r ON h.company_id = r.company_id AND h.year_clean = r.year_clean
    LEFT JOIN fact_growth_analytics g ON h.company_id = g.company_id
    LEFT JOIN fact_peer_rankings p ON h.company_id = p.company_id
    LEFT JOIN fact_cashflow_intelligence cf ON h.company_id = cf.company_id
    ORDER BY h.composite_health_score DESC;
    """
    df_leaderboard = pd.read_sql_query(query_leaderboard, conn)
    
    # 2. Gather Sheet 2: Growth & Peer Alpha Compounders (Institutional Screen)
    print("Extracting High-Alpha Screener records...")
    query_screener = """
    SELECT r.company_id, c.company_name, r.roe_percentage, r.debt_to_equity, r.npm_percentage,
           g.revenue_cagr_3y, p.roe_percentile, cf.free_cash_flow
    FROM fact_financial_ratios r
    JOIN dim_companies c ON r.company_id = c.id
    LEFT JOIN fact_growth_analytics g ON r.company_id = g.company_id
    LEFT JOIN fact_peer_rankings p ON r.company_id = p.company_id
    LEFT JOIN fact_cashflow_intelligence cf ON r.company_id = cf.company_id
    WHERE r.year_clean = (SELECT MAX(year_clean) FROM fact_financial_ratios WHERE company_id = r.company_id)
      AND r.roe_percentage >= 15.0
      AND r.npm_percentage >= 10.0
      AND r.debt_to_equity <= 0.5
      AND COALESCE(g.revenue_cagr_3y, 0) >= 10.0
    ORDER BY g.revenue_cagr_3y DESC;
    """
    df_screener = pd.read_sql_query(query_screener, conn)

    # 3. Write securely to a multi-tab Excel workbook using ExcelWriter
    print(f"Constructing multi-tab workbook sheet structural layers -> {OUTPUT_XLSX}")
    with pd.ExcelWriter(OUTPUT_XLSX, engine='openpyxl') as writer:
        df_leaderboard.to_excel(writer, sheet_name="Health Leaderboard", index=False)
        df_screener.to_excel(writer, sheet_name="Alpha Screener Tier", index=False)
        
    conn.close()
    print(f"\nExecutive compilation successful! File finalized and saved as: `{OUTPUT_XLSX}`")

if __name__ == "__main__":
    generate_excel_report()