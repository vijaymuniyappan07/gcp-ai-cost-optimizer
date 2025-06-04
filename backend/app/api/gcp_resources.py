from fastapi import APIRouter

router = APIRouter()

@router.get("/resources/vms")
def get_vms():
    """
    Returns mock VM data for testing.
    """
    return {
        "vms": [
            {"id": "vm-1", "name": "test-vm-1", "status": "RUNNING"},
            {"id": "vm-2", "name": "test-vm-2", "status": "TERMINATED"}
        ]
    }

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
