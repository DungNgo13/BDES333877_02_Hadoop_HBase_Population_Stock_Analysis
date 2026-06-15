#!/bin/bash
# hdfs_check.sh — Kiểm tra dữ liệu đã upload lên HDFS
set -e

echo "=========================================="
echo "  HDFS CHECK — Kiểm tra dữ liệu HDFS"
echo "=========================================="

HDFS_INPUT="/bigdata_project/input"

# Liệt kê file trong thư mục input
echo "[1/3] Danh sách file trong ${HDFS_INPUT}:"
echo "------------------------------------------"
hdfs dfs -ls "${HDFS_INPUT}/"

# In 5 dòng đầu của population_clean.csv
echo ""
echo "[2/3] 5 dòng đầu của population_clean.csv:"
echo "------------------------------------------"
hdfs dfs -cat "${HDFS_INPUT}/population_clean.csv" | head -n 5

# In 5 dòng đầu của stock_clean.csv
echo ""
echo "[3/3] 5 dòng đầu của stock_clean.csv:"
echo "------------------------------------------"
hdfs dfs -cat "${HDFS_INPUT}/stock_clean.csv" | head -n 5

echo ""
echo "HDFS CHECK hoàn tất."
