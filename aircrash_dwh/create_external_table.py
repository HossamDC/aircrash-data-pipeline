import psycopg2

# Redshift connection details
host = "demo-cluster.cnp6ksjha1o5.us-west-2.redshift.amazonaws.com"
port = 5439
dbname = "demo_db"
user = "admin"
password = "YourStrongPassword123!"  # ← غيّرها لو مختلف

# External schema/table config
schema_name = "spectrum_schema"
table_name = "airplane_crashes_parquet"
external_db = "airplane_crashes"
iam_role_arn = "arn:aws:iam::381492085524:role/RedshiftSpectrumRole"

# SQL to create external schema
create_schema_sql = f"""
CREATE EXTERNAL SCHEMA IF NOT EXISTS {schema_name}
FROM data catalog
DATABASE '{external_db}'
IAM_ROLE '{iam_role_arn}';
"""

# SQL to create external table
create_table_sql = f"""
CREATE EXTERNAL TABLE {schema_name}.{table_name} (
  crash_date        date,
  location          varchar,
  operator          varchar,
  type              varchar,
  aircraft_maker    varchar,
  aboard            int,
  fatalities        int,
  ground            int,
  survivors         int,
  is_fatal          boolean,
  crash_severity    varchar
)
PARTITIONED BY (
  year varchar,
  month varchar
)
STORED AS PARQUET
LOCATION 's3://my-spark-stage-23-3-1998-v1-01/plane_crashes/processed_parquet/';
"""

# Connect to Redshift
conn = psycopg2.connect(
    dbname=dbname,
    user=user,
    password=password,
    host=host,
    port=port
)
cur = conn.cursor()

# Step 1: Create external schema if not exists
print(f"🧱 Ensuring external schema exists: {schema_name}")
cur.execute(create_schema_sql)
conn.commit()

# Step 2: Check if external table exists
check_sql = f"""
SELECT 1 FROM SVV_EXTERNAL_TABLES
WHERE schemaname = '{schema_name}'
AND tablename = '{table_name}';
"""
cur.execute(check_sql)
exists = cur.fetchone()

# Step 3: Create external table if it doesn't exist
if exists:
    print(f"✅ External table already exists: {schema_name}.{table_name}")
else:
    print(f"⚙️ Creating external table: {schema_name}.{table_name}")
    cur.execute(create_table_sql)
    conn.commit()
    print("✅ Table created!")

cur.close()
conn.close()
