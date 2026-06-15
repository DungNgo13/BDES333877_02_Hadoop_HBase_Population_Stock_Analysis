#!/bin/bash
# hdfs_backup.sh — Sao lưu dữ liệu input trên HDFS theo timestamp
set -e

echo "=========================================="
echo "  HDFS BACKUP — Sao lưu dữ liệu"
echo "=========================================="

HDFS_INPUT="/bigdata_project/input"
HDFS_BACKUP="/bigdata_project/backup"

# Tạo tên thư mục backup theo thời gian: YYYYMMDD_HHMMSS
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="${HDFS_BACKUP}/${TIMESTAMP}"

# Tạo thư mục backup mới
echo "[1/3] Tạo thư mục backup: ${BACKUP_DIR}"
hdfs dfs -mkdir -p "${BACKUP_DIR}"

# Copy file population vào backup
echo "[2/3] Sao lưu population_clean.csv..."
hdfs dfs -cp "${HDFS_INPUT}/population_clean.csv" "${BACKUP_DIR}/"
echo "  -> OK"

# Copy file stock vào backup
echo "[3/3] Sao lưu stock_clean.csv..."
hdfs dfs -cp "${HDFS_INPUT}/stock_clean.csv" "${BACKUP_DIR}/"
echo "  -> OK"

echo ""
echo "=========================================="
echo "  Kiểm tra thư mục backup"
echo "=========================================="
hdfs dfs -ls "${BACKUP_DIR}/"

echo ""
echo "Backup path: ${BACKUP_DIR}"
echo "HDFS BACKUP hoàn tất."
