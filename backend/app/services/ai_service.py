from google.cloud import monitoring_v3
from datetime import datetime, timedelta, timezone

def recommend_machine_type(current_type, cpu_util):
    if not current_type:
        return None, None
    parts = current_type.split("-")
    if len(parts) < 2:
        return None, None
    family = parts[0]
    vcpu = None
    for p in parts:
        if p.isdigit():
            vcpu = int(p)
    if cpu_util is None or vcpu is None:
        return None, None
    if cpu_util < 10 and vcpu > 1:
        new_vcpu = max(1, vcpu // 2)
        return current_type, f"{family}-standard-{new_vcpu}"
    elif cpu_util > 80:
        new_vcpu = vcpu * 2
        return current_type, f"{family}-standard-{new_vcpu}"
    return current_type, None

def fetch_vms_cpu_utilization_batch(project_id, vms, days=7):
    client = monitoring_v3.MetricServiceClient()
    project_name = f"projects/{project_id}"
    interval = monitoring_v3.TimeInterval(
        end_time=datetime.now(timezone.utc),
        start_time=datetime.now(timezone.utc) - timedelta(days=days),
    )
    metric_type = "compute.googleapis.com/instance/cpu/utilization"
    instance_zones = [(vm.get("name"), vm.get("zone")) for vm in vms if vm.get("name") and vm.get("zone")]
    if not instance_zones:
        return {}
    filter_str = f'metric.type="{metric_type}"'
    results = client.list_time_series(
        request={
            "name": project_name,
            "filter": filter_str,
            "interval": interval,
            "view": monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL,
        }
    )
    util_map = {k: [] for k in instance_zones}
    for ts in results:
        labels = ts.resource.labels
        zone = labels.get("zone")
        metric_labels = ts.metric.labels
        name = metric_labels.get("instance_name") or labels.get("instance_name") or labels.get("instance_id")
        key = (name, zone)
        if key in util_map:
            for point in ts.points:
                util_map[key].append(point.value.double_value)
        else:
            for k in util_map:
                if k[1] == zone:
                    util_map[k].extend([point.value.double_value for point in ts.points])
    avg_map = {}
    for k, vals in util_map.items():
        if vals:
            avg_map[k] = round(sum(vals) / len(vals) * 100, 2)
        else:
            avg_map[k] = None
    return avg_map

def suggest_vm_actions(vm, cpu_util=None):
    status = vm.get("status", "")
    name = vm.get("name", "")
    zone = vm.get("zone", "")
    machine_type = vm.get("machineType", "")
    if status == "RUNNING":
        if cpu_util is not None and cpu_util < 10:
            curr_type, rec_type = recommend_machine_type(machine_type, cpu_util)
            if rec_type:
                return {
                    "text": f"VM '{name}' in {zone} is underutilized (avg CPU {cpu_util}%). Suggest: Resize to {rec_type} or stop.",
                    "current_type": curr_type,
                    "proposed_type": rec_type
                }
            else:
                return {
                    "text": f"VM '{name}' in {zone} is underutilized (avg CPU {cpu_util}%). Suggest: Stop or resize.",
                    "current_type": curr_type,
                    "proposed_type": ""
                }
        elif cpu_util is not None and cpu_util > 80:
            curr_type, rec_type = recommend_machine_type(machine_type, cpu_util)
            if rec_type:
                return {
                    "text": f"VM '{name}' in {zone} is highly utilized (avg CPU {cpu_util}%). Suggest: Resize to {rec_type}.",
                    "current_type": curr_type,
                    "proposed_type": rec_type
                }
            else:
                return {
                    "text": f"VM '{name}' in {zone} is highly utilized (avg CPU {cpu_util}%). Suggest: Consider upgrading.",
                    "current_type": curr_type,
                    "proposed_type": ""
                }
    elif status == "TERMINATED":
        # Only suggest delete if stopped for > 50 days
        days_stopped = vm.get("daysStopped")
        try:
            days_stopped_val = int(days_stopped)
        except Exception:
            days_stopped_val = None
        if days_stopped_val is not None and days_stopped_val > 50:
            return {
                "text": f"VM '{name}' in {zone} is terminated for {days_stopped_val} days. Suggest: Delete if not needed.",
                "current_type": machine_type,
                "proposed_type": ""
            }
    return None

def analyze_vms(project_id, vms, days=7):
    cpu_map = fetch_vms_cpu_utilization_batch(project_id, vms, days=days)
    suggestions = []
    for vm in vms:
        name = vm.get("name")
        zone = vm.get("zone")
        status = vm.get("status")
        machine_type = vm.get("machineType", "")
        cpu_util = None
        if status == "RUNNING" and name and zone:
            cpu_util = cpu_map.get((name, zone))
        suggestion = suggest_vm_actions(
            {"name": name, "zone": zone, "status": status, "machine_type": machine_type},
            cpu_util
        )
        if suggestion:
            suggestions.append({
                "vm": name,
                "zone": zone,
                "status": status,
                "cpu_util": cpu_util,
                "suggestion": suggestion["text"],
                "current_type": suggestion.get("current_type", ""),
                "proposed_type": suggestion.get("proposed_type", "")
            })
    return suggestions

def get_vm_recommendations_recommender(project_id, zone):
    """
    Fetch VM recommendations from GCP Recommender API for a given project and zone.
    The project_id is passed from the UI and used in the API call, not from default credentials.
    """
    from googleapiclient.discovery import build
    from google.auth import default
    try:
        credentials, _ = default()
        service = build("recommender", "v1", credentials=credentials)
        recommender_id = "google.compute.instance.MachineTypeRecommender"
        parent = f"projects/{project_id}/locations/{zone}/recommenders/{recommender_id}"
        print(f"[RECOMMENDER DEBUG] (UI project_id) Fetching recommendations for project: {project_id}, zone: {zone}")
        print(f"[RECOMMENDER DEBUG] Parent path: {parent}")
        response = service.projects().locations().recommenders().recommendations().list(parent=parent).execute()
        recs = []
        for rec in response.get("recommendations", []):
            content = rec.get("content", {})
            op_groups = content.get("operationGroups", [])
            current_type = ""
            proposed_type = ""
            instance_name = ""
            for group in op_groups:
                for op in group.get("operations", []):
                    if op.get("path") == "/machineType":
                        current_type = op.get("resource", "")
                        proposed_type = op.get("value", "")
                    if op.get("path") == "/":
                        # Try to extract instance name from resource path
                        resource_path = op.get("resource", "")
                        if "/instances/" in resource_path:
                            instance_name = resource_path.split("/instances/")[-1]
            # Fallback: try to extract instance name from current_type
            if not instance_name and "/instances/" in current_type:
                instance_name = current_type.split("/instances/")[-1]
            # Cost savings
            cost_saving = ""
            impact = rec.get("primaryImpact", {})
            if impact.get("category") == "COST":
                try:
                    cost_saving = impact["costProjection"]["cost"]["units"]
                    if "nanos" in impact["costProjection"]["cost"]:
                        nanos = impact["costProjection"]["cost"]["nanos"]
                        cost_saving = f"${float(cost_saving) + nanos / 1e9:.2f} (monthly)"
                    else:
                        cost_saving = f"${cost_saving} (monthly)"
                except Exception:
                    cost_saving = ""
            recs.append({
                "text": rec.get("description", ""),
                "type": "cost",
                "severity": rec.get("priority", "medium"),
                "resource": rec.get("name", ""),
                "instance_name": instance_name,
                "rationale": rec.get("description", ""),
                "current_type": current_type.split("/machineTypes/")[-1] if "/machineTypes/" in current_type else current_type,
                "proposed_type": proposed_type.split("/machineTypes/")[-1] if "/machineTypes/" in proposed_type else proposed_type,
                "cost_saving": cost_saving
            })
        print(f"[RECOMMENDER DEBUG] Got {len(recs)} recommendations from Recommender API for project: {project_id}")
        return recs
    except Exception as e:
        import traceback
        print(f"[Recommender API] Exception for project {project_id}: {e}\n{traceback.format_exc()}")
        return [{
            "text": f"Recommender API error: {e}",
            "type": "error",
            "severity": "high",
            "resource": "",
            "rationale": ""
        }]

def get_vm_recommendations(vms, project_id=None):
    """
    Analyze VM data and return actionable recommendations using real utilization or GCP Recommender API.
    """
    import os
    use_recommender = os.getenv("USE_GCP_RECOMMENDER", "false").lower() == "true"
    if use_recommender:
        # Fetch recommendations from all unique zones in the VM list
        zones = sorted(set(vm["zone"] for vm in vms if vm.get("zone")))
        all_recs = []
        for zone in zones:
            recs = get_vm_recommendations_recommender(project_id, zone)
            all_recs.extend(recs)
        return all_recs
    if not project_id:
        project_id = os.getenv("GCP_PROJECT_ID")
    suggestions = analyze_vms(project_id, vms, days=7)
    recommendations = []
    for s in suggestions:
        text = s["suggestion"]
        severity = "medium"
        if "highly utilized" in text:
            severity = "high"
        elif "terminated" in text:
            severity = "low"
        rec = {
            "text": text,
            "type": "cost" if "underutilized" in text or "stop" in text else "performance",
            "severity": severity,
            "resource": s["vm"],
            "rationale": f"Status: {s['status']}, Avg CPU: {s['cpu_util']}" if s["cpu_util"] is not None else f"Status: {s['status']}"
        }
        if s.get("current_type") and s.get("proposed_type"):
            rec["current_type"] = s["current_type"]
            rec["proposed_type"] = s["proposed_type"]
        recommendations.append(rec)
    if not recommendations:
        recommendations.append({
            "text": "No optimization recommendations found for current VMs.",
            "type": "info",
            "severity": "info",
            "resource": "",
            "rationale": ""
        })
    return recommendations
