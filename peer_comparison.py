import sqlite3
import pandas as pd

DB_PATH = "nifty100_intelligence.db"

def compute_peer_ranks():
    print("\nLaunching Sprint 4 Peer Comparison Engine...")
    conn = sqlite3.connect(DB_PATH)
    
    # 1. Gather latest financial metrics
    query = """
    SELECT company_id, roe_percentage, opm_percentage, npm_percentage, debt_to_equity
    FROM fact_financial_ratios r
    WHERE r.year_clean = (SELECT MAX(year_clean) FROM fact_financial_ratios WHERE company_id = r.company_id);
    """
    df = pd.read_sql_query(query, conn)
    
    if df.empty:
        print("Error: No ratio records found. Run ratio_engine.py first.")
        conn.close()
        return

    print("Computing universe-wide relative percentile rankings...")
    
    # 2. Compute true percentile ranks (Higher is better for returns/margins, lower is better for leverage)
    df['roe_percentile'] = df['roe_percentage'].rank(pct=True) * 100
    df['opm_percentile'] = df['opm_percentage'].rank(pct=True) * 100
    df['npm_percentile'] = df['npm_percentage'].rank(pct=True) * 100
    df['debt_percentile'] = (1 - df['debt_to_equity'].rank(pct=True)) * 100  # Lower debt = Higher score
    
    # Clean up formatting
    rank_cols = ['roe_percentile', 'opm_percentile', 'npm_percentile', 'debt_percentile']
    df[rank_cols] = df[rank_cols].round(2)
    
    # 3. Create database schema and write data cleanly
    print("Seeding 'fact_peer_rankings' table layout...")
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS fact_peer_rankings;")
    cursor.execute("""
    CREATE TABLE fact_peer_rankings (
        company_id TEXT PRIMARY KEY,
        roe_percentile REAL,
        opm_percentile REAL,
        npm_percentile REAL,
        debt_percentile REAL,
        FOREIGN KEY (company_id) REFERENCES dim_companies(id)
    );
    """)
    conn.commit()
    
    df_db = df[['company_id', 'roe_percentile', 'opm_percentile', 'npm_percentile', 'debt_percentile']]
    df_db.to_sql('fact_peer_rankings', conn, if_exists='append', index=False)
    conn.close()
    
    print("\nPeer rankings successfully finalized with 0 errors! Top 5 Elite Percentile Leaders:")
    print(df_db.sort_values(by='roe_percentile', ascending=False).head(5).to_string(index=False))

if __name__ == "__main__":
    compute_peer_ranks()