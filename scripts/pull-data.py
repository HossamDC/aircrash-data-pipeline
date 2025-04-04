#!pip install datasets s3fs pandas

import pandas as pd
from datasets import load_dataset
import s3fs

# Step 1: Load dataset from Hugging Face
dataset = load_dataset("nateraw/airplane-crashes-and-fatalities", split="train")
df = pd.DataFrame(dataset)

# Step 2: Initialize S3 with correct region
fs = s3fs.S3FileSystem(anon=False, client_kwargs={"region_name": "us-west-2"})

# Step 3: Define path (NO 's3://' prefix when using s3fs.open)
s3_path = "my-spark-stage-23-3-1998-v1-01/plane_crashes/raw_hf_airplane_crashes.csv"

# Step 4: Upload
with fs.open(s3_path, "w") as f:
    df.to_csv(f, index=False)

print("✅ Uploaded to:", s3_path)
