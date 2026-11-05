import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px

# Set up Streamlit page layout
st.set_page_config(page_title="TMDb Movie Analytics", page_icon="🎬", layout="wide")

st.title("🎬 TMDb Movie Analytics Dashboard")
st.markdown("Explore box-office performance, financial returns, and temporal trends powered by DuckDB and Streamlit.")

# 1. Cached DuckDB Connection (Singleton resource best practice)
@st.cache_resource
def get_duckdb_connection():
    # Connect to your local DuckDB file containing the TMDb star schema
    conn = duckdb.connect("tmdb.duckdb", read_only=True)
    return conn

conn = get_duckdb_connection()

# 2. Sidebar Filters
st.sidebar.header("🔍 Filter Options")

# Fetch available genres dynamically
genres_df = conn.execute("SELECT DISTINCT genre_name FROM dim_genre ORDER BY genre_name").fetchdf()
selected_genre = st.sidebar.selectbox("Select Genre", options=["All Genres"] + list(genres_df['genre_name']))

# Fetch year range dynamically
years = conn.execute("SELECT MIN(release_year), MAX(release_year) FROM dim_movie").fetchone()
min_year, max_year = int(years[0] or 1970), int(years[1] or 2026)
year_range = st.sidebar.slider("Release Year Range", min_year, max_year, (2000, max_year))

# Build dynamic SQL filter clause
where_clauses = [f"m.release_year BETWEEN {year_range[0]} AND {year_range[1]}"]
if selected_genre != "All Genres":
    where_clauses.append(f"g.genre_name = '{selected_genre}'")

where_sql = " WHERE " + " AND ".join(where_clauses)

# 3. Top Metrics Summary Row
col1, col2, col3 = st.columns(3)

metrics_query = f"""
    SELECT 
        COUNT(DISTINCT m.movie_id) as total_movies,
        AVG(m.budget) as avg_budget,
        AVG(m.revenue) as avg_revenue
    FROM dim_movie m
    LEFT JOIN fact_movie_genres fg ON m.movie_id = fg.movie_id
    LEFT JOIN dim_genre g ON fg.genre_id = g.genre_id
    {where_sql}
"""
metrics_df = conn.execute(metrics_query).fetchdf()

with col1:
    st.metric("Total Movies", f"{metrics_df['total_movies'].iloc[0]:,}")
with col2:
    st.metric("Average Budget", f"${metrics_df['avg_budget'].iloc[0]:,.0f}" if pd.notnull(metrics_df['avg_budget'].iloc[0]) else "$0")
with col3:
    st.metric("Average Revenue", f"${metrics_df['avg_revenue'].iloc[0]:,.0f}" if pd.notnull(metrics_df['avg_revenue'].iloc[0]) else "$0")

st.markdown("---")

# 4. Visualizations Section (Row 1)
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.subheader("Budget vs. Revenue (ROI Scatter)")
    scatter_query = f"""
        SELECT m.title, m.budget, m.revenue, m.vote_average, m.release_year
        FROM dim_movie m
        LEFT JOIN fact_movie_genres fg ON m.movie_id = fg.movie_id
        LEFT JOIN dim_genre g ON fg.genre_id = g.genre_id
        {where_sql} AND m.budget > 0 AND m.revenue > 0
        LIMIT 1500
    """
    df_scatter = conn.execute(scatter_query).fetchdf()
    
    fig_scatter = px.scatter(
        df_scatter, 
        x="budget", 
        y="revenue", 
        color="vote_average",
        hover_name="title",
        log_x=True, 
        log_y=True,
        labels={"budget": "Budget (USD, Log)", "revenue": "Revenue (USD, Log)", "vote_average": "Rating"},
        color_continuous_scale="Viridis"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

with row1_col2:
    st.subheader("Average Revenue Trend Over Time")
    trend_query = f"""
        SELECT m.release_year, AVG(m.revenue) as avg_revenue
        FROM dim_movie m
        LEFT JOIN fact_movie_genres fg ON m.movie_id = fg.movie_id
        LEFT JOIN dim_genre g ON fg.genre_id = g.genre_id
        {where_sql} AND m.release_year IS NOT NULL AND m.revenue > 0
        GROUP BY m.release_year
        ORDER BY m.release_year
    """
    df_trend = conn.execute(trend_query).fetchdf()
    
    fig_trend = px.line(
        df_trend, 
        x="release_year", 
        y="avg_revenue",
        markers=True,
        labels={"release_year": "Release Year", "avg_revenue": "Average Revenue (USD)"}
    )
    st.plotly_chart(fig_trend, use_container_width=True)

# 5. Full-Width Visualizations (Row 2)
st.subheader("Top Genres by Total Box Office Revenue")
genre_bar_query = """
    SELECT g.genre_name, SUM(m.revenue) as total_revenue
    FROM dim_movie m
    JOIN fact_movie_genres fg ON m.movie_id = fg.movie_id
    JOIN dim_genre g ON fg.genre_id = g.genre_id
    WHERE m.revenue > 0
    GROUP BY g.genre_name
    ORDER BY total_revenue DESC
    LIMIT 10
"""
df_genre = conn.execute(genre_bar_query).fetchdf()

fig_genre = px.bar(
    df_genre,
    x="genre_name",
    y="total_revenue",
    color="total_revenue",
    labels={"genre_name": "Genre", "total_revenue": "Total Revenue (USD)"},
    color_continuous_scale="Blues"
)
st.plotly_chart(fig_genre, use_container_width=True)
  
