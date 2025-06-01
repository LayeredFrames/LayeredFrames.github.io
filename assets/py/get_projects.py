import os
import requests
from bs4 import BeautifulSoup
from imdb import Cinemagoer
from pprint import pprint
import json
import sys

# # create an instance of the Cinemagoer class
# ia = Cinemagoer()

# # Load the HTML content from the file
# with open('/Users/timo/Documents/LayeredFrames/site/LayeredFrames.github.io/assets/py/imdb_page_2.html') as f:
#     response = f.read()

# soup = BeautifulSoup(response, 'html.parser')

# # Extract movie details (titles, years, roles, and IDs)
# movies = []
# film_items = soup.find_all('li', class_='ipc-metadata-list-summary-item')
# for film_item in film_items:
#     # Extract title
#     title_tag = film_item.find('a', class_='ipc-metadata-list-summary-item__t')
#     title = title_tag.text.strip() if title_tag else "Unknown Title"

#     # Extract year
#     year_tag = film_item.find('span', class_='ipc-metadata-list-summary-item__li')
#     year = year_tag.text.strip() if year_tag else "Unknown Year"

#     # Extract role
#     role_tag = film_item.find('span', class_='ipc-btn--not-interactable')
#     role = role_tag.text.strip() if role_tag else "Unknown Role"

#     # Extract movie ID
#     movie_id = None
#     if title_tag and title_tag.has_attr('href'):
#         href = title_tag['href']
#         if '/title/' in href:
#             movie_id = href.split('/title/')[1].split('/')[0]

#     movies.append({'title': title, 'year': year, 'role': role, 'movie_id': movie_id})

# # Update the existing movies dictionary with additional details
# for movie in movies:
#     print("updating movie:", movie['title'])
#     movie_id = movie.get('movie_id')
#     if movie_id:
#         try:
#             # Fetch movie details
#             movie_data = ia.get_movie(movie_id[2:])  # Remove 'tt' prefix for cinemagoer
#             # Update the movie dictionary with additional details
#             movie['director'] = ', '.join(d['name'] for d in movie_data.get('director', []))
#             movie['cover_url'] = movie_data.get('full-size cover url')
#             movie['plot_outline'] = movie_data.get('plot outline', '')
#             movie['videos'] = movie_data.get('videos', [])
#             movie['title'] = movie_data.get('title', movie['title'])
#             movie['year'] = movie_data.get('year', movie['year'])
#             movie['date'] = movie_data.get('original air date')
#         except Exception as e:
#             print(f"Failed to fetch details for movie ID {movie_id}: {e}")

# # Print the extracted movies
# # Save the updated movies data to a JSON file
# output_file = '/Users/timo/Documents/LayeredFrames/site/LayeredFrames.github.io/assets/py/movies-2.json'
# with open(output_file, 'w') as json_file:
#     json.dump(movies, json_file, indent=4)


# Load the movies data from the JSON file
input_file = 'assets/py/movies.json'
output_dir = 'assets/img/portfolio-covers'

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Load movies from JSON
with open(input_file) as f:
    movies = json.load(f)

# Download cover photos
for movie in movies:
    title = movie.get('title', 'unknown_title').replace(' ', '_').replace('/', '_')
    movie_id = movie.get('movie_id', 'unknown_id')
    cover_url = movie.get('cover_url')

    if cover_url:
        try:
            print(f"Downloading cover for {title} ({movie_id})...")
            response = requests.get(cover_url, stream=True)
            response.raise_for_status()  # Raise an error for bad HTTP responses

            # Create filename using title and movie ID
            filename = f"{title}_{movie_id}.jpg"
            filepath = os.path.join(output_dir, filename)

            # Save the image
            with open(filepath, 'wb') as img_file:
                for chunk in response.iter_content(1024):
                    img_file.write(chunk)

            print(f"Saved cover to {filepath}")
        except Exception as e:
            print(f"Failed to download cover for {title} ({movie_id}): {e}")
    else:
        print(f"No cover URL found for {title} ({movie_id})")