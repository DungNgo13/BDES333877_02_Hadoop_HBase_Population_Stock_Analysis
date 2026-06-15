================================================================================
                         PROJECT INFORMATION
================================================================================

Project Code : BDES333877_02
Project Name : Hadoop HBase Population Stock Analysis
Topic        : Applying Hadoop MapReduce and HBase to analyze Vietnam urban
               population data and infrastructure/consumer stock price movements.
Course       : Big Data Essentials
Semester     : <SEMESTER>
Instructor   : <INSTRUCTOR_NAME>

================================================================================
                         GROUP INFORMATION
================================================================================

Member 1 (Leader):
  Full Name  : <FULL_NAME>
  Student ID : <STUDENT_ID>
  Email      : <EMAIL>
  Phone      : <PHONE>
  Role       : Hadoop core, HDFS, HBase, stock MapReduce, integration

Member 2:
  Full Name  : <FULL_NAME>
  Student ID : <STUDENT_ID>
  Email      : <EMAIL>
  Phone      : <PHONE>
  Role       : Population crawler, population cleaning, population MapReduce

Member 3:
  Full Name  : <FULL_NAME>
  Student ID : <STUDENT_ID>
  Email      : <EMAIL>
  Phone      : <PHONE>
  Role       : Stock crawler, stock cleaning, visualization, Flask GUI

================================================================================
                         PROJECT DESCRIPTION
================================================================================

This project collects Vietnam's provincial population data and stock price data
(REE, MWG, FPT) from public sources, cleans and stores them in HDFS and HBase,
performs analytical MapReduce jobs, and presents results via charts and a Flask
web GUI.

================================================================================
                         TECHNOLOGIES USED
================================================================================

- Python 3.x
- Hadoop HDFS / YARN / MapReduce (Hadoop Streaming)
- HBase (via happybase / Thrift)
- pandas, matplotlib (data processing and visualization)
- Flask (web GUI)
- BeautifulSoup4 / requests (web crawling)
- Git / GitHub (version control)

================================================================================
                         FOLDER STRUCTURE
================================================================================

BDES333877_02_Hadoop_HBase_Population_Stock_Analysis/
├── readme.txt                  <- This file
├── PROJECT_DETAIL.md           <- Technical diary and documentation
├── requirements.txt            <- Python dependencies
├── .gitignore                  <- Git ignore rules
├── source-code/
│   ├── 01_crawling/            <- Web crawlers
│   ├── 02_cleaning/            <- Data cleaning and validation
│   ├── 03_hdfs/                <- HDFS shell scripts
│   ├── 04_hbase/               <- HBase create, import, query, CRUD
│   ├── 05_mapreduce/           <- Hadoop Streaming MapReduce jobs
│   ├── 06_visualization/       <- Charts (matplotlib)
│   └── 07_gui/                 <- Flask web application
├── dataset/
│   ├── raw/                    <- Raw crawled data
│   ├── clean/                  <- Cleaned data
│   └── sample/                 <- Fallback sample data
├── reports/
│   └── screenshots/            <- Screenshots for documentation
├── refs/                       <- Reference materials
└── libs/                       <- External libraries (if any)

================================================================================
                         HOW TO RUN
================================================================================

1. Install dependencies:
   pip install -r requirements.txt

2. Crawl data (or use sample fallback):
   python source-code/01_crawling/crawl_population.py
   python source-code/01_crawling/crawl_stock.py

3. Clean data:
   python source-code/02_cleaning/clean_population.py
   python source-code/02_cleaning/clean_stock.py

4. Upload to HDFS:
   bash source-code/03_hdfs/hdfs_prepare.sh
   bash source-code/03_hdfs/hdfs_upload.sh

5. Create HBase tables and import data:
   hbase shell source-code/04_hbase/hbase_create_tables.txt
   python source-code/04_hbase/hbase_put_population.py
   python source-code/04_hbase/hbase_put_stock.py

6. Run MapReduce jobs (example):
   bash source-code/05_mapreduce/stock_monthly_avg_close/run.sh

7. Generate charts:
   python source-code/06_visualization/export_all_charts.py

8. Launch GUI:
   cd source-code/07_gui
   python app.py

9. Run local checklist:
   python source-code/run_all_local_check.py

================================================================================
