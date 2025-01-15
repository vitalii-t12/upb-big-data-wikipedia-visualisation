import json
import os
import sys

import requests
from pyhdfs import HdfsClient

hdfs_host = os.getenv("HDFS_HOST", "localhost:50070")  # Default value if not set
print(f"HDFS Host: {hdfs_host}")
BASE_FOLDER_PATH = "/user/zeppelin/top-by-country"
DEFAULT_USER = "zeppelin"

# Parse arguments
year = sys.argv[1]  # First argument: year
month = sys.argv[2]  # Second argument: month, remove leading zero if present
month = f"{int(month):02d}"

def get_views_per_country(year, month):
    # Construct the API URL
    url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/top-by-country/en.wikipedia.org/all-access/{year}/{month}"
    print(url)
    # Headers with User-Agent
    headers = {
        "User-Agent": "YourAppName/1.0 (contact@example.com)"
    }

    try:
        # Make the GET request
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise error for HTTP issues

        # Parse JSON response
        data = response.json()
        return data

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

def process_request():
    # Example usage
    hdfs = HdfsClient(hosts=hdfs_host, user_name=DEFAULT_USER)

    print('=' * 60)
    hdfs.mkdirs("/user/hdfs/zeppelin_test")
    print('=' * 60)

    connected_user = hdfs.user_name
    print(f"Connected HDFS user: {connected_user}")

    file_path = f"{BASE_FOLDER_PATH}/{year}/countries_visits_{year}_{month}.json"
    print(f"Checking for data at: {file_path}")

    if not hdfs.exists(file_path):
        print(f"Data for {year}-{month} is missing. Downloading...")
        data = get_views_per_country(year, month)

        print(os.path.dirname(file_path))
        hdfs.mkdirs(os.path.dirname(file_path))
        hdfs.create(file_path, overwrite=True, data=json.dumps(data, indent=4).encode('utf-8'))

        print(f"Data for {year}-{month} saved to HDFS.")
        # Add fetching and saving logic here
    else:
        print(f"Data for {year}-{month} already exists.")

process_request()
# # backend-top-by-country.py
#
# from pyhdfs import HdfsClient
# import os
# from pyspark.sql import SparkSession
#
# # Initialize Spark session
# spark = SparkSession.builder.appName("DynamicDataFetch").getOrCreate()
#
# hdfs_host = os.getenv("HDFS_HOST", "localhost:50070")  # Default value if not set
# print(f"HDFS Host: {hdfs_host}")
#
# # User inputs
# year = z.input("year", "2024")
# month = z.input("month", "01")
# #
#
# def process_data(hdfs_host, year, month):
#     hdfs = HdfsClient(hosts=hdfs_host, user_name="hadoop-user")
#     file_path = f"/data/{year}_{month}.json"
#
#     if not hdfs.exists(file_path):
#         print(f"Data for {year}-{month} is missing. Fetching...")
#         # Add your logic to fetch data from the API and save it
#         print(f"Data for {year}-{month} saved to HDFS.")
#     else:
#         print(f"Data for {year}-{month} already exists.")
#
#     return f"HDFS file path: {file_path}"
#

# %pyspark
#
# import os
# import requests
# from pyhdfs import HdfsClient
# from pyspark.sql import SparkSession
#

# # User inputs
# year = z.input("year", "2024")
# month = z.input("month", "01")
#
# print(f"Fetching data for {year}-{month}...")
# # HDFS client setup
# hdfs = HdfsClient(hosts=hdfs_host, user_name='hadoop')
# file_path = f"/user/input/top-by-country/{year}/country_visits_{year}_{month}.json"
#
#
# def fetch_and_save_data(year, month, file_path):
#     """Fetch data from API and save to HDFS if not already present."""
#     if not hdfs.exists(file_path):
#         print(f"Data for {year}-{month} not found in HDFS. Fetching...")
#
#         # Fetch data from API
#         api_url = f"https://api.example.com/data?year={year}&month={month}"
#         response = requests.get(api_url)
#
#         if response.status_code == 200:
#             # Save fetched data to HDFS
#             hdfs.create(file_path, response.content, overwrite=True)
#             print(f"Data for {year}-{month} saved to HDFS.")
#         else:
#             raise Exception(f"API call failed with status: {response.status_code}")
#     else:
#         print(f"Data for {year}-{month} already exists in HDFS.")
#
#
# # Step 1: Check and fetch data if missing
# fetch_and_save_data(year, month, file_path)
#
# # Step 2: Load data into Spark DataFrame
# hdfs_uri = f"hdfs://localhost:9000{file_path}"  # Update with your HDFS URI
# df = spark.read.json(hdfs_uri)
#
# # Step 3: Display the DataFrame
# df.show()
