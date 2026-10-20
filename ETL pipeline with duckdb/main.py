from etl.extract import extract_movie_details
from etl.transform import transform_movie_details
from etl.load import load_movie_details


if __name__ == "__main__":
    load_movie_details()
