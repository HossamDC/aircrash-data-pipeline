import psycopg2

# Redshift connection details
host = "demo-cluster.cnp6ksjha1o5.us-west-2.redshift.amazonaws.com"
port = 5439
dbname = "demo_db"
user = "admin"
password = "YourStrongPassword123!"

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

# SQL to drop old table
drop_table_sql = f"""
DROP TABLE IF EXISTS {schema_name}.{table_name};
"""

# ✅ SQL to create table with the correct schema including `crash_severity`
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
  year int
)
STORED AS PARQUET
LOCATION 's3://my-spark-stage-23-3-1998-v1-01/plane_crashes/processed_parquet/';
"""

# ✅ Run it
def main():
    print("🚀 Connecting to Redshift...")
    conn = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
    )
    conn.autocommit = True
    cur = conn.cursor()

    print("🧱 Ensuring schema exists...")
    cur.execute(create_schema_sql)

    print("🧨 Dropping old table if exists...")
    cur.execute(drop_table_sql)

    print("✅ Creating new external table with full schema...")
    cur.execute(create_table_sql)

    cur.close()
    conn.close()
    print("🎯 Done! Table created successfully.")

if __name__ == "__main__":
    main()
