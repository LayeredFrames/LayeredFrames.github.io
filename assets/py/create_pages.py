import json
import os
import requests

input_file = 'assets/py/movies-3.json'
md_file = '_portfolio/_drafts/py-template.md'
download_dir = 'assets/img/portfolio-covers-original'
output_dir = 'assets/img/portfolio-covers'
drafts_folder = './_portfolio/drafts'

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
                img = img.resize((new_width, 620), Image.ANTIALIAS)

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
    title = movie.get('title', 'unknown_title').replace(' ', '_').replace('/', '_').replace(':', '_')
    movie_id = movie.get('movie_id', 'unknown_id')
    return f"{title}_{movie_id}.{extension}"



# # Load movie data from movies.json
with open(input_file, 'r') as file:
    movies_data = json.load(file)

# # Read the example markdown template
with open(md_file, 'r') as template_file:
    template = template_file.read()

# # Create _portfolio/drafts directory if it doesn't exis
if not os.path.exists(drafts_folder):
    print(f"Creating directory {drafts_folder}")
    os.makedirs(drafts_folder, exist_ok=True)

sanitize_keys = ["title","subtitle"]
            
safe_filename = lambda s: s.replace(' ', '_').replace('/', '_').replace(':', '_')

categories = []

for movie in movies_data:
    if not movie['category'] in categories:
        categories.append(movie['category'])

    movie['alt'] = safe_filename(movie['title'])
    videos = movie.pop('videos', [])
    if videos:
        movie['video_url'] = videos[0]
    else:
        movie['video_url'] = ""
    
    if not movie['date']:
        movie['date'] = ""
    else:
        movie['date'] = f"date: {movie['date']}"

    movie['release_date'] = '[{{ page.date | date: "%d %B %Y" | default: "IMDb" }}]({{ page.imdb_url }}/releaseinfo/){:target="_blank"}'

    movie['role'] = movie['role'].title() if movie['role'] else 'N/A'

    movie['cover_url'] = download_cover(movie) or f'https://placehold.co/434x620?text={movie["title"].replace(" ", "+")}'

    # movie['imdb_url'] = f'"[IMDb page](https://www.imdb.com/title/{movie["movie_id"]})"'
    movie['imdb_url'] = f'https://www.imdb.com/title/{movie["movie_id"]}'
    
    movie['page_role'] = '{{ page.caption.role | default: "N/A" }}'

    page_content = template.format(**movie)
    with open(f'{drafts_folder}/{safe_filename(movie["title"])}.md', 'w') as page_file:
        page_file.write(page_content)

