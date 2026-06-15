"""
clean_population.py — Lam sach du lieu dan so.

Input:  dataset/raw/population_raw.csv
Output: dataset/clean/population_clean.csv
"""

import pandas as pd
import sys
from pathlib import Path

# Đảm bảo console Windows hiển thị được tiếng Việt
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Đường dẫn tĩnh tương đối từ file chạy
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
INPUT_FILE = PROJECT_ROOT / "dataset" / "raw" / "population_raw.csv"
OUTPUT_FILE = PROJECT_ROOT / "dataset" / "clean" / "population_clean.csv"

def clean_data(df):
    """Thuc hien lam sach du lieu theo quy tac."""
    # 1. Chuan hoa ten cot
    df.columns = ["province", "population", "area", "density", "region"]
    
    # 2. Xoa khoang trang thuoc tinh string
    for col in ["province", "region"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
    
    # 3. Loai bo cac dong thieu province
    df = df.dropna(subset=["province"])
    df = df[df["province"] != ""]
    df = df[df["province"].str.lower() != "nan"]
    
    # 4. Chuyen kieu du lieu
    df["population"] = pd.to_numeric(df["population"], errors="coerce").fillna(0).astype(int)
    df["area"] = pd.to_numeric(df["area"], errors="coerce").fillna(0.0).astype(float)
    df["density"] = pd.to_numeric(df["density"], errors="coerce").fillna(0.0).astype(float)
    
    # 5. Xoa cac dong am hoac 0
    df = df[df["population"] > 0]
    df = df[df["area"] > 0]
    
    # 6. Tinh lai density neu thieu hoac = 0
    df.loc[(df["density"] <= 0) & (df["area"] > 0), "density"] = df["population"] / df["area"]
    
    # 7. Xoa trung lap province
    df = df.drop_duplicates(subset=["province"], keep="first")
    
    # 8. Sap xep giam dan theo dan so
    df = df.sort_values(by="population", ascending=False)
    
    return df

def main():
    print("=" * 55)
    print("  CLEAN POPULATION — Lam sach du lieu dan so")
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
    
    print("  5 dong dau tien (da sap xep theo dan so):")
    print(f"  {'province':<20} {'population':>12} {'area':>10} {'density':>10} {'region'}")
    print("  " + "-" * 75)
    for _, row in clean_df.head(5).iterrows():
        print(f"  {row['province']:<20} {int(row['population']):>12,} {row['area']:>10.1f} {row['density']:>10.1f} {row['region']}")
    print()

if __name__ == "__main__":
    main()
