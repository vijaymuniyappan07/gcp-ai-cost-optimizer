from googleapiclient.discovery import build
import os
from dotenv import load_dotenv
import subprocess

load_dotenv()

class CloudSQLService:
    def __init__(self, project_id=None):
        env_projects = os.getenv("GCP_PROJECT_ID", "")
        self.project_ids = [p.strip() for p in env_projects.split(",") if p.strip()]
        if not self.project_ids:
            raise ValueError("GCP_PROJECT_ID environment variable is not set. Please add it to your .env file.")
        self.project_id = project_id or self.project_ids[0]

    def get_instance_state_gcloud(self, project_id, instance_name):
        """
        Use gcloud CLI to get the real state of a Cloud SQL instance.
        Returns "" if gcloud fails for any reason.
        """
        try:
            cmd = [
                "gcloud", "sql", "instances", "describe",
                "--project", project_id,
                instance_name,
                "--format=value(state)"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                print(f"[gcloud error] {result.stderr}")
                return ""
        except Exception as e:
            print(f"[gcloud exception] {e}")
            return ""

    def list_cloudsql_instances_gcloud(self, project_id=None):
        """
        List all Cloud SQL instances using gcloud CLI for performance.
        Returns a list of instance details (dicts).
        """
        import json
        project_id = project_id or self.project_id
        try:
            cmd = [
                "gcloud", "sql", "instances", "list",
                "--project", project_id,
                "--format=json"
            ]
            print(f"[DEBUG] Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if result.returncode != 0:
                print(f"[gcloud error] {result.stderr}")
                return []
            instances_json = json.loads(result.stdout)
            instances = []
            for instance in instances_json:
                settings = instance.get("settings", {})
                instance_name = instance.get("name", "")
                state = instance.get("state", "")
                labels = settings.get("userLabels", {})
                labels_str = ", ".join(f"{k}:{v}" for k, v in labels.items()) if labels else ""
                vpc_network = ""
                ip_config = settings.get("ipConfiguration", {})
                if "privateNetwork" in ip_config:
                    vpc_url = ip_config["privateNetwork"]
                    vpc_network = vpc_url.split("/")[-1] if vpc_url else ""
                elif "authorizedNetworks" in ip_config and ip_config["authorizedNetworks"]:
                    vpc_network = ip_config["authorizedNetworks"][0].get("value", "")
                # Compute daysStopped if lastStoppedTime is available
                last_stopped_time = instance.get("lastStoppedTime")
                days_stopped = None
                if last_stopped_time:
                    from datetime import datetime, timezone as dt_timezone
                    try:
                        dt = datetime.fromisoformat(last_stopped_time.replace("Z", "+00:00"))
                        now = datetime.now(dt_timezone.utc)
                        days_stopped = (now - dt).days
                    except Exception:
                        days_stopped = None
                instances.append({
                    "name": instance_name,
                    "region": instance.get("region", ""),
                    "databaseVersion": instance.get("databaseVersion", ""),
                    "state": state,
                    "gceZone": instance.get("gceZone", ""),
                    "ipAddresses": [ip.get("ipAddress", "") for ip in instance.get("ipAddresses", [])],
                    "tier": settings.get("tier", ""),
                    "creationTime": instance.get("createTime", ""),
                    "availabilityType": settings.get("availabilityType", ""),
                    "dataDiskType": settings.get("dataDiskType", ""),
                    "dataDiskSizeGb": settings.get("dataDiskSizeGb", ""),
                    "storageAutoResize": settings.get("storageAutoResize", ""),
                    "pricingPlan": settings.get("pricingPlan", ""),
                    "labels": labels_str,
                    "vpcNetwork": vpc_network,
                    "lastStoppedTime": last_stopped_time,
                    "daysStopped": days_stopped,
                })
            print(f"[DEBUG] gcloud: fetched {len(instances)} Cloud SQL instances")
            return instances
        except Exception as e:
            print(f"[gcloud exception] {e}")
            return []

    def list_cloudsql_instances(self, project_id=None):
        # Use gcloud-based method for performance
        return self.list_cloudsql_instances_gcloud(project_id=project_id)
