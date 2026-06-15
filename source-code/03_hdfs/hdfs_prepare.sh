#!/bin/bash
# hdfs_prepare.sh — Tạo cấu trúc thư mục HDFS cho dự án Big Data
set -e

echo "=========================================="
echo "  HDFS PREPARE — Tạo thư mục HDFS"
echo "=========================================="

# Thư mục gốc dự án
PROJECT_DIR="/bigdata_project"

# Tạo thư mục input (chứa dữ liệu sạch)
echo "[1/3] Tạo thư mục input..."
hdfs dfs -mkdir -p ${PROJECT_DIR}/input
echo "  -> ${PROJECT_DIR}/input OK"

# Tạo thư mục output (kết quả MapReduce)
echo "[2/3] Tạo thư mục output..."
hdfs dfs -mkdir -p ${PROJECT_DIR}/output
echo "  -> ${PROJECT_DIR}/output OK"

# Tạo thư mục backup (sao lưu dữ liệu)
echo "[3/3] Tạo thư mục backup..."
hdfs dfs -mkdir -p ${PROJECT_DIR}/backup
echo "  -> ${PROJECT_DIR}/backup OK"

echo ""
echo "=========================================="
echo "  Kiểm tra cấu trúc thư mục HDFS"
echo "=========================================="
hdfs dfs -ls -R ${PROJECT_DIR}

echo ""
echo "HDFS PREPARE hoàn tất."
