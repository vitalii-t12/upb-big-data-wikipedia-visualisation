import requests
import json
from datetime import datetime, timedelta
from urllib.parse import quote

def fetch_pageviews(title):
    encoded_title = quote(title.replace(" ", "_"))
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/all-agents/{encoded_title}/daily/{start_date.strftime('%Y%m%d')}/{end_date.strftime('%Y%m%d')}"
    
    # Add required headers
    headers = {
        'User-Agent': 'MyWikipediaApp/1.0 (your-email@example.com)',
        'Accept': 'application/json'
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            total_views = sum(item['views'] for item in data['items'])
            daily_average = total_views / len(data['items'])
            return {
                'total_views': total_views,
                'daily_average': round(daily_average, 2),
                'status': 'success'
            }
        else:
            print(f"API Error: Status Code {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"Error fetching pageviews: {str(e)}")
        return None

# Test the function
title = "Elon_Musk"
pageview_data = fetch_pageviews(title)
if pageview_data:
    print(f"Page views for {title}:")
    print(f"Total views: {pageview_data['total_views']:,}")
    print(f"Daily average: {pageview_data['daily_average']:,.2f}")