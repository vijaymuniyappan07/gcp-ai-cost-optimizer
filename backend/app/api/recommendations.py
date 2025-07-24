from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter()

@router.post("/recommendations")
async def get_recommendations(request: Request):
    """
    Return AI/ML recommendations for a given resource type and project.
    """
    import time
    from app.services.vm_service import VMService
    from app.services.ai_service import get_vm_recommendations
    data = await request.json()
    project_id = data.get("project_id")
    resource_type = data.get("resource_type")
    print(f"[DEBUG] /recommendations called for project_id={project_id}, resource_type={resource_type}")
    if resource_type == "vms":
        # Fetch real VM data
        vm_service = VMService(project_id=project_id)
        vms = vm_service.list_vms(project_id=project_id)
        # Call AI/ML service (placeholder)
        recommendations = get_vm_recommendations(vms, project_id=project_id)
    elif resource_type == "cloudsql":
        from app.services.cloudsql_service import CloudSQLService
        from app.services.ai_service import get_cloudsql_recommendations
        sql_service = CloudSQLService(project_id=project_id)
        instances = sql_service.list_cloudsql_instances(project_id=project_id)
        recommendations = get_cloudsql_recommendations(instances, project_id=project_id)
    elif resource_type == "gke":
        from app.services.gke_service import GKEService
        from app.services.ai_service import get_gke_recommendations
        gke_service = GKEService(project_id=project_id)
        clusters = gke_service.list_gke_clusters(project_id=project_id)
        recommendations = get_gke_recommendations(clusters, project_id=project_id)
    else:
        recommendations = [
            {
                "text": f"No AI recommendations available for resource type: {resource_type}",
                "type": "info",
                "severity": "info",
                "resource": "",
                "rationale": ""
            }
        ]
    time.sleep(1)  # Simulate processing delay
    return JSONResponse(content={"recommendations": recommendations})
