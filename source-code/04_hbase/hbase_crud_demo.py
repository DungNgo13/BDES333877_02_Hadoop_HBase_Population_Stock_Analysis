"""
hbase_crud_demo.py — Demo CRUD (Create, Read, Update, Delete) trên bảng HBase 'population'.

Các bước:
1. CREATE: put TEST_PROVINCE vào bảng population
2. READ: get TEST_PROVINCE
3. UPDATE: cập nhật info:density
4. READ AGAIN: đọc lại sau update
5. DELETE: xóa TEST_PROVINCE
6. VERIFY DELETE: xác nhận đã xóa
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
TABLE_NAME = "population"

# Dữ liệu test
TEST_ROWKEY = "TEST_PROVINCE"
TEST_DATA = {
    "info:population": "999999",
    "info:area": "1234.5",
    "info:density": "810",
    "info:region": "Test Region",
}
UPDATED_DENSITY = "1500"


def decode_row(row_data):
    """Chuyển bytes → string cho tất cả key/value."""
    result = {}
    for key, value in row_data.items():
        k = key.decode("utf-8") if isinstance(key, bytes) else key
        v = value.decode("utf-8") if isinstance(value, bytes) else value
        result[k] = v
    return result


def print_row(rowkey, data):
    """Hiển thị dữ liệu 1 dòng."""
    if data:
        decoded = decode_row(data)
        print(f"  Rowkey: {rowkey}")
        for col, val in sorted(decoded.items()):
            print(f"    {col}: {val}")
    else:
        print(f"  Rowkey: {rowkey} — KHÔNG TÌM THẤY (trống)")


def main():
    """Demo CRUD trên bảng population."""
    print("=" * 55)
    print("  HBASE CRUD DEMO — Create/Read/Update/Delete")
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

    # Kiểm tra bảng tồn tại
    tables = [t.decode("utf-8") for t in connection.tables()]
    if TABLE_NAME not in tables:
        print(f"[LỖI] Bảng '{TABLE_NAME}' chưa được tạo.")
        print("  Chạy: hbase shell source-code/04_hbase/hbase_create_tables.txt")
        connection.close()
        sys.exit(1)

    table = connection.table(TABLE_NAME)

    # ============================================================
    # Bước 1: CREATE — Tạo dòng mới
    # ============================================================
    print()
    print("-" * 55)
    print("  [1/6] CREATE — Tạo dòng TEST_PROVINCE")
    print("-" * 55)
    try:
        table.put(TEST_ROWKEY.encode("utf-8"), TEST_DATA)
        print(f"  -> Đã tạo rowkey '{TEST_ROWKEY}' với dữ liệu:")
        for col, val in sorted(TEST_DATA.items()):
            print(f"    {col}: {val}")
    except Exception as e:
        print(f"  [LỖI] Không thể tạo dòng: {e}")
        connection.close()
        sys.exit(1)

    # ============================================================
    # Bước 2: READ — Đọc dòng vừa tạo
    # ============================================================
    print()
    print("-" * 55)
    print("  [2/6] READ — Đọc TEST_PROVINCE")
    print("-" * 55)
    try:
        data = table.row(TEST_ROWKEY.encode("utf-8"))
        print_row(TEST_ROWKEY, data)
    except Exception as e:
        print(f"  [LỖI] Không thể đọc dòng: {e}")

    # ============================================================
    # Bước 3: UPDATE — Cập nhật density
    # ============================================================
    print()
    print("-" * 55)
    print(f"  [3/6] UPDATE — Cập nhật info:density = {UPDATED_DENSITY}")
    print("-" * 55)
    try:
        table.put(TEST_ROWKEY.encode("utf-8"), {
            "info:density": UPDATED_DENSITY,
        })
        print(f"  -> Đã cập nhật info:density thành {UPDATED_DENSITY}")
    except Exception as e:
        print(f"  [LỖI] Không thể cập nhật: {e}")

    # ============================================================
    # Bước 4: READ AGAIN — Đọc lại sau update
    # ============================================================
    print()
    print("-" * 55)
    print("  [4/6] READ AGAIN — Đọc lại sau update")
    print("-" * 55)
    try:
        data = table.row(TEST_ROWKEY.encode("utf-8"))
        print_row(TEST_ROWKEY, data)
        # Kiểm tra giá trị mới
        decoded = decode_row(data)
        new_density = decoded.get("info:density", "")
        if new_density == UPDATED_DENSITY:
            print(f"  -> [OK] info:density đã được cập nhật đúng: {new_density}")
        else:
            print(f"  -> [CẢNH BÁO] info:density = {new_density}, mong đợi {UPDATED_DENSITY}")
    except Exception as e:
        print(f"  [LỖI] Không thể đọc dòng: {e}")

    # ============================================================
    # Bước 5: DELETE — Xóa dòng test
    # ============================================================
    print()
    print("-" * 55)
    print("  [5/6] DELETE — Xóa TEST_PROVINCE")
    print("-" * 55)
    try:
        table.delete(TEST_ROWKEY.encode("utf-8"))
        print(f"  -> Đã xóa rowkey '{TEST_ROWKEY}'")
    except Exception as e:
        print(f"  [LỖI] Không thể xóa: {e}")

    # ============================================================
    # Bước 6: VERIFY DELETE — Xác nhận đã xóa
    # ============================================================
    print()
    print("-" * 55)
    print("  [6/6] VERIFY DELETE — Xác nhận xóa thành công")
    print("-" * 55)
    try:
        data = table.row(TEST_ROWKEY.encode("utf-8"))
        if not data:
            print(f"  -> [OK] Rowkey '{TEST_ROWKEY}' đã bị xóa thành công.")
        else:
            print(f"  -> [CẢNH BÁO] Rowkey '{TEST_ROWKEY}' vẫn còn tồn tại!")
            print_row(TEST_ROWKEY, data)
    except Exception as e:
        print(f"  [LỖI] Không thể xác nhận xóa: {e}")

    # Đóng kết nối
    connection.close()

    print()
    print("=" * 55)
    print("  CRUD DEMO hoàn tất.")
    print("=" * 55)
    print()


if __name__ == "__main__":
    main()
