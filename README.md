# 🎬 TMDB ETL Data Pipeline & Analytics Dashboard

A simple, idempotent ETL (Extract, Transform, Load) pipeline built in Python and DuckDB that ingests movie metadata from The Movie Database (TMDB) API, cleans and structures the records into a star schema, and loads them into a high-performance local data warehouse. 

It also includes an **interactive Streamlit web application** for browsing tables, inspecting ERD schema architecture, and analyzing movie performance metrics visually.

---

## Project Architecture

```text
tmdb-etl-with-duckdb/
│
├── etl/
│   ├── extract_and_transform.py        # Fetches raw data from TMDB API, cleans and makes transformations idempotent
│   └── load.py                         # Manages DuckDB connection and upserts into data warehouse
│
├── streamlit_visualization.py          # Streamlit interactive dashboard & visualization app
├── movies_warehouse.duckdb             # Local DuckDB database file
├── main.py                             # Pipeline orchestration script
└── README.md
```

Tech Stack
Language: Python

Data Processing: Pandas

Data Warehouse: DuckDB

Visualization & UI: Streamlit & Plotly

Data Source: TMDB API

Dependencies: requests, pandas, duckdb, ratelimit, load_dotenv

# 📊 Visualizing the Database
Before running main.py, you'll need an API key from TMDB. However, you can explore the db through the streamlit dashboard. You can instantly explore the schema, view database statistics, and interact with financial/rating charts using the built-in Streamlit Dashboard.

## Dependencies for visualization: 
```
pip install duckdb streamlit plotly
```

How to run the dashboard (bash):

```Bash
streamlit run streamlit_visualization.py
```

# What the dashboard includes:

Schema Architecture: Interactive Mermaid.js Entity-Relationship Diagram (ERD) mapping all table structures (dim_movie, dim_genre, dim_date, dim_production_company, and fact_movie).

## Table Browser: 

Inspect table rows, counts, and schemas directly from DuckDB.

## Visual Analytics:

Database Size Distribution: Table record counts.

Genre Breakdowns & Filtering: Pie charts and dynamic multi-select genre filters.

Budget vs. Revenue (Log-Log Scale): Interactive financial scatter plots by genre.

Top Production Companies & Rated Movies: Bar charts highlighting top-performing studios and user ratings.

## Custom SQL Playground: 

Run arbitrary SQL joins and queries directly against the local warehouse from the UI.


#🛠️ Roadmap / To-Do
[ ] Add TV Show data ingestion.

[ ] Containerize the workflow using Docker.
