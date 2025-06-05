import os
from google.cloud import storage
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

class StorageService:
    def __init__(self, project_id=None):
        env_projects = os.getenv("GCP_PROJECT_ID", "")
        self.project_ids = [p.strip() for p in env_projects.split(",") if p.strip()]
        if not self.project_ids:
            raise ValueError("GCP_PROJECT_ID environment variable is not set. Please add it to your .env file.")
        self.project_id = project_id or self.project_ids[0]

    def list_buckets(self, project_id=None):
        project_id = project_id or self.project_id
        client = storage.Client(project=project_id)
        buckets = []
        from concurrent.futures import ThreadPoolExecutor, as_completed

        def get_bucket_info(bucket):
            print(f"[DEBUG] Processing bucket: {bucket.name}")
            location_type = getattr(bucket, "location_type", "region")
            public_access = "No"
            try:
                policy = bucket.get_iam_policy(requested_policy_version=3)
                for binding in policy.bindings:
                    if "allUsers" in binding["members"] or "allAuthenticatedUsers" in binding["members"]:
                        public_access = "Yes"
                        break
            except Exception:
                public_access = "Unknown"
            last_modified = ""
            try:
                if hasattr(bucket, "updated") and bucket.updated:
                    last_modified = bucket.updated.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    blobs = list(client.list_blobs(bucket.name, max_results=1, order_by=["-updated"]))
                    if blobs:
                        last_modified = blobs[0].updated.strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                last_modified = ""
            # Size: sum of all object sizes (expensive for large buckets)
            size = ""
            try:
                total_size = 0
                for blob in client.list_blobs(bucket.name):
                    total_size += blob.size or 0
                if total_size > 0:
                    if total_size >= 1024**3:
                        size = f"{round(total_size / (1024**3), 2)} GB"
                    elif total_size >= 1024**2:
                        size = f"{round(total_size / (1024**2), 2)} MB"
                    elif total_size >= 1024:
                        size = f"{round(total_size / 1024, 2)} KB"
                    else:
                        size = f"{total_size} B"
            except Exception as e:
                print(f"[WARN] Could not fetch size for bucket {bucket.name}: {e}")
            labels = ", ".join(f"{k}:{v}" for k, v in (bucket.labels or {}).items()) if hasattr(bucket, "labels") else ""
            return {
                "name": bucket.name,
                "location": bucket.location,
                "location_type": location_type,
                "storage_class": bucket.storage_class,
                "size": size,
                "created": bucket.time_created.strftime("%Y-%m-%d %H:%M:%S") if bucket.time_created else "",
                "last_modified": last_modified,
                "public_access": public_access,
                "labels": labels,
            }

        try:
            all_buckets = list(client.list_buckets(project=project_id))
            print(f"[DEBUG] Total buckets to process: {len(all_buckets)}")
            max_workers = int(os.getenv("GCP_GCS_FETCH_MAX_WORKERS", 8))
            print(f"[DEBUG] Using max_workers={max_workers} for bucket size threads")
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_bucket = {executor.submit(get_bucket_info, bucket): bucket for bucket in all_buckets}
                for future in as_completed(future_to_bucket):
                    try:
                        info = future.result()
                        buckets.append(info)
                    except Exception as exc:
                        print(f"[ERROR] Exception in bucket thread: {exc}")
        except Exception as e:
            print(f"[ERROR] StorageService.list_buckets: {e}")
        return buckets
