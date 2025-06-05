import os
from google.cloud import filestore_v1
from dotenv import load_dotenv

load_dotenv()

class FilestoreService:
    def __init__(self, project_id=None):
        env_projects = os.getenv("GCP_PROJECT_ID", "")
        self.project_ids = [p.strip() for p in env_projects.split(",") if p.strip()]
        if not self.project_ids:
            raise ValueError("GCP_PROJECT_ID environment variable is not set. Please add it to your .env file.")
        self.project_id = project_id or self.project_ids[0]

    def list_filestore_instances(self, project_id=None):
        project_id = project_id or self.project_id
        client = filestore_v1.CloudFilestoreManagerClient()
        parent = f"projects/{project_id}/locations/-"
        instances = []
        try:
            for instance in client.list_instances(parent=parent):
                # Extract NFS path, IP address, protocol, and label
                nfs_path = ""
                ip_address = ""
                protocol = "NFSv3"  # GCP Filestore is NFSv3/NFSv4, but API may not specify
                if instance.file_shares:
                    nfs_path = instance.file_shares[0].name if instance.file_shares else ""
                if instance.networks:
                    ip_address = instance.networks[0].ip_addresses[0] if instance.networks[0].ip_addresses else ""
                label = ", ".join(f"{k}:{v}" for k, v in instance.labels.items()) if instance.labels else ""
                # Extract location from instance.name (projects/{project}/locations/{location}/instances/{instance})
                location = ""
                try:
                    parts = instance.name.split("/")
                    if "locations" in parts:
                        idx = parts.index("locations")
                        location = parts[idx + 1]
                except Exception:
                    location = ""
                instances.append({
                    "name": instance.name.split("/")[-1],
                    "location": location,
                    "tier": instance.tier.name if hasattr(instance.tier, "name") else str(instance.tier),
                    "capacity": instance.file_shares[0].capacity_gb if instance.file_shares else "",
                    "status": instance.state.name if hasattr(instance.state, "name") else str(instance.state),
                    "network": instance.networks[0].network.split("/")[-1] if instance.networks else "",
                    "nfs_path": nfs_path,
                    "ip_address": ip_address,
                    "protocol": protocol,
                    "label": label,
                    "createTime": instance.create_time.strftime("%Y-%m-%d %H:%M:%S") if hasattr(instance, "create_time") and instance.create_time else "",
                })
        except Exception as e:
            print(f"[ERROR] FilestoreService.list_filestore_instances: {e}")
        return instances
