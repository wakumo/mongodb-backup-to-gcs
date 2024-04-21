import base64
import json
import os
import subprocess
import tempfile
from datetime import datetime, timedelta, timezone

from google.cloud import storage
from google.oauth2 import service_account

# Configuration from environment variables
MONGODB_HOST = os.getenv("MONGODB_HOST", "localhost")
BACKUP_FILE_PREFIX = os.getenv("BACKUP_FILE_PREFIX", "backup")
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
GCP_SERVICE_ACCOUNT_KEY_BASE64 = os.getenv("GCP_SERVICE_ACCOUNT_KEY_BASE64")
MONGODUMP_OPTS = os.getenv("MONGODUMP_OPTS", "")


def log(message):
    print(f"{datetime.now()}: {message}", flush=True)


def backup_mongodb_to_gcs():
    # Create a secure temporary file for the backup
    with tempfile.NamedTemporaryFile(suffix=".gz", delete=True) as tmpfile:
        backup_filepath = tmpfile.name
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        backup_filename = f"{BACKUP_FILE_PREFIX}-{timestamp}.gz"
        # Run the mongodump command to backup and compress using gzip
        dump_cmd = f"mongodump --host={MONGODB_HOST} --archive={backup_filepath} --gzip {MONGODUMP_OPTS}"
        log(f"Execute({datetime.now()}): {dump_cmd}")
        try:
            subprocess.run(dump_cmd, shell=True, check=True)
            file_size = os.path.getsize(backup_filepath)
            log(
                f"...done({datetime.now()}), file size: {file_size / (1024 * 1024):.2f} MB"
            )
            upload_to_gcs(backup_filepath, backup_filename)
        except subprocess.CalledProcessError as e:
            log(f"...error({datetime.now()}): {e}")
            return


def get_storage_client():
    # decode base64 GCP_SERVICE_ACCOUNT_KEY_BASE64 and parse json
    service_account_key = json.loads(
        base64.b64decode(GCP_SERVICE_ACCOUNT_KEY_BASE64).decode("utf-8")
    )
    credentials = service_account.Credentials.from_service_account_info(
        service_account_key
    )
    storage_client = storage.Client(project=GCP_PROJECT_ID, credentials=credentials)
    return storage_client


def list_bucket():
    storage_client = get_storage_client()
    bucket = storage_client.bucket(GCS_BUCKET_NAME)
    blobs = bucket.list_blobs()
    for blob in blobs:
        log(blob.name)


def prune_bucket(days=7, minimum_backups=7):
    log(f"Prune bucket days:{days} minimum_backups:{minimum_backups}")
    storage_client = get_storage_client()
    bucket = storage_client.bucket(GCS_BUCKET_NAME)
    blobs = list(bucket.list_blobs())
    if len(blobs) <= minimum_backups:
        log(f"Do not prune if not enough backups {len(blobs)}/{minimum_backups}")
        return
    cutoff_date = datetime.now(timezone.utc) - timedelta(
        days=days
    )  # Include timezone information
    for blob in blobs:
        if blob.time_created < cutoff_date:
            blob.delete()
            log(f"Deleted {blob.name}")


def upload_to_gcs(file_path, name):
    log(f"Upload to GCS {file_path} {name}")
    storage_client = get_storage_client()
    bucket = storage_client.bucket(GCS_BUCKET_NAME)

    blob = bucket.blob(name)

    blob.upload_from_filename(file_path, timeout=20 * 60)
    log(f"A file {file_path} has been uploaded to {GCS_BUCKET_NAME}.")


if __name__ == "__main__":
    backup_mongodb_to_gcs()
    prune_bucket()
