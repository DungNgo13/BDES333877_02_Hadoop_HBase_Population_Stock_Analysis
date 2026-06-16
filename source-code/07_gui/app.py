"""
app.py - Ung dung web Flask giao dien nguoi dung.
"""
import sys
import os
from pathlib import Path
from flask import Flask, render_template, request
import pandas as pd

# Dam bao hien thi tieng Viet tren console Windows
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

app = Flask(__name__)

# Duong dan tinh
PROJECT_ROOT = Path(__file__).resolve().parents[2]
POPULATION_CSV = PROJECT_ROOT / "dataset" / "clean" / "population_clean.csv"
STOCK_CSV = PROJECT_ROOT / "dataset" / "clean" / "stock_clean.csv"
CHART_DIR = Path(__file__).resolve().parent / "static" / "charts"

# Dam bao thu muc static/charts ton tai
CHART_DIR.mkdir(parents=True, exist_ok=True)

def dataframe_to_html(df):
    if df is None or df.empty:
        return "<div class='empty-state'>Không có dữ liệu để hiển thị.</div>"
    return df.to_html(
        classes="data-table",
        index=False,
        border=0,
        escape=False
    )

def load_data(filepath):
    """Doc file CSV bang pandas, tra ve DataFrame hoac None, err_msg."""
    if filepath.exists():
        try:
            return pd.read_csv(filepath), ""
        except Exception as e:
            return None, f"Lỗi đọc file: {e}"
    return None, f"Không tìm thấy file: {filepath.name}"

@app.route('/favicon.ico')
def favicon():
    return "", 204

@app.route("/")
def index():
    """Trang chu"""
    return render_template("index.html")

@app.route("/population")
def population():
    """Trang hien thi du lieu dan so"""
    df, err = load_data(POPULATION_CSV)
    if df is not None:
        table_html = dataframe_to_html(df.head(100))
        total_rows = len(df)
        columns = df.columns.tolist()
    else:
        table_html = dataframe_to_html(None)
        total_rows = 0
        columns = []
        
    return render_template("population.html", 
                           table_html=table_html, 
                           total_rows=total_rows, 
                           columns=columns, 
                           error=err)

@app.route("/stocks")
def stocks():
    """Trang hien thi du lieu chung khoan"""
    df, err = load_data(STOCK_CSV)
    if df is not None:
        table_html = dataframe_to_html(df.head(100))
        total_rows = len(df)
        columns = df.columns.tolist()
    else:
        table_html = dataframe_to_html(None)
        total_rows = 0
        columns = []
        
    return render_template("stocks.html", 
                           table_html=table_html, 
                           total_rows=total_rows, 
                           columns=columns, 
                           error=err)

@app.route("/charts")
def charts():
    """Trang hien thi bieu do tu thu muc static/charts"""
    charts = []
    if CHART_DIR.exists():
        charts = [f for f in os.listdir(CHART_DIR) if f.endswith(".png")]
    return render_template("charts.html", charts=charts)

@app.route("/search")
def search():
    """Trang tim kiem (tinh thanh hoac ma co phieu)"""
    query = request.args.get("q", "").strip().lower()
    pop_table = ""
    stock_table = ""
    
    if query:
        # Tim kiem dan so
        df_pop, _ = load_data(POPULATION_CSV)
        if df_pop is not None and "province" in df_pop.columns:
            mask = df_pop["province"].astype(str).str.lower().str.contains(query, na=False)
            filtered_pop = df_pop[mask]
            if not filtered_pop.empty:
                pop_table = dataframe_to_html(filtered_pop)
            
        # Tim kiem chung khoan
        df_stock, _ = load_data(STOCK_CSV)
        if df_stock is not None and "symbol" in df_stock.columns:
            mask = df_stock["symbol"].astype(str).str.lower().str.contains(query, na=False)
            filtered_stock = df_stock[mask]
            if not filtered_stock.empty:
                stock_table = dataframe_to_html(filtered_stock)
            
    return render_template("search.html", 
                           query=query, 
                           population_table=pop_table, 
                           stock_table=stock_table)

def main():
    print("=" * 55)
    print("  KHOI DONG FLASK WEB APP")
    print("=" * 55)
    print("  Truy cap: http://localhost:5000")
    print("=" * 55)
    # Chay host 0.0.0.0 port 5000
    app.run(host="0.0.0.0", port=5000, debug=True)

if __name__ == "__main__":
    main()
