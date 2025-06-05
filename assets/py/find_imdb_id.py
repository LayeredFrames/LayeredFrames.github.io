import csv
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
from pprint import pprint

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


def find_shows(title):
    base_url = 'https://www.imdb.com/find?q='
    soup = request_page(base_url + quote(title))
    
    shows = []
    
    section = soup.find('section', attrs={'data-testid': 'find-results-section-title'})
    if not section:
        print(f"No results found for {title}")
        return shows

    items = section.find_all('li', class_='find-result-item')
    for item in items:
        url = item.find('a')['href']
        shows.append(url.split('/')[2])  # Extract the show ID from the URL
    
    return shows


def get_show_list(csv_file):
    # Read the csv for the project title and imdb_id
    shows = []
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=';')
        for row in reader:
            title = row.get('Project Title')
            if title:
                shows.append((
                    title.strip(),
                    row.get('IMDb', '').strip(),
                    row.get("Category").strip()
                    ))

    return shows


def get_imdb_ids(input_csv, output_csv):
    shows = get_show_list(input_csv)
    output_shows = []
    
    for show in shows:
        title, imdb_id, category = show
        if imdb_id or category.lower() == 'advertising':
            output_shows.append([title, imdb_id])
        else:
            print(f"Searching IMDb ID for: {title}")
            show_ids = find_shows(title)
            output_shows.append([title] + show_ids)
            print(f"Found IMDb IDs: {show_ids} for {title}")
    
    with open(output_csv, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['Project Title', 'IMDb ID', "IMDb ID 2", "IMDb ID 3", "IMDb ID 4", "IMDb ID 5"])  # Header row
        writer.writerows(output_shows)
        
    #     for title, imdb_id in shows:
    #         if not imdb_id:  # If IMDb ID is missing, search for it
    #             print(f"Searching IMDb ID for: {title}")
    #             show_ids = find_shows(title)
    #             if show_ids:
    #                 imdb_id = show_ids[0]  # Take the first result
    #                 print(f"Found IMDb ID: {imdb_id} for {title}")
    #             else:
    #                 print(f"No IMDb ID found for {title}")
    #         writer.writerow([title, imdb_id])

# shows = find_shows("The Little Vampire 3D")

# Example usage
input_csv = './assets/py/project-list.csv'
output_csv = './project-list_with_imdb.csv'

# pprint(get_show_list(input_csv))

base_url = 'https://www.imdb.com/find?q='

get_imdb_ids(input_csv, output_csv)