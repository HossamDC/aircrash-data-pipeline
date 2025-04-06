import json
import os

# اقرأ الـ terraform output
with open("tf_outputs.json") as f:
    tf_outputs = json.load(f)

# استخرج القيم
host = tf_outputs["redshift_host"]["value"]
dbname = tf_outputs["redshift_db"]["value"]
user = tf_outputs["redshift_user"]["value"]
password = "YourStrongPassword123!"  # 🔐 حطها manually أو خزنها بمصدر آمن

# بُنية ملف dbt profile
profile = f"""
aircrash_dwh:
  target: dev
  outputs:
    dev:
      type: redshift
      host: {host}
      user: {user}
      password: {password}
      port: 5439
      dbname: {dbname}
      schema: public
      threads: 4
      keepalives_idle: 0
      connect_timeout: 10
      sslmode: prefer
"""

# أنشئ المجلد إذا مش موجود
os.makedirs(os.path.expanduser("~/.dbt"), exist_ok=True)

# اكتب الملف
with open(os.path.expanduser("~/.dbt/profiles.yml"), "w") as f:
    f.write(profile)

print("✅ profiles.yml generated at ~/.dbt/profiles.yml")
