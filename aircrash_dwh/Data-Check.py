import pandas as pd

path = "s3://my-spark-stage-23-3-1998-v1-01/plane_crashes/processed_parquet/year=2009/part-00000-e7a9927f-da2c-44d8-a0b2-70d3d834e511.c000.snappy.parquet"

df = pd.read_parquet(path, engine="pyarrow")
print(df.columns)
print(df.head())
