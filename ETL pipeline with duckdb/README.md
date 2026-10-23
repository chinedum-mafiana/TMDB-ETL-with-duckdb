# 🎬 TMDB ETL Data Pipeline

A simple, idempotent ETL (Extract, Transform, Load) pipeline built in Python and DuckDB that ingests movie metadata from The Movie Database (TMDB) API, cleans and structures the records, and loads them into a high-performance local data warehouse. 

To do: dockerize and add metabase for visualization

---

## Project Architecture

```text
tmdb_project/
│
├── etl/
│   ├── extract.py      # Fetches raw data from TMDB API
│   ├── transform.py    # Cleans and makes transformations idempotent
│   └── load.py         # Manages DuckDB connection and upserts into data warehouse
│
├── df.ipynb            # testing script
├── movies_warehouse.duckdb  # Local DuckDB database file
├── main.py                  # Orchestration script
└── README.md

Tech Stack
Language: Python
Data Processing: Pandas
Data Warehouse: DuckDB 
Data Source: TMDB API 
