from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from app.services.gcp_client import GCPClient
from app.services.vm_service import VMService
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
        print(f"[DEBUG] GCPClient project_ids: {gcp_client.project_ids}")
        zones = gcp_client.list_zones()
        geo_map = {}
        for zone_name in zones:
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
        print(f"[DEBUG] Returning project_ids: {gcp_client.project_ids}, zones: {zones}, geo_map: {geo_map}")
        return JSONResponse(content={
            "project_ids": gcp_client.project_ids,
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
        vm_service = VMService(project_id=project_id)
        selected_zones = [z.strip() for z in zones.split(",")] if zones else None
        vms = vm_service.list_vms(project_id=project_id, zones=selected_zones)
        return JSONResponse(content={"vms": vms})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

from app.services.cloudsql_service import CloudSQLService

@router.get("/resources/cloudsql")
def get_cloudsql(project_id: str = Query(None, description="GCP project id")):
    """
    Returns real Cloud SQL data for the given project.
    """
    try:
        cloudsql_service = CloudSQLService(project_id=project_id)
        instances = cloudsql_service.list_cloudsql_instances(project_id=project_id)
        return JSONResponse(content={"cloudsql": instances})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

from app.services.gke_service import GKEService

@router.get("/resources/gke")
def get_gke(project_id: str = Query(None, description="GCP project id")):
    """
    Returns real GKE cluster data for the given project.
    """
    try:
        gke_service = GKEService(project_id=project_id)
        clusters = gke_service.list_gke_clusters(project_id=project_id)
        return JSONResponse(content={"gke": clusters})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

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
