import os
import requests
from bs4 import BeautifulSoup
from imdb import Cinemagoer
from pprint import pprint
import json
import sys
import re

ia = Cinemagoer()

show_db_path = './assets/py/shows.json'

# input_file = 'assets/py/movies-3.json'
md_file = './_portfolio/_drafts/py-template.md'
download_dir = './assets/img/portfolio-covers-original'
output_dir = './assets/img/portfolio-covers'
drafts_folder = './_portfolio/drafts'

def load_shows():
    """Load shows from the JSON database."""
    if os.path.exists(show_db_path):
        with open(show_db_path, 'r', encoding='utf-8') as file:
            try:
                return json.load(file)
            except json.JSONDecodeError as e:
                print(f"Error loading {show_db_path}: {e}")
                return {}
    else:
        print(f"{show_db_path} does not exist. Returning an empty dictionary.")
        return {}


def get_initial_data(show_id):
    show = {}
    try:
        # Fetch show details
        show_data = ia.get_movie(show_id[2:])  # Remove 'tt' prefix for cinemagoer
        # Update the show dictionary with additional details
        show['director'] = ', '.join(d['name'] for d in show_data.get('director', []))
        show['cover_url'] = show_data.get('full-size cover url')
        show['plot_outline'] = show_data.get('plot outline', '')
        show['videos'] = show_data.get('videos', [])
        show['title'] = show_data.get('title')
        show['year'] = show_data.get('year')

    except Exception as e:
        print(f"Failed to fetch details for show ID {show_id}: {e}")
        raise
    
    return show

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
    print("Extracting release date...")
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
    print("Extracting category...")
    main = soup.find('main')
    hero_title = main.find('span', class_="hero__primary-text")
    main_info = hero_title.find_next('ul')

    items = main_info.find_all('li')

    if len(items) > 1 and not items[0].find('a'):
        category = items[0].text.strip()
    else:
        category = "Film"
    
    return category


def get_seasons(soup):
    print("Extracting seasons...")
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

def get_plot_outline(soup):
    """Extract the plot outline from the soup object."""
    print("Extracting plot outline...")
    plot_outline = soup.find('span', {'data-testid': 'plot-xl'})

    if plot_outline:
        return plot_outline.text.strip()


def get_episodes(movie_id, season):
    """Fetch episodes for a given movie ID and season."""
    print(f"Fetching episodes for movie ID {movie_id} and season {season}")
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

def safe_string(s):
    """Sanitize strings for use in filenames."""
    return re.sub(r'\W+', '_', s)

def convert_image(input_path, output_path):
    """Convert an image to the desired format."""
    if os.path.exists(output_path):
        print(f"Output file {output_path} already exists. Skipping conversion.")
        return output_path

    from PIL import Image
    try:
        with Image.open(input_path) as img:
            # Resize the image if the height is more than 620px
            if img.size[1] > 620:
                width_percent = 620 / float(img.size[1])
                new_width = int(float(img.size[0]) * float(width_percent))
                img = img.resize((new_width, 620), Image.LANCZOS)

            # Save the resized image in WEBP format
            img.save(output_path, 'WEBP')
            print(f"Converted {input_path} to {output_path}")

    except Exception as e:
        print(f"Failed to convert image {input_path}: {e}")
        return input_path

    return output_path

def download_cover(movie):
    print(f"Downloading cover for {movie['title']}...")
    if movie.get('cover_url'):
        file_path = os.path.join(download_dir, get_cover_name(movie))
        output_path = os.path.join(output_dir, get_cover_name(movie, extension='webp'))

        if not os.path.exists(download_dir):
            os.makedirs(download_dir, exist_ok=True)
        
        if not os.path.exists(file_path):
            # Download the cover image
            try:
                response = requests.get(movie['cover_url'], stream=True)
                response.raise_for_status()  # Check for HTTP errors
                with open(file_path, 'wb') as file:
                    for chunk in response.iter_content(1024):
                        file.write(chunk)
                print(f"Downloaded cover for {movie['title']} to {file_path}")

            except requests.RequestException as e:
                print(f"Error downloading cover for {movie['title']}: {e}")
        
        return convert_image(file_path, output_path)

    else:
        print(f"No cover URL found for {movie['title']}")


def get_cover_name(movie, extension='jpg'):
    """Generate a filename for the movie cover."""
    title = safe_string(movie.get('title', 'unknown_title'))
    movie_id = movie.get('movie_id', 'unknown_id')
    return f"{title}_{movie_id}.{extension}"

def create_md_file(show, show_id):
    show['movie_id'] = show_id
    show['alt'] = safe_string(show['title'])
    show['video_url'] = show['videos'][0] if show['videos'] else ""
    
    if not show['date']:
        show['date'] = ""
    else:
        show['date'] = f"date: {show['date']}"

    show['release_date'] = '[{{ page.date | date: "%d %B %Y" | default: "IMDb" }}]({{ page.imdb_url }}/releaseinfo/){:target="_blank"}'
    show['cover_url'] = download_cover(show) or f'https://placehold.co/434x620?text={show["title"].replace(" ", "+")}'
    show['imdb_url'] = f'https://www.imdb.com/title/{show_id}'
    show['page_role'] = '{{ page.caption.role | default: "N/A" }}'

    # # Read the example markdown template
    with open(md_file, 'r') as template_file:
        template = template_file.read()

    page_content = template.format(**show)
    
    show_md_file = f'{drafts_folder}/{safe_string(show["title"])}.md'
    print(f"Creating markdown file {show_md_file}...")
    with open(show_md_file, 'w') as page_file:
        page_file.write(page_content)

def add_show(imdb_id, role='VFX Artist', overwrite=False):
    show_db = load_shows()
    if imdb_id in show_db:
        print(f"Show with ID {imdb_id} already exists in the database.")
        if not overwrite:
            print("Use 'overwrite=True' to update the existing show.")
            return
        show = show_db[imdb_id]

    show = get_initial_data(imdb_id)
    soup = request_page(imdb_page(imdb_id))
    
    if not show['plot_outline']:
        show['plot_outline'] = get_plot_outline(soup)

    show['category'] = get_category(soup)
    show['date'] = get_release_date(imdb_id)
    seasons = get_seasons(soup)
    if seasons:
        episodes = get_episodes(imdb_id, seasons[-1])
        show['date'] = episodes[-1]['date']
        
    show['role'] = role
        
    # Add show to shows.json
    with open(show_db_path, 'w', encoding='utf-8') as file:
        show_db[imdb_id] = show
        json.dump(show_db, file, indent=4)

    # Create the markdown file
    create_md_file(show, imdb_id)

    pprint(show)


def add_md_file(show_id):
    """Create a markdown file for the show."""
    show_db = load_shows()
    if show_id not in show_db:
        print(f"Show with ID {show_id} not found in the database.")
        return

    show = show_db[show_id]
    create_md_file(show, show_id)

add_md_file('tt9573150')

# print(os.path.abspath(show_db_path)

# movies_path = './assets/py/movies-3.json'
# with open(movies_path, 'r', encoding='utf-8') as file:
#     movies_data = json.load(file)

# for movie in movies_data:
#     add_show(movie['movie_id'], role=movie['role'].title(), overwrite=True)