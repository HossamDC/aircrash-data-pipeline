from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    to_date, year, month, col, when, round, split, trim
)

# Create Spark Session
spark = SparkSession.builder.appName("HFPlaneCrashes").getOrCreate()

# Load CSV from S3
df = spark.read.option("header", True).csv("s3://my-spark-stage-23-3-1998-v1-01/plane_crashes/raw_hf_airplane_crashes.csv")

# Clean and cast numeric fields
df = df.withColumn("Aboard", col("Aboard").cast("int")) \
       .withColumn("Fatalities", col("Fatalities").cast("int")) \
       .withColumn("Ground", col("Ground").cast("int"))

# Parse Date
df = df.withColumn("Crash_Date", to_date("Date", "MM/dd/yyyy")) \
       .withColumn("Year", year("Crash_Date")) \
       .withColumn("Month", month("Crash_Date"))

# Aircraft Maker
df = df.withColumn("Aircraft_Maker", trim(split(col("Type"), " ").getItem(0)))

# Survivors
df = df.withColumn("Survivors", (col("Aboard") - col("Fatalities")))

# Crash Severity
df = df.withColumn("Severity_Pct", round((col("Fatalities") / col("Aboard")) * 100, 1))
df = df.withColumn("Crash_Severity", when(col("Fatalities") == 0, "None")
                   .when(col("Severity_Pct") < 5, "Low")
                   .when(col("Severity_Pct") < 30, "Medium")
                   .otherwise("High"))

# Is Fatal Flag
df = df.withColumn("Is_Fatal", (col("Fatalities") > 0).cast("boolean"))

# Final columns
df_final = df.select(
    "Crash_Date", "Year", "Location", "Operator", "Type",
    "Aircraft_Maker", "Aboard", "Fatalities", "Ground", "Survivors",
    "Is_Fatal", "Crash_Severity"
)

# Write Parquet partitioned by Year only
df_final.write.mode("overwrite") \
    .partitionBy("Year") \
    .parquet("s3://my-spark-stage-23-3-1998-v1-01/plane_crashes/processed_parquet/")

print("✅ ETL Complete: Parquet written to S3 partitioned by Year only.")
