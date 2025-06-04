import os
from dotenv import load_dotenv
from google.auth.exceptions import DefaultCredentialsError
from google.auth import load_credentials_from_file
from googleapiclient.discovery import build

def load_gcp_credentials():
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

def validate_gcp_credentials():
    """
    Attempts to use the loaded credentials to make a simple GCP API call.
    Returns (success: bool, message: str)
    """
    try:
        creds = load_gcp_credentials()
        # Try listing GCP projects as a simple check
        service = build("cloudresourcemanager", "v1", credentials=creds)
        request = service.projects().list(pageSize=1)
        response = request.execute()
        return True, "GCP credentials are valid."
    except FileNotFoundError as e:
        return False, f"Credentials file error: {e}"
    except DefaultCredentialsError as e:
        return False, f"Credentials error: {e}"
    except Exception as e:
        return False, f"GCP API call failed: {e}"
