import logging
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # Initialize Spark session
    logger.info("Initializing Spark session")
    spark = SparkSession.builder \
        .appName("Process Country Visits") \
        .getOrCreate()

    # Load raw JSON files
    logger.info("Loading raw JSON files from HDFS")
    raw_data = spark.read.json("hdfs://192.168.1.10:9000/user/zeppelin/top-by-country/raw/*.json", multiLine=True)
    raw_data1 = spark.read.json("hdfs://192.168.1.10:9000/user/zeppelin/top-by-country/raw/countries_visits_2024_01.json", multiLine=True)
    # raw_data = spark.read.json("hdfs://namenode:9000/user/zeppelin/top-by-country/raw/*.json")

    # Extract relevant fields and flatten the data
    logger.info("Processing raw data")
    processed_data = raw_data.withColumn("country_data", explode(col("items")[0]["countries"])) \
        .select(
        col("items")[0]["year"].alias("year"),
        col("items")[0]["month"].alias("month"),
        col("country_data.country").alias("country"),
        col("country_data.views_ceil").cast("long").alias("views"),
        col("country_data.rank").alias("rank")
    )

    # Write data partitioned by year and month
    output_path = "hdfs://namenode:9000/user/zeppelin/top-by-country/processed/processed_data.parquet"
    logger.info(f"Writing processed data to {output_path}")
    processed_data.write \
        .partitionBy("year", "month") \
        .mode("overwrite") \
        .parquet(output_path)

    logger.info("Stopping Spark session")
    spark.stop()
    logger.info("Processing completed")
