class GCPClient:
    """
    Stub class for handling GCP API calls (Compute, SQL, GKE, Filestore, Storage).
    """

    def __init__(self, credentials):
        """
        Initialize the GCP client with provided credentials.
        """
        self.credentials = credentials

    def list_vms(self):
        """
        Placeholder method for listing VMs.
        """
        pass

    def list_cloudsql_instances(self):
        """
        Placeholder method for listing Cloud SQL instances.
        """
        pass

    def list_gke_clusters(self):
        """
        Placeholder method for listing GKE clusters.
        """
        pass

    def list_filestore_instances(self):
        """
        Placeholder method for listing Filestore instances.
        """
        pass

    def list_storage_buckets(self):
        """
        Placeholder method for listing Cloud Storage buckets.
        """
        pass
