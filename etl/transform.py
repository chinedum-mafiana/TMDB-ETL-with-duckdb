import pandas as pd
from etl.extract import extract_movie_details

def transform_movie_details():
    """
    Transforming the extracted movie details into a pandas DataFrames
    """
    movie_details = extract_movie_details()
    movie_details_df = pd.DataFrame(movie_details)
    
    movie_details_df.drop(columns = ['adult','homepage', 'belongs_to_collection', 'imdb_id', 'origin_country', 'original_title',  'production_countries', 'softcore', 'spoken_languages', 'video'], inplace=True)  
    movie_details_df['release_date_id'] = movie_details_df['release_date'].apply(lambda x: x.replace('-', ''))
    movie_details_df['genres'] = movie_details_df['genres'].apply(lambda x: [d['id'] for d in x])
    movie_details_df['production_companies'] = movie_details_df['production_companies'].apply(lambda x: [d['id'] for d in x])


    # creating the dim_genre_df and dim_prod_company_df for the genre and production comapnies tables
    extracted_genres = [genre for x in range(len(movie_details)) for genre in movie_details[x]['genres']]
    extracted_prod_companies = [company for x in range(len(movie_details)) for company in movie_details[x]['production_companies']]
    dim_genre_df = pd.DataFrame(extracted_genres).drop_duplicates().reset_index(drop=True)
    dim_prod_company_df = pd.DataFrame(extracted_prod_companies).drop_duplicates().reset_index(drop=True)[['id', 'name']]


    # Renaming columns names to column names in db for easier insert
    dim_genre_df.columns = ['genre_id', 'genre_name']
    dim_prod_company_df.columns = ['production_company_id', 'production_company_name']
    movie_details_df.rename(columns={'id': 'movie_id',
                                    'genres': 'genre_ids',
                                    'production_companies': 'production_company_ids'}, inplace=True)
    
    return movie_details_df, dim_genre_df, dim_prod_company_df
