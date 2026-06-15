"""
crawl_stock.py — Thu thap du lieu gia co phieu REE, MWG, FPT.
"""

import sys
import csv
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

# Du lieu mau fallback
FALLBACK_DATA = [
    # REE
    {"symbol": "REE", "date": "2024-01-02", "open_price": 62.5, "high_price": 63.8, "low_price": 62.0, "close_price": 63.5, "volume": 1250000, "change_value": 1.0, "change_percent": 1.6},
    {"symbol": "REE", "date": "2024-01-03", "open_price": 63.5, "high_price": 64.2, "low_price": 63.0, "close_price": 63.8, "volume": 1180000, "change_value": 0.3, "change_percent": 0.47},
    {"symbol": "REE", "date": "2024-01-04", "open_price": 63.8, "high_price": 63.8, "low_price": 62.5, "close_price": 62.7, "volume": 980000, "change_value": -1.1, "change_percent": -1.72},
    # MWG
    {"symbol": "MWG", "date": "2024-01-02", "open_price": 52.0, "high_price": 53.5, "low_price": 51.8, "close_price": 53.2, "volume": 2500000, "change_value": 1.2, "change_percent": 2.31},
    {"symbol": "MWG", "date": "2024-01-03", "open_price": 53.2, "high_price": 54.0, "low_price": 52.8, "close_price": 53.8, "volume": 2350000, "change_value": 0.6, "change_percent": 1.13},
    {"symbol": "MWG", "date": "2024-01-04", "open_price": 53.8, "high_price": 54.2, "low_price": 53.0, "close_price": 53.0, "volume": 2100000, "change_value": -0.8, "change_percent": -1.49},
    # FPT
    {"symbol": "FPT", "date": "2024-01-02", "open_price": 89.0, "high_price": 91.0, "low_price": 88.5, "close_price": 90.5, "volume": 1800000, "change_value": 1.5, "change_percent": 1.69},
    {"symbol": "FPT", "date": "2024-01-03", "open_price": 90.5, "high_price": 92.0, "low_price": 90.0, "close_price": 91.8, "volume": 1750000, "change_value": 1.3, "change_percent": 1.44},
    {"symbol": "FPT", "date": "2024-01-04", "open_price": 91.8, "high_price": 92.5, "low_price": 90.5, "close_price": 90.8, "volume": 1600000, "change_value": -1.0, "change_percent": -1.09},
]

def build_stock_url(symbol, page=1):
    """
    Ham tao URL crawl du lieu.
    Co the doi endpoint tai day neu API doi.
    """
    url = "https://finfo-api.vndirect.com.vn/v4/stock_prices"
    params = f"?sort=date&q=code:{symbol}&size=10&page={page}"
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
        print("Dung du lieu mau fallback (FALLBACK_DATA).")
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
