from fastapi import APIRouter

router = APIRouter()

@router.post("/recommendations")
def get_recommendations():
    """
    Returns mock AI-generated recommendations.
    """
    return {
        "recommendations": [
            "Consider shutting down unused VMs.",
            "Resize Cloud SQL instances for cost savings.",
            "Delete unused storage buckets."
        ]
    }
