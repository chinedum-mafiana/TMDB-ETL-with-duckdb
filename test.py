import duckdb
import pandas as pd
import plotly.express as px
import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Movie Database Analytics & Explorer",
    page_icon="🎬",
    layout="wide",
)

DB_PATH = "movies_warehouse.duckdb"  # Update to your actual file name


@st.cache_resource
def get_duckdb_connection(db_path):
    """Establish a cached read-only connection to DuckDB."""
    try:
        return duckdb.connect(db_path, read_only=True)
    except Exception as e:
        return None


conn = get_duckdb_connection(DB_PATH)

st.title("🎬 Movie Database Dashboard")

if conn is None:
    st.error(
        f"Could not connect to DuckDB at `{DB_PATH}`. Please check your file"
        " path."
    )
else:
    tables = [
        "dim_movie",
        "dim_genre",
        "dim_date",
        "dim_production_company",
        "fact_movie",
    ]

    # Expanded Sidebar Navigation
    st.sidebar.header("Navigation")
    mode = st.sidebar.radio(
        "Select Mode", ["Browse Tables & Schema", "Visualizations", "Custom SQL Query"]
    )

    # ==========================================
    # 1. BROWSE TABLES & SCHEMA MODE
    # ==========================================
    if mode == "Browse Tables & Schema":
        st.subheader("📊 Complete Database Schema Architecture")
        st.markdown(
            "Here is the complete relationship map and column schema for your DuckDB warehouse:"
        )

        # Full Mermaid ERD Diagram with all columns and data types
        st.markdown("""
            ```mermaid
            erDiagram
                dim_movie {
                    integer movie_id PK
                    varchar title
                    text overview
                    text tagline
                    varchar original_language
                    varchar status
                    varchar poster_path
                    integer[] production_company_ids
                    integer[] genre_ids
                }
                
                dim_genre {
                    integer genre_id PK
                    varchar genre_name
                }
                
                dim_date {
                    integer date_id PK
                    date full_date
                    integer year
                    integer quarter
                    integer month
                    varchar month_name
                    varchar day_of_week
                    boolean is_weekend
                }
                
                dim_production_company {
                    integer production_company_id PK
                    varchar production_company_name
                }
                
                fact_movie {
                    integer movie_id PK
                    integer release_date_id FK
                    integer runtime
                    decimal vote_average
                    integer vote_count
                    decimal popularity
                    integer budget
                    bigint revenue
                }

                fact_movie }o--|| dim_movie : "references"
                fact_movie }o--|| dim_date : "released on"
                dim_movie }o--o{ dim_genre : "contains array of"
                dim_movie }o--o{ dim_production_company : "contains array of"
            ```
            """)

        st.markdown("---")
        st.sidebar.subheader("Table Selection")
        selected_table = st.sidebar.selectbox("Choose a table to view", tables)
        row_limit = st.sidebar.slider(
            "Rows to display", min_value=10, max_value=300, value=100, step=10
        )

        if selected_table:
            total_rows = conn.execute(
                f"SELECT COUNT(*) FROM {selected_table}"
            ).fetchone()[0]

            col1, col2 = st.columns(2)
            with col1:
                st.subheader(f"Table: `{selected_table}`")
            with col2:
                st.metric(label="Total Records", value=f"{total_rows:,}")

            # Fetch and display
            query = f"SELECT * FROM {selected_table} LIMIT {row_limit}"
            df = conn.execute(query).fetchdf()
            st.dataframe(df, use_container_width=True)

            with st.expander("View Table Schema"):
                schema_df = conn.execute(f"DESCRIBE {selected_table}").fetchdf()
                st.dataframe(schema_df, use_container_width=True)

    # ==========================================
    # 2. VISUALIZATIONS MODE
    # ==========================================
    elif mode == "Visualizations":
        st.subheader("📊 Database Visualizations & Analytics")
        
        viz_type = st.selectbox(
            "Select Visual / Analysis",
            [
                "Overview: Table Record Counts",
                "Genre Breakdown",
                "Top Production Companies",
                "Budget vs Revenue by Genre",
            ],
        )

        st.markdown("---")

        if viz_type == "Overview: Table Record Counts":
            st.markdown("### Total Records per Table")
            counts = []
            for t in tables:
                cnt = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
                counts.append({"Table": t, "Record Count": cnt})

            counts_df = pd.DataFrame(counts)

            # Bar chart using Plotly
            fig = px.bar(
                counts_df,
                x="Table",
                y="Record Count",
                text="Record Count",
                color="Table",
                title="Database Size Distribution",
            )
            fig.update_traces(texttemplate="%{text:,}", textposition="outside")
            st.plotly_chart(fig, use_container_width=True)

        elif viz_type == "Genre Breakdown":
            st.markdown("### Movie Distribution Across Genres")
            genre_query = """
                SELECT 
                    g.genre_name,
                    count(m.movie_id) as movie_count
                FROM dim_movie m,
                UNNEST(m.genre_ids) AS u(genre_id)
                JOIN dim_genre g ON u.genre_id = g.genre_id
                GROUP BY g.genre_name
                ORDER BY movie_count DESC
            """
            try:
                genre_df = conn.execute(genre_query).fetchdf()
                if not genre_df.empty:
                    fig = px.pie(
                        genre_df,
                        names="genre_name",
                        values="movie_count",
                        title="Top Movie Genres",
                        hole=0.4,
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning(
                        "No data returned. Check if table join columns (`genre_id`)"
                        " match your schema."
                    )
            except Exception as e:
                st.error(
                    f"Query Error (Check column names like `genre_id`): `{e}`"
                )

        elif viz_type == "Top Production Companies":
            st.markdown("### Production Companies with Most Movies")
            comp_query = """
                SELECT 
                    pc.production_company_name as company_name,
                    COUNT(dm.movie_id) as movie_count
                FROM dim_movie dm,
                UNNEST(dm.production_company_ids) as u(production_company_id) 
                JOIN dim_production_company pc ON pc.production_company_id = u.production_company_id
                GROUP BY pc.production_company_name
                ORDER BY movie_count DESC
                LIMIT 10;
            """
            try:
                comp_df = conn.execute(comp_query).fetchdf()
                if not comp_df.empty:
                    fig = px.bar(
                        comp_df,
                        x="movie_count",
                        y="company_name",
                        orientation="h",
                        title="Top 10 Production Companies",
                        labels={
                            "movie_count": "Number of Movies",
                            "company_name": "Company",
                        },
                    )
                    fig.update_layout(yaxis={"categoryorder": "total ascending"})
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("No data returned. Check your foreign key names.")
            except Exception as e:
                st.error(
                    f"Query Error (Check column names like `company_id`): `{e}`"
                )

        elif viz_type == "Budget vs Revenue by Genre":
            st.markdown("### Explore box-office performance, financial returns, and temporal trends")
            
            rev_roi_query = """
                SELECT movie_id, title, dg.genre_name, f.budget, f.revenue, genre_ids, ROUND(f.revenue / NULLIF(f.budget, 0), 2) AS roi
                FROM dim_movie
                FULL JOIN fact_movie f USING (movie_id)
                CROSS JOIN LATERAL unnest(genre_ids) AS t(genre_id)
                JOIN dim_genre dg ON t.genre_id = dg.genre_id
                WHERE f.budget > 1000 AND f.revenue > 1000
            """

            genres = conn.execute(rev_roi_query).fetchdf()
            
            if not genres.empty and "genre_name" in genres.columns:
                all_genres = sorted([str(g) for g in genres["genre_name"].dropna().unique() if str(g).strip()])
            else:
                all_genres = []

            # Multi-select filter for specific genres
            selected_genres = st.multiselect(
                "Filter by specific genres:",
                options=all_genres,
                default=all_genres,
            )
            
            if selected_genres and not genres.empty:
                filtered_genres = genres[genres["genre_name"].isin(selected_genres)]
            else:
                filtered_genres = genres.iloc[0:0]
                
            try:
                if not filtered_genres.empty:
                    fig = px.scatter(
                        filtered_genres,
                        x="budget",
                        y="revenue",
                        color="genre_name",
                        log_x=True,
                        log_y=True,
                        hover_name="title",
                        hover_data=["budget", "revenue", "roi", "genre_name"],
                        labels={
                            "budget": "Production Budget (USD, Log Scale)",
                            "revenue": "Box Office Revenue (USD, Log Scale)",
                            "roi": "ROI Multiplier",
                            "genre_name": "Genre",
                        },
                        title="Movie Budget vs. Revenue by Genre (Log-Log Scale)",
                    )

                    fig.update_layout(
                        xaxis=dict(tickprefix="$", dtick=1),
                        yaxis=dict(tickprefix="$", dtick=1),
                        height=700,
                    )

                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning(
                        "No movies found for the selected genre(s)."
                    )
            except Exception as e:
                st.error(
                    f"Query Error: `{e}`"
                )

    # ==========================================
    # 3. CUSTOM SQL QUERY MODE
    # ==========================================
    elif mode == "Custom SQL Query":
        st.subheader("🛠️ Custom SQL Playground")
        st.markdown(
            "Run custom queries joining your dimensions (`dim_movie`, `dim_genre`,"
            " etc.) with your `fact_movie` table."
        )

        default_query = (
            "SELECT f.*, m.title FROM fact_movie f JOIN dim_movie m ON f.movie_id ="
            " m.movie_id LIMIT 50"
        )
        sql_query = st.text_area("Enter SQL Query", value=default_query, height=150)

        if st.button("Execute Query", type="primary"):
            try:
                result_df = conn.execute(sql_query).fetchdf()
                st.success(f"Query executed successfully! Returned {len(result_df)} rows.")
                st.dataframe(result_df, use_container_width=True)
            except Exception as e:
                st.error(f"SQL Error: {e}")