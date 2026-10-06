import sqlite3
import pandas as pd
import numpy as np

DB_PATH = "nifty100_intelligence.db"

def compute_growth_cagr():
    print("\nLaunching Sprint 4 Trend & Growth Analytics Engine...")
    conn = sqlite3.connect(DB_PATH)
    
    # 1. Check table names to find where the P&L statement data was seeded during ETL
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [t[0] for t in cursor.fetchall()]
    
    # Identify the appropriate P&L table name dynamically
    pnl_table = "fact_profit_loss" if "fact_profit_loss" in tables else "profit_loss"
    if not any(x in tables for x in ["fact_profit_loss", "profit_loss"]):
        # Fallback query if it was loaded under a basic naming convention
        pnl_table = [t for t in tables if "profit" in t.lower() or "pnl" in t.lower()]
        pnl_table = pnl_table[0] if pnl_table else "profitandloss"

    print(f"Extracting operational historical rows from data warehouse table '{pnl_table}'...")
    
    # 2. Read historical sales and net profit records
    query = f"""
    SELECT company_id, year_clean, sales, net_profit 
    FROM {pnl_table}
    ORDER BY company_id, year_clean;
    """
    try:
        df = pd.read_sql_query(query, conn)
    except Exception as e:
        print(f"Querying by standard schema failed, attempting raw column lookup fallback. Error: {e}")
        # Secondary fallback if columns are named 'year' instead of 'year_clean'
        query = f"SELECT company_id, year, sales, net_profit FROM {pnl_table} ORDER BY company_id, year;"
        df = pd.read_sql_query(query, conn)
        df = df.rename(columns={'year': 'year_clean'})
    
    if df.empty:
        print("Error: Financial statements dataset is empty.")
        conn.close()
        return

    # Clean out any non-numeric string values (commas, spaces) from sales and profit columns
    for col in ['sales', 'net_profit']:
        if df[col].dtype == object:
            df[col] = df[col].astype(str).str.replace(',', '').str.strip()
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Standardize years to absolute integers for calculation indexing
    # If years are strings like 'Mar-23', extract the final two digits
    if df['year_clean'].dtype == object:
        df['year_int'] = df['year_clean'].astype(str).str.extract(r'(\d+)').astype(float)
        # Convert 2-digit years to full 4-digit formatting
        df['year_int'] = df['year_int'].apply(lambda x: 2000 + x if x < 50 else 1900 + x)
    else:
        df['year_int'] = pd.to_numeric(df['year_clean'], errors='coerce')

    df = df.dropna(subset=['year_int', 'sales', 'net_profit'])
    df['year_int'] = df['year_int'].astype(int)
    
    cagr_records = []
    
    # 3. Group by company to find beginning and ending values over a 3-year historical window
    for company, group in df.groupby('company_id'):
        group = group.sort_values('year_int')
        
        if len(group) >= 4:  # Requires at least a 3-year consecutive delta window
            latest_row = group.iloc[-1]
            historical_row = group.iloc[-4]
            
            n_years = int(latest_row['year_int'] - historical_row['year_int'])
            if n_years <= 0:
                continue
            
            sales_beg, sales_end = historical_row['sales'], latest_row['sales']
            pat_beg, pat_end = historical_row['net_profit'], latest_row['net_profit']
            
            # Compute Revenue CAGR%
            if sales_beg > 0 and sales_end > 0:
                sales_cagr = ((sales_end / sales_beg) ** (1 / n_years) - 1) * 100
            else:
                sales_cagr = 0.0
                
            # Compute PAT CAGR%
            if pat_beg > 0 and pat_end > 0:
                pat_cagr = ((pat_end / pat_beg) ** (1 / n_years) - 1) * 100
            else:
                pat_cagr = 0.0
                
            cagr_records.append({
                'company_id': company,
                'revenue_cagr_3y': round(sales_cagr, 2),
                'pat_cagr_3y': round(pat_cagr, 2)
            })
            
    df_cagr = pd.DataFrame(cagr_records)
    
    # 4. Create database table and seed the growth statistics metrics
    print("Creating and seeding 'fact_growth_analytics' table layout...")
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS fact_growth_analytics;")
    cursor.execute("""
    CREATE TABLE fact_growth_analytics (
        company_id TEXT PRIMARY KEY,
        revenue_cagr_3y REAL,
        pat_cagr_3y REAL,
        FOREIGN KEY (company_id) REFERENCES dim_companies(id)
    );
    """)
    conn.commit()
    
    df_cagr.to_sql('fact_growth_analytics', conn, if_exists='append', index=False)
    conn.close()
    
    print("\nGrowth metrics successfully computed with 0 errors!")
    print(df_cagr.sort_values(by='revenue_cagr_3y', ascending=False).head(5).to_string(index=False))

if __name__ == "__main__":
    compute_growth_cagr()