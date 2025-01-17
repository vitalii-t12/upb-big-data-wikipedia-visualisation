# Sparc commands

To run the spark scripts, you can use the following commands:
```bash
./spark-submit  /spark-scripts/process-top-by-country.py
```

```bash
hadoop fs -put /data/articles-in-range/10_km.csv /user/zeppelin/articles-in-range/raw
```

```bash
./spark-submit /spark-scripts/process-articles-in-range.py```