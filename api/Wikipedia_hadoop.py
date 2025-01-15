import wikipedia
from wikipedia.exceptions import DisambiguationError, PageError
import pandas as pd
import os
from datetime import datetime
import sys
from mrjob.job import MRJob
from mrjob.step import MRStep

class WikipediaHadoop(MRJob):
    
    def configure_args(self):
        super(WikipediaHadoop, self).configure_args()
        self.add_file_arg('--capitals', help='Path to capitals CSV file')
    
    def get_wiki_content(self, page_title):
        try:
            page = wikipedia.page(page_title)
            return page.content
        except (DisambiguationError, PageError, Exception) as e:
            return f"Error: {str(e)}"

    def get_nearby_articles_count(self, lat, lon, radius=25):
        try:
            articles = wikipedia.geosearch(lat, lon, radius=radius*1000)
            return len(articles)
        except Exception as e:
            return 0

    def mapper_get_articles(self, _, line):
        # Skip header
        if line.startswith('Country,'):
            return
        
        try:
            # Parse CSV line
            parts = line.split(',')
            country = parts[0]
            capital = parts[1]
            lat = float(parts[2])
            lon = float(parts[3])
            
            # Get article count
            article_count = self.get_nearby_articles_count(lat, lon)
            
            # Emit key-value pair
            yield country, {
                'capital': capital,
                'latitude': lat,
                'longitude': lon,
                'article_count': article_count
            }
        except Exception as e:
            yield 'error', str(e)

    def reducer_aggregate_results(self, key, values):
        if key != 'error':
            for value in values:
                yield key, value

    def steps(self):
        return [
            MRStep(
                mapper=self.mapper_get_articles,
                reducer=self.reducer_aggregate_results
            )
        ]

def save_results_to_csv(results):
    # Create results directory
    os.makedirs('wiki_pages', exist_ok=True)
    
    # Convert results to DataFrame
    data = []
    for country, info in results:
        row = {
            'Country': country,
            'Capital': info['capital'],
            'Latitude': info['latitude'],
            'Longitude': info['longitude'],
            'Articles_Within_25km': info['article_count']
        }
        data.append(row)
    
    df = pd.DataFrame(data)
    
    # Save to CSV
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'wiki_pages/capitals_articles_hadoop_{timestamp}.csv'
    df.to_csv(filename, index=False)
    return filename

if __name__ == '__main__':
    # Run Hadoop job
    wiki_job = WikipediaHadoop(args=['--capitals', 'country-capital-lat-long-population.csv'])
    results = wiki_job.run()
    
    # Save results
    output_file = save_results_to_csv(results)
    print(f"Results saved to: {output_file}")
