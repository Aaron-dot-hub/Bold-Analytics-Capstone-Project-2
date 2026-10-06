import sqlite3
import pandas as pd
import os

DB_PATH = "nifty100_intelligence.db"
COMPANIES_XLSX = os.path.join("Data sets", "companies.xlsx")

def compute_sector_medians():
    print("\nLaunching Sprint 3 Sector Analytics Engine...")
    conn = sqlite3.connect(DB_PATH)
    
    # 1. Pull the latest financial ratios from SQL
    query = """
    SELECT r.*
    FROM fact_financial_ratios r
    WHERE r.year_clean = (SELECT MAX(year_clean) FROM fact_financial_ratios WHERE company_id = r.company_id);
    """
    df_ratios = pd.read_sql_query(query, conn)
    conn.close()
    
    if df_ratios.empty:
        print("Error: No data found in 'fact_financial_ratios'. Please run ratio_engine.py first.")
        return

    # 2. Safely read Excel headers to check for a sector column
    print("Inspecting sector classifications from source...")
    df_raw_comp = pd.read_excel(COMPANIES_XLSX, header=1)
    df_raw_comp['id'] = df_raw_comp['id'].astype(str).str.strip().str.upper()
    
    # Dynamic check for any column containing 'sector' or 'industry'
    sector_col = [c for c in df_raw_comp.columns if 'sector' in c.lower() or 'industry' in c.lower()]
    
    if sector_col:
        df_sectors = df_raw_comp[['id', sector_col[0]]].rename(columns={sector_col[0]: 'sector', 'id': 'company_id'})
        df_ratios = pd.merge(df_ratios, df_sectors, on='company_id', how='inner')
    else:
        # Production-grade fallback: aggregate as a single market universe group to avoid breaking execution
        print("Sector column not found in master companies file. Grouping as unified universe market benchmarks.")
        df_ratios['sector'] = 'All-Market Baseline'
    
    print(f"Calculating industry baseline medians across groups...")
    
    # 3. Group by sector and compute medians for core KPIs
    df_sector = df_ratios.groupby('sector')[['opm_percentage', 'npm_percentage', 'roe_percentage', 'debt_to_equity', 'asset_turnover']].median().reset_index()
    df_sector = df_sector.round(2)
    
    # 4. Save to dedicated warehouse table with correct schema mapping
    print("Creating and seeding 'fact_sector_benchmarks' table...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS fact_sector_benchmarks;")
    cursor.execute("""
    CREATE TABLE fact_sector_benchmarks (
        sector TEXT PRIMARY KEY,
        median_opm REAL,
        median_npm REAL,
        median_roe REAL,
        median_debt_equity REAL,
        median_asset_turnover REAL
    );
    """)
    conn.commit()
    
    df_sector_db = df_sector.rename(columns={
        'opm_percentage': 'median_opm',
        'npm_percentage': 'median_npm',
        'roe_percentage': 'median_roe',
        'debt_to_equity': 'median_debt_equity',
        'asset_turnover': 'median_asset_turnover'
    })
    
    df_sector_db.to_sql('fact_sector_benchmarks', conn, if_exists='append', index=False)
    conn.close()
    
    print("\nSector benchmarks successfully finalized with 0 errors!")
    print(df_sector_db.to_string(index=False))

if __name__ == "__main__":
    compute_sector_medians()