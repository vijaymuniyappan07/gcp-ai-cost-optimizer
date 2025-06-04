from googleapiclient.discovery import build
import os
from dotenv import load_dotenv

load_dotenv()

class GKEService:
    def __init__(self, project_id=None):
        env_projects = os.getenv("GCP_PROJECT_ID", "")
        self.project_ids = [p.strip() for p in env_projects.split(",") if p.strip()]
        if not self.project_ids:
            raise ValueError("GCP_PROJECT_ID environment variable is not set. Please add it to your .env file.")
        self.project_id = project_id or self.project_ids[0]

    def list_gke_clusters(self, project_id=None):
        """
        List all GKE clusters in the given GCP project.
        Returns a list of cluster details (dicts).
        """
        project_id = project_id or self.project_id
        try:
            service = build("container", "v1")
            clusters = []
            try:
                req = service.projects().locations().clusters().list(parent=f"projects/{project_id}/locations/-")
                resp = req.execute()
                for cluster in resp.get("clusters", []):
                    # Node pools info
                    node_pools = cluster.get("nodePools", [])
                    node_pool_names = [np.get("name", "") for np in node_pools]
                    autoscaling_status = []
                    min_node_count = []
                    max_node_count = []
                    for np in node_pools:
                        autoscaling = np.get("autoscaling", {})
                        if autoscaling:
                            enabled = autoscaling.get("enabled", False)
                            autoscaling_status.append("ENABLED" if enabled else "DISABLED")
                            min_node_count.append(str(autoscaling.get("minNodeCount", "")))
                            max_node_count.append(str(autoscaling.get("maxNodeCount", "")))
                        else:
                            autoscaling_status.append("DISABLED")
                            min_node_count.append("")
                            max_node_count.append("")
                    clusters.append({
                        "name": cluster.get("name", ""),
                        "location": cluster.get("location", ""),
                        "status": cluster.get("status", ""),
                        "endpoint": cluster.get("endpoint", ""),
                        "nodeCount": cluster.get("currentNodeCount", ""),
                        "nodeVersion": cluster.get("currentNodeVersion", ""),
                        "masterVersion": cluster.get("currentMasterVersion", ""),
                        "network": cluster.get("network", ""),
                        "subnetwork": cluster.get("subnetwork", ""),
                        "labels": ", ".join(f"{k}:{v}" for k, v in cluster.get("resourceLabels", {}).items()) if cluster.get("resourceLabels") else "",
                        "createTime": cluster.get("createTime", ""),
                        "clustertype": cluster.get("clusterIpv4Cidr", ""),  # Not a true type, but a unique field
                        "autoscalingStatus": ", ".join(autoscaling_status),
                        "minNodeCount": ", ".join(min_node_count),
                        "maxNodeCount": ", ".join(max_node_count),
                        "nodePools": ", ".join(node_pool_names),
                    })
            except Exception as e:
                print(f"[GKE] Error fetching clusters: {e}")
            return clusters
        except Exception as e:
            print(f"Error listing GKE clusters: {e}")
            return []
