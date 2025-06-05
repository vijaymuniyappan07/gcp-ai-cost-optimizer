import os
import json
from google.cloud import storage
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def main():
    project_id = os.getenv("GCP_PROJECT_ID")
    if not project_id:
        print("GCP_PROJECT_ID not set in .env")
        return

    client = storage.Client(project=project_id)
    cache = {}
    print(f"Fetching bucket sizes for project: {project_id}")
    for bucket in client.list_buckets(project=project_id):
        print(f"Processing bucket: {bucket.name}")
        total_size = 0
        try:
            for blob in client.list_blobs(bucket.name):
                total_size += blob.size or 0
            if total_size >= 1024**3:
                size_str = f"{round(total_size / (1024**3), 2)} GB"
            elif total_size >= 1024**2:
                size_str = f"{round(total_size / (1024**2), 2)} MB"
            elif total_size >= 1024:
                size_str = f"{round(total_size / 1024, 2)} KB"
            else:
                size_str = f"{total_size} B"
            cache[bucket.name] = {
                "size": size_str,
                "last_updated": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
            }
            print(f"  Size: {size_str}")
        except Exception as e:
            print(f"  [WARN] Could not fetch size for bucket {bucket.name}: {e}")
            cache[bucket.name] = {
                "size": "N/A",
                "last_updated": ""
            }
    cache_file = os.getenv("GCS_BUCKET_SIZE_CACHE", "storage_bucket_sizes.json")
    with open(cache_file, "w") as f:
        json.dump(cache, f, indent=2)
    print(f"Bucket size cache written to {cache_file}")

if __name__ == "__main__":
    main()
