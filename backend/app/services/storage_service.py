import os
from google.cloud import storage
from dotenv import load_dotenv
from datetime import datetime
from pebble import ProcessPool
import concurrent.futures

load_dotenv()

def get_bucket_info_for_process(bucket_name, project_id):
    from google.cloud import storage
    print(f"[DEBUG] Processing bucket: {bucket_name}")
    client = storage.Client(project=project_id)
    bucket = client.get_bucket(bucket_name)
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
        import time

        all_buckets = []
        try:
            all_buckets = list(client.list_buckets(project=project_id))
            print(f"[DEBUG] Total buckets to process: {len(all_buckets)}")
        except Exception as e:
            print(f"[ERROR] StorageService.list_buckets: {e}")
            return buckets

        max_workers = int(os.getenv("GCP_GCS_FETCH_MAX_WORKERS", 8))
        print(f"[DEBUG] Using max_workers={max_workers} for bucket size processes")
        timeout = int(os.getenv("BACKEND_GCS_FETCH_TIMEOUT", 60))
        per_bucket_timeout = int(os.getenv("BACKEND_GCS_PER_BUCKET_TIMEOUT", 30))
        start = time.time()
        completed_buckets = set()
        future_to_bucket = {}
        with ProcessPool(max_workers=max_workers) as pool:
            for bucket in all_buckets:
                print(f"[TRACE] Scheduling process for bucket: {bucket.name}")
                future = pool.schedule(get_bucket_info_for_process, args=(bucket.name, project_id), timeout=per_bucket_timeout)
                future_to_bucket[future] = bucket
            unfinished = set(future_to_bucket.keys())
            while unfinished:
                now = time.time()
                elapsed = now - start
                print(f"[TRACE] Elapsed time: {elapsed:.2f}s, {len(unfinished)} unfinished, {len(completed_buckets)} completed")
                if elapsed > timeout:
                    print("[WARN] Timeout reached while fetching bucket sizes.")
                    break
                done = set()
                for future in list(unfinished):
                    if future.done():
                        try:
                            info = future.result()
                            print(f"[TRACE] Completed process for bucket: {future_to_bucket[future].name}")
                            buckets.append(info)
                            completed_buckets.add(future_to_bucket[future].name)
                        except concurrent.futures.TimeoutError:
                            print(f"[WARN] Per-bucket timeout for {future_to_bucket[future].name}")
                            buckets.append({
                                "name": future_to_bucket[future].name,
                                "location": future_to_bucket[future].location,
                                "location_type": getattr(future_to_bucket[future], "location_type", "region"),
                                "storage_class": future_to_bucket[future].storage_class,
                                "size": "Timed out",
                                "size_last_updated": "",
                                "created": future_to_bucket[future].time_created.strftime("%Y-%m-%d %H:%M:%S") if future_to_bucket[future].time_created else "",
                                "last_modified": "",
                                "public_access": "Unknown",
                                "labels": ", ".join(f"{k}:{v}" for k, v in (getattr(future_to_bucket[future], "labels", {}) or {}).items()),
                            })
                        except Exception as exc:
                            print(f"[ERROR] Exception in bucket process: {exc}")
                        done.add(future)
                unfinished -= done
                time.sleep(0.2)
            # After timeout, do not wait for unfinished futures; just mark as timed out
            print(f"[TRACE] Completed buckets: {len(completed_buckets)}, Timed out: {len(all_buckets) - len(completed_buckets)}")
            for bucket in all_buckets:
                if bucket.name not in completed_buckets:
                    print(f"[WARN] Bucket {bucket.name} size could not be processed within timeout.")
                    buckets.append({
                        "name": bucket.name,
                        "location": bucket.location,
                        "location_type": getattr(bucket, "location_type", "region"),
                        "storage_class": bucket.storage_class,
                        "size": "Timed out",
                        "size_last_updated": "",
                        "created": bucket.time_created.strftime("%Y-%m-%d %H:%M:%S") if bucket.time_created else "",
                        "last_modified": "",
                        "public_access": "Unknown",
                        "labels": ", ".join(f"{k}:{v}" for k, v in (bucket.labels or {}).items()) if hasattr(bucket, "labels") else "",
                    })
        return buckets
