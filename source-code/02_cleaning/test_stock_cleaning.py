"""
test_stock_cleaning.py — Kiem tra tinh hop le cua du lieu sau khi lam sach.

Input: dataset/clean/stock_clean.csv
"""

import sys
import csv
from pathlib import Path
from datetime import datetime

# Dam bao console Windows hien thi tieng Viet
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CLEAN_FILE = PROJECT_ROOT / "dataset" / "clean" / "stock_clean.csv"

REQUIRED_COLUMNS = [
    "symbol", "date", "open_price", "high_price", "low_price",
    "close_price", "volume", "change_value", "change_percent"
]

def check_file_exists():
    """Kiem tra file co ton tai khong."""
    if CLEAN_FILE.exists():
        print(f"[OK] File ton tai: {CLEAN_FILE}")
        return True
    else:
        print(f"[FAIL] Khong tim thay file: {CLEAN_FILE}")
        return False

def run_tests():
    """Chay cac bai kiem tra tren file CSV."""
    with open(CLEAN_FILE, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        headers = next(reader, [])
        
        # 1. Kiem tra columns
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
                
            symbol = row[header_map["symbol"]].strip()
            date_str = row[header_map["date"]].strip()
            
            # 2. Symbol khong rong
            if not symbol:
                print(f"[FAIL] Dong {i}: Symbol bi rong.")
                errors += 1
            
            # 3. Kiem tra dinh dang ngay
            try:
                datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                print(f"[FAIL] Dong {i}: Ngay '{date_str}' khong hop le (yyyy-mm-dd).")
                errors += 1
                
            # 4. Kiem tra trung lap
            key = (symbol, date_str)
            if key in seen_keys:
                print(f"[FAIL] Dong {i}: Trung lap du lieu - {key}")
                errors += 1
            seen_keys.add(key)
            
            # 5. Kiem tra gia tri so
            try:
                close_price = float(row[header_map["close_price"]])
                high_price = float(row[header_map["high_price"]])
                low_price = float(row[header_map["low_price"]])
                volume = int(row[header_map["volume"]])
                
                # close_price > 0
                if close_price <= 0:
                    print(f"[FAIL] Dong {i}: close_price <= 0 ({close_price}).")
                    errors += 1
                    
                # volume >= 0
                if volume < 0:
                    print(f"[FAIL] Dong {i}: volume < 0 ({volume}).")
                    errors += 1
                    
                # low <= close <= high
                if not (low_price <= close_price <= high_price):
                    print(f"[FAIL] Dong {i}: Logic gia sai (low: {low_price}, close: {close_price}, high: {high_price}).")
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
    print("  TEST STOCK CLEANING — Kiem tra du lieu sau lam sach")
    print("=" * 55)
    print()
    
    if not check_file_exists():
        sys.exit(1)
        
    print()
    if run_tests():
        print("\n=> [PASS] DU LIEU HOP LE!")
    else:
        print("\n=> [FAIL] DU LIEU CO LOI! Vui long kiem tra lai clean_stock.py")
        sys.exit(1)

if __name__ == "__main__":
    main()
