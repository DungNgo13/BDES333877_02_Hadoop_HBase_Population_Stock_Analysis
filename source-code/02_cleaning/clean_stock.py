"""
clean_stock.py — Lam sach du lieu gia co phieu.

Input:  dataset/raw/stock_raw.csv
Output: dataset/clean/stock_clean.csv
"""

import pandas as pd
import sys
from pathlib import Path

# Dam bao console Windows hien thi tieng Viet
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Duong dan tinh tuong doi tu file chay
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
INPUT_FILE = PROJECT_ROOT / "dataset" / "raw" / "stock_raw.csv"
OUTPUT_FILE = PROJECT_ROOT / "dataset" / "clean" / "stock_clean.csv"

def clean_data(df):
    """Thuc hien lam sach du lieu chung khoan theo quy tac."""
    # 1. Chuan hoa ten cot
    df.columns = ["symbol", "date", "open_price", "high_price", "low_price", 
                  "close_price", "volume", "change_value", "change_percent"]
    
    # 2. Xoa cac dong thieu symbol, date, close_price
    df = df.dropna(subset=["symbol", "date", "close_price"])
    df = df[(df["symbol"] != "") & (df["date"] != "")]
    
    # 3. Chuyen doi symbol sang chu in hoa
    df["symbol"] = df["symbol"].astype(str).str.strip().str.upper()
    
    # 4. Chuyen doi date sang yyyy-mm-dd
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%Y-%m-%d")
    df = df.dropna(subset=["date"]) # Loai bo neu parse date that bai
    
    # 5. Chuyen kieu du lieu so
    float_cols = ["open_price", "high_price", "low_price", "close_price", "change_value", "change_percent"]
    for col in float_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0).astype(float)
        
    df["volume"] = pd.to_numeric(df["volume"], errors="coerce").fillna(0).astype(int)
    
    # 6. Loai bo gia <= 0 (it nhat close_price phai > 0)
    df = df[df["close_price"] > 0]
    
    # 7. Kiem tra tinh hop le cua gia: low <= close <= high
    df = df[(df["low_price"] <= df["close_price"]) & (df["close_price"] <= df["high_price"])]
    
    # 8. Xoa trung lap symbol + date
    df = df.drop_duplicates(subset=["symbol", "date"], keep="first")
    
    # 9. Sap xep theo symbol va date
    df = df.sort_values(by=["symbol", "date"], ascending=[True, True])
    
    return df

def main():
    print("=" * 55)
    print("  CLEAN STOCK — Lam sach du lieu gia co phieu")
    print("=" * 55)
    print()

    # Kiem tra file input
    if not INPUT_FILE.exists():
        print(f"[LOI] Khong tim thay file: {INPUT_FILE}")
        sys.exit(1)
        
    print(f"[1/3] Doc du lieu tu: {INPUT_FILE}")
    try:
        df = pd.read_csv(INPUT_FILE)
    except Exception as e:
        print(f"[LOI] Khong the doc file CSV: {e}")
        sys.exit(1)
        
    initial_rows = len(df)
    print(f"  -> Doc duoc {initial_rows} dong.")
    
    print("[2/3] Dang lam sach du lieu...")
    clean_df = clean_data(df)
    final_rows = len(clean_df)
    removed_rows = initial_rows - final_rows
    
    print(f"[3/3] Luu du lieu sach ra file...")
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    clean_df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")
    print(f"  -> Da luu vao: {OUTPUT_FILE}")
    
    print()
    print("=" * 55)
    print("  TOM TAT")
    print("=" * 55)
    print(f"  So dong input:  {initial_rows}")
    print(f"  So dong bi xoa: {removed_rows}")
    print(f"  So dong output: {final_rows}")
    print()
    
    print("  5 dong dau tien:")
    print(f"  {'symbol':<8} {'date':<12} {'open':>8} {'close':>8} {'volume':>12}")
    print("  " + "-" * 55)
    for _, row in clean_df.head(5).iterrows():
        print(f"  {row['symbol']:<8} {row['date']:<12} {row['open_price']:>8.2f} {row['close_price']:>8.2f} {row['volume']:>12,}")
    print()

if __name__ == "__main__":
    main()
