import pyarrow.parquet as pq
import s3fs

s3 = s3fs.S3FileSystem()

# S3 prefix path to list files under
prefix = "my-spark-stage-23-3-1998-v1-01/plane_crashes/processed_parquet/Year=1981/Month=1/"

# احصل على قائمة الملفات الفعلية
files = s3.ls(prefix)

# خذ أول ملف موجود
first_file = files[0]
print(f"🔍 Reading: {first_file}")

# اقرأ الـ schema
with s3.open(first_file, 'rb') as f:
    table = pq.read_table(f)
    schema = table.schema

# اطبع الـ schema
print("📄 Schema:")
for field in schema:
    print(f"{field.name} — {field.type}")

