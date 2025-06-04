from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from app.services.gcp_client import GCPClient
from googleapiclient.discovery import build
import traceback

print("[DEBUG] Loading gcp_resources router")
router = APIRouter()

@router.get("/gcp/options")
def get_gcp_options():
    """
    Returns available project ids and zones for the user to select.
    Also groups zones by geo location (us, europe, asia, etc).
    """
    try:
        print("[DEBUG] /gcp/options called")
        gcp_client = GCPClient()
        print(f"[DEBUG] GCPClient project_id: {gcp_client.project_id}")
        compute = gcp_client.credentials and build("compute", "v1", credentials=gcp_client.credentials)
        zones = []
        geo_map = {}
        if compute:
            print("[DEBUG] Fetching zones from GCP...")
            zones_req = compute.zones().list(project=gcp_client.project_id)
            zones_resp = zones_req.execute()
            print(f"[DEBUG] zones_resp: {zones_resp}")
            for z in zones_resp.get("items", []):
                zone_name = z["name"]
                region = zone_name.split("-")[0]
                # Map region prefix to geo (lowercase)
                if region.startswith("us"):
                    geo = "us"
                elif region.startswith("europe"):
                    geo = "europe"
                elif region.startswith("asia"):
                    geo = "asia"
                elif region.startswith("australia"):
                    geo = "australia"
                elif region.startswith("southamerica"):
                    geo = "southamerica"
                elif region.startswith("northamerica"):
                    geo = "northamerica"
                else:
                    geo = "other"
                geo_map.setdefault(geo, []).append(zone_name)
                zones.append(zone_name)
        print(f"[DEBUG] Returning project_ids: {[gcp_client.project_id]}, zones: {zones}, geo_map: {geo_map}")
        return JSONResponse(content={
            "project_ids": [gcp_client.project_id] if gcp_client.project_id else [],
            "zones": zones,
            "geo_map": geo_map
        })
    except Exception as e:
        tb = traceback.format_exc()
        print(f"[ERROR] /gcp/options exception: {e}\n{tb}")
        return JSONResponse(content={"error": f"{e}\n{tb}"}, status_code=500)

@router.get("/resources/vms")
def get_vms(
    project_id: str = Query(None, description="GCP project id"),
    zones: str = Query(None, description="Comma-separated list of zones")
):
    """
    Returns live VM data from GCP for the given project and zones.
    """
    try:
        gcp_client = GCPClient()
        use_project_id = project_id or gcp_client.project_id
        selected_zones = [z.strip() for z in zones.split(",")] if zones else None
        vms = gcp_client.list_vms(project_id=use_project_id, zones=selected_zones)
        return JSONResponse(content={"vms": vms})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@router.get("/resources/cloudsql")
def get_cloudsql():
    """
    Returns mock Cloud SQL data for testing.
    """
    return {
        "cloudsql": [
            {"id": "sql-1", "name": "test-sql-1", "status": "RUNNABLE"},
            {"id": "sql-2", "name": "test-sql-2", "status": "SUSPENDED"}
        ]
    }

@router.get("/resources/gke")
def get_gke():
    """
    Returns mock GKE cluster data for testing.
    """
    return {
        "gke": [
            {"id": "gke-1", "name": "test-gke-1", "status": "RUNNING"},
            {"id": "gke-2", "name": "test-gke-2", "status": "STOPPED"}
        ]
    }

@router.get("/resources/filestore")
def get_filestore():
    """
    Returns mock Filestore data for testing.
    """
    return {
        "filestore": [
            {"id": "fs-1", "name": "test-fs-1", "status": "READY"},
            {"id": "fs-2", "name": "test-fs-2", "status": "CREATING"}
        ]
    }

@router.get("/resources/storage")
def get_storage():
    """
    Returns mock Cloud Storage bucket data for testing.
    """
    return {
        "storage": [
            {"id": "bucket-1", "name": "test-bucket-1", "location": "US"},
            {"id": "bucket-2", "name": "test-bucket-2", "location": "EU"}
        ]
    }
