import sqlite3
import pandas as pd

pd.set_option('future.no_silent_downcasting', True)
DB_PATH = "nifty100_intelligence.db"

def compute_financial_health_scores():
    print("\nLaunching Sprint 3 Financial Health Scoring Model...")
    conn = sqlite3.connect(DB_PATH)
    
    # Query the latest financial year records for all companies
    query = """
    SELECT r.*, c.company_name
    FROM fact_financial_ratios r
    JOIN dim_companies c ON r.company_id = c.id
    WHERE r.year_clean = (SELECT MAX(year_clean) FROM fact_financial_ratios WHERE company_id = r.company_id);
    """
    df = pd.read_sql_query(query, conn)
    
    print(f"Processing diagnostic data matrices for {len(df)} target firms...")
    
    # 1. Component Scoring out of 25 points each (Total = 100)
    # Clip and bound ROE so crazy outliers (like INDIGO) cap out at 25 points max
    df['roe_score'] = (df['roe_percentage'] / 20.0 * 25).clip(0, 25)
    
    # Net Profit Margin score (Targeting 15% NPM for full points)
    df['npm_score'] = (df['npm_percentage'] / 15.0 * 25).clip(0, 25)
    
    # Asset Efficiency score (Targeting 1.5x turnover for full points)
    df['asset_score'] = (df['asset_turnover'] / 1.5 * 25).clip(0, 25)
    
    # Leverage Penalty: Starts at 25 points, drops to 0 if Debt/Equity >= 2.0
    df['debt_score'] = (25 - (df['debt_to_equity'] / 2.0 * 25)).clip(0, 25)
    
    # 2. Sum up Component Pillars to arrive at overall Composite Health Score (0 - 100)
    df['composite_health_score'] = df['roe_score'] + df['npm_score'] + df['asset_score'] + df['debt_score']
    df['composite_health_score'] = df['composite_health_score'].round(2)
    
    # 3. Create and Seed table inside the database warehouse
    print("Creating and seeding 'fact_financial_health_scores' table...")
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS fact_financial_health_scores;")
    cursor.execute("""
    CREATE TABLE fact_financial_health_scores (
        company_id TEXT PRIMARY KEY,
        year_clean TEXT,
        composite_health_score REAL,
        FOREIGN KEY (company_id) REFERENCES dim_companies(id)
    );
    """)
    conn.commit()
    
    df[['company_id', 'year_clean', 'composite_health_score']].to_sql('fact_financial_health_scores', conn, if_exists='append', index=False)
    
    # Display topmost robust balance sheets
    df_sorted = df.sort_values(by='composite_health_score', ascending=False)
    print("\nTop 5 Elite Financial Health Score Ranking Winners:")
    print(df_sorted[['company_id', 'company_name', 'composite_health_score']].head(5).to_string(index=False))
    
    conn.close()

if __name__ == "__main__":
    compute_financial_health_scores()