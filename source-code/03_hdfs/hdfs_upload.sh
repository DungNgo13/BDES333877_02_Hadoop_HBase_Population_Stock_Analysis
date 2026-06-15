#!/bin/bash
# hdfs_upload.sh — Upload file CSV sạch lên HDFS
set -e

echo "=========================================="
echo "  HDFS UPLOAD — Upload dữ liệu sạch"
echo "=========================================="

# Đường dẫn local (tương đối từ project root)
LOCAL_POP="dataset/clean/population_clean.csv"
LOCAL_STOCK="dataset/clean/stock_clean.csv"

# Đường dẫn HDFS đích
HDFS_INPUT="/bigdata_project/input"

# Kiểm tra file population tồn tại
echo "[1/2] Upload population_clean.csv..."
if [ -f "${LOCAL_POP}" ]; then
    hdfs dfs -put -f "${LOCAL_POP}" "${HDFS_INPUT}/"
    echo "  -> Upload ${LOCAL_POP} thành công"
else
    echo "  [LỖI] Không tìm thấy file: ${LOCAL_POP}"
    echo "  Hãy chạy clean_population.py trước."
    exit 1
fi

# Kiểm tra file stock tồn tại
echo "[2/2] Upload stock_clean.csv..."
if [ -f "${LOCAL_STOCK}" ]; then
    hdfs dfs -put -f "${LOCAL_STOCK}" "${HDFS_INPUT}/"
    echo "  -> Upload ${LOCAL_STOCK} thành công"
else
    echo "  [LỖI] Không tìm thấy file: ${LOCAL_STOCK}"
    echo "  Hãy chạy clean_stock.py trước."
    exit 1
fi

echo ""
echo "=========================================="
echo "  Kiểm tra file trên HDFS"
echo "=========================================="
hdfs dfs -ls "${HDFS_INPUT}/"

echo ""
echo "HDFS UPLOAD hoàn tất."
