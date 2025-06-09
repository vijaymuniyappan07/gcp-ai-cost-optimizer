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
            print(f"[RECOMMENDER DEBUG] Full recommendation object:\n{rec}\n")
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
            # Extract detailed rationale from insights if available
            rationale = rec.get("description", "")
            insights = rec.get("associatedInsights", [])
            print(f"[RECOMMENDER DEBUG] associatedInsights for {instance_name}: {insights}")
            # Try to fetch insight details for a better rationale
            from googleapiclient.discovery import build as build_insight
            try:
                credentials, _ = default()
                insight_service = build_insight("recommender", "v1", credentials=credentials)
                for insight_ref in insights:
                    insight_id = insight_ref.get("insight")
                    if insight_id:
                        print(f"[RECOMMENDER DEBUG] Fetching insight: {insight_id}")
                        try:
                            insight_obj = insight_service.projects().locations().insightTypes().insights().get(name=insight_id).execute()
                            # Try to use description or content
                            if "description" in insight_obj and insight_obj["description"]:
                                rationale = insight_obj["description"]
                            elif "content" in insight_obj and isinstance(insight_obj["content"], dict):
                                for k, v in insight_obj["content"].items():
                                    if isinstance(v, str) and "utilization" in v:
                                        rationale = v
                                    if isinstance(v, dict):
                                        for subk, subv in v.items():
                                            if isinstance(subv, str) and "utilization" in subv:
                                                rationale = subv
                                    if isinstance(v, list):
                                        for subv in v:
                                            if isinstance(subv, str) and "utilization" in subv:
                                                rationale = subv
                        except Exception as e:
                            print(f"[RECOMMENDER DEBUG] Could not fetch insight {insight_id}: {e}")
            except Exception as e:
                print(f"[RECOMMENDER DEBUG] Could not build insight service: {e}")
            recs.append({
                "text": rec.get("description", ""),
                "type": "cost",
                "severity": rec.get("priority", "medium"),
                "resource": rec.get("name", ""),
                "instance_name": instance_name,
                "rationale": rationale,
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
# --- Cloud SQL Recommendations ---

def analyze_cloudsql_instances(instances):
    """
    Analyze Cloud SQL instances and return actionable recommendations.
    """
    recommendations = []
    for inst in instances:
        name = inst.get("name", "")
        region = inst.get("region", "")
        tier = inst.get("tier", "")
        state = inst.get("state", "")
        data_disk_size = inst.get("dataDiskSizeGb", 0)
        storage_auto_resize = inst.get("storageAutoResize", False)
        pricing_plan = inst.get("pricingPlan", "")
        db_version = inst.get("databaseVersion", "")
        creation_time = inst.get("creationTime", "")
        rationale = []
        # Recommend enabling storage auto-resize if not enabled
        if not storage_auto_resize:
            recommendations.append({
                "text": f"Cloud SQL instance '{name}' in {region} does not have storage auto-resize enabled. Enable it to avoid outages.",
                "type": "reliability",
                "severity": "medium",
                "resource": name,
                "rationale": "Storage auto-resize is recommended to prevent downtime when disk is full."
            })
        # Recommend upgrading old database versions
        if db_version and ("MYSQL_5_6" in db_version or "POSTGRES_9" in db_version):
            recommendations.append({
                "text": f"Cloud SQL instance '{name}' in {region} is running an old database version ({db_version}). Upgrade to a supported version.",
                "type": "security",
                "severity": "high",
                "resource": name,
                "rationale": f"Database version {db_version} is deprecated or soon to be unsupported."
            })
        # Recommend resizing if disk is very large and instance is small
        try:
            disk_gb = float(data_disk_size)
        except Exception:
            disk_gb = 0
        if disk_gb > 500 and "db-f1-micro" in tier:
            recommendations.append({
                "text": f"Cloud SQL instance '{name}' in {region} has a large disk ({disk_gb}GB) but is using a micro tier ({tier}). Consider resizing for better performance.",
                "type": "performance",
                "severity": "medium",
                "resource": name,
                "rationale": f"Large disk on a micro instance may cause performance issues."
            })
        # Recommend stopping or deleting stopped/terminated instances
        if state in ("STOPPED", "TERMINATED"):
            recommendations.append({
                "text": f"Cloud SQL instance '{name}' in {region} is {state.lower()}. Consider deleting if not needed.",
                "type": "cost",
                "severity": "low",
                "resource": name,
                "rationale": f"Stopped/terminated instances may still incur storage costs."
            })
        # Recommend reviewing pricing plan
        if pricing_plan and pricing_plan.lower() == "per_use":
            recommendations.append({
                "text": f"Cloud SQL instance '{name}' in {region} is on a per-use pricing plan. Review if this is optimal for your workload.",
                "type": "cost",
                "severity": "medium",
                "resource": name,
                "rationale": "Per-use pricing may be more expensive for always-on workloads."
            })
    if not recommendations:
        recommendations.append({
            "text": "No optimization recommendations found for current Cloud SQL instances.",
            "type": "info",
            "severity": "info",
            "resource": "",
            "rationale": ""
        })
    return recommendations

def get_cloudsql_recommendations(instances, project_id=None):
    """
    Analyze Cloud SQL data and return actionable recommendations.
    """
    return analyze_cloudsql_instances(instances)

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
