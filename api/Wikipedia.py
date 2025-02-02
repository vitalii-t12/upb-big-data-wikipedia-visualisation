import wikipedia
from wikipedia.exceptions import DisambiguationError, PageError
import pandas as pd
import os
from datetime import datetime
import multiprocessing
from itertools import islice
from tqdm import tqdm

PAGE_TITLE = "Python (programming language)"

def get_wiki_content(page_title: str) -> str:
    try:
        # Get the full page content
        page = wikipedia.page(page_title)
        return page.content
    except DisambiguationError as e:
        return f"Disambiguation Error: Multiple pages found. Options: {e.options[:5]}"
    except PageError:
        return f"Error: Page '{page_title}' not found"
    except Exception as e:
        return f"Error: {str(e)}"

def save_wiki_content(page_title: str) -> str:
    print(f"Fetching content for: {page_title}")
    content = get_wiki_content(page_title)
    
    # Create wiki_pages directory if it doesn't exist
    os.makedirs('wiki_pages', exist_ok=True)
    print(f"Created/verified wiki_pages directory")
    
    # Create DataFrame with page title and content
    df = pd.DataFrame({
        'title': [page_title],
        'content': [content]
    })
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'wiki_pages/wiki_content_{timestamp}.csv'
    
    # Save to CSV
    df.to_csv(filename, index=False, encoding='utf-8')
    print(f"Saved content to: {filename}")
    return f"Content saved to {filename}"

def get_nearby_articles_count(latitude: float, longitude: float, radius: int = 10) -> int:
    try:
        # Get all articles within radius (in km)
        articles = wikipedia.geosearch(latitude, longitude, results = 999999, radius=radius*1000)  # Convert to meters
        return len(articles)
    except Exception as e:
        print(f"Error getting articles for coordinates ({latitude}, {longitude}): {str(e)}")
        return 0

def process_capitals_geosearch():
    print("Starting geosearch process for capitals...")
    
    # Read capitals CSV
    capitals_df = pd.read_csv('country-capital-lat-long-population.csv')
    
    # Create results list
    results = []
    
    # Process each capital
    for _, row in capitals_df.iterrows():
        country = row['Country']
        capital = row['Capital City']
        lat = row['Latitude']
        lon = row['Longitude']
        
        print(f"Processing {capital}, {country}...")
        article_count = get_nearby_articles_count(lat, lon)
        
        results.append({
            'Country': country,
            'Capital': capital,
            'Latitude': lat,
            'Longitude': lon,
            'Articles_Within_10km': article_count
        })
    
    # Create DataFrame and save to CSV
    results_df = pd.DataFrame(results)
    
    # Create wiki_pages directory if it doesn't exist
    os.makedirs('wiki_pages', exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'wiki_pages/capitals_articles_{timestamp}.csv'
    
    # Save to CSV
    results_df.to_csv(filename, index=False, encoding='utf-8')
    print(f"Results saved to {filename}")
    return filename

def process_city_batch(cities_batch):
    results = []
    for city_data in cities_batch:
        city, country, lat, lng = city_data
        try:
            article_count = get_nearby_articles_count(lat, lng)
            results.append((city, country, lat, lng, article_count))
        except Exception as e:
            print(f"Error processing {city}, {country}: {str(e)}")
            results.append((city, country, lat, lng, 0))
    return results

def process_world_cities(batch_size=100):
    print("Starting parallel geosearch process for world cities...")
    
    # Read worldcities CSV
    cities_df = pd.read_csv('worldcities.csv')
    
    # Prepare city data for parallel processing
    city_data = [(row['city'], row['country'], row['lat'], row['lng']) 
                 for _, row in cities_df.iterrows()]
    
    # Calculate number of batches
    n_batches = (len(city_data) + batch_size - 1) // batch_size
    
    # Create batches
    batches = [city_data[i:i + batch_size] for i in range(0, len(city_data), batch_size)]
    
    # Initialize multiprocessing pool
    num_processes = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(processes=num_processes)
    
    print(f"Processing {len(city_data)} cities using {num_processes} processes...")
    
    # Process batches in parallel with progress bar
    all_results = []
    with tqdm(total=len(batches), desc="Processing batches") as pbar:
        for batch_results in pool.imap(process_city_batch, batches):
            all_results.extend(batch_results)
            pbar.update(1)
    
    pool.close()
    pool.join()
    
    # Create results DataFrame
    results_df = pd.DataFrame(all_results, 
                            columns=['city', 'country', 'lat', 'lng', 'articles_within_10km'])
    
    # Merge with original dataframe to preserve all columns
    cities_df['articles_within_10km'] = results_df['articles_within_10km']
    
    # Create wiki_pages directory if it doesn't exist
    os.makedirs('wiki_pages', exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'wiki_pages/world_cities_{timestamp}.csv'
    
    # Save to CSV
    cities_df.to_csv(filename, index=False, encoding='utf-8')
    print(f"Results saved to {filename}")
    return filename

if __name__ == "__main__":
    # result = save_wiki_content(PAGE_TITLE)
    # print(result)
    # process_capitals_geosearch()
    process_world_cities(batch_size=100)
