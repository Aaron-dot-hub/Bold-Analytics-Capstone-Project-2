import pandas as pd

def run_data_audit(df_comp, df_pl, df_bs, df_cf):
    print("\nRunning Sprint 1 Data Quality Audit...")
    valid_tickers = set(df_comp['id'])
    critical_errors = 0
    
    # 1. Check for Orphaned Records
    for name, df in [("Profit & Loss", df_pl), ("Balance Sheet", df_bs), ("Cash Flow", df_cf)]:
        orphans = df[~df['company_id'].isin(valid_tickers)]
        if not orphans.empty:
            print(f"CRITICAL: Found {len(orphans)} orphaned rows in {name}! Example tickers: {orphans['company_id'].unique()[:3]}")
            critical_errors += 1
        else:
            print(f"Referential Integrity: No orphaned rows in {name}.")
            
    # 2. Check for Missing Critical Values
    if df_pl['sales'].isna().sum() > 0 or df_pl['net_profit'].isna().sum() > 0:
        print(f"WARNING: Null values detected in key P&L columns.")
    else:
        print("Completeness: Critical financial metrics contain zero null values.")

    # 3. Mathematical Integrity Check (Sales - Expenses = Operating Profit)
    # We allow a small 1% margin for rounding discrepancies in the raw sheets
    pl_calc = df_pl.copy()
    pl_calc['expected_op'] = pl_calc['sales'] - pl_calc['expenses']
    mismatches = pl_calc[abs(pl_calc['operating_profit'] - pl_calc['expected_op']) > (pl_calc['sales'] * 0.01)]
    
    if not mismatches.empty:
        print(f"WARNING: Found {len(mismatches)} rows where Sales - Expenses != Operating Profit.")
    else:
        print("Mathematical Integrity: Operating profits perfectly match structural expectations.")
        
    print("-" * 60)
    if critical_errors == 0:
        print("🎉 PASSED: Data quality meets production exit gates. Ready for database warehousing!")
    else:
        print(f"FAILED: Resolve the {critical_errors} critical errors before proceeding.")