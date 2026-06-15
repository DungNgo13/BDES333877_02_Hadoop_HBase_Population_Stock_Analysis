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
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
POP_FILE = PROJECT_ROOT / "dataset" / "clean" / "population_clean.csv"
STOCK_FILE = PROJECT_ROOT / "dataset" / "clean" / "stock_clean.csv"
CHARTS_DIR = Path(__file__).resolve().parent / "static" / "charts"

# Dam bao thu muc static/charts ton tai
CHARTS_DIR.mkdir(parents=True, exist_ok=True)

def load_data(filepath):
    """Doc file CSV bang pandas, tra ve DataFrame hoac None."""
    if filepath.exists():
        try:
            return pd.read_csv(filepath)
        except Exception as e:
            print(f"[LOI] Khong the doc {filepath}: {e}")
            return None
    return None

@app.route("/")
def index():
    """Trang chu"""
    return render_template("index.html")

@app.route("/population")
def population():
    """Trang hien thi du lieu dan so"""
    df = load_data(POP_FILE)
    if df is not None:
        data = df.head(100).to_dict(orient="records")
        columns = df.columns.tolist()
    else:
        data = []
        columns = []
    return render_template("population.html", data=data, columns=columns)

@app.route("/stocks")
def stocks():
    """Trang hien thi du lieu chung khoan"""
    df = load_data(STOCK_FILE)
    if df is not None:
        data = df.head(100).to_dict(orient="records")
        columns = df.columns.tolist()
    else:
        data = []
        columns = []
    return render_template("stocks.html", data=data, columns=columns)

@app.route("/charts")
def charts():
    """Trang hien thi bieu do tu thu muc static/charts"""
    images = []
    if CHARTS_DIR.exists():
        images = [f for f in os.listdir(CHARTS_DIR) if f.endswith(".png")]
    return render_template("charts.html", images=images)

@app.route("/search")
def search():
    """Trang tim kiem (tinh thanh hoac ma co phieu)"""
    query = request.args.get("q", "").strip().lower()
    results_pop = []
    results_stock = []
    
    if query:
        # Tim kiem dan so
        df_pop = load_data(POP_FILE)
        if df_pop is not None and "province" in df_pop.columns:
            mask = df_pop["province"].astype(str).str.lower().str.contains(query, na=False)
            results_pop = df_pop[mask].to_dict(orient="records")
            
        # Tim kiem chung khoan
        df_stock = load_data(STOCK_FILE)
        if df_stock is not None and "symbol" in df_stock.columns:
            mask = df_stock["symbol"].astype(str).str.lower().str.contains(query, na=False)
            results_stock = df_stock[mask].to_dict(orient="records")
            
    return render_template("search.html", query=query, pop_data=results_pop, stock_data=results_stock)

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
