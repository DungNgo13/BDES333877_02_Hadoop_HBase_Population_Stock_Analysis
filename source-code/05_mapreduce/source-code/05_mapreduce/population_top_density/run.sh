#!/bin/bash
# run.sh - Chay MapReduce job bang Hadoop Streaming

echo "=========================================================="
echo "  MAPREDUCE: POPULATION_TOP_DENSITY"
echo "=========================================================="

# Thu muc tren HDFS
INPUT_DIR="/bigdata_project/input/population_clean.csv"
OUTPUT_DIR="/bigdata_project/output/population_top_density"

# Xoa thu muc output cu neu co
echo "[1/3] Xoa thu muc output cu tren HDFS..."
hdfs dfs -rm -r -f $OUTPUT_DIR

# Chay job Hadoop Streaming
echo "[2/3] Dang chay Hadoop Streaming..."
hadoop jar /usr/local/hadoop/share/hadoop/tools/lib/hadoop-streaming-*.jar \
    -files mapper.py,reducer.py \
    -mapper "python3 mapper.py" \
    -reducer "python3 reducer.py" \
    -input $INPUT_DIR \
    -output $OUTPUT_DIR

# In ket qua
echo "[3/3] Ket qua Top 10 tinh thanh co mat do dan so cao nhat:"
echo "----------------------------------------------------------"
hdfs dfs -cat $OUTPUT_DIR/part-00000
echo "----------------------------------------------------------"
echo "Hoan tat!"
