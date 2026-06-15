"""
crawl_stock.py — Thu thập dữ liệu giá cổ phiếu REE, MWG, FPT từ nguồn công khai.
Nếu crawl thất bại, dùng fallback từ dataset/sample/stock_sample.csv.

Output: dataset/raw/stock_raw.csv
Columns: symbol,date,open_price,high_price,low_price,close_price,volume,change_value,change_percent
"""

import csv
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Đảm bảo console Windows hiển thị được tiếng Việt
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

try:
    import requests
except ImportError:
    print("[CẢNH BÁO] Thiếu thư viện requests.")
    print("Chạy: pip install requests")
    requests = None

# Đường dẫn tương đối từ project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RAW_OUTPUT = PROJECT_ROOT / "dataset" / "raw" / "stock_raw.csv"
SAMPLE_FILE = PROJECT_ROOT / "dataset" / "sample" / "stock_sample.csv"

# Danh sách mã cổ phiếu cần crawl
SYMBOLS = ["REE", "MWG", "FPT"]

# Khoảng thời gian: 1 năm gần nhất
DATE_TO = datetime.now()
DATE_FROM = DATE_TO - timedelta(days=365)


def crawl_from_vndirect(symbol, date_from, date_to):
    """Crawl dữ liệu từ VNDirect API (finfo-api)."""
    url = "https://finfo-api.vndirect.com.vn/v4/stock_prices"
    params = {
        "sort": "date",
        "q": f"code:{symbol}~date:gte:{date_from}~date:lte:{date_to}",
        "size": 500,
        "page": 1,
    }
    headers = {"User-Agent": "Mozilla/5.0 (BigDataProject/1.0; Educational)"}

    response = requests.get(url, params=params, headers=headers, timeout=15)
    response.raise_for_status()
    data = response.json()

    if "data" not in data or not data["data"]:
        return []

    results = []
    for row in data["data"]:
        try:
            close_price = float(row.get("close", 0))
            open_price = float(row.get("open", 0))
            # Tính change từ open -> close nếu API không cung cấp
            change_val = float(row.get("change", close_price - open_price))
            ref_price = float(row.get("adClose", open_price)) if open_price == 0 else open_price
            change_pct = round((change_val / ref_price) * 100, 2) if ref_price != 0 else 0.0

            results.append({
                "symbol": symbol,
                "date": row.get("date", row.get("tradingDate", ""))[:10],
                "open_price": round(open_price, 2),
                "high_price": round(float(row.get("high", 0)), 2),
                "low_price": round(float(row.get("low", 0)), 2),
                "close_price": round(close_price, 2),
                "volume": int(float(row.get("nmVolume", row.get("volume", 0)))),
                "change_value": round(change_val, 2),
                "change_percent": change_pct,
            })
        except (ValueError, TypeError, KeyError) as e:
            print(f"    [CẢNH BÁO] Bỏ qua dòng lỗi: {e}")
            continue

    return results


def crawl_from_cafef(symbol, date_from, date_to):
    """Crawl dữ liệu từ CafeF (nguồn dự phòng)."""
    from bs4 import BeautifulSoup

    url = f"https://s.cafef.vn/Lich-su-giao-dich-{symbol}-1.chn"
    headers = {"User-Agent": "Mozilla/5.0 (BigDataProject/1.0; Educational)"}

    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", {"id": "GirdTable"})
    if not table:
        return []

    results = []
    rows = table.find_all("tr")[2:]  # Bỏ 2 hàng header
    prev_close = None

    for row in rows:
        cells = row.find_all("td")
        if len(cells) < 7:
            continue
        try:
            date_str = cells[0].get_text().strip()
            # Chuyển dd/mm/yyyy -> yyyy-mm-dd
            parts = date_str.split("/")
            if len(parts) == 3:
                date_fmt = f"{parts[2]}-{parts[1]}-{parts[0]}"
            else:
                continue

            close_price = float(cells[4].get_text().strip().replace(",", ""))
            open_price = float(cells[3].get_text().strip().replace(",", ""))
            high_price = float(cells[5].get_text().strip().replace(",", ""))
            low_price = float(cells[6].get_text().strip().replace(",", ""))
            volume_text = cells[1].get_text().strip().replace(",", "")
            volume = int(float(volume_text)) if volume_text else 0

            # Tính change
            if prev_close is not None:
                change_val = round(close_price - prev_close, 2)
                change_pct = round((change_val / prev_close) * 100, 2) if prev_close != 0 else 0.0
            else:
                change_val = round(close_price - open_price, 2)
                change_pct = round((change_val / open_price) * 100, 2) if open_price != 0 else 0.0

            prev_close = close_price

            results.append({
                "symbol": symbol,
                "date": date_fmt,
                "open_price": round(open_price * 1000, 2),  # CafeF dùng đơn vị nghìn
                "high_price": round(high_price * 1000, 2),
                "low_price": round(low_price * 1000, 2),
                "close_price": round(close_price * 1000, 2),
                "volume": volume,
                "change_value": round(change_val * 1000, 2),
                "change_percent": change_pct,
            })
        except (ValueError, IndexError) as e:
            continue

    return results


