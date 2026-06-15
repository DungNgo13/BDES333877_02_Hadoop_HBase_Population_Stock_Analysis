# PROJECT DETAIL — Technical Diary

**Project:** BDES333877_02 — Hadoop HBase Population Stock Analysis  
**Topic:** Applying Hadoop MapReduce and HBase to analyze Vietnam urban population data and infrastructure/consumer stock price movements.

---

## 1. Project Overview

This project demonstrates a complete Big Data pipeline:

1. **Crawl** population and stock data from public Vietnamese sources.
2. **Clean** the raw data into standardized CSVs.
3. **Store** data in HDFS and HBase.
4. **Analyze** data using Hadoop Streaming MapReduce jobs.
5. **Visualize** results with matplotlib charts.
6. **Present** everything through a Flask web GUI.

---

## 2. Goals

- Collect Vietnam provincial population statistics and stock price history (REE, MWG, FPT).
- Demonstrate HDFS file management (upload, check, backup).
- Demonstrate HBase CRUD operations.
- Run at least 6 MapReduce analytical jobs.
- Generate at least 5 charts of at least 3 different types.
- Build a simple Flask GUI to browse data and charts.

---

## 3. Scope

| Area | Included | Excluded |
|------|----------|----------|
| Data sources | Population (web), Stock prices (web/API) | Real-time streaming |
| Storage | HDFS, HBase | MySQL, MongoDB |
| Processing | Hadoop Streaming MapReduce | Spark, Kafka, Airflow |
| Visualization | matplotlib | seaborn, plotly |
| Frontend | Flask (server-side) | React, Vue, complex SPA |
| ML/AI | Not included | Prediction models |

---

## 4. Technologies

| Component | Technology |
|-----------|------------|
| Language | Python 3.x |
| Crawling | requests, BeautifulSoup4 |
| Cleaning | pandas |
| Distributed Storage | Hadoop HDFS |
| NoSQL Database | HBase (via happybase / Thrift) |
| Batch Processing | Hadoop Streaming MapReduce |
| Visualization | matplotlib |
| Web GUI | Flask |
| Version Control | Git / GitHub |

---

## 5. Pipeline Architecture

```text
[Web Sources] 
    │
    ▼
[01_crawling] ─── crawl_population.py ──► dataset/raw/population_raw.csv
              ─── crawl_stock.py      ──► dataset/raw/stock_raw.csv
    │
    ▼
[02_cleaning] ─── clean_population.py ──► dataset/clean/population_clean.csv
              ─── clean_stock.py      ──► dataset/clean/stock_clean.csv
    │
    ▼
[03_hdfs]     ─── hdfs_upload.sh      ──► /bigdata_project/input/
    │
    ├──► [04_hbase]  ─── hbase_put_*.py ──► HBase tables
    │
    ├──► [05_mapreduce] ─── 6 MR jobs  ──► /bigdata_project/output/
    │
    ▼
[06_visualization] ─── chart_*.py     ──► reports/screenshots/*.png
    │
    ▼
[07_gui]       ─── app.py            ──► Flask web application
```

---

## 6. Work Assignment

| Role | Member | Responsibilities |
|------|--------|-----------------|
| Leader | Member 1 | Hadoop core, HDFS scripts, HBase scripts, stock MapReduce, integration, PROJECT_DETAIL |
| Member 2 | Member 2 | Population crawler, population cleaning, population MapReduce |
| Member 3 | Member 3 | Stock crawler, stock cleaning, visualization, Flask GUI |

---

## 7. Deployment Environment

| Component | Version / Notes |
|-----------|----------------|
| OS | Ubuntu / WSL / VM with Hadoop |
| Java | JDK 8 or 11 |
| Hadoop | 3.x (HDFS + YARN) |
| HBase | 2.x with Thrift server |
| Python | 3.8+ |

---

## 8. Data Sources

### 8.1 Population Data
- **Source:** Vietnamese government statistics / Wikipedia
- **Format:** HTML table → CSV
- **Columns:** `province, population, area, density, region`

### 8.2 Stock Price Data
- **Source:** Public stock market APIs / websites
- **Symbols:** REE, MWG, FPT
- **Format:** CSV
- **Columns:** `symbol, date, open_price, high_price, low_price, close_price, volume, change_value, change_percent`

---

## 9. Data Collection (01_crawling)

| Item | Detail |
|------|--------|
| Date | 2026-06-15 |
| Role | Member 2 (population), Member 3 (stock) |
| Source files | `source-code/01_crawling/crawl_population.py`, `crawl_stock.py` |
| Input | Web sources |
| Output | `dataset/raw/population_raw.csv`, `dataset/raw/stock_raw.csv` |

