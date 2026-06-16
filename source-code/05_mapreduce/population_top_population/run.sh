#!/bin/bash
set -e
# run.sh - Chay MapReduce job bang Hadoop Streaming

# Xac dinh thu muc chua script hien tai de lay duong dan tuyet doi cua mapper/reducer
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=========================================================="
echo "  MAPREDUCE: POPULATION_TOP_POPULATION"
echo "=========================================================="

# Thu muc tren HDFS
INPUT_DIR="/bigdata_project/input/population_clean.csv"
OUTPUT_DIR="/bigdata_project/output/population_top_population"

if [ -z "$HADOOP_STREAMING_JAR" ]; then
    if [ -n "$HADOOP_HOME" ]; then
        HADOOP_STREAMING_JAR=$(find "$HADOOP_HOME/share/hadoop/tools/lib" -name "hadoop-streaming*.jar" | head -1)
    fi
fi

if [ -z "$HADOOP_STREAMING_JAR" ] || [ ! -f "$HADOOP_STREAMING_JAR" ]; then
    HADOOP_STREAMING_JAR=$(find /home/user01/hadoop/share/hadoop/tools/lib -name "hadoop-streaming*.jar" | head -1)
fi

if [ -z "$HADOOP_STREAMING_JAR" ] || [ ! -f "$HADOOP_STREAMING_JAR" ]; then
    echo "[FAIL] Khong tim thay Hadoop Streaming JAR."
    echo "Hay export HADOOP_STREAMING_JAR=/path/to/hadoop-streaming.jar"
    exit 1
fi

# Xoa thu muc output cu neu co
echo "[1/3] Xoa thu muc output cu tren HDFS..."
hdfs dfs -rm -r -f $OUTPUT_DIR || true

# Chay job Hadoop Streaming
echo "[2/3] Dang chay Hadoop Streaming..."
hadoop jar "$HADOOP_STREAMING_JAR" \
    -files "$SCRIPT_DIR/mapper.py,$SCRIPT_DIR/reducer.py" \
    -mapper "python3 mapper.py" \
    -reducer "python3 reducer.py" \
    -input $INPUT_DIR \
    -output $OUTPUT_DIR

# In ket qua
echo "[3/3] Ket qua Top 10 tinh thanh dong dan nhat:"
echo "----------------------------------------------------------"
hdfs dfs -cat $OUTPUT_DIR/part-00000
echo "----------------------------------------------------------"
echo "Hoan tat!"
