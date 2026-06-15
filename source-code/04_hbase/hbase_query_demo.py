"""
hbase_query_demo.py — Truy vấn dữ liệu mẫu từ bảng HBase population và stock_price.

Scan 5 dòng đầu tiên của mỗi bảng và hiển thị kết quả dễ đọc.
"""

import sys

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

# Cấu hình HBase
HBASE_HOST = "localhost"
HBASE_PORT = 9090
SCAN_LIMIT = 5


def decode_row(row_data):
    """Chuyển bytes → string cho tất cả key/value."""
    result = {}
    for key, value in row_data.items():
        k = key.decode("utf-8") if isinstance(key, bytes) else key
        v = value.decode("utf-8") if isinstance(value, bytes) else value
        result[k] = v
    return result


def scan_table(connection, table_name, limit=SCAN_LIMIT):
    """Scan và hiển thị các dòng đầu tiên của bảng."""
    # Kiểm tra bảng tồn tại
    tables = [t.decode("utf-8") for t in connection.tables()]
    if table_name not in tables:
        print(f"  [CẢNH BÁO] Bảng '{table_name}' chưa được tạo.")
        return

    table = connection.table(table_name)
    rows = list(table.scan(limit=limit))

    if not rows:
        print(f"  [THÔNG BÁO] Bảng '{table_name}' trống — chưa có dữ liệu.")
        print(f"  Hãy chạy hbase_put_*.py để import dữ liệu trước.")
        return

    print(f"  Tìm thấy dữ liệu. Hiển thị {len(rows)} dòng đầu tiên:")
    print()

    for i, (rowkey, data) in enumerate(rows, 1):
        rk = rowkey.decode("utf-8") if isinstance(rowkey, bytes) else rowkey
        decoded = decode_row(data)

        print(f"  --- Dòng {i} ---")
        print(f"  Rowkey: {rk}")
        for col, val in sorted(decoded.items()):
            print(f"    {col}: {val}")
        print()


def main():
    """Truy vấn mẫu từ HBase."""
    print("=" * 55)
    print("  HBASE QUERY DEMO — Truy vấn dữ liệu HBase")
    print("=" * 55)
    print()

    # Kết nối HBase
    print(f"Kết nối HBase tại {HBASE_HOST}:{HBASE_PORT}...")
    try:
        connection = happybase.Connection(host=HBASE_HOST, port=HBASE_PORT)
        connection.open()
        print("  -> Kết nối thành công.")
    except Exception as e:
        print(f"[LỖI] Không thể kết nối HBase: {e}")
        print("  Kiểm tra HBase và Thrift server đang chạy.")
        sys.exit(1)

    # Scan bảng population
    print()
    print("=" * 55)
    print(f"  BẢNG: population (top {SCAN_LIMIT} dòng)")
    print("=" * 55)
    scan_table(connection, "population", SCAN_LIMIT)

    # Scan bảng stock_price
    print("=" * 55)
    print(f"  BẢNG: stock_price (top {SCAN_LIMIT} dòng)")
    print("=" * 55)
    scan_table(connection, "stock_price", SCAN_LIMIT)

    # Đóng kết nối
    connection.close()
    print("Hoàn tất. Kết nối đã đóng.")


if __name__ == "__main__":
    main()