### 9.1 Population Crawler (`crawl_population.py`)

| Item | Detail |
|------|--------|
| Source URL | `https://en.wikipedia.org/wiki/Provinces_of_Vietnam` |
| Method | requests + BeautifulSoup4 (HTML table parsing) |
| Fallback | `dataset/sample/population_sample.csv` |
| Output | `dataset/raw/population_raw.csv` |
| Columns | `province, population, area, density, region` |

**Features:**
- Parses the first wikitable with Province/Population/Area columns
- Handles rowspan-merged Region column
- Strips Vietnamese diacritics from province names (e.g., Cao Bằng → Cao Bang)
- Removes "province" / "city" suffixes
- Falls back to sample data if crawl fails (network error, page structure change)
- Prints clear error messages and summary
- Windows-compatible UTF-8 console output

**Test command:**
```bash
python source-code/01_crawling/crawl_population.py
```

**Test result:** 34 provinces crawled successfully from Wikipedia.

### 9.2 Stock Crawler (`crawl_stock.py`)

| Item | Detail |
|------|--------|
| Date | 2026-06-15 |
| Role | Member 3 |
| Source APIs | VNDirect API (primary), CafeF (secondary) |
| Fallback | `dataset/sample/stock_sample.csv` |
| Output | `dataset/raw/stock_raw.csv` |
| Symbols | REE, MWG, FPT |
| Columns | `symbol, date, open_price, high_price, low_price, close_price, volume, change_value, change_percent` |

**Features:**
- Tries VNDirect API first (`finfo-api.vndirect.com.vn/v4/stock_prices`)
- Falls back to CafeF HTML scraping if VNDirect fails
- Falls back to sample data if both sources fail
- Crawls 1 year of daily data per symbol
- Computes `change_value` and `change_percent` if not provided by API
- Sorts output by symbol + date
- Prints per-symbol statistics summary
- Windows-compatible UTF-8 console output

**Test command:**
```bash
python source-code/01_crawling/crawl_stock.py
```

**Test result:** Fallback to sample data — 36 rows (12 per symbol) for REE, MWG, FPT.

| Screenshot | — |
| Git commit | `feat: add stock crawler with vndirect cafef and fallback` |

---

## 10. Data Cleaning (02_cleaning)

| Item | Detail |
|------|--------|
| Date | — |
| Role | Member 2 (population), Member 3 (stock) |
| Source files | `source-code/02_cleaning/clean_population.py`, `clean_stock.py` |
| Input | `dataset/raw/*.csv` |
| Output | `dataset/clean/population_clean.csv`, `dataset/clean/stock_clean.csv` |
| Validation | `test_population_cleaning.py`, `test_stock_cleaning.py` |
| Command | `python source-code/02_cleaning/clean_population.py` |
| Result | — |
| Screenshot | — |
| Git commit | — |

---

## 11. Sample Datasets

| Item | Detail |
|------|--------|
| Date | 2026-06-15 |
| Role | Leader |
| Files | `dataset/sample/population_sample.csv`, `dataset/sample/stock_sample.csv` |
| Purpose | Fallback data for local testing without crawling |

### 11.1 population_sample.csv
- **Rows:** 20 provinces/cities
- **Columns:** `province, population, area, density, region`
- **Regions covered:** Red River Delta, Southeast, South Central Coast, North Central Coast, Mekong River Delta, Central Highlands, Northern Midlands
- **Notes:** Approximate values based on public statistics. Suitable for MapReduce top-population/top-density jobs and all population charts.

### 11.2 stock_sample.csv
- **Rows:** 36 (12 per symbol)
- **Symbols:** REE, MWG, FPT
- **Columns:** `symbol, date, open_price, high_price, low_price, close_price, volume, change_value, change_percent`
- **Date range:** 2024-01 to 2024-04
- **Movement types:** UP (positive change_value), DOWN (negative), FLAT (zero) — all three present for each symbol
- **Notes:** Covers multiple months for monthly-avg-close job, single year for yearly-volume/extreme-price jobs, and mixed movements for movement-ratio job.

### Verification
```bash
python -c "import pandas as pd; df=pd.read_csv('dataset/sample/population_sample.csv'); print('population_sample:', df.shape); print(df.head())"
python -c "import pandas as pd; df=pd.read_csv('dataset/sample/stock_sample.csv'); print('stock_sample:', df.shape); print(df.head())"
```

| Git commit | `chore: add sample datasets for local testing` |

---

## 12. HDFS (03_hdfs)

