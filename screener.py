import sqlite3
import pandas as pd

DB_PATH = "nifty100_intelligence.db"

def run_financial_screener(min_roe=15.0, max_debt_equity=0.5, min_npm=8.0):
    print(f"\nRunning Investment Screener Filter Criteria...")
    print(f"   [Filters] Min ROE: {min_roe}% | Max Debt/Equity: {max_debt_equity} | Min Net Margin: {min_npm}%")
    
    conn = sqlite3.connect(DB_PATH)
    
    # Query only the most recent financial year data for screening
    query = """
    SELECT r.company_id, r.year_clean, r.roe_percentage, r.debt_to_equity, r.npm_percentage, c.company_name
    FROM fact_financial_ratios r
    JOIN dim_companies c ON r.company_id = c.id
    WHERE r.year_clean = (SELECT MAX(year_clean) FROM fact_financial_ratios WHERE company_id = r.company_id)
      AND r.roe_percentage >= ?
      AND r.debt_to_equity <= ?
      AND r.npm_percentage >= ?
    ORDER BY r.roe_percentage DESC;
    """
    
    df_results = pd.read_sql_query(query, conn, params=(min_roe, max_debt_equity, min_npm))
    conn.close()
    
    print(f"\nScreening complete! Found {len(df_results)} high-performing companies matching criteria:")
    if not df_results.empty:
        print(df_results[['company_id', 'company_name', 'roe_percentage', 'debt_to_equity', 'npm_percentage']].to_string(index=False))
    else:
        print("No companies matched the strict criteria combination.")
        
    return df_results

if __name__ == "__main__":
    # Test a strict institutional quality screen right out of the gate
    run_financial_screener(min_roe=18.0, max_debt_equity=0.3, min_npm=10.0)