def crawl_single_symbol(symbol, date_from, date_to):
    """Crawl dữ liệu cho 1 mã cổ phiếu, thử nhiều nguồn."""
    from_str = date_from.strftime("%Y-%m-%d")
    to_str = date_to.strftime("%Y-%m-%d")

    # Nguồn 1: VNDirect API
    try:
        print(f"    Nguồn 1: VNDirect API...")
        data = crawl_from_vndirect(symbol, from_str, to_str)
        if data and len(data) >= 5:
            print(f"    -> Thành công: {len(data)} dòng từ VNDirect")
            return data
        else:
            print(f"    -> Không đủ dữ liệu từ VNDirect ({len(data) if data else 0} dòng)")
    except Exception as e:
        print(f"    -> VNDirect lỗi: {e}")

    # Nguồn 2: CafeF
    try:
        print(f"    Nguồn 2: CafeF...")
        data = crawl_from_cafef(symbol, date_from, date_to)
        if data and len(data) >= 5:
            print(f"    -> Thành công: {len(data)} dòng từ CafeF")
            return data
        else:
            print(f"    -> Không đủ dữ liệu từ CafeF ({len(data) if data else 0} dòng)")
    except Exception as e:
        print(f"    -> CafeF lỗi: {e}")

    return None


def crawl_all_symbols():
    """Crawl dữ liệu cho tất cả mã cổ phiếu."""
    if requests is None:
        print("[LỖI] Không có thư viện requests.")
        return None

    print(f"[1/2] Crawl dữ liệu cổ phiếu: {', '.join(SYMBOLS)}")
    print(f"  Khoảng thời gian: {DATE_FROM.strftime('%Y-%m-%d')} -> {DATE_TO.strftime('%Y-%m-%d')}")
    print()

    all_data = []
    failed_symbols = []

    for symbol in SYMBOLS:
        print(f"  [{symbol}] Đang crawl...")
        data = crawl_single_symbol(symbol, DATE_FROM, DATE_TO)
        if data:
            all_data.extend(data)
        else:
            failed_symbols.append(symbol)
            print(f"  [{symbol}] Crawl thất bại.")

    if failed_symbols:
        print(f"\n[CẢNH BÁO] Các mã crawl thất bại: {', '.join(failed_symbols)}")

    if not all_data:
        print("[LỖI] Không crawl được dữ liệu từ bất kỳ nguồn nào.")
        return None

    # Sắp xếp theo symbol, date
    all_data.sort(key=lambda x: (x["symbol"], x["date"]))

    print(f"\n[2/2] Tổng cộng: {len(all_data)} dòng dữ liệu.")
    return all_data


def load_fallback():
    """Tải dữ liệu fallback từ file sample."""
    if not SAMPLE_FILE.exists():
        print(f"[LỖI] Không tìm thấy file fallback: {SAMPLE_FILE}")
        return None

    print(f"[FALLBACK] Đang tải dữ liệu mẫu từ: {SAMPLE_FILE}")
    results = []
    with open(SAMPLE_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            results.append({
                "symbol": row["symbol"].strip(),
                "date": row["date"].strip(),
                "open_price": float(row["open_price"]),
                "high_price": float(row["high_price"]),
                "low_price": float(row["low_price"]),
                "close_price": float(row["close_price"]),
                "volume": int(row["volume"]),
                "change_value": float(row["change_value"]),
                "change_percent": float(row["change_percent"]),
            })

    symbols_found = set(r["symbol"] for r in results)
    print(f"  Đã tải {len(results)} dòng cho {len(symbols_found)} mã: {', '.join(sorted(symbols_found))}")
    return results


def save_csv(data, output_path):
    """Lưu dữ liệu ra file CSV."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "symbol", "date", "open_price", "high_price", "low_price",
        "close_price", "volume", "change_value", "change_percent",
    ]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

    print(f"[OK] Đã lưu {len(data)} dòng -> {output_path}")


def main():
    """Hàm chính: crawl cổ phiếu hoặc dùng fallback."""
    print("=" * 55)
    print("  CRAWL STOCK — Dữ liệu giá cổ phiếu REE, MWG, FPT")
    print("=" * 55)
    print()

    # Bước 1: Thử crawl từ nguồn công khai
    data = crawl_all_symbols()

    # Bước 2: Nếu crawl thất bại, dùng fallback
    if data is None:
        print()
        print("[CẢNH BÁO] Crawl thất bại. Chuyển sang dữ liệu mẫu.")
        data = load_fallback()

    # Bước 3: Kiểm tra dữ liệu
    if data is None or len(data) == 0:
        print("[LỖI NGHIÊM TRỌNG] Không có dữ liệu nào. Dừng chương trình.")
        sys.exit(1)

    # Bước 4: Lưu file
    print()
    save_csv(data, RAW_OUTPUT)

    # Bước 5: Tóm tắt
    print()
    print("=" * 55)
    print("  TÓM TẮT")
    print("=" * 55)

    symbols = set(r["symbol"] for r in data)
    print(f"  Số mã cổ phiếu: {len(symbols)} ({', '.join(sorted(symbols))})")
    print(f"  Tổng số dòng:   {len(data)}")
    print(f"  Output file:     {RAW_OUTPUT}")
    print(f"  Columns:         symbol, date, open_price, high_price, low_price,")
    print(f"                   close_price, volume, change_value, change_percent")

    # Thống kê theo mã
    print()
    print(f"  {'Symbol':<8} {'Rows':>6} {'Date Range':<25} {'Avg Close':>10}")
    print("  " + "-" * 55)
    for sym in sorted(symbols):
        sym_rows = [r for r in data if r["symbol"] == sym]
        dates = [r["date"] for r in sym_rows]
        avg_close = sum(r["close_price"] for r in sym_rows) / len(sym_rows)
        print(f"  {sym:<8} {len(sym_rows):>6} {min(dates)} ~ {max(dates)} {avg_close:>10.2f}")

    print()


if __name__ == "__main__":
    main()
