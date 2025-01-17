from pyspark.sql import SparkSession

if __name__ == "__main__":
    # Initialize Spark session
    spark = SparkSession.builder \
        .appName("Process Cities CSV") \
        .getOrCreate()

    # Path to the CSV file
    csv_path = "/user/zeppelin/articles-in-range/raw/10_km.csv"

    # Load the CSV file into a DataFrame
    df = spark.read.csv(csv_path, header=True, inferSchema=True)

    # Select and rename the required columns
    processed_df = df.select(
        "city",
        "lat",
        "lng",
        "country",
        df["iso2"].alias("country_code"),
        "population",
        "articles_within_10km"
    )

    # Path to save the processed Parquet file
    parquet_output_path = "hdfs://namenode:9000//user/zeppelin/articles-in-range/processed/processed.parquet"

    # Write the DataFrame to Parquet format
    processed_df.write.mode("overwrite").parquet(parquet_output_path)

    # Stop the Spark session
    spark.stop()
