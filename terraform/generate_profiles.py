import json
import os

# اقرأ مخرجات Terraform
with open("tf_outputs.json") as f:
    tf_outputs = json.load(f)

# استخرج القيم
host_with_port = tf_outputs["redshift_host"]["value"]
host = host_with_port.split(":")[0]  # 🔧 نحذف البورت لو موجود
dbname = tf_outputs["redshift_db"]["value"]
user = tf_outputs["redshift_user"]["value"]
password = "YourStrongPassword123!"  # 🔐 حطها يدويًا أو من source آمن

# بناء الـ profile
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
      sslmode: require
"""

# أنشئ مجلد dbt إذا مش موجود
os.makedirs(os.path.expanduser("~/.dbt"), exist_ok=True)

# اكتب الـ profile
with open(os.path.expanduser("~/.dbt/profiles.yml"), "w") as f:
    f.write(profile)

print("✅ profiles.yml generated at ~/.dbt/profiles.yml")
