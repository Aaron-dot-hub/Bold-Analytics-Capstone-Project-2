import os
import pandas as pd
from utils import normalize_year
from validation import run_data_audit
from db_store import save_to_warehouse  # <-- Import database writer

BASE_DIR = "Data sets"
COMPANIES_PATH = os.path.join(BASE_DIR, "companies.xlsx")
PL_PATH = os.path.join(BASE_DIR, "profitandloss.xlsx")
BS_PATH = os.path.join(BASE_DIR, "balancesheet.xlsx")
CF_PATH = os.path.join(BASE_DIR, "cashflow.xlsx")

def load_transform_and_audit():
    print("Starting Sprint 1 ETL Pipeline with Universe Filtering...")
    
    # 1. Load Master Universe
    df_companies = pd.read_excel(COMPANIES_PATH, header=1)
    df_companies['id'] = df_companies['id'].astype(str).str.strip().str.upper()
    universe_tickers = set(df_companies['id'])

    # 2. Load & Filter Profit & Loss
    df_pl_raw = pd.read_excel(PL_PATH, header=1)
    df_pl_raw['company_id'] = df_pl_raw['company_id'].astype(str).str.strip().str.upper()
    df_pl = df_pl_raw[df_pl_raw['company_id'].isin(universe_tickers)].copy()
    df_pl['year_clean'] = df_pl['year'].apply(normalize_year)
    # Deduplicate composite primary key
    df_pl = df_pl.drop_duplicates(subset=['company_id', 'year_clean'], keep='last')
    print(f"Filtered & Deduplicated Profit & Loss: Kept {len(df_pl)} rows.")

    # 3. Load & Filter Balance Sheet
    df_bs_raw = pd.read_excel(BS_PATH, header=1)
    df_bs_raw['company_id'] = df_bs_raw['company_id'].astype(str).str.strip().str.upper()
    df_bs = df_bs_raw[df_bs_raw['company_id'].isin(universe_tickers)].copy()
    df_bs['year_clean'] = df_bs['year'].apply(normalize_year)
    # Deduplicate composite primary key
    df_bs = df_bs.drop_duplicates(subset=['company_id', 'year_clean'], keep='last')
    print(f"Filtered & Deduplicated Balance Sheet: Kept {len(df_bs)} rows.")

    # 4. Load & Filter Cash Flow
    df_cf_raw = pd.read_excel(CF_PATH, header=1)
    df_cf_raw['company_id'] = df_cf_raw['company_id'].astype(str).str.strip().str.upper()
    df_cf = df_cf_raw[df_cf_raw['company_id'].isin(universe_tickers)].copy()
    df_cf['year_clean'] = df_cf['year'].apply(normalize_year)
    # Deduplicate composite primary key
    df_cf = df_cf.drop_duplicates(subset=['company_id', 'year_clean'], keep='last')
    print(f"Filtered & Deduplicated Cash Flow: Kept {len(df_cf)} rows.")
    
    # Run audit pass
    run_data_audit(df_companies, df_pl, df_bs, df_cf)
    
    # WRITE DATA TO SQL WAREHOUSE
    save_to_warehouse(df_companies, df_pl, df_bs, df_cf)

if __name__ == "__main__":
    load_transform_and_audit()