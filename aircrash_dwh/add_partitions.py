import boto3
import psycopg2
import psycopg2.extensions

# Redshift connection
host = "demo-cluster.cnp6ksjha1o5.us-west-2.redshift.amazonaws.com"
port = 5439
dbname = "demo_db"
user = "admin"
password = "YourStrongPassword123!"

# S3 settings
bucket = "my-spark-stage-23-3-1998-v1-01"
prefix = "plane_crashes/processed_parquet/"

# Table config
schema_name = "spectrum_schema"
table_name = "airplane_crashes_parquet"

# Connect to Redshift with autocommit
conn = psycopg2.connect(
    dbname=dbname,
    user=user,
    password=password,
    host=host,
    port=port
)
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
cur = conn.cursor()

# Get list of partitions from S3
s3 = boto3.client("s3")
paginator = s3.get_paginator("list_objects_v2")
pages = paginator.paginate(Bucket=bucket, Prefix=prefix)

partitions = set()
for page in pages:
    for obj in page.get("Contents", []):
        key = obj["Key"]
        if "Year=" in key and "Month=" in key:
            parts = key.split("/")
            year = next((p.split("=")[1] for p in parts if p.startswith("Year=")), None)
            month = next((p.split("=")[1] for p in parts if p.startswith("Month=")), None)
            if year and month:
                partitions.add((year, month))

print(f"🔍 Found {len(partitions)} partitions in S3")

# Add partitions one by one with autocommit
for year, month in sorted(partitions):
    s3_path = f"s3://{bucket}/{prefix}Year={year}/Month={month}/"
    sql = f"""
    ALTER TABLE {schema_name}.{table_name}
    ADD IF NOT EXISTS PARTITION (year = '{year}', month = '{month}')
    LOCATION '{s3_path}';
    """
    print(f"⚙️ Adding partition: Year={year}, Month={month}")
    cur.execute(sql)

print("✅ All partitions added successfully.")

cur.close()
conn.close()
