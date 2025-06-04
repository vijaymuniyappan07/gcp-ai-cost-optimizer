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
                    node_pool_machine_types = [np.get("config", {}).get("machineType", "") for np in node_pools]
                    autoscaling_status = []
                    min_node_count = []
                    max_node_count = []
                    for np in node_pools:
                        autoscaling = np.get("autoscaling", {})
                        if autoscaling:
                            enabled = autoscaling.get("enabled", False)
                            autoscaling_status.append("ENABLED" if enabled else "DISABLED")
                            min_node_count.append(str(autoscaling.get("minNodeCount", 0) or 0))
                            max_node_count.append(str(autoscaling.get("maxNodeCount", 0) or 0))
                        else:
                            autoscaling_status.append("DISABLED")
                            min_node_count.append("0")
                            max_node_count.append("0")
                    # Cluster type: Autopilot or Standard
                    clustertype = "Autopilot" if cluster.get("autopilot", {}).get("enabled") else "Standard"
                    node_count = int(cluster.get("currentNodeCount", 0) or 0)
                    status = cluster.get("status", "")
                    if node_count == 0:
                        status = "STOPPED"
                    # Is public cluster?
                    private_config = cluster.get("privateClusterConfig", {})
                    is_public = not private_config.get("enablePrivateNodes", False)
                    clusters.append({
                        "name": cluster.get("name", ""),
                        "location": cluster.get("location", ""),
                        "status": status,
                        "endpoint": cluster.get("endpoint", ""),
                        "nodeCount": node_count,
                        "nodeVersion": cluster.get("currentNodeVersion", ""),
                        "masterVersion": cluster.get("currentMasterVersion", ""),
                        "network": cluster.get("network", ""),
                        "subnetwork": cluster.get("subnetwork", ""),
                        "labels": ", ".join(f"{k}:{v}" for k, v in cluster.get("resourceLabels", {}).items()) if cluster.get("resourceLabels") else "",
                        "createTime": cluster.get("createTime", ""),
                        "clustertype": clustertype,
                        "nodePools": ", ".join(node_pool_names),
                        "nodePoolsMachineType": ", ".join(node_pool_machine_types),
                        "autoscalingStatus": ", ".join(autoscaling_status),
                        "minNodeCount": ", ".join(min_node_count),
                        "maxNodeCount": ", ".join(max_node_count),
                        "isPublicCluster": "Yes" if is_public else "No",
                    })
            except Exception as e:
                print(f"[GKE] Error fetching clusters: {e}")
            return clusters
        except Exception as e:
            print(f"Error listing GKE clusters: {e}")
            return []
