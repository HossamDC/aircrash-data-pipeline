import boto3
import psycopg2
import re

# Redshift connection details
host = "demo-cluster.cnp6ksjha1o5.us-west-2.redshift.amazonaws.com"
port = 5439
dbname = "demo_db"
user = "admin"
password = "YourStrongPassword123!"

schema = "spectrum_schema"
table = "airplane_crashes_parquet"
bucket = "my-spark-stage-23-3-1998-v1-01"
prefix = "plane_crashes/processed_parquet/"

conn = psycopg2.connect(
    dbname=dbname, user=user, password=password, host=host, port=port
)
conn.autocommit = True
cur = conn.cursor()

s3 = boto3.client("s3")
result = s3.list_objects_v2(Bucket=bucket, Prefix=prefix, Delimiter='/')

partitions = []
for obj in result.get('CommonPrefixes', []):
    key = obj['Prefix']
    match = re.search(r"year=(\d{4})", key)
    if match:
        year = match.group(1)
        s3_path = f"s3://{bucket}/{key}"
        print(f"🧩 Registering partition year={year} -> {s3_path}")
        sql = f"""
        ALTER TABLE {schema}.{table}
        ADD IF NOT EXISTS PARTITION (year = {year})
        LOCATION '{s3_path}';
        """
        try:
            cur.execute(sql)
        except Exception as e:
            print(f"❌ Error adding year={year}: {e}")

cur.close()
conn.close()
print("✅ Partition registration complete.")
