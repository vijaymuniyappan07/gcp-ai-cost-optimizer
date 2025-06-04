from googleapiclient.discovery import build
import os
from dotenv import load_dotenv

load_dotenv()

class CloudSQLService:
    def __init__(self, project_id=None):
        env_projects = os.getenv("GCP_PROJECT_ID", "")
        self.project_ids = [p.strip() for p in env_projects.split(",") if p.strip()]
        if not self.project_ids:
            raise ValueError("GCP_PROJECT_ID environment variable is not set. Please add it to your .env file.")
        self.project_id = project_id or self.project_ids[0]

    def list_cloudsql_instances(self, project_id=None):
        """
        List all Cloud SQL instances in the given GCP project.
        Returns a list of instance details (dicts).
        """
        project_id = project_id or self.project_id
        try:
            service = build("sqladmin", "v1beta4")
            request = service.instances().list(project=project_id)
            response = request.execute()
            instances = []
            for instance in response.get("items", []):
                settings = instance.get("settings", {})
                instances.append({
                    "name": instance.get("name", ""),
                    "region": instance.get("region", ""),
                    "databaseVersion": instance.get("databaseVersion", ""),
                    "state": instance.get("state", ""),
                    "gceZone": instance.get("gceZone", ""),
                    "ipAddresses": [ip.get("ipAddress", "") for ip in instance.get("ipAddresses", [])],
                    "tier": settings.get("tier", ""),
                    "creationTime": instance.get("createTime", ""),
                    "availabilityType": settings.get("availabilityType", ""),
                    "dataDiskType": settings.get("dataDiskType", ""),
                    "dataDiskSizeGb": settings.get("dataDiskSizeGb", ""),
                    "storageAutoResize": settings.get("storageAutoResize", ""),
                    "pricingPlan": settings.get("pricingPlan", ""),
                })
            return instances
        except Exception as e:
            print(f"Error listing Cloud SQL instances: {e}")
            return []
