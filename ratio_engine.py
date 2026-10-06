import sqlite3
import pandas as pd

# Suppress the future downcasting warning to keep the console clean
pd.set_option('future.no_silent_downcasting', True)

DB_PATH = "nifty100_intelligence.db"

def compute_financial_ratios():
    print("\nLaunching Sprint 2 Advanced Financial Ratio Engine...")
    conn = sqlite3.connect(DB_PATH)
    
    # 1. Fetch complete tables from the warehouse
    df_pl = pd.read_sql_query("SELECT * FROM fact_profit_loss", conn)
    df_bs = pd.read_sql_query("SELECT * FROM fact_balance_sheet", conn)
    df_cf = pd.read_sql_query("SELECT * FROM fact_cash_flow", conn)
    
    # 2. Merge P&L, Balance Sheet, and Cash Flow on Composite Key
    df_merged = pd.merge(df_pl, df_bs, on=['company_id', 'year_clean'], how='inner')
    df_merged = pd.merge(df_merged, df_cf, on=['company_id', 'year_clean'], how='inner')
    
    print(f"Computing advanced cross-statement KPIs across {len(df_merged)} rows...")
    
    # --- Vectorized Financial KPI Calculations ---
    # Margins
    df_merged['opm_percentage'] = (df_merged['operating_profit'] / df_merged['sales'].replace(0, pd.NA)) * 100
    df_merged['npm_percentage'] = (df_merged['net_profit'] / df_merged['sales'].replace(0, pd.NA)) * 100
    
    # Return Profiles
    df_merged['total_equity'] = df_merged['equity_capital'] + df_merged['reserves']
    df_merged['roe_percentage'] = (df_merged['net_profit'] / df_merged['total_equity'].replace(0, pd.NA)) * 100
    
    # Leverage Metrics
    df_merged['debt_to_equity'] = df_merged['borrowings'] / df_merged['total_equity'].replace(0, pd.NA)
    df_merged['debt_to_assets'] = df_merged['borrowings'] / df_merged['total_liabilities'].replace(0, pd.NA)
    df_merged['leverage_multiplier'] = df_merged['total_liabilities'] / df_merged['total_equity'].replace(0, pd.NA)
    
    # Efficiency & Liquidity Metrics
    df_merged['asset_turnover'] = df_merged['sales'] / df_merged['total_liabilities'].replace(0, pd.NA)
    df_merged['cash_conversion_efficiency'] = (df_merged['operating_activity'] / df_merged['sales'].replace(0, pd.NA)) * 100

    # Clean up Infinities/NaNs safely
    df_merged = df_merged.fillna(0)
    
    # 4. Save to Dedicated Analytical Fact Table
    print("Overwriting 'fact_financial_ratios' with cross-statement schema...")
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS fact_financial_ratios;")
    cursor.execute("""
    CREATE TABLE fact_financial_ratios (
        company_id TEXT,
        year_clean TEXT,
        opm_percentage REAL,
        npm_percentage REAL,
        roe_percentage REAL,
        debt_to_equity REAL,
        debt_to_assets REAL,
        leverage_multiplier REAL,
        asset_turnover REAL,
        cash_conversion_efficiency REAL,
        PRIMARY KEY (company_id, year_clean),
        FOREIGN KEY (company_id) REFERENCES dim_companies(id)
    );
    """)
    conn.commit()
    
    # Export results
    df_ratios = df_merged[[
        'company_id', 'year_clean', 'opm_percentage', 'npm_percentage', 
        'roe_percentage', 'debt_to_equity', 'debt_to_assets', 'leverage_multiplier', 
        'asset_turnover', 'cash_conversion_efficiency'
    ]]
    df_ratios.to_sql('fact_financial_ratios', conn, if_exists='append', index=False)
    
    print("\nMulti-Statement Engine Execution Successful! Verification:")
    print(df_ratios[['company_id', 'year_clean', 'npm_percentage', 'cash_conversion_efficiency']].head(4))
    
    conn.close()

if __name__ == "__main__":
    compute_financial_ratios()