from google.cloud import compute_v1
from google.auth.exceptions import DefaultCredentialsError
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

def parse_timestamp(ts):
    try:
        return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S.%f%z")
    except Exception:
        try:
            return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S%z")
        except Exception:
            return None

def geo_choices():
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
        "global": [],
    }
    return list(GEO_MAP.keys())

class VMService:
    def __init__(self, project_id=None):
        env_projects = os.getenv("GCP_PROJECT_ID", "")
        self.project_ids = [p.strip() for p in env_projects.split(",") if p.strip()]
        if not self.project_ids:
            raise ValueError("GCP_PROJECT_ID environment variable is not set. Please add it to your .env file.")
        self.project_id = project_id or self.project_ids[0]
        self.max_workers = int(os.getenv("GCP_VM_FETCH_MAX_WORKERS", 8))
        self.zone_timeout = int(os.getenv("GCP_ZONE_FETCH_TIMEOUT", 10))

    def list_zones(self, project_id=None):
        try:
            pid = project_id or self.project_id
            zones_client = compute_v1.ZonesClient()
            return [z.name for z in zones_client.list(project=pid)]
        except Exception as e:
            print(f"Error listing zones: {e}")
            return []

    def list_vms(self, project_id=None, zone=None, regions=None, geo_choices=None, zones=None):
        project_id = project_id or self.project_id
        start_time = time.time()
        try:
            instances_client = compute_v1.InstancesClient()
            vms = []
            if zone:
                request = compute_v1.ListInstancesRequest(project=project_id, zone=zone)
                for instance in instances_client.list(request=request):
                    vms.append(self._instance_to_dict(instance))
            else:
                zones_client = compute_v1.ZonesClient()
                all_zones = [z.name for z in zones_client.list(project=project_id)]
                if zones:
                    use_zones = zones
                else:
                    use_zones = all_zones
                def fetch_zone(zone):
                    local_vms = []
                    try:
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
                        try:
                            vms.extend(future.result())
                        except Exception as exc:
                            print(f"[ERROR] Zone generated an exception: {exc}")
                        if time.time() - start_time > 60:
                            print("[ERROR] Timeout: listing VMs took too long.")
                            break
            return vms
        except DefaultCredentialsError:
            print("GCP credentials not found. Please set up authentication.")
            return []
        except Exception as e:
            print(f"Error listing VMs: {e}")
            return []

    def _instance_to_dict(self, instance):
        creation_time = getattr(instance, "creation_timestamp", "")
        last_stopped = getattr(instance, "last_terminated_timestamp", "") or getattr(instance, "last_suspended_timestamp", "") or ""
        last_started = getattr(instance, "last_start_timestamp", "")
        last_suspended = getattr(instance, "last_suspended_timestamp", "")
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

        internal_ip = "N/A"
        external_ip = "N/A"
        vpc_name = "N/A"
        if hasattr(instance, "network_interfaces") and instance.network_interfaces:
            ni = instance.network_interfaces[0]
            internal_ip = getattr(ni, "network_i_p", None) or getattr(ni, "network_ip", None) or "N/A"
            if hasattr(ni, "access_configs") and ni.access_configs:
                ac = ni.access_configs[0]
                external_ip = getattr(ac, "nat_i_p", None) or getattr(ac, "nat_ip", None) or "N/A"
            if hasattr(ni, "network"):
                vpc_url = getattr(ni, "network", "")
                vpc_name = vpc_url.split("/")[-1] if vpc_url else "N/A"
        labels = getattr(instance, "labels", {})
        labels_str = ", ".join(f"{k}:{v}" for k, v in labels.items()) if labels else ""

        # Extract disk types and sizes
        disks = getattr(instance, "disks", [])
        disk_types = []
        disk_sizes = []
        for disk in disks:
            disk_type = getattr(disk, "type_", "") or getattr(disk, "type", "")
            disk_size = getattr(disk, "disk_size_gb", "") or getattr(disk, "diskSizeGb", "")
            disk_types.append(disk_type.split("/")[-1] if "/" in disk_type else disk_type)
            disk_sizes.append(str(disk_size))

        # Fetch CPU and memory from machine type
        cpu = "N/A"
        memory = "N/A"
        try:
            zone = getattr(instance, "zone", "").split("/")[-1] if getattr(instance, "zone", "") else ""
            machine_type = getattr(instance, "machine_type", "").split("/")[-1] if getattr(instance, "machine_type", "") else ""
            if zone and machine_type:
                mt_client = compute_v1.MachineTypesClient()
                mt = mt_client.get(project=self.project_id, zone=zone, machine_type=machine_type)
                cpu = getattr(mt, "guest_cpus", "N/A")
                memory_mb = getattr(mt, "memory_mb", None)
                if memory_mb is not None:
                    memory = f"{round(memory_mb/1024, 2)} GB"
        except Exception as e:
            print(f"[WARN] Could not fetch CPU/memory for {machine_type} in {zone}: {e}")

        return {
            "id": getattr(instance, "id", ""),
            "name": getattr(instance, "name", ""),
            "status": status,
            "zone": getattr(instance, "zone", "").split("/")[-1] if getattr(instance, "zone", "") else "",
            "machineType": getattr(instance, "machine_type", "").split("/")[-1] if getattr(instance, "machine_type", "") else "",
            "cpu": cpu,
            "memory": memory,
            "creationTime": creation_time,
            "lastStoppedTime": stopped_time,
            "lastStartedTime": last_started,
            "lastSuspendedTime": last_suspended,
            "daysStarted": days_running,
            "daysStopped": days_stopped,
            "internalIp": internal_ip,
            "externalIp": external_ip,
            "vpcName": vpc_name,
            "labels": labels_str,
            "diskTypes": ", ".join(disk_types),
            "diskSizes": ", ".join(disk_sizes),
        }
