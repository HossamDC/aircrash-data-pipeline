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

conn = psycopg2.connect(
    dbname=dbname, user=user, password=password, host=host, port=port
)
conn.autocommit = True
cur = conn.cursor()

# 👇 نجيب كل مسارات البارتيشن ونسحب منها السنة باستخدام regex
fetch_sql = f"""
SELECT location FROM SVV_EXTERNAL_PARTITIONS
WHERE schemaname = '{schema}' AND tablename = '{table}';
"""
cur.execute(fetch_sql)
locations = [row[0] for row in cur.fetchall()]

# Extract year using regex
years = []
for loc in locations:
    match = re.search(r"year=(\d{4})", loc.lower())
    if match:
        years.append(match.group(1))

print(f"📦 Found {len(years)} partitions to drop")

# Drop each partition
for year in sorted(set(years)):
    print(f"🧨 Dropping partition year={year}")
    try:
        sql = f"ALTER TABLE {schema}.{table} DROP PARTITION (year = '{year}');"
        cur.execute(sql)
    except Exception as e:
        print(f"❌ Error dropping year={year}: {e}")

cur.close()
conn.close()
print("✅ Done dropping all partitions.")
