import pandas as pd 
import requests 
import os
from ratelimit import limits, sleep_and_retry


api_key = os.environ.get("TMDB_APIKEY")
if not api_key:
   raise ValueError("API KEY missing")

headers = {"accept": "application/json", "Authorization": f"Bearer {api_key}"}
# # movie_url = f"https://api.themoviedb.org/3/discover/movie?include_adult=false&include_video=false&language=en-US&page=1&primary_release_date.gte=2024-01-01&sort_by=popularity.desc&vote_average.gte=7&vote_count.gte=1000"
# tv_url = "https://api.themoviedb.org/3/discover/tv?include_adult=false&include_null_first_air_dates=false&language=en-US&page=1&sort_by=popularity.desc"
# persons_url = "https://api.themoviedb.org/3/person/popular?language=en-US&page=1"

@sleep_and_retry
@limits(calls=25, period=1)
def extract_movie_ids(date = "2024-01-01", rating=7.0, votes=1000, max_pages=10):
    """
    Extract movie_ids from TMDB API. This method is better bcos it allows getting more movie info from movie details on tmdb
    
    Args:
        date (str): The minimum release date of the movies to be fetched. Format: YYYY-MM-DD
        rating (float): The minimum average rating of the movies to be fetched.
        votes (int): The minimum number of votes of the movies to be fetched.
        max_pages (int): The maximum number of pages to fetch. Each page contains 20 movies.
        """
        
    date = str(date)
    rating = float(rating)
    votes = int(votes)
    max_pages =int(max_pages)

    movie_url = f"https://api.themoviedb.org/3/discover/movie?include_adult=false&include_video=false&language=en-US&page=1&primary_release_date.gte={date}&sort_by=popularity.desc&vote_average.gte={rating}&vote_count.gte={votes}"
    
    response = requests.get(url=movie_url, headers=headers)
    data = response.json()
    total_pages = data.get("total_pages")
    if total_pages > max_pages:
        print(f"Requesting too many pages. The maximum is {max_pages} pages. Stopping fetch.")
        return        
    
    try:
        all_movies = []
        for num in range(1, total_pages + 1):
            movie_url = f"https://api.themoviedb.org/3/discover/movie?include_adult=false&include_video=false&language=en-US&page={num}&primary_release_date.gte={date}&sort_by=popularity.desc&vote_average.gte={rating}&vote_count.gte={votes}"

            response = requests.get(url=movie_url, headers=headers)

            data = response.json()
            movies_on_page = data.get("results", [])
            all_movies.extend(movies_on_page)
        
        ids = [all_movies[x].get('id') for x in range(len(all_movies))]
        return list(dict.fromkeys(ids)) # checking that the ids are not duplicates by converting it to dict and back to list. dict disallows duplicates and retains order
                
            # print(f"Fetched page {num} of {total_pages}") 
    except Exception as e:
        print(f'An unexpected error occured: {e}')
    
@sleep_and_retry
@limits(calls=25, period=1)
def extract_movie_details():
    """
    Extracting movie details using the movie id
    """
    movie_ids = extract_movie_ids()
    details = []
    for movie_id in movie_ids:
        try:
            url = f"https://api.themoviedb.org/3/movie/{movie_id}?language=en-US"
            response = requests.get(url=url, headers=headers)
            data = response.json()
            details.append(data)
        except Exception as e:
            print(f'An unexpected error occured: {e}')
    return details
