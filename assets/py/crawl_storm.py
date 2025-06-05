import requests
from bs4 import BeautifulSoup
import json
from pprint import pprint
import os
import csv


def get_projects(url):
    # Fetch the main portfolio page
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all <article> elements with the class "work"
        articles = soup.find_all('article', class_='work')

        # Extract links to project pages
        project_links = []
        for article in articles:
            link_tag = article.find('a')
            if link_tag and 'href' in link_tag.attrs:
                project_links.append(link_tag['href'])

        # Print the number of projects found
        print(f"Found {len(project_links)} projects.")
        return project_links
    else:
        print(f"Failed to fetch the main portfolio page. Status code: {response.status_code}")
        raise Exception(f"Error fetching {url} - Status code: {response.status_code} Response: {response.text}")


    # # Crawl each project page
    # for link in project_links:

def crawl_project(link):
    print(f"Processing project: {link}")
    # project_url = f"https://stormpostproduction.com{link}"
    project_response = requests.get(link)
    if project_response.status_code == 200:
        project_soup = BeautifulSoup(project_response.text, 'html.parser')

        # Extract project title from multiple possible locations
        title_tag = project_soup.find('h1', class_='h2')
        if not title_tag:
            # Check for title in <div class="portfolio-title">
            title_div = project_soup.find('div', class_='portfolio-title')
            if title_div:
                hilited_title = title_div.find('div', class_='hilited-title')
                if hilited_title:
                    title_tag = hilited_title.find('h3')

        project_title = title_tag.text.strip() if title_tag else "Unknown Title"

        # Extract credits
        credits_section = project_soup.find('aside', class_='portfolio-credits') or project_soup.find('aside', class_='portfolio-content')
        if credits_section:
            credits_list = credits_section.find_all('li')
            for i in range(0, len(credits_list), 2):  # Iterate over roles and names
                role = credits_list[i].text.strip()
                if role.endswith("s"):
                    role = role[:-1]

                names = credits_list[i + 1].text.strip() if i + 1 < len(credits_list) else ""
                if "timo" in names.lower():
                    print(f"Found project: {project_title} - Role: {role}")
                    # Save project title and Timo's role
                    return {
                        "title": project_title,
                        "role": role,
                        "url": link
                    }


def get_projects(pages, db_file):
    # Load existing database if it exists
    if os.path.exists(db_file):
        with open(db_file, 'r') as f:
            try:
                timo_projects = json.load(f)
            except json.JSONDecodeError:
                timo_projects = []  # If the file is corrupted, start fresh
    else:
        timo_projects = []

    # Get the existing project URLs to avoid duplicates
    existing_urls = {project['url'] for project in timo_projects}
    new_projects = 0

    for page in pages:
        try:
            project_links = get_projects(page)
        except Exception as e:
            print(f"Error fetching projects from {page}: {e}")
            continue

        for link in project_links:
            project_url = f"https://stormpostproduction.com{link}"
            print(project_url)
            if project_url not in existing_urls:  # Avoid duplicates
                try:
                    project_data = crawl_project(project_url)
                    if project_data:
                        timo_projects.append(project_data)
                        existing_urls.add(project_url)  # Add to existing URLs to avoid duplicates
                        new_projects += 1

                except Exception as e:
                    print(f"Error processing project {link}: {e}")
            else:
                print(f"Project {link} already exists in the database, skipping.")


    # Save the updated database to the JSON file
    with open(db_file, 'w') as f:
        json.dump(timo_projects, f, indent=4)

    print(f"Database saved to {db_file}")


def export_to_csv(db_file, csv_file):
    # Load the database
    if os.path.exists(db_file):
        with open(db_file, 'r') as f:
            try:
                timo_projects = json.load(f)
            except json.JSONDecodeError:
                print("Error: Unable to read the database file.")
                return
    else:
        print("Error: Database file not found.")
        return

    # Define categories based on URL patterns
    url_categories = {
        'film-tv': 'Film & TV',
        'advertising': 'Advertising',
        'vfx-animation': 'VFX & Animation',
        'documentary': 'Documentary'
    }

    # Prepare data for CSV
    csv_data = []
    for project in timo_projects:
        title = project.get('title', 'Unknown Title')
        url = project.get('url', '')
        category = 'Unknown Category'
        role = project.get('role', 'N/A')

        # Determine category based on URL
        for key, value in url_categories.items():
            if key in url:
                category = value
                break

        # Add row to CSV data
        csv_data.append([title, '', '', '', category, url, role])

    # Write to CSV file
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Project Title', '', '', '', 'Category', 'URL', "Role"])  # Header row
        writer.writerows(csv_data)

    print(f"CSV file saved to {csv_file}")

def check_timo_drent_in_projects(db_file):
    # Load the database
    try:
        with open(db_file, 'r') as f:
            projects = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print("Error: Unable to load the database file.")
        return []

    projects_with_timo_drent = []

    # Iterate through each project URL in the database
    for project in projects:
        project_url = project.get('url')
        if not project_url:
            continue

        print(f"Checking project: {project_url}")
        try:
            response = requests.get(project_url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # Search for "Timo Drent" in the page content
                if "timo drent" in soup.text.lower():
                    print(f"Found Timo Drent in project: {project.get('title', 'Unknown Title')}")
                    projects_with_timo_drent.append({
                        "title": project.get('title', 'Unknown Title'),
                        "url": project_url,
                        "role": project.get('role', 'Unknown Role')
                    })
            else:
                print(f"Failed to fetch page: {project_url}. Status code: {response.status_code}")
        except requests.RequestException as e:
            print(f"Error fetching page {project_url}: {e}")

    return projects_with_timo_drent

# Example usage
db_file = './assets/py/timo_projects.json'
projects_with_timo_drent = check_timo_drent_in_projects(db_file)

# Print the results
if projects_with_timo_drent:
    print("Projects with Timo Drent in credits:")
    for project in projects_with_timo_drent:
        print(f"- {project['title']} ({project['role']}) - {project['url']}")
else:
    print("No projects found with Timo Drent in credits.")

# # URL of the main portfolio page
# # main_page = 'https://stormpostproduction.com/portfolio/film-tv/'
# pages = [
#     'https://stormpostproduction.com/portfolio/film-tv/',
#     'https://stormpostproduction.com/portfolio/advertising/',
#     'https://stormpostproduction.com/portfolio/vfx-animation/',
#     'https://stormpostproduction.com/portfolio/documentary/'
# ]

# # Initialize the database file path
# db_file = './assets/py/timo_projects.json'
# csv_file = './assets/py/timo_projects.csv'
# export_to_csv(db_file, csv_file)
