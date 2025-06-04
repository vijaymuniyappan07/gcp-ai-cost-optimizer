import os
from dotenv import load_dotenv
from google.auth import default, load_credentials_from_file
from typing import Any

def load_gcp_credentials() -> Any:
    """
    Loads GCP credentials from the path specified in the .env file.
    Returns a credentials object usable by Google Cloud SDKs.
    """
    load_dotenv()
    cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not cred_path or not os.path.exists(cred_path):
        raise FileNotFoundError(
            "GCP credentials file not found. Set GOOGLE_APPLICATION_CREDENTIALS in your .env."
        )
    credentials, project = load_credentials_from_file(cred_path)
    return credentials
