# upb-big-data-wikipedia-visualisation

# Big Data Setup with Hadoop and Zeppelin

## Table of Contents
- [Prerequisites](#prerequisites)
- [Setup Instructions](#setup-instructions)
  - [Clone the repository](#clone-the-repository)
  - [Build and start the containers](#build-and-start-the-containers)
  - [Access the web interfaces](#access-the-web-interfaces)
  - [Use Zeppelin to interact with Hadoop](#use-zeppelin-to-interact-with-hadoop)


## Prerequisites
- Docker and Docker Compose installed.

## Setup Instructions
1. Clone the repository:
   ```bash
   git clone https://github.com/vitalii-t12/upb-big-data-wikipedia-visualisation.git
   cd upb-big-data-wikipedia-visualisation
    ```

2. Build and start the containers:

    ``` bash
    docker-compose up --build


3. Access the web interfaces:

- Hadoop Namenode UI: http://localhost:9870
- Zeppelin UI: http://localhost:8080

4. Use Zeppelin to interact with Hadoop via SQL or other interpreters.
 

# Hadoop configuration
To connect to Hadoop CLI from the terminal, you can use the following command:
   ```bash
     docker exec -it hadoop bash
  ```
To add hadoop user:
    ```bash
      adduser --disabled-password --gecos "" hadoop
     ```
Set apropriate permissions for the Hadoop directories:
   ```bash
    chown -R hadoop:hadoop /opt/hadoop
   ```

## Working with data
### Get top countries by pageviews
To load data, you have to open the `playground` notebook and select the dates that you want to download data for.
Unprocessed data is saved at `/user/zeppelin/top-by-country/raw/countries_visits_{year}_{month}.json`


### Process countries by pageviews
To process data from `/user/zeppelin/top-by-country/raw` you have to follow the next steps:
Connect to `spark-master` container:
```bash
docker exec -it spark-master bash
```

And run the next script:
```bash
./spark-submit  /spark-scripts/process-top-by-country.py
```

The output will be saved at path `/user/zeppelin/top-by-country/processed/processed.parquet` 


### Process large CSV with geographical data
To process data from `/data/articles-in-range/10_km.csv` you have to follow the next steps:

- Check that `10_km.csv` file is in the `/data/articles-in-range/` folder (this folder is mounted to the `namenode` container)

- Upload the `10_km.csv` file to HDFS (run this command in `namenode` container):
```bash
- hadoop fs -put /data/articles-in-range/10_km.csv /user/zeppelin/articles-in-range/raw
```

Connect to `spark-master` container:
```bash
docker exec -it spark-master bash
```

And run the next script (from `/spark/bin` folder:
```bash
./spark-submit /spark-scripts/process-articles-in-range.py
```

## Future Enhancements

To improve the capabilities and performance of the system, several tools and frameworks can be integrated:

1. **Apache Airflow**: Automates workflows, ensuring tasks are executed in sequence, with real-time monitoring and error handling.
2. **Apache Hive**: Introduces a SQL-like interface for querying processed data, enabling easier access for non-technical users and serving as a robust data warehouse.
3. **Grafana**: Enhances visualization and monitoring, providing advanced dashboards for real-time system metrics and resource usage tracking.
4. **Apache Kafka and Apache Flink**: Enables real-time data ingestion and processing, allowing analysis of trends as they emerge.
5. **Machine Learning Models**: Adds intelligence to the system by implementing trend analysis and predictive models using TensorFlow or PyTorch.

These enhancements will make the system more scalable, user-friendly, and capable of handling complex analytical workflows.
