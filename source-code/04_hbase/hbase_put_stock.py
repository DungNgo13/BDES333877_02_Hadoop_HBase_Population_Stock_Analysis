"""
hbase_put_stock.py — Import dữ liệu giá cổ phiếu từ CSV vào bảng HBase 'stock_price'.

Input:  dataset/clean/stock_clean.csv
Table:  stock_price
Rowkey: symbol_date (ví dụ: REE_2024-01-15)
Column family: info
Columns: info:symbol, info:date, info:open_price, info:high_price,
         info:low_price, info:close_price, info:volume,
         info:change_value, info:change_percent
"""

import csv
import sys
from pathlib import Path

# Đảm bảo console Windows hiển thị được tiếng Việt
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

try:
    import happybase
except ImportError:
    print("[LỖI] Thiếu thư viện happybase.")
    print("Chạy: pip install happybase")
    sys.exit(1)

# Đường dẫn tương đối từ project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CLEAN_FILE = PROJECT_ROOT / "dataset" / "clean" / "stock_clean.csv"

# Cấu hình HBase
HBASE_HOST = "localhost"
HBASE_PORT = 9090
TABLE_NAME = "stock_price"
COLUMN_FAMILY = "info"

# Các cột cần import
STOCK_COLUMNS = [
    "symbol", "date", "open_price", "high_price", "low_price",
    "close_price", "volume", "change_value", "change_percent",
]


def main():
    """Import dữ liệu cổ phiếu vào HBase."""
    print("=" * 55)
    print("  HBASE PUT STOCK — Import cổ phiếu vào HBase")
    print("=" * 55)
    print()

    # Bước 1: Kiểm tra file CSV tồn tại
    print(f"[1/3] Kiểm tra file: {CLEAN_FILE}")
    if not CLEAN_FILE.exists():
        print(f"[LỖI] Không tìm thấy file: {CLEAN_FILE}")
        print("  Hãy chạy clean_stock.py trước.")
        sys.exit(1)
    print("  -> File tồn tại.")

    # Bước 2: Kết nối HBase
    print(f"\n[2/3] Kết nối HBase tại {HBASE_HOST}:{HBASE_PORT}...")
    try:
        connection = happybase.Connection(host=HBASE_HOST, port=HBASE_PORT)
        connection.open()
        print("  -> Kết nối thành công.")
    except Exception as e:
        print(f"[LỖI] Không thể kết nối HBase: {e}")
        print("  Kiểm tra HBase và Thrift server đang chạy.")
        sys.exit(1)

    # Kiểm tra bảng tồn tại
    tables = [t.decode("utf-8") for t in connection.tables()]
    if TABLE_NAME not in tables:
        print(f"[LỖI] Bảng '{TABLE_NAME}' chưa được tạo.")
        print("  Chạy: hbase shell source-code/04_hbase/hbase_create_tables.txt")
        connection.close()
        sys.exit(1)

    table = connection.table(TABLE_NAME)

    # Bước 3: Đọc CSV và import từng dòng
    print(f"\n[3/3] Import dữ liệu vào bảng '{TABLE_NAME}'...")
    row_count = 0
    error_count = 0
    symbols_count = {}

    with open(CLEAN_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                # Tạo rowkey = symbol_date
                symbol = row["symbol"].strip()
                date = row["date"].strip()
                if not symbol or not date:
                    error_count += 1
                    continue

                rowkey = f"{symbol}_{date}"

                # Dữ liệu cột — tất cả giá trị lưu dạng string trong HBase
                data = {}
                for col in STOCK_COLUMNS:
                    value = str(row.get(col, "")).strip()
                    data[f"{COLUMN_FAMILY}:{col}"] = value

                # Ghi vào HBase
                table.put(rowkey.encode("utf-8"), data)
                row_count += 1

                # Đếm theo mã
                symbols_count[symbol] = symbols_count.get(symbol, 0) + 1

            except KeyError as e:
                print(f"  [CẢNH BÁO] Thiếu cột {e} ở dòng {row_count + error_count + 1}")
                error_count += 1
            except Exception as e:
                print(f"  [LỖI] Dòng {row_count + error_count + 1}: {e}")
                error_count += 1

    # Đóng kết nối
    connection.close()

    # Tóm tắt
    print()
    print("=" * 55)
    print("  TÓM TẮT")
    print("=" * 55)
    print(f"  Bảng:          {TABLE_NAME}")
    print(f"  Rowkey:        symbol_date (ví dụ: REE_2024-01-15)")
    print(f"  Column family: {COLUMN_FAMILY}")
    print(f"  Rows imported: {row_count}")
    if error_count > 0:
        print(f"  Rows lỗi:     {error_count}")
    print(f"  Input file:    {CLEAN_FILE}")

    # Thống kê theo mã
    if symbols_count:
        print()
        print("  Theo mã cổ phiếu:")
        for sym in sorted(symbols_count):
            print(f"    {sym}: {symbols_count[sym]} dòng")

    print()


if __name__ == "__main__":
    main()
