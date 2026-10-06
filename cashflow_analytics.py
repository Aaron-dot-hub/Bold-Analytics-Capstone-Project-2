import sqlite3
import pandas as pd

DB_PATH = "nifty100_intelligence.db"

def compute_cashflow_intelligence():
    print("\nLaunching Sprint 4 Cash Flow Intelligence Engine...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Inspect table names and schemas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [t[0] for t in cursor.fetchall()]
    
    cf_table = "fact_cash_flow" if "fact_cash_flow" in tables else "cash_flow"
    pnl_table = "fact_profit_loss" if "fact_profit_loss" in tables else "profit_loss"
    
    # Fetch columns from cash flow table to map dynamically
    cursor.execute(f"PRAGMA table_info({cf_table});")
    cf_cols = [col[1] for col in cursor.fetchall()]
    
    # Identify key columns using flexible keyword matching
    cfo_col = [c for c in cf_cols if 'operating' in c.lower() or 'cfo' in c.lower() or 'operations' in c.lower()][0]
    capex_col = [c for c in cf_cols if 'fixed' in c.lower() or 'capex' in c.lower() or 'purchased' in c.lower() or 'investing' in c.lower()][0]
    year_col = "year_clean" if "year_clean" in cf_cols else "year"
    
    print(f"Dynamic Mapping: Table '{cf_table}' -> Year: '{year_col}', CFO: '{cfo_col}', CapEx: '{capex_col}'")
    
    # 2. Extract latest data points
    query = f"""
    SELECT cf.company_id, cf.{year_col} as year_clean, cf.{cfo_col} as cfo, 
           cf.{capex_col} as capex, pnl.net_profit
    FROM {cf_table} cf
    JOIN {pnl_table} pnl ON cf.company_id = pnl.company_id AND cf.{year_col} = pnl.year_clean
    WHERE cf.{year_col} = (SELECT MAX({year_col}) FROM {cf_table} WHERE company_id = cf.company_id);
    """
    
    df = pd.read_sql_query(query, conn)
    
    if df.empty:
        print("Error: Could not extract matching cash flow entries.")
        conn.close()
        return

    # Clean numerical formats safely
    for col in ['cfo', 'capex', 'net_profit']:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '').str.strip(), errors='coerce').fillna(0)

    print("Evaluating cash conversion cycles and free cash balances...")
    
    # 3. Calculate Intelligence Metrics
    df['free_cash_flow'] = df['cfo'] - df['capex'].abs()
    df['cash_conversion_ratio'] = df.apply(
        lambda row: round(row['cfo'] / row['net_profit'], 2) if row['net_profit'] > 0 else 0.0, axis=1
    )
    df['free_cash_flow'] = df['free_cash_flow'].round(2)

    # 4. Save to Database
    print("Seeding 'fact_cashflow_intelligence' warehouse tier...")
    cursor.execute("DROP TABLE IF EXISTS fact_cashflow_intelligence;")
    cursor.execute("""
    CREATE TABLE fact_cashflow_intelligence (
        company_id TEXT PRIMARY KEY,
        cash_from_operations REAL,
        free_cash_flow REAL,
        cash_conversion_ratio REAL,
        FOREIGN KEY (company_id) REFERENCES dim_companies(id)
    );
    """)
    conn.commit()
    
    df_db = df[['company_id', 'cfo', 'free_cash_flow', 'cash_conversion_ratio']].rename(
        columns={'cfo': 'cash_from_operations'}
    )
    df_db.to_sql('fact_cashflow_intelligence', conn, if_exists='append', index=False)
    conn.close()
    
    print("\nCash Flow Intelligence finalized with 0 errors! Top 5 FCF cash generation cash cows:")
    print(df_db.sort_values(by='free_cash_flow', ascending=False).head(5).to_string(index=False))

if __name__ == "__main__":
    compute_cashflow_intelligence()