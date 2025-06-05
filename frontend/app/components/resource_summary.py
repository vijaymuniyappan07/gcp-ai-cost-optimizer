import requests
import os
from dotenv import load_dotenv

load_dotenv()
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000")

class ResourceSummary:
    """
    Component for displaying a summary of VM resources from the backend API.
    """

    def fetch_vm_data(self):
        """
        Fetches VM data from the backend /resources/vms endpoint.
        Returns a list of VMs or an error message.
        """
        try:
            url = f"{BACKEND_API_URL}/resources/vms"
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            return data.get("vms", [])
        except Exception as e:
            return f"Error fetching VM data: {e}"

    def render(self):
        """
        Renders the VM summary as HTML.
        """
        vms = self.fetch_vm_data()
        if isinstance(vms, str):
            # Error message
            return f"<div class='error'>{vms}</div>"
        if not vms:
            return "<div>No VMs found.</div>"
        html = "<div><h2>VMs (Compute Engine)</h2><table border='1' cellpadding='5'><tr><th>Name</th><th>Status</th><th>Zone</th><th>Machine Type</th></tr>"
        for vm in vms:
            html += f"<tr><td>{vm.get('name')}</td><td>{vm.get('status')}</td><td>{vm.get('zone')}</td><td>{vm.get('machineType')}</td></tr>"
        html += "</table></div>"
        return html
