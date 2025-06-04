from google.cloud import compute_v1
import os
from dotenv import load_dotenv

load_dotenv()

class GCPClient:
    def __init__(self, project_id=None):
        env_projects = os.getenv("GCP_PROJECT_ID", "")
        self.project_ids = [p.strip() for p in env_projects.split(",") if p.strip()]
        if not self.project_ids:
            raise ValueError("GCP_PROJECT_ID environment variable is not set. Please add it to your .env file.")
        self.project_id = project_id or self.project_ids[0]

    def list_zones(self, project_id=None):
        try:
            pid = project_id or self.project_id
            zones_client = compute_v1.ZonesClient()
            return [z.name for z in zones_client.list(project=pid)]
        except Exception as e:
            print(f"Error listing zones: {e}")
            return []
