import pandas as pd
import duckdb
from etl.transform import transform_movie_details

def load_movie_details():
    """
    Loading the transformed movie details into a DuckDB database
    """
    movie_details_df, dim_genre_df, dim_prod_company_df = transform_movie_details()
    
    # Create a DuckDB connection
    conn = duckdb.connect(database='movies.db', read_only=False)
    
    # Load the DataFrames into DuckDB tables
    conn.execute("CREATE TABLE IF NOT EXISTS movie_details AS SELECT * FROM movie_details_df")
    conn.execute("CREATE TABLE IF NOT EXISTS dim_genre AS SELECT * FROM dim_genre_df")
    conn.execute("CREATE TABLE IF NOT EXISTS dim_prod_company AS SELECT * FROM dim_prod_company_df")
    
    # Commit and close the connection
    conn.commit()
    conn.close()
    
    return



