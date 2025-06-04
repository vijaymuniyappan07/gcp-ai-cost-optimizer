from google.cloud import compute_v1
from google.auth.exceptions import DefaultCredentialsError
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

GEO_MAP = {
    "us": ["us-"],
    "europe": ["europe-"],
    "asia": ["asia-"],
    "australia": ["australia-"],
    "southamerica": ["southamerica-"],
    "northamerica": ["northamerica-"],
    "canada": ["northamerica-", "canada-"],
    "africa": ["africa-"],
    "me": ["me-"],
    "asia-pacific": ["asia-", "australia-"],
    "global": [],  # special: all regions
}

def geo_choices():
    return list(GEO_MAP.keys())

def parse_timestamp(ts):
    try:
        return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S.%f%z")
    except Exception:
        try:
            return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S%z")
        except Exception:
            return None

class GCPClient:
    def __init__(self, project_id=None):
        env_projects = os.getenv("GCP_PROJECT_ID", "")
        self.project_ids = [p.strip() for p in env_projects.split(",") if p.strip()]
        if not self.project_ids:
            raise ValueError("GCP_PROJECT_ID environment variable is not set. Please add it to your .env file.")
        self.project_id = project_id or self.project_ids[0]
        self.max_workers = int(os.getenv("GCP_VM_FETCH_MAX_WORKERS", 8))
        self.zone_timeout = int(os.getenv("GCP_ZONE_FETCH_TIMEOUT", 10))  # seconds

    def list_regions(self, project_id=None):
        try:
            pid = project_id or self.project_id
            zones_client = compute_v1.ZonesClient()
            zones = [z.name for z in zones_client.list(project=pid)]
            regions = sorted(set(z.split("-")[0] + "-" + z.split("-")[1] for z in zones if "-" in z))
            return regions
        except Exception as e:
            print(f"Error listing regions: {e}")
            return []

    def list_zones(self, project_id=None):
        try:
            pid = project_id or self.project_id
            zones_client = compute_v1.ZonesClient()
            return [z.name for z in zones_client.list(project=pid)]
        except Exception as e:
            print(f"Error listing zones: {e}")
            return []

    def list_vms(self, project_id=None, zone=None, regions=None, geo_choices=None, zones=None):
        print(f"[DEBUG] list_vms called with project_id={project_id}, zone={zone}, regions={regions}, geo_choices={geo_choices}, zones={zones}")
        project_id = project_id or self.project_id
        start_time = time.time()
        try:
            instances_client = compute_v1.InstancesClient()
            vms = []
            if zone:
                print(f"[DEBUG] Listing VMs in zone: {zone}")
                request = compute_v1.ListInstancesRequest(project=project_id, zone=zone)
                for instance in instances_client.list(request=request):
                    vms.append(self._instance_to_dict(instance))
            else:
                print("[DEBUG] Listing all zones in the project")
                zones_client = compute_v1.ZonesClient()
                all_zones = [z.name for z in zones_client.list(project=project_id)]
                if zones:
                    use_zones = zones
                elif geo_choices:
                    region_prefixes = []
                    for geo in geo_choices:
                        region_prefixes.extend(GEO_MAP.get(geo, []))
                    if "global" in geo_choices:
                        use_zones = all_zones
                    else:
                        use_zones = [z for z in all_zones if any(z.startswith(prefix) for prefix in region_prefixes)]
                elif regions:
                    use_zones = [z for z in all_zones if any(z.startswith(region + "-") for region in regions)]
                else:
                    use_zones = all_zones
                print(f"[DEBUG] Using zones: {use_zones}")

                def fetch_zone(zone):
                    local_vms = []
                    try:
                        print(f"[DEBUG] Listing VMs in zone: {zone}")
                        request = compute_v1.ListInstancesRequest(project=project_id, zone=zone)
                        for instance in instances_client.list(request=request):
                            local_vms.append(self._instance_to_dict(instance))
                    except Exception as e:
                        print(f"[ERROR] Failed to fetch VMs in zone {zone}: {e}")
                    return local_vms

                vms = []
                with ThreadPoolExecutor(max_workers=min(self.max_workers, len(use_zones))) as executor:
                    future_to_zone = {executor.submit(fetch_zone, zone): zone for zone in use_zones}
                    for future in as_completed(future_to_zone):
                        zone = future_to_zone[future]
                        try:
                            vms.extend(future.result())
                        except Exception as exc:
                            print(f"[ERROR] Zone {zone} generated an exception: {exc}")
                        if time.time() - start_time > 60:
                            print("[ERROR] Timeout: listing VMs took too long.")
                            break
            print(f"[DEBUG] Found {len(vms)} VMs")
            return vms
        except DefaultCredentialsError:
            print("GCP credentials not found. Please set up authentication.")
            return []
        except Exception as e:
            print(f"Error listing VMs: {e}")
            return []

    def _instance_to_dict(self, instance):
        # Extract creation time
        creation_time = getattr(instance, "creation_timestamp", "")
        # Try to extract last stopped/started/suspended times if present
        last_stopped = getattr(instance, "last_terminated_timestamp", "") or getattr(instance, "last_suspended_timestamp", "") or ""
        last_started = getattr(instance, "last_start_timestamp", "")
        last_suspended = getattr(instance, "last_suspended_timestamp", "")
        # Compute days_running and days_stopped
        status = getattr(instance, "status", "")
        days_running = ""
        days_stopped = ""
        stopped_time = last_stopped
        try:
            now = datetime.now(timezone.utc)
            if status == "RUNNING" and creation_time:
                created = parse_timestamp(creation_time)
                if created:
                    days_running = (now - created).days
                days_stopped = "N/A"
                stopped_time = "N/A"
            elif status == "TERMINATED":
                if not stopped_time:
                    stopped_time = creation_time
                if stopped_time:
                    stopped = parse_timestamp(stopped_time)
                    if stopped:
                        days_stopped = (now - stopped).days
                    else:
                        days_stopped = "N/A"
                    if not stopped_time:
                        stopped_time = "N/A"
                else:
                    stopped_time = "N/A"
                    days_stopped = "N/A"
                days_running = "N/A"
            else:
                days_running = "N/A"
                days_stopped = "N/A"
                stopped_time = "N/A"
        except Exception:
            days_running = "N/A"
            days_stopped = "N/A"
            stopped_time = "N/A"
        return {
            "id": getattr(instance, "id", ""),
            "name": getattr(instance, "name", ""),
            "status": status,
            "zone": getattr(instance, "zone", "").split("/")[-1] if getattr(instance, "zone", "") else "",
            "machineType": getattr(instance, "machine_type", "").split("/")[-1] if getattr(instance, "machine_type", "") else "",
            "creationTime": creation_time,
            "lastStoppedTime": stopped_time,
            "lastStartedTime": last_started,
            "lastSuspendedTime": last_suspended,
            "daysStarted": days_running,
            "daysStopped": days_stopped,
            "networkInterfaces": [getattr(ni, "network_i_p", "") for ni in getattr(instance, "network_interfaces", [])],
        }

    # Stubs for other resources
    def list_cloudsql_instances(self):
        pass

    def list_gke_clusters(self):
        pass

    def list_filestore_instances(self):
        pass

    def list_storage_buckets(self):
        pass
