from pyspark.sql import SparkSession
from pyspark.sql.functions import col

# ✅ Create spark session
spark = SparkSession.builder.appName("LocalDataTest").getOrCreate()

# ✅ Create small DataFrame manually
data = [
    ("Airbus", 180, 150),
    ("Boeing", 200, 180),
    ("Cessna", 4, 2),
    ("Antonov", 50, 45)
]

columns = ["Aircraft_Type", "Aboard", "Survivors"]

df = spark.createDataFrame(data, columns)

# ✅ Add derived column: Survival Rate
df = df.withColumn("Survival_Rate", (col("Survivors") / col("Aboard")) * 100)

# ✅ Show results
df.show()

# ✅ Row count
print(f"✅ Number of rows: {df.count()}")

# ✅ Done
spark.stop()
