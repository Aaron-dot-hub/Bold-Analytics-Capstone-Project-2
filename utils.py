import pandas as pd

def normalize_year(year_val):
    """
    Standardizes financial year markers (e.g., 'Mar 24', 'Dec 2012', 'Mar-23') 
    into a uniform YYYY-MM string standard.
    """
    if pd.isna(year_val):
        return None
    
    year_str = str(year_val).strip()
    
    # Map common month formats to numbers
    month_map = {
        'JAN': '01', 'FEB': '02', 'MAR': '03', 'APR': '04', 'MAY': '05', 'JUN': '06',
        'JUL': '07', 'AUG': '08', 'SEP': '09', 'OCT': '10', 'NOV': '11', 'DEC': '12'
    }
    
    # Standardize separators to spaces for clean parsing
    clean_str = year_str.replace('-', ' ').replace(',', ' ')
    parts = clean_str.split()
    
    if len(parts) == 2:
        # Check if format is like 'Mar 24' or 'Dec 2012'
        month_part = parts[0].upper()[:3]
        year_part = parts[1]
        
        # Convert 2-digit years to 4-digit years (assuming 2000s)
        if len(year_part) == 2:
            yyyy = f"20{year_part}"
        else:
            yyyy = year_part
            
        mm = month_map.get(month_part, "03") # Default to March if not matched
        return f"{yyyy}-{mm}"
            
    return year_str