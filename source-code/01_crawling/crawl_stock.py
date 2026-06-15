"""
crawl_stock.py — Thu thap du lieu gia co phieu REE, MWG, FPT.
"""

import sys
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

# Dam bao hien thi tieng Viet tren Windows
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

try:
    import requests
except ImportError:
    print("[LOI] Thieu thu vien requests. Chay: pip install requests")
    requests = None

# Duong dan tinh
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RAW_OUTPUT = PROJECT_ROOT / "dataset" / "raw" / "stock_raw.csv"

SYMBOLS = ["REE", "MWG", "FPT"]

def generate_fallback_data():
    """Sinh du lieu fallback gia lap tu nam 2020 den 2025 (>= 1000 dong)."""
    base_prices = {"REE": 60.0, "MWG": 50.0, "FPT": 80.0}
    data = []
    start_date = datetime(2020, 1, 1)
    end_date = datetime(2025, 12, 31)
    
    for sym, base_price in base_prices.items():
        curr_date = start_date
        curr_price = base_price
        while curr_date <= end_date:
            if curr_date.weekday() < 5:  # Chi lay tu Thu 2 den Thu 6
                change_pct = random.uniform(-0.05, 0.05)
                open_p = curr_price
                close_p = open_p * (1 + change_pct)
                
                # Dam bao logic gia: low <= open/close <= high
                high_p = max(open_p, close_p) * (1 + random.uniform(0.001, 0.02))
                low_p = min(open_p, close_p) * (1 - random.uniform(0.001, 0.02))
                
                # Dam bao gia luon > 0
                if low_p <= 0:
                    low_p = 0.1
                if close_p <= 0:
                    close_p = 0.1
                    
                volume = random.randint(100000, 5000000)
                change_val = close_p - open_p
                
                data.append({
                    "symbol": sym,
                    "date": curr_date.strftime("%Y-%m-%d"),
                    "open_price": round(open_p, 2),
                    "high_price": round(high_p, 2),
                    "low_price": round(low_p, 2),
                    "close_price": round(close_p, 2),
                    "volume": volume,
                    "change_value": round(change_val, 2),
                    "change_percent": round(change_pct * 100, 2)
                })
                curr_price = close_p
            curr_date += timedelta(days=1)
    return data

FALLBACK_DATA = generate_fallback_data()

def build_stock_url(symbol, page=1):
    """
    Ham tao URL crawl du lieu tren VNDirect API.
    Mo rong size len 2000 va lay tu 2020-01-01 den 2025-12-31.
    """
    url = "https://finfo-api.vndirect.com.vn/v4/stock_prices"
    params = f"?sort=date&q=code:{symbol}~date:gte:2020-01-01~date:lte:2025-12-31&size=2000&page={page}"
    return url + params

def crawl_symbol(symbol):
    """Crawl du lieu cho 1 ma co phieu."""
    if not requests:
        return None
        
    url = build_stock_url(symbol, 1)
    headers = {"User-Agent": "Mozilla/5.0 (BigDataProject/1.0; Educational)"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        results = []
        if "data" in data and data["data"]:
            for item in data["data"]:
                try:
                    open_p = float(item.get("open", 0))
                    close_p = float(item.get("close", 0))
                    change_val = float(item.get("change", close_p - open_p))
                    ref_p = float(item.get("adClose", open_p)) if open_p == 0 else open_p
                    change_pct = round((change_val / ref_p) * 100, 2) if ref_p != 0 else 0.0
                    
                    results.append({
                        "symbol": symbol,
                        "date": item.get("date", "")[:10],
                        "open_price": round(open_p, 2),
                        "high_price": round(float(item.get("high", 0)), 2),
                        "low_price": round(float(item.get("low", 0)), 2),
                        "close_price": round(close_p, 2),
                        "volume": int(float(item.get("nmVolume", 0))),
                        "change_value": round(change_val, 2),
                        "change_percent": change_pct
                    })
                except (ValueError, TypeError):
                    continue
        return results if results else None
    except Exception as e:
        print(f"    [LOI] Khong the crawl {symbol}: {e}")
        return None

def main():
    print("=" * 55)
    print("  CRAWL STOCK — Du lieu gia co phieu")
    print("=" * 55)
    print()
    
    all_data = []
    crawl_success = True
    
    # 1. Thu crawl truc tuyen
    for sym in SYMBOLS:
        print(f"[+] Dang thu crawl: {sym}...")
        res = crawl_symbol(sym)
        if res:
            print(f"    -> Thanh cong: lay duoc {len(res)} dong.")
            all_data.extend(res)
        else:
            print(f"    -> That bai khi lay du lieu {sym}.")
            crawl_success = False
            break
            
    # 2. Neu co loi, dung du lieu mau fallback
    if not crawl_success or not all_data:
        print("\n[CANH BAO] Crawl mang that bai hoac API bi khoa.")
        print("Dung du lieu mau fallback (sinh tu dong tu 2020 den 2025).")
        all_data = FALLBACK_DATA
        
    # Sap xep theo ma co phieu va ngay
    all_data.sort(key=lambda x: (x["symbol"], x["date"]))
    
    # 3. Luu file CSV
    RAW_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "symbol", "date", "open_price", "high_price", "low_price",
        "close_price", "volume", "change_value", "change_percent"
    ]
    
    with open(RAW_OUTPUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_data)
        
    print(f"\n[OK] Da luu {len(all_data)} dong -> {RAW_OUTPUT}")

if __name__ == "__main__":
    main()
