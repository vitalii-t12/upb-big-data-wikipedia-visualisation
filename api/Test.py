import requests
import json
from datetime import datetime, timedelta
import pandas as pd
import time

def get_top_articles(date, limit=20):
    """Get most viewed Wikipedia articles for a specific date"""
    headers = {
        'User-Agent': 'MyWikipediaApp/1.0 (gavrielshaw@gmail.com)',
        'Accept': 'application/json'
    }
    
    url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/top/en.wikipedia/all-access/{date.strftime('%Y/%m/%d')}"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            articles = []
            for article in data['items'][0]['articles']:
                # More strict filtering for actual Wikipedia articles
                if (not any(x in article['article'] for x in ['Special:', 'Main_Page', 'Wikipedia:', 'File:', 'Help:', 'User:', 'Talk:', 'Template:']) 
                    and not article['article'].startswith('Portal:')):
                    articles.append({
                        'title': article['article'].replace('_', ' '),
                        'daily_views': article['views']
                    })
            return articles[:limit]
        else:
            print(f"Error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def get_article_views(article, start_date, end_date):
    """Get total views for an article between two dates"""
    headers = {
        'User-Agent': 'MyWikipediaApp/1.0 (gavrielshaw@gmail.com)',
        'Accept': 'application/json'
    }
    
    url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/all-agents/{article}/daily/{start_date.strftime('%Y%m%d')}/{end_date.strftime('%Y%m%d')}"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            total_views = sum(item['views'] for item in data['items'])
            return total_views
        return None
    except Exception as e:
        print(f"Error for {article}: {str(e)}")
        return None

def main():
    print("Fetching top 20 Wikipedia articles...")
    
    # Get yesterday's top articles (more reliable than today)
    yesterday = datetime.now() - timedelta(days=1)
    articles = get_top_articles(yesterday)
    
    if not articles:
        print("No articles retrieved!")
        return
    
    print(f"Found {len(articles)} top articles")
    
    # Calculate date range for the last year
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    # Collect annual views for each article
    all_data = []
    for i, article in enumerate(articles, 1):
        title = article['title']
        print(f"Processing {i}/{len(articles)}: {title}")
        views = get_article_views(title.replace(' ', '_'), start_date, end_date)
        
        if views is not None:
            all_data.append({
                'article': title,
                'daily_views': article['daily_views'],
                'annual_views': views,
                'date_range': f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
            })
        time.sleep(1)  # Rate limiting
    
    # Save to CSV
    if all_data:
        df = pd.DataFrame(all_data)
        df = df.sort_values('annual_views', ascending=False)
        output_file = 'top_wikipedia_articles.csv'
        df.to_csv(output_file, index=False)
        print(f"\nSaved {len(df)} articles to {output_file}")
        print("\nTop Wikipedia articles by annual views:")
        print(df.head(20))
    else:
        print("No data was collected!")

if __name__ == "__main__":
    main()