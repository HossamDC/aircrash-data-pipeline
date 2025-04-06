import pyarrow.parquet as pq
import pyarrow as pa
import s3fs
import boto3
import pandas as pd
import os

bucket = "my-spark-stage-23-3-1998-v1-01"
input_prefix = "plane_crashes/processed_parquet_year_only/"
output_prefix = "plane_crashes/processed_parquet/"

fs = s3fs.S3FileSystem()
s3 = boto3.client("s3")

# 1. Get all folders Year=YYYY/data.parquet/*.parquet
paginator = s3.get_paginator("list_objects_v2")
pages = paginator.paginate(Bucket=bucket, Prefix=input_prefix)

parquet_paths = []
for page in pages:
    for obj in page.get("Contents", []):
        key = obj["Key"]
        if key.endswith(".parquet") and "Year=" in key and "data.parquet/" in key:
            parquet_paths.append(f"s3://{bucket}/{key}")

print(f"🔍 Found {len(parquet_paths)} parquet files to reorganize")

# 2. Read each and write directly to new Year=YYYY/ folder
for path in parquet_paths:
    try:
        print(f"📥 Reading {path}")
        table = pq.read_table(path, filesystem=fs)
        df = table.to_pandas()

        # Extract year from path
        year = path.split("Year=")[1].split("/")[0]
        output_path = f"s3://{bucket}/{output_prefix}Year={year}/"

        print(f"📝 Writing to {output_path}")
        table_out = pa.Table.from_pandas(df)
        pq.write_to_dataset(table_out, root_path=output_path, filesystem=fs)

    except Exception as e:
        print(f"❌ Error with {path}: {e}")

print("✅ Re-organization to processed_parquet/Year=YYYY/ complete.")