| Item | Detail |
|------|--------|
| Date | 2026-06-15 |
| Role | Leader |
| Source files | `hdfs_prepare.sh`, `hdfs_upload.sh`, `hdfs_check.sh`, `hdfs_backup.sh` |
| HDFS Layout | `/bigdata_project/input/`, `/bigdata_project/output/`, `/bigdata_project/backup/` |

### 12.1 Script Details

| Script | Purpose | Key Commands |
|--------|---------|-------------|
| `hdfs_prepare.sh` | Create HDFS directory structure | `hdfs dfs -mkdir -p` |
| `hdfs_upload.sh` | Upload clean CSVs to HDFS input | `hdfs dfs -put -f` |
| `hdfs_check.sh` | List files and preview first 5 lines | `hdfs dfs -ls`, `hdfs dfs -cat \| head` |
| `hdfs_backup.sh` | Backup input to timestamped folder | `hdfs dfs -cp` |

### 12.2 HDFS Directory Layout

```text
/bigdata_project/
├── input/
│   ├── population_clean.csv
│   └── stock_clean.csv
├── output/
│   ├── population_top_population/
│   ├── population_top_density/
│   ├── stock_monthly_avg_close/
│   ├── stock_yearly_volume/
│   ├── stock_movement_ratio/
│   └── stock_yearly_extreme_price/
└── backup/
    └── YYYYMMDD_HHMMSS/
        ├── population_clean.csv
        └── stock_clean.csv
```

### 12.3 Test Commands

```bash
bash source-code/03_hdfs/hdfs_prepare.sh
bash source-code/03_hdfs/hdfs_upload.sh
bash source-code/03_hdfs/hdfs_check.sh
bash source-code/03_hdfs/hdfs_backup.sh
```

### 12.4 Script Features
- All scripts use `#!/bin/bash` and `set -e` (fail-fast)
- Vietnamese comments for readability
- No hard-coded personal paths
- `hdfs_upload.sh` checks local file existence before upload
- `hdfs_backup.sh` creates timestamped backup folders

| Screenshot | — |
| Git commit | `feat: add hdfs prepare upload check and backup scripts` |

---

## 13. HBase Schema (04_hbase)

### 13.1 Table: `population`
- **Rowkey:** province name (e.g., `Ha Noi`)
- **Column family:** `info`
- **Columns:** `info:population`, `info:area`, `info:density`, `info:region`

### 13.2 Table: `stock_price`
- **Rowkey:** `symbol_date` (e.g., `REE_2024-01-15`)
- **Column family:** `info`
- **Columns:** `info:symbol`, `info:date`, `info:open_price`, `info:high_price`, `info:low_price`, `info:close_price`, `info:volume`, `info:change_value`, `info:change_percent`

### 13.3 Creation Script

| Item | Detail |
|------|--------|
| Date | 2026-06-15 |
| Role | Leader |
| Source file | `source-code/04_hbase/hbase_create_tables.txt` |
| Command | `hbase shell source-code/04_hbase/hbase_create_tables.txt` |

**Script behavior:**
1. Disable and drop `population` if it exists
2. Create `population` with column family `info`
3. Disable and drop `stock_price` if it exists
4. Create `stock_price` with column family `info`
5. Run `list` to verify both tables exist
6. Exit HBase shell

