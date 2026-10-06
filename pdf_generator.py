import sqlite3
import os
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

DB_PATH = "nifty100_intelligence.db"

def generate_company_pdf(company_id):
    print(f"\nGenerating Executive PDF Dossier for {company_id}...")
    
    if not os.path.exists(DB_PATH):
        print(f"Error: Database file not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    
    # Query complete multi-dimensional analytics for the target firm without health_label column
    query = """
    SELECT h.company_id, c.company_name, h.composite_health_score,
           r.roe_percentage, r.npm_percentage, r.debt_to_equity,
           g.revenue_cagr_3y, g.pat_cagr_3y,
           cf.free_cash_flow, cf.cash_conversion_ratio
    FROM fact_financial_health_scores h
    JOIN dim_companies c ON h.company_id = c.id
    JOIN fact_financial_ratios r ON h.company_id = r.company_id AND h.year_clean = r.year_clean
    LEFT JOIN fact_growth_analytics g ON h.company_id = g.company_id
    LEFT JOIN fact_cashflow_intelligence cf ON h.company_id = cf.company_id
    WHERE h.company_id = ?;
    """
    
    df = pd.read_sql_query(query, conn, params=(company_id,))
    conn.close()
    
    if df.empty:
        print(f"Company ID '{company_id}' not found or metrics are incomplete.")
        return

    row = df.iloc[0]
    pdf_filename = f"{company_id}_Executive_Analysis.pdf"
    
    # Dynamically assign health tier label based on the numerical composite score
    score = row['composite_health_score']
    if score >= 75:
        health_label = "STRONG ALPHA"
    elif score >= 50:
        health_label = "STABLE / PASS"
    else:
        health_label = "HIGH RISK / WATCHLIST"
    
    # Document Setup
    doc = SimpleDocTemplate(pdf_filename, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom Typography Styling
    title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontSize=24, textColor=colors.HexColor("#1A365D"), spaceAfter=6)
    subtitle_style = ParagraphStyle('DocSub', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor("#4A5568"), spaceAfter=20)
    section_style = ParagraphStyle('SectionHeading', parent=styles['Heading2'], fontSize=14, textColor=colors.HexColor("#2B6CB0"), spaceBefore=12, spaceAfter=8)
    
    # Header Banner Elements
    story.append(Paragraph(f"{row['company_name']} ({row['company_id']})", title_style))
    story.append(Paragraph("Institutional Investment Intelligence Dossier | Generated via B100 Analytics", subtitle_style))
    story.append(Spacer(1, 10))
    
    # Section 1: Risk & Health Scoring Summary
    story.append(Paragraph("Health Matrix Evaluation", section_style))
    health_data = [
        ["Composite Health Score", f"{score} / 100"],
        ["Risk Tier Classification", health_label]
    ]
    t1 = Table(health_data, colWidths=[200, 300])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F7FAFC")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('PADDING', (0,0), (-1,-1), 8),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (1,1), (1,1), colors.HexColor("#2F855A") if score >= 50 else colors.HexColor("#C53030"))
    ]))
    story.append(t1)
    story.append(Spacer(1, 15))
    
    # Section 2: Financial Metrics & Ratios Grid
    story.append(Paragraph("Core Financial Metrics & Growth Trends", section_style))
    metric_data = [
        ["Financial KPI Metric", "Calculated Core Value", "Historical 3y Trend (CAGR) / Note"],
        ["Return on Equity (ROE)", f"{row['roe_percentage']}%", "Universe Percentile Indexed"],
        ["Net Profit Margin (NPM)", f"{row['npm_percentage']}%", "Operating Efficiency Baseline"],
        ["Leverage Ratio (D/E)", f"{row['debt_to_equity']}x", "Capital Structure Risk Metric"],
        ["Revenue Expansion Profile", f"{row['revenue_cagr_3y']}% Growth", "3Y Geometric Compounding Rate"],
        ["Net Profit Profile (PAT Growth)", f"{row['pat_cagr_3y']}% Growth", "Turnaround Capped Metrics Verified"],
        ["Free Cash Flow Balance", f"Cr {row['free_cash_flow']:,}", "Liquid Available Surplus Cash"],
        ["Liquidity Cash Conversion", f"{row['cash_conversion_ratio']}x Factor", "CFO / PAT Earnings Quality Metric"]
    ]
    t2 = Table(metric_data, colWidths=[180, 160, 160])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#2B6CB0")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F7FAFC")]),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t2)
    
    # Build PDF File Layout
    doc.build(story)
    print(f"Standalone PDF analysis successfully generated: `{pdf_filename}`")

if __name__ == "__main__":
    generate_company_pdf("BEL")