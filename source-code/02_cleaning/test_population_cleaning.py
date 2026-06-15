"""
test_population_cleaning.py - Kiem tra tinh hop le cua du lieu dan so sau khi lam sach.

Input: dataset/clean/population_clean.csv
"""

import sys
import csv
from pathlib import Path

# Dam bao console Windows hien thi tieng Viet
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CLEAN_FILE = PROJECT_ROOT / "dataset" / "clean" / "population_clean.csv"

REQUIRED_COLUMNS = ["province", "population", "area", "density", "region"]

def check_file_exists():
    if CLEAN_FILE.exists():
        print(f"[OK] File ton tai: {CLEAN_FILE}")
        return True
    else:
        print(f"[FAIL] Khong tim thay file: {CLEAN_FILE}")
        return False

def run_tests():
    with open(CLEAN_FILE, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        headers = next(reader, [])
        
        missing_cols = [c for c in REQUIRED_COLUMNS if c not in headers]
        if missing_cols:
            print(f"[FAIL] Thieu cot: {missing_cols}")
            return False
        else:
            print("[OK] Day du cac cot bat buoc.")
            
        header_map = {col: i for i, col in enumerate(headers)}
        
        seen_keys = set()
        errors = 0
        total_rows = 0
        
        for i, row in enumerate(reader, start=2):
            total_rows += 1
            if len(row) < len(REQUIRED_COLUMNS):
                print(f"[FAIL] Dong {i}: Thieu du lieu.")
                errors += 1
                continue
                
            province = row[header_map["province"]].strip()
            if not province:
                print(f"[FAIL] Dong {i}: Tinh thanh bi rong.")
                errors += 1
                
            if province in seen_keys:
                print(f"[FAIL] Dong {i}: Trung lap tinh thanh - {province}")
                errors += 1
            seen_keys.add(province)
            
            try:
                population = int(row[header_map["population"]])
                area = float(row[header_map["area"]])
                density = float(row[header_map["density"]])
                
                if population <= 0:
                    print(f"[FAIL] Dong {i}: Dan so <= 0 ({population}).")
                    errors += 1
                if area <= 0:
                    print(f"[FAIL] Dong {i}: Dien tich <= 0 ({area}).")
                    errors += 1
                if density <= 0:
                    print(f"[FAIL] Dong {i}: Mat do <= 0 ({density}).")
                    errors += 1
            except ValueError:
                print(f"[FAIL] Dong {i}: Loi kieu du lieu so.")
                errors += 1
                
        if errors == 0:
            print(f"[OK] Kiem tra thanh cong tat ca {total_rows} dong.")
            return True
        else:
            print(f"\n[FAIL] Phat hien {errors} loi tren tong so {total_rows} dong.")
            return False

def main():
    print("=" * 55)
    print("  TEST POPULATION CLEANING — Kiem tra du lieu dan so")
    print("=" * 55)
    print()
    
    if not check_file_exists():
        sys.exit(1)
        
    print()
    if run_tests():
        print("\n=> [PASS] DU LIEU HOP LE!")
    else:
        print("\n=> [FAIL] DU LIEU CO LOI!")
        sys.exit(1)

if __name__ == "__main__":
    main()
