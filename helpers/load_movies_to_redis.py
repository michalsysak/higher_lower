import requests
from dotenv import load_dotenv
import os
import redis

load_dotenv()

# TMDB settings
API_URL = "https://api.themoviedb.org/3/movie/popular"
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/"
POPULAR_MOVIES_ENDPOINT = "/movie/popular"
POSTER_SIZE = "w500"

# API token and redis client setting and connection
API_TOKEN = os.getenv("TMDB_API_TOKEN")
redis_client = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)


headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {API_TOKEN}"
}

def fetch_movies(max_pages = None):
    all_movies = []
    for page in range(1, max_pages + 1):
        params = {"language": "en-US", "page": page}
        response = requests.get(API_URL, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            movies = data.get("results", [])

            # Extract relevant fields from each movie
            filtered_movies = [
                {
                    "id": movie["id"],
                    "title": movie["title"],
                    "vote_average": movie["vote_average"],
                    "vote_count": movie["vote_count"],
                    "poster_url": f"{IMAGE_BASE_URL}{POSTER_SIZE}{movie['poster_path']}" if movie["poster_path"] else None,
                }
                for movie in movies
                # Filter out movies with vote_average * vote_count == 0
                if movie["vote_average"] > 0 and movie["vote_count"] > 0
            ]
            all_movies.extend(filtered_movies)
            print(f"Fetched page {page} successfully.")
        else:
            print(f"Failed to fetch page {page}: {response.status_code}")
            break  # Stop fetching if there's an error

    return all_movies


# Fetch movies
movies = fetch_movies(max_pages=4)

# Print the movies data in terminal as json
#print(json.dumps(movies, indent=4))

# Print the number of movies fetched
print(f"Fetched {len(movies)} movies")
print("Adding data to redis database...")
movies_added = 0
for movie in movies:
    # Define a unique key for each movie
    redis_key = f"movie:{movie['id']}"

    # Add each field only if it does not exist
    redis_client.hsetnx(redis_key, "id", movie["id"])
    redis_client.hsetnx(redis_key, "title", movie["title"])
    redis_client.hsetnx(redis_key, "vote_average", movie["vote_average"])
    redis_client.hsetnx(redis_key, "vote_count", movie["vote_count"])
    redis_client.hsetnx(redis_key, "poster_url", movie["poster_url"])

    print(f"Added movie '{movie['title']}' to Redis.")
    movies_added +=1

print(f"Added {movies_added} movies")