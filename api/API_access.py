import requests
import json
from datetime import datetime, timedelta
from urllib.parse import quote
import pandas as pd

#hyperparameters
TIME = 365
TITLE = "Elon_Musk"
TOP_ARTICLES = 10
COUNTRY = 'FR'     # Use 'ALL' for worldwide statistics or country code (e.g., 'US', 'GB', 'FR', etc.)

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

def fetch_top_articles(days, region, limit=100):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=1)  # API only supports daily stats
    
    headers = {
        'User-Agent': 'MyWikipediaApp/1.0 (your-email@example.com)',
        'Accept': 'application/json'
    }
    
    try:
        if region.upper() == 'ALL':
            # For worldwide stats
            url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/top/en.wikipedia/all-access/{start_date.strftime('%Y/%m/%d')}"
        else:
            # For specific country - using correct endpoint structure
            formatted_date = start_date.strftime('%Y%m%d00')  # Format: YYYYMMDD00
            url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/top-by-country/{region.upper()}/all-access/{formatted_date}"
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            articles = []
            rank = 1
            
            # Handle different JSON structure for country-specific response
            if region.upper() == 'ALL':
                article_list = data['items'][0]['articles']
            else:
                # Check if data exists for the country
                if not data['items'] or len(data['items']) == 0:
                    print(f"No data available for country code: {region}")
                    return None, None
                article_list = data['items'][0]['view_history'][0]['articles']
            
            for article in article_list:
                if 'article' in article and article['article'] not in ['Main_Page', 'Special:Search']:
                    articles.append({
                        'article': article['article'],
                        'views': article['views'],
                        'rank': rank
                    })
                    rank += 1
                    if len(articles) >= limit:
                        break
            
            if articles:
                df = pd.DataFrame(articles)
                filename = f'top_articles_{region.lower()}_{days}days.csv'
                df.to_csv(filename, index=False)
                return df, region.upper()
            else:
                print("No valid articles found")
                return None, None
        else:
            print(f"API Error: Status Code {response.status_code}")
            if response.status_code == 404:
                print(f"Country code '{region}' might be invalid or no data available for this region")
            print(f"Response: {response.text}")
            return None, None
            
    except Exception as e:
        print(f"Error fetching top articles: {str(e)}")
        return None, None

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

print(f"\nFetching top {TOP_ARTICLES} articles for the last {TIME} days:")
result = fetch_top_articles(TIME, COUNTRY, TOP_ARTICLES)
if result[0] is not None:
    df, region = result
    region_text = "worldwide" if region == "ALL" else f"in {region}"
    print(f"\nTop viewed articles {region_text}:")
    for _, row in df.iterrows():
        print(f"Rank {row['rank']}: {row['article']} - {row['views']:,} views")
    print(f"\nDetailed data saved to top_articles_{region.lower()}_{TIME}days.csv")

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