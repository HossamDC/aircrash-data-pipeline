from pyspark.sql import SparkSession
from pyspark.sql.functions import to_date, year, month, col, when, round, split, trim

# Create Spark session
spark = SparkSession.builder.appName("RewriteForRedshift").getOrCreate()

# Read original CSV
df = spark.read.option("header", True).csv("s3://my-spark-stage-23-3-1998-v1-01/plane_crashes/raw_hf_airplane_crashes.csv")

# Transformations
df = df.withColumn("crash_date", to_date("Date", "MM/dd/yyyy")) \
       .withColumn("year", year("crash_date")) \
       .withColumn("aircraft_maker", trim(split(col("Type"), " ").getItem(0))) \
       .withColumn("aboard", col("Aboard").cast("int")) \
       .withColumn("fatalities", col("Fatalities").cast("int")) \
       .withColumn("ground", col("Ground").cast("int")) \
       .withColumn("survivors", (col("aboard") - col("fatalities"))) \
       .withColumn("severity_pct", round((col("fatalities") / col("aboard")) * 100, 1)) \
       .withColumn("crash_severity", when(col("fatalities") == 0, "None")
                   .when(col("severity_pct") < 5, "Low")
                   .when(col("severity_pct") < 30, "Medium")
                   .otherwise("High")) \
       .withColumn("is_fatal", (col("fatalities") > 0).cast("boolean"))

# Final columns in lowercase to match Redshift schema
df_final = df.select(
    "crash_date", "Location", "Operator", "Type", "aircraft_maker",
    "aboard", "fatalities", "ground", "survivors", "is_fatal",
    "crash_severity", "year"
)

# Repartition by year and write to S3
df_final.write.mode("overwrite") \
    .partitionBy("year") \
    .option("compression", "snappy") \
    .parquet("s3://my-spark-stage-23-3-1998-v1-01/plane_crashes/processed_parquet/")

print("✅ Parquet rewritten with compatible schema for Redshift Spectrum.")