> **Note:** The script is idempotent — safe to run multiple times. The `disable`/`drop` commands will show errors on first run (table doesn't exist yet), but this is expected and does not affect table creation.

| Screenshot | — |
| Git commit | `feat: add hbase table creation script` |

---

## 14. HBase CRUD / Query (04_hbase)

| Item | Detail |
|------|--------|
| Date | — |
| Role | Leader |
| Source files | `hbase_query_demo.py`, `hbase_crud_demo.py` |
| Command | `python source-code/04_hbase/hbase_query_demo.py` |
| Result | — |
| Screenshot | — |
| Git commit | — |

---

## 15. MapReduce Jobs (05_mapreduce)

| # | Job Name | Input | Output Key | Description |
|---|----------|-------|------------|-------------|
| 1 | `population_top_population` | population_clean.csv | province | Top provinces by population |
| 2 | `population_top_density` | population_clean.csv | province | Top provinces by density |
| 3 | `stock_monthly_avg_close` | stock_clean.csv | symbol_yyyy-mm | Monthly avg close price |
| 4 | `stock_yearly_volume` | stock_clean.csv | symbol_year | Yearly total trading volume |
| 5 | `stock_movement_ratio` | stock_clean.csv | symbol | UP/DOWN/FLAT ratio |
| 6 | `stock_yearly_extreme_price` | stock_clean.csv | symbol_year | Max/min close with dates |

Each job folder contains: `mapper.py`, `reducer.py`, `run.sh`.

| Item | Detail |
|------|--------|
| Date | — |
| Role | Leader (stock jobs), Member 2 (population jobs) |
| Command | `bash source-code/05_mapreduce/<job_name>/run.sh` |
| Result | — |
| Screenshot | — |
| Git commit | — |

---

## 16. Backup / Restore (03_hdfs)

| Item | Detail |
|------|--------|
| Date | 2026-06-15 |
| Role | Leader |
| Script | `hdfs_backup.sh` |
| Backup path | `/bigdata_project/backup/YYYYMMDD_HHMMSS/` |
| Command | `bash source-code/03_hdfs/hdfs_backup.sh` |

### 16.1 Backup Strategy
- Each backup creates a new timestamped subfolder: `/bigdata_project/backup/YYYYMMDD_HHMMSS/`
- Both `population_clean.csv` and `stock_clean.csv` are copied from HDFS input (not local)
- Uses `hdfs dfs -cp` for HDFS-to-HDFS copy (no network transfer)
- Timestamp format: `date +"%Y%m%d_%H%M%S"` ensures unique backup names
- Backup path is printed at the end for logging

| Result | — |
| Git commit | `feat: add hdfs prepare upload check and backup scripts` |

---

## 17. Visualization (06_visualization)

| # | Chart | Type | File |
|---|-------|------|------|
| 1 | Top 10 provinces by population | Bar chart | `chart_population.py` |
| 2 | Top 10 provinces by density | Bar chart | `chart_population.py` |
| 3 | Area vs population scatter | Scatter | `chart_population.py` |
| 4 | Monthly avg close price by symbol | Line chart | `chart_stock.py` |
| 5 | Yearly trading volume by symbol | Bar chart | `chart_stock.py` |
| 6 | UP/DOWN/FLAT movement ratio | Pie chart | `chart_stock.py` |

| Item | Detail |
|------|--------|
| Date | — |
| Role | Member 3 |
| Output | `reports/screenshots/*.png` |
| Command | `python source-code/06_visualization/export_all_charts.py` |
| Result | — |
| Screenshot | — |
| Git commit | — |

---

## 18. GUI (07_gui)

| Route | Description |
|-------|-------------|
| `/` | Home page |
| `/population` | Population data table |
| `/stocks` | Stock data table |
| `/charts` | Display generated charts |
| `/search` | Search/filter data |

| Item | Detail |
|------|--------|
| Date | — |
| Role | Member 3 |
| Source | `source-code/07_gui/app.py` |
| Command | `cd source-code/07_gui && python app.py` |
| Result | — |
| Screenshot | — |
| Git commit | — |

---

## 19. GitHub Workflow

| Branch | Owner | Scope |
|--------|-------|-------|
| `feature/hadoop-core` | Leader | HDFS, HBase, stock MR, integration |
| `feature/population-pipeline` | Member 2 | Population crawl, clean, MR |
| `feature/stock-dashboard` | Member 3 | Stock crawl, clean, viz, GUI |

Commit format: conventional commits, one commit per task.

---

## 20. GitHub Log

| Date | Author | Branch | Commit Message | Files |
|------|--------|--------|----------------|-------|
| — | Leader | main | `init: create big data project structure` | readme.txt, PROJECT_DETAIL.md, requirements.txt, .gitignore, all folders |

---

## 21. Screenshot Checklist

| # | Screenshot | Status |
|---|-----------|--------|
| 1 | Folder structure | ☐ |
| 2 | Raw data sample | ☐ |
| 3 | Clean data sample | ☐ |
| 4 | HDFS file listing | ☐ |
| 5 | HBase table scan | ☐ |
| 6 | HBase CRUD demo | ☐ |
| 7 | MapReduce job output (×6) | ☐ |
| 8 | Charts (×6) | ☐ |
| 9 | Flask GUI pages | ☐ |
| 10 | GitHub commit history | ☐ |

---

## 22. Final Checklist

- [ ] readme.txt follows submission format.
- [ ] PROJECT_DETAIL.md documents the workflow.
- [ ] Raw and clean datasets exist.
- [ ] HDFS scripts exist and can run.
- [ ] HBase create/import/query/CRUD scripts exist.
- [ ] Six MapReduce jobs exist.
- [ ] At least 5 charts of at least 3 types are generated.
- [ ] Flask GUI displays data and charts.
- [ ] Validation scripts pass.
- [ ] Folder structure matches required format.
- [ ] Each logical role has multiple small commits.
- [ ] Each student can explain their assigned files.

Git operation note:
Because two members were not familiar with Git CLI, the leader supported commit/push operations after each member reviewed the assigned files. Technical ownership remains aligned with the task assignment table.
