import sqlite3
import os

DB_PATH = "nifty100_intelligence.db"

def save_to_warehouse(df_comp, df_pl, df_bs, df_cf):
    print("\nInitializing Local SQL Data Warehouse...")
    
    # Connect to SQLite (Creates the file if it doesn't exist)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Enable Foreign Key Constraints
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # 2. Drop existing tables if re-running pipeline
    cursor.execute("DROP TABLE IF EXISTS fact_cash_flow;")
    cursor.execute("DROP TABLE IF EXISTS fact_balance_sheet;")
    cursor.execute("DROP TABLE IF EXISTS fact_profit_loss;")
    cursor.execute("DROP TABLE IF EXISTS dim_companies;")
    
    # 3. Create Star Schema Table Layouts
    print("Building relational database schemas...")
    
    cursor.execute("""
    CREATE TABLE dim_companies (
        id TEXT PRIMARY KEY,
        company_name TEXT NOT NULL,
        about_company TEXT,
        website TEXT,
        face_value REAL
    );
    """)
    
    cursor.execute("""
    CREATE TABLE fact_profit_loss (
        company_id TEXT,
        year_clean TEXT,
        sales REAL,
        expenses REAL,
        operating_profit REAL,
        net_profit REAL,
        eps REAL,
        PRIMARY KEY (company_id, year_clean),
        FOREIGN KEY (company_id) REFERENCES dim_companies(id)
    );
    """)
    
    cursor.execute("""
    CREATE TABLE fact_balance_sheet (
        company_id TEXT,
        year_clean TEXT,
        equity_capital REAL,
        reserves REAL,
        borrowings REAL,
        total_liabilities REAL,
        PRIMARY KEY (company_id, year_clean),
        FOREIGN KEY (company_id) REFERENCES dim_companies(id)
    );
    """)
    
    cursor.execute("""
    CREATE TABLE fact_cash_flow (
        company_id TEXT,
        year_clean TEXT,
        operating_activity REAL,
        investing_activity REAL,
        financing_activity REAL,
        net_cash_flow REAL,
        PRIMARY KEY (company_id, year_clean),
        FOREIGN KEY (company_id) REFERENCES dim_companies(id)
    );
    """)
    
    conn.commit()
    
    # 4. Export Pandas Dataframes into SQL Tables
    print("Seeding Fact and Dimension records into SQL storage...")
    
    # We only slice columns that match our database definitions
    df_comp[['id', 'company_name', 'about_company', 'website', 'face_value']].to_sql('dim_companies', conn, if_exists='append', index=False)
    df_pl[['company_id', 'year_clean', 'sales', 'expenses', 'operating_profit', 'net_profit', 'eps']].to_sql('fact_profit_loss', conn, if_exists='append', index=False)
    df_bs[['company_id', 'year_clean', 'equity_capital', 'reserves', 'borrowings', 'total_liabilities']].to_sql('fact_balance_sheet', conn, if_exists='append', index=False)
    df_cf[['company_id', 'year_clean', 'operating_activity', 'investing_activity', 'financing_activity', 'net_cash_flow']].to_sql('fact_cash_flow', conn, if_exists='append', index=False)
    
    conn.close()
    print(f"SUCCESS: Data Warehouse finalized at '{DB_PATH}'!")