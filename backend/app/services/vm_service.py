from google.cloud import compute_v1
from google.auth.exceptions import DefaultCredentialsError
import os
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

    def list_vms_gcloud(self, project_id=None):
        """
        List all VMs using gcloud CLI for performance.
        Returns a list of VM details (dicts).
        """
        import subprocess
        import json
        project_id = project_id or self.project_id
        try:
            # Fetch all VMs
            cmd = [
                "gcloud", "compute", "instances", "list",
                "--project", project_id,
                "--format=json"
            ]
            print(f"[DEBUG] Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if result.returncode != 0:
                print(f"[gcloud error] {result.stderr}")
                return []
            instances = json.loads(result.stdout)
            # Build a set of (zone, machineType) pairs
            machine_types_needed = set()
            for inst in instances:
                zone = inst.get("zone", "").split("/")[-1] if inst.get("zone", "") else ""
                machine_type = inst.get("machineType", "").split("/")[-1] if inst.get("machineType", "") else ""
                if zone and machine_type:
                    machine_types_needed.add((zone, machine_type))
            # Fetch machine type info in parallel
            machine_type_info = {}
            def fetch_machine_type(zone, machine_type):
                try:
                    mt_client = compute_v1.MachineTypesClient()
                    mt = mt_client.get(project=project_id, zone=zone, machine_type=machine_type)
                    return (zone, machine_type, getattr(mt, "guest_cpus", "N/A"), getattr(mt, "memory_mb", "N/A"))
                except Exception as e:
                    print(f"[WARN] Could not fetch machine type {machine_type} in {zone}: {e}")
                    return (zone, machine_type, "N/A", "N/A")
            with ThreadPoolExecutor(max_workers=8) as executor:
                futures = [executor.submit(fetch_machine_type, zone, mt) for (zone, mt) in machine_types_needed]
                for future in as_completed(futures):
                    zone, mt, cpu, memory_mb = future.result()
                    machine_type_info[(zone, mt)] = (cpu, memory_mb)
            vms = []
            for inst in instances:
                labels = inst.get("labels", {})
                labels_str = ", ".join(f"{k}:{v}" for k, v in labels.items()) if labels else ""
                disks = inst.get("disks", [])
                disk_types = []
                disk_sizes = []
                for disk in disks:
                    disk_type = disk.get("type", "")
                    disk_size = disk.get("diskSizeGb", "")
                    disk_types.append(disk_type.split("/")[-1] if "/" in disk_type else disk_type)
                    disk_sizes.append(str(disk_size))
                zone = inst.get("zone", "").split("/")[-1] if inst.get("zone", "") else ""
                machine_type = inst.get("machineType", "").split("/")[-1] if inst.get("machineType", "") else ""
                cpu, memory_mb = machine_type_info.get((zone, machine_type), ("N/A", "N/A"))
                memory = f"{round(memory_mb/1024, 2)} GB" if memory_mb not in ("N/A", None) else "N/A"
                # Parse start/stop times and days started/stopped (match working script logic)
                last_start = inst.get("lastStartTimestamp", "")
                last_stop = inst.get("lastStopTimestamp", "")
                status = inst.get("status", "")
                now = datetime.now(timezone.utc)
                days_started = "N/A"
                days_stopped = "N/A"
                last_started_time = ""
                last_stopped_time = ""
                try:
                    if status == "RUNNING" and last_start:
                        dt_start = parse_timestamp(last_start)
                        last_started_time = dt_start.strftime("%Y-%m-%d %H:%M:%S") if dt_start else last_start
                        if dt_start:
                            days_started = (now - dt_start).days
                        days_stopped = "N/A"
                        last_stopped_time = "N/A"
                    elif status == "TERMINATED":
                        if last_stop:
                            dt_stop = parse_timestamp(last_stop)
                            last_stopped_time = dt_stop.strftime("%Y-%m-%d %H:%M:%S") if dt_stop else last_stop
                            if dt_stop:
                                days_stopped = (now - dt_stop).days
                            else:
                                days_stopped = "N/A"
                        else:
                            last_stopped_time = "N/A"
                            days_stopped = "N/A"
                        days_started = "N/A"
                        last_started_time = "N/A"
                    else:
                        days_started = "N/A"
                        days_stopped = "N/A"
                        last_started_time = "N/A"
                        last_stopped_time = "N/A"
                except Exception:
                    pass
                vms.append({
                    "id": inst.get("id", ""),
                    "name": inst.get("name", ""),
                    "status": inst.get("status", ""),
                    "zone": zone,
                    "machineType": machine_type,
                    "cpu": cpu,
                    "memory": memory,
                    "creationTime": inst.get("creationTimestamp", ""),
                    "lastStoppedTime": last_stopped_time,
                    "lastStartedTime": last_started_time,
                    "lastSuspendedTime": "",
                    "daysStarted": days_started,
                    "daysStopped": days_stopped,
                    "internalIp": inst.get("networkInterfaces", [{}])[0].get("networkIP", "N/A"),
                    "externalIp": inst.get("networkInterfaces", [{}])[0].get("accessConfigs", [{}])[0].get("natIP", "N/A"),
                    "vpcName": inst.get("networkInterfaces", [{}])[0].get("network", "").split("/")[-1] if inst.get("networkInterfaces", [{}])[0].get("network", "") else "N/A",
                    "labels": labels_str,
                    "diskTypes": ", ".join(disk_types),
                    "diskSizes": ", ".join(disk_sizes),
                })
            print(f"[DEBUG] gcloud: fetched {len(vms)} VMs")
            return vms
        except Exception as e:
            print(f"[gcloud exception] {e}")
            return []

    def list_vms(self, project_id=None, zone=None, regions=None, geo_choices=None, zones=None):
        # Use gcloud-based method for performance
        return self.list_vms_gcloud(project_id=project_id)
