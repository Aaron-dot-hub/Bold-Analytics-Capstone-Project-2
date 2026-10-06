import pytest
import pandas as pd
import numpy as np

# Mocking core algorithmic logic to verify math behaviors safely
def calculate_roe(net_profit, equity):
    if equity <= 0:
        return 0.0
    return round((net_profit / equity) * 100, 2)

def calculate_cagr(end_val, start_val, periods):
    if start_val <= 0 or end_val <= 0 or periods <= 0:
        return 0.0
    return round((pow(end_val / start_val, 1 / periods) - 1) * 100, 2)

def calculate_percentile_rank(value, all_values):
    if len(all_values) <= 1:
        return 100.0
    sorted_vals = sorted(all_values)
    count_below = sum(1 for v in sorted_vals if v < value)
    return round((count_below / (len(all_values) - 1)) * 100, 2)


# --- UNIT TESTS FOR FINANCIAL LOGIC ---

def test_roe_standard_calculation():
    """Verify that normal positive values yield accurate ROE percentages."""
    assert calculate_roe(25, 100) == 25.0
    assert calculate_roe(15.5, 50) == 31.0

def test_roe_zero_or_negative_equity_edge_case():
    """Ensure zero or negative equity avoids division-by-zero crashes gracefully."""
    assert calculate_roe(10, 0) == 0.0
    assert calculate_roe(10, -50) == 0.0

def test_cagr_compounding_growth():
    """Verify standard geometric multi-period compound growth calculations."""
    # 100 growing to 144 over 2 years is a 20% CAGR
    assert calculate_cagr(144, 100, 2) == 20.0

def test_cagr_negative_or_zero_bounds():
    """Ensure negative starting values return a zero fallback rather than breaking."""
    assert calculate_cagr(100, 0, 3) == 0.0
    assert calculate_cagr(100, -10, 3) == 0.0

def test_percentile_ranking_universe():
    """Verify percentile boundaries rank elements correctly inside an ordered set."""
    universe = [10, 20, 30, 40, 50]
    # 50 is the maximum, so 4 values are below it. (4 / 4) * 100 = 100%
    assert calculate_percentile_rank(50, universe) == 100.0
    # 10 is the minimum, so 0 values are below it. (0 / 4) * 100 = 0%
    assert calculate_percentile_rank(10, universe) == 0.0
    # 30 is the median, 2 values below it. (2 / 4) * 100 = 50%
    assert calculate_percentile_rank(30, universe) == 50.0