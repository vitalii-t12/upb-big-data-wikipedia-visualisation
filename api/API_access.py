import requests
import json
from datetime import datetime, timedelta
from urllib.parse import quote
import pandas as pd
import time

#hyperparameters
TIME = 365
TITLE = "Elon_Musk"
TOP_LIMIT = 20

def fetch_device_statistics(days):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Get data for each access type
    access_types = ['desktop', 'mobile-web', 'mobile-app']
    device_stats = {}
    
    for access in access_types:
        url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/aggregate/en.wikipedia/{access}/all-agents/daily/{start_date.strftime('%Y%m%d')}/{end_date.strftime('%Y%m%d')}"
        headers = {
            'User-Agent': 'MyWikipediaApp/1.0 (your-email@example.com)',
            'Accept': 'application/json'
        }
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                device_stats[access] = sum(item['views'] for item in data['items'])
            else:
                print(f"API Error for {access}: Status Code {response.status_code}")
                return None
        except Exception as e:
            print(f"Error fetching {access} statistics: {str(e)}")
            return None
    
    total_views = sum(device_stats.values())
    percentages = {device: (views/total_views*100) for device, views in device_stats.items()}
    
    # Find most used device
    most_used = max(device_stats.items(), key=lambda x: x[1])
    
    return {
        'stats': device_stats,
        'total_views': total_views,
        'percentages': percentages,
        'most_used': most_used
    }

def fetch_pageviews(title):
    encoded_title = quote(title.replace(" ", "_"))
    end_date = datetime.now()
    start_date = end_date - timedelta(days=TIME)
    base_url = "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia"
    headers = {
        'User-Agent': 'MyWikipediaApp/1.0 (your-email@example.com)',
        'Accept': 'application/json'
    }

    daily_data = {'date': [], 'desktop': [], 'mobile': [], 'total': []}
    access_types = ['desktop', 'mobile-web']
    
    try:
        for access in access_types:
            url = f"{base_url}/{access}/all-agents/{encoded_title}/daily/{start_date.strftime('%Y%m%d')}/{end_date.strftime('%Y%m%d')}"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                if access == 'desktop':
                    daily_data['date'] = [item['timestamp'][:8] for item in data['items']]
                    daily_data['desktop'] = [item['views'] for item in data['items']]
                else:
                    daily_data['mobile'] = [item['views'] for item in data['items']]

        # Calculate totals and create DataFrame
        daily_data['total'] = [d + m for d, m in zip(daily_data['desktop'], daily_data['mobile'])]
        df = pd.DataFrame(daily_data)
        
        # Convert date string to datetime
        df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
        
        # Calculate summary statistics
        total_views = sum(daily_data['total'])
        daily_average = total_views / TIME
        desktop_views = sum(daily_data['desktop'])
        mobile_views = sum(daily_data['mobile'])

        # Save data for Zeppelin
        df.to_csv(f'pageviews_{title}.csv', index=False)
        
        return {
            'desktop_views': desktop_views,
            'mobile_views': mobile_views,
            'total_views': total_views,
            'daily_average': round(daily_average, 2),
            'daily_data': df
        }
    except Exception as e:
        print(f"Error fetching pageviews: {str(e)}")
        return None

def get_top_articles(date, limit=20):
    headers = {
        'User-Agent': 'MyWikipediaApp/1.0 (your-email@example.com)',
        'Accept': 'application/json'
    }
    
    url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/top/en.wikipedia/all-access/{date.strftime('%Y/%m/%d')}"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            articles = []
            for article in data['items'][0]['articles']:
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

def fetch_annual_top_articles():
    print(f"\nFetching top {TOP_LIMIT} Wikipedia articles...")
    
    yesterday = datetime.now() - timedelta(days=1)
    articles = get_top_articles(yesterday, TOP_LIMIT)
    
    if not articles:
        print("No articles retrieved!")
        return None
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    all_data = []
    for i, article in enumerate(articles, 1):
        title = article['title']
        print(f"Processing {i}/{len(articles)}: {title}")
        views = fetch_pageviews(title.replace(' ', '_'))
        
        if views is not None:
            all_data.append({
                'article': title,
                'daily_views': article['daily_views'],
                'annual_views': views['total_views'],
                'daily_average': views['daily_average']
            })
        time.sleep(1)  # Rate limiting
    
    if all_data:
        df = pd.DataFrame(all_data)
        df = df.sort_values('annual_views', ascending=False)
        df.to_csv('top_wikipedia_articles.csv', index=False)
        return df
    return None

# Fetch and print the data
print(f"\nFetching global usage statistics for the last {TIME} days:")
device_stats = fetch_device_statistics(TIME)
if device_stats:
    print("\nWikipedia Usage Statistics by Device:")
    print(f"Total views: {device_stats['total_views']:,}")
    print("\nBreakdown by device:")
    for device, views in device_stats['stats'].items():
        print(f"{device}: {views:,} views ({device_stats['percentages'][device]:.1f}%)")
    print(f"\nMost used platform: {device_stats['most_used'][0]} with {device_stats['most_used'][1]:,} views "
          f"({device_stats['percentages'][device_stats['most_used'][0]]:.1f}% of total views)")

print("\nFetching specific article statistics:")
pageview_data = fetch_pageviews(TITLE)
if pageview_data:
    print(f"\nView statistics for {TITLE} (last {TIME} days):")
    print(f"Desktop views: {pageview_data['desktop_views']:,}")
    print(f"Mobile views:  {pageview_data['mobile_views']:,}")
    print(f"Total views:   {pageview_data['total_views']:,}")
    print(f"Daily average: {pageview_data['daily_average']:,.2f}")
    print(f"\nDetailed daily data saved to pageviews_{TITLE}.csv")
else:
    print("Failed to fetch data")

print("\nFetching top articles statistics worldwide:")
top_articles_data = fetch_annual_top_articles()
if top_articles_data is not None:
    print("\nTop Wikipedia articles by annual views:")
    print(top_articles_data.head(TOP_LIMIT))
    print("\nDetailed data saved to top_wikipedia_articles.csv")