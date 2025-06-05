from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse
from app.services.gcp_client import GCPClient
from app.services.vm_service import VMService
from app.services.cloudsql_service import CloudSQLService
from app.services.gke_service import GKEService
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

from app.services.filestore_service import FilestoreService

@router.get("/resources/filestore")
def get_filestore(project_id: str = Query(None, description="GCP project id")):
    """
    Returns real Filestore data for the given project.
    """
    try:
        filestore_service = FilestoreService(project_id=project_id)
        instances = filestore_service.list_filestore_instances(project_id=project_id)
        return {"filestore": instances}
    except Exception as e:
        return {"error": str(e)}

from app.services.storage_service import StorageService

@router.get("/resources/storage")
def get_storage(project_id: str = Query(None, description="GCP project id")):
    """
    Returns real Cloud Storage bucket data for the given project.
    """
    import time
    try:
        print(f"[TRACE] get_storage: Start fetching buckets at {time.strftime('%Y-%m-%d %H:%M:%S')}")
        storage_service = StorageService(project_id=project_id)
        buckets = storage_service.list_buckets(project_id=project_id)
        print(f"[TRACE] get_storage: Fetched {len(buckets)} buckets, sending response at {time.strftime('%Y-%m-%d %H:%M:%S')}")
        return {"storage": buckets}
    except Exception as e:
        print(f"[TRACE] get_storage: Exception occurred at {time.strftime('%Y-%m-%d %H:%M:%S')}: {e}")
        return {"error": str(e)}


@router.post("/resources/gke/resize")
async def resize_gke_nodepool(request: Request):
    """
    Resize a GKE node pool (autoscaling or static) for a given cluster.
    """
    try:
        data = await request.json()
        project_id = data.get("project_id")
        cluster_name = data.get("cluster_name")
        nodepool_name = data.get("nodepool")  # FIX: match frontend key
        autoscaling = data.get("autoscaling")
        min_node = data.get("min_node")
        max_node = data.get("max_node")
        node_count = data.get("node_count")
        location = data.get("location")  # Should be passed from frontend

        gke_service = GKEService(project_id=project_id)
        result = gke_service.resize_nodepool(
            project_id=project_id,
            location=location,
            cluster_name=cluster_name,
            nodepool_name=nodepool_name,
            autoscaling=autoscaling,
            min_node=min_node,
            max_node=max_node,
            node_count=node_count
        )
        return JSONResponse(content=result)
    except Exception as e:
        tb = traceback.format_exc()
        print(f"[ERROR] /resources/gke/resize exception: {e}\n{tb}")
        return JSONResponse(content={"success": False, "error": str(e), "traceback": tb}, status_code=500)
