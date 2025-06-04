from googleapiclient.discovery import build
from app.utils.auth import load_gcp_credentials
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

class GCPClient:
    """
    Handles GCP API calls (Compute, SQL, GKE, Filestore, Storage).
    """

    def __init__(self):
        self.credentials = load_gcp_credentials()
        self.project_id = os.getenv("GCP_PROJECT_ID")
        if not self.project_id:
            raise ValueError("GCP_PROJECT_ID environment variable is not set. Please add it to your .env file.")
        self.max_workers = int(os.getenv("GCP_VM_FETCH_MAX_WORKERS", 8))

    def _fetch_zone_vms(self, compute, zone, project_id):
        vms = []
        print(f"[DEBUG] Fetching instances in zone: {zone}")
        req = compute.instances().list(project=project_id, zone=zone)
        try:
            resp = req.execute()
            print(f"[DEBUG] Response for zone {zone}: {resp}")
            for inst in resp.get("items", []):
                vms.append({
                    "id": inst.get("id"),
                    "name": inst.get("name"),
                    "status": inst.get("status"),
                    "zone": zone,
                    "machineType": inst.get("machineType", "").split("/")[-1],
                    "networkInterfaces": inst.get("networkInterfaces", []),
                })
        except Exception as e:
            print(f"[DEBUG] Exception in zone {zone}: {e}")
        return vms

    def list_vms(self, project_id=None, zones=None):
        """
        Fetches VM instances from Google Compute Engine in parallel across zones.
        Returns a list of dicts with VM info.
        """
        print("[DEBUG] Starting list_vms")
        project_id = project_id or self.project_id
        if not project_id:
            print("[DEBUG] GCP_PROJECT_ID is missing")
            raise ValueError("GCP_PROJECT_ID environment variable is not set. Please add it to your .env file.")
        print(f"[DEBUG] Using project_id: {project_id}")
        compute = build("compute", "v1", credentials=self.credentials)
        print("[DEBUG] Fetching zones...")
        if zones is None:
            zones_req = compute.zones().list(project=project_id)
            zones_resp = zones_req.execute()
            zones = [z["name"] for z in zones_resp.get("items", [])]
        print(f"[DEBUG] Using zones: {zones}")

        vms = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_zone = {executor.submit(self._fetch_zone_vms, compute, zone, project_id): zone for zone in zones}
            for future in as_completed(future_to_zone):
                zone = future_to_zone[future]
                try:
                    zone_vms = future.result()
                    vms.extend(zone_vms)
                except Exception as e:
                    print(f"[DEBUG] Exception in thread for zone {zone}: {e}")
            # Wait for all futures to complete

        print(f"[DEBUG] Total VMs found: {len(vms)}")
        return vms

    # Stubs for other resources
    def list_cloudsql_instances(self):
        pass

    def list_gke_clusters(self):
        pass

    def list_filestore_instances(self):
        pass

    def list_storage_buckets(self):
        pass
