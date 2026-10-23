import pandas as pd
import duckdb
from etl.transform import transform_movie_details

dw_name = "movies_warehouse.duckdb"

def create_db(dw_name):
    with duckdb.connect(dw_name) as con: 
        print(f"Creating DW: {dw_name}")
        con.execute("""
            CREATE TABLE IF NOT EXISTS dim_date (
                date_id INTEGER PRIMARY KEY,
                full_date DATE,
                year INTEGER,
                quarter INTEGER,
                month INTEGER, 
                month_name VARCHAR,
                day_of_week VARCHAR,
                is_weekend BOOLEAN
            );

            CREATE TABLE IF NOT EXISTS dim_genre (
                genre_id INTEGER PRIMARY KEY,
                genre_name VARCHAR
            );

            CREATE TABLE IF NOT EXISTS dim_movie (
                movie_id INTEGER PRIMARY KEY,
                title VARCHAR,
                overview TEXT,
                tagline TEXT,
                original_language VARCHAR,
                status VARCHAR,
                poster_path VARCHAR,
                production_company_ids INTEGER[],
                genre_ids INTEGER[] 
            );

            CREATE TABLE IF NOT EXISTS fact_movie (
                movie_id INTEGER PRIMARY KEY,
                release_date_id INTEGER,
                runtime INTEGER, 
                vote_average DECIMAL(3,1),
                vote_count INTEGER,
                popularity DECIMAL(10,3),
                budget INTEGER,
                revenue BIGINT
                
            );

            CREATE TABLE IF NOT EXISTS dim_production_company (
                production_company_id INTEGER PRIMARY KEY,
                production_company_name VARCHAR
            );
            """
            
)
        print("DW created")

def load_movie_details():
    """
    Loading the transformed movie details into a DuckDB database
    """
    create_db(dw_name)
    print(f'Inserting data into datawarehouse: {dw_name}')

    movie_details_df, dim_genre_df, dim_prod_company_df = transform_movie_details()

    
    with duckdb.connect(dw_name) as con:
        con.execute("""
            INSERT OR REPLACE INTO dim_genre (genre_id, genre_name)
            SELECT
                genre_id::INTEGER,
                genre_name::VARCHAR
            FROM dim_genre_df;

            
            INSERT OR REPLACE INTO dim_production_company (production_company_id, production_company_name)
            SELECT         
                production_company_id::INTEGER,
                production_company_name::VARCHAR
            FROM dim_prod_company_df;

            INSERT OR REPLACE INTO dim_movie(movie_id, title, overview, tagline, original_language, status, poster_path, production_company_ids, genre_ids)
            SELECT 
                movie_id::INTEGER,
                title::VARCHAR,
                overview::TEXT,
                tagline::TEXT,
                original_language::VARCHAR,
                status::VARCHAR,
                poster_path::VARCHAR,
                production_company_ids::INTEGER[],
                genre_ids::INTEGER[]
            FROM movie_details_df;

            
            INSERT OR REPLACE INTO fact_movie(movie_id, release_date_id, runtime, vote_average, vote_count, popularity, budget, revenue)
            SELECT 
                movie_id::INTEGER,
                release_date_id::INTEGER,
                runtime::INTEGER,
                vote_average::DECIMAL(3,1) as vote_average,
                vote_count::INTEGER as vote_count,
                popularity::DECIMAL(10,3) as popularity,
                budget::INTEGER as budget,
                revenue::BIGINT as revenue
            FROM movie_details_df;


            INSERT OR REPLACE INTO dim_date(date_id, full_date, year, quarter, month, month_name, day_of_week, is_weekend)
            SELECT 
                release_date_id::INTEGER as date_id,
                release_date::DATE as full_date,
                year(release_date::DATE) as year,
                quarter(release_date::DATE) as quarter,
                month(release_date::DATE) as month,
                strftime(release_date::DATE, '%B') as month_name,
                strftime(release_date::DATE, '%w') as day_of_week,
                CASE WHEN EXTRACT(DOW FROM release_date::DATE) IN (0, 6) THEN TRUE ELSE FALSE END as is_weekend
            FROM movie_details_df

    """)
    print("Insert Successful!!")

    
    return



