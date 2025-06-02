import os
import requests
from bs4 import BeautifulSoup
from imdb import Cinemagoer
from pprint import pprint
import json
import sys

input_file = 'assets/py/movies.json'
output_file = 'assets/py/movies-3.json'
# # Load movie data from movies.json

with open(input_file, 'r') as file:
    movies = json.load(file)


def imdb_page(movie_id, subpage=''):
    """Construct the IMDb URL for a movie."""
    movie_id = str(movie_id).strip()
    if not movie_id.startswith('tt'):
        movie_id = 'tt' + movie_id
    return f"https://www.imdb.com/title/{movie_id}/{subpage}"


def request_page(url):
    """Request a page and return the BeautifulSoup object."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch {url}: {response.status_code}")
        return None

    return BeautifulSoup(response.content, 'html.parser')


def get_release_date(movie_id):
    date = None
    soup = request_page(imdb_page(movie_id, 'releaseinfo'))

    release_sections = soup.find_all('section', class_='ipc-page-section')

    for section in release_sections:
        if section.find('span', id='releases'):
            span = section.find('span', class_="ipc-metadata-list-item__list-content-item ipc-btn--not-interactable")
            if span:
                date= span.text.strip()
    
    return date

def get_category(soup):
    main = soup.find('main')
    hero_title = main.find('span', class_="hero__primary-text")
    main_info = hero_title.find_next('ul')

    items = main_info.find_all('li')

    if len(items) > 1 and not items[0].find('a'):
        category = items[0].text.strip()
    else:
        category = "Film"
    
    return category

def episodes(soup):
    episodes_link = soup.find('a', href=lambda href: href and '/episodes/' in href)

    if episodes_link:
        return episodes_link['href']

    return None

def get_seasons(soup):
    seasons = []
    season_selector = soup.find('select', id="browse-episodes-season")
    if not season_selector:
        return seasons

    for option in season_selector.find_all('option'):
        season_number = option['value']
        if season_number.isdigit():
            seasons.append(int(season_number))
    seasons.sort()
    
    return seasons


def get_episodes(movie_id, season):
    """Fetch episodes for a given movie ID and season."""
    url = imdb_page(movie_id, f'episodes/?season={season}')
    soup = request_page(url)

    if not soup:
        return []

    episodes_list = []
    
    episode_articles = soup.find_all('article', class_='episode-item-wrapper')
    
    for article in episode_articles:
        episode = {}
        title_div = article.find('div', class_='ipc-title__text')
        episode['title'] = title_div.text.strip()
        episode['url'] = f"https://www.imdb.com/{title_div.parent['href']}" if title_div.parent and title_div.parent.has_attr('href') else None
        episode['date'] = title_div.find_next('span').text.strip() if article.find_next('span') else "Unknown Date"
        
        episodes_list.append(episode)
    
    return episodes_list


with open(input_file, 'r') as file:
    movies = json.load(file)

for movie in movies:
    print(f"Updating movie: {movie['title']} ({movie['movie_id']})")

    soup = request_page(imdb_page(movie['movie_id']))

    movie['category'] = get_category(soup)
    print(f"Category: {movie['category']}")
    
    seasons = get_seasons(soup)
    if not seasons:
        movie['date'] = get_release_date(movie['movie_id'])
    else:
        last_episode = get_episodes(movie['movie_id'], seasons[-1])[-1]
        print(f"Taking date from: {last_episode['title']} ({last_episode['date']})")
        movie['date'] = last_episode['date']

    print(movie['date'])

# Output the updated movies dictionary to a JSON file
with open(output_file, 'w') as json_file:
    json.dump(movies, json_file, indent=4)

# print('requesting page')
# # tt6922038
# movie_id = 'tt3487478'

# soup = request_page(imdb_page(movie_id))
# last_season = get_seasons(soup)[-1]

# get_episodes(movie_id, 5)

# for section in soup.find_all('a', _class="ipc-title-link-wrapper"):
#     print(section.text.strip())

# for movie in movies[1:]:
#     if not movie['date']:
#         print(f"Fetching date for {movie['title']} ({movie['movie_id']})")
#         date = get_release_date(movie['movie_id'])
#         print(date)

#         break

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


# # Load the movies data from the JSON file
# input_file = 'assets/py/movies.json'
# download_dir = 'assets/img/portfolio-covers-original'
# output_dir = 'assets/img/portfolio-covers'

# # Ensure the output directory exists
# os.makedirs(download_dir, exist_ok=True)

# # Load movies from JSON
# with open(input_file) as f:
#     movies = json.load(f)

# # Download cover photos
# for movie in movies:
#     title = movie.get('title', 'unknown_title').replace(' ', '_').replace('/', '_')
#     movie_id = movie.get('movie_id', 'unknown_id')
#     cover_url = movie.get('cover_url')

#     if cover_url:
#         try:
#             print(f"Downloading cover for {title} ({movie_id})...")
#             response = requests.get(cover_url, stream=True)
#             response.raise_for_status()  # Raise an error for bad HTTP responses

#             # Create filename using title and movie ID
#             filename = f"{title}_{movie_id}.jpg"
#             filepath = os.path.join(download_dir, filename)

#             # Save the image
#             with open(filepath, 'wb') as img_file:
#                 for chunk in response.iter_content(1024):
#                     img_file.write(chunk)

#             print(f"Saved cover to {filepath}")
#         except Exception as e:
#             print(f"Failed to download cover for {title} ({movie_id}): {e}")
#     else:
#         print(f"No cover URL found for {title} ({movie_id})")
        
# def convert_image(input_path, output_path):
#     """Convert an image to the desired format."""
#     from PIL import Image
#     try:
#         with Image.open(input_path) as img:
#             # Resize the image to have a maximum height of 620px
#             width_percent = 620 / float(img.size[1])
#             new_width = int(float(img.size[0]) * float(width_percent))
#             img = img.resize((new_width, 620), Image.ANTIALIAS)

#             # Save the resized image in WEBP format
#             img.save(output_path, 'WEBP')
#             print(f"Converted {input_path} to {output_path}")

#     except Exception as e:
#         print(f"Failed to convert image {input_path}: {e}")
#         return input_path

#     return output_path

# def download_cover(movie):
#     if movie.get('cover_url'):
#         filename = get_cover_name(movie)
#         file_path = os.path.join(download_dir, get_cover_name(movie))
#         output_path = os.path.join(output_dir, get_cover_name(movie, extension='webp'))

#         if not os.path.exists(download_dir):
#             os.makedirs(download_dir, exist_ok=True)
        
#         if not os.path.exists(file_path):
#             # Download the cover image
#             try:
#                 response = requests.get(movie['cover_url'], stream=True)
#                 response.raise_for_status()  # Check for HTTP errors
#                 with open(file_path, 'wb') as file:
#                     for chunk in response.iter_content(1024):
#                         file.write(chunk)
#                 print(f"Downloaded cover for {movie['title']} to {file_path}")

#                 return convert_image(file_path, output_path)

#             except requests.RequestException as e:
#                 print(f"Error downloading cover for {movie['title']}: {e}")

# def get_cover_name(movie, extension='jpg'):
#     """Generate a filename for the movie cover."""
#     title = movie.get('title', 'unknown_title').replace(' ', '_').replace('/', '_')
#     movie_id = movie.get('movie_id', 'unknown_id')
#     return f"{title}_{movie_id}.{extension}